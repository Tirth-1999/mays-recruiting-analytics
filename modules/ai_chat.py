"""
AI Chat Assistant Page Module
Natural language interface to query the Mays Analytics Platform
"""

import streamlit as st
from datetime import datetime

# Import utilities
from utils import auth
from utils.ai_chat import (
    GeminiClient,
    VectorStore,
    QueryProcessor,
    ChatHistory,
    RateLimiter
)


class ChatManager:
    """Manages chat state and interactions."""
    
    def __init__(self):
        """Initialize chat manager."""
        self.history = ChatHistory()
        
        # Suggested queries based on query type
        self.suggested_queries = {
            'data_query': [
                "Compare this with last year",
                "Show me the same for a different program",
                "What's the trend over time?",
                "Break this down by cohort"
            ],
            'navigation': [
                "How do I export this data?",
                "Where can I see detailed metrics?",
                "Show me related analytics",
                "What filters are available?"
            ],
            'help': [
                "How many MBA applications in 2026?",
                "Compare MBA vs MS ACCT enrollments",
                "What's the cost per inquiry for all programs?",
                "Where can I see year-over-year comparisons?"
            ],
            'conversational': [
                "Tell me more about this",
                "How does this compare to other programs?",
                "What should I look at next?",
                "Show me the data"
            ]
        }
        
        # Initialize rate limiter
        if 'rate_limiter' not in st.session_state:
            st.session_state.rate_limiter = RateLimiter(
                per_user_limit=10,
                per_user_window=60,
                global_limit=100,
                global_window=60
            )
        
        # Initialize session state
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        if 'chat_conversation_id' not in st.session_state:
            st.session_state.chat_conversation_id = ChatHistory.generate_conversation_id()
        
        if 'chat_processor' not in st.session_state:
            try:
                st.session_state.chat_processor = QueryProcessor()
            except Exception as e:
                st.session_state.chat_processor = None
                # Capture full error details
                import traceback
                error_str = str(e) if str(e) else repr(e)
                error_type = type(e).__name__
                error_trace = traceback.format_exc()
                st.session_state.chat_error = f"{error_type}: {error_str}\n\nFull traceback:\n{error_trace}"
    
    def get_suggested_queries(self, query_type: str, limit: int = 3):
        """Get suggested follow-up queries based on query type."""
        suggestions = self.suggested_queries.get(query_type, self.suggested_queries['help'])
        return suggestions[:limit]
    
    def send_message(self, user_message: str, user_id: int):
        """Process and send user message."""
        if not user_message.strip():
            return
        
        # Check rate limit
        limiter = st.session_state.rate_limiter
        rate_status = limiter.check_rate_limit(user_id)
        
        if not rate_status['allowed']:
            # Rate limit exceeded
            error_message = limiter.get_wait_message(
                rate_status['reset_seconds'],
                rate_status['limit_type']
            )
            
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': f"⚠️ {error_message}",
                'timestamp': datetime.now().isoformat(),
                'error': True,
                'rate_limited': True
            })
            return
        
        # Record request for rate limiting
        limiter.record_request(user_id)
        
        # Add user message to UI
        st.session_state.chat_messages.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Save user message to database
        conversation_id = st.session_state.chat_conversation_id
        self.history.save_message(
            user_id=user_id,
            conversation_id=conversation_id,
            message=user_message,
            role='user'
        )
        
        # Get conversation context
        context = self.history.get_conversation_context(user_id, conversation_id, limit=3)
        
        # Process query
        try:
            processor = st.session_state.chat_processor
            if processor is None:
                raise Exception("Chat processor not initialized. Please check API configuration.")
            
            result = processor.process_query(
                user_message, 
                context,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # Add assistant response to UI
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': result['response'],
                'timestamp': datetime.now().isoformat(),
                'query_type': result.get('query_type'),
                'sql_query': result.get('sql_query'),
                'tokens_used': result.get('tokens_used', 0)
            })
            
            # Save assistant response to database
            chat_id = self.history.save_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message=result['response'],
                role='assistant',
                tokens_used=result.get('tokens_used', 0),
                query_type=result.get('query_type'),
                sql_query=result.get('sql_query')
            )
            
            # Store chat_id in the message for feedback
            st.session_state.chat_messages[-1]['chat_id'] = chat_id
            
        except Exception as e:
            error_message = f"I encountered an error: {str(e)}\n\nPlease try again or rephrase your question."
            
            # Log error for monitoring
            import traceback
            error_details = {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'query': user_message,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            print(f"❌ Chat Error: {error_details}")
            
            # Provide helpful suggestions based on error type
            if "API" in str(e) or "quota" in str(e).lower():
                error_message = "⚠️ I'm having trouble connecting to my AI service. This might be temporary.\n\n**What you can do:**\n- Wait a moment and try again\n- Try a simpler question\n- Check the Data Explorer page for raw data access"
            elif "database" in str(e).lower() or "sql" in str(e).lower():
                error_message = "⚠️ I had trouble accessing the data.\n\n**Try these instead:**\n- 'How many MBA applications in 2026?'\n- 'Show me inquiries for MS ACCT'\n- 'Where can I see year-over-year comparisons?'"
            elif "timeout" in str(e).lower():
                error_message = "⏱️ That query took too long to process.\n\n**Try:**\n- Simplifying your question\n- Asking about a specific program or year\n- Breaking it into smaller questions"
            
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': error_message,
                'timestamp': datetime.now().isoformat(),
                'error': True
            })
    
    def clear_conversation(self):
        """Start a new conversation."""
        st.session_state.chat_messages = []
        st.session_state.chat_conversation_id = ChatHistory.generate_conversation_id()
    
    def load_conversation(self, user_id: int, conversation_id: str):
        """Load a previous conversation."""
        messages = self.history.get_conversation(user_id, conversation_id)
        
        st.session_state.chat_messages = [
            {
                'role': msg['role'],
                'content': msg['message'],
                'timestamp': msg['timestamp'],
                'query_type': msg.get('query_type'),
                'sql_query': msg.get('sql_query'),
                'tokens_used': msg.get('tokens_used', 0)
            }
            for msg in messages
        ]
        
        st.session_state.chat_conversation_id = conversation_id


def render():
    """Render the AI Chat Assistant page"""
    
    # Initialize auth
    auth.init_session_state()
    
    # Check authentication
    if not auth.is_authenticated():
        st.info("Please sign in with your Google account to use the AI Chat Assistant")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            auth_url = auth.get_authorization_url()
            st.link_button("Sign in with Google", auth_url, use_container_width=True, type="primary")
        return
    
    # Check for configuration errors
    if 'chat_error' in st.session_state:
        st.error("⚠️ AI Chat Assistant Configuration Error")
        
        error_msg = st.session_state.chat_error
        
        # Show the actual error for debugging
        with st.expander("🔍 Error Details", expanded=True):
            st.code(error_msg, language="text")
        
        # Provide specific guidance based on error
        if "api_key" in error_msg.lower() or "gemini" in error_msg.lower() or "secret" in error_msg.lower():
            st.markdown("""
            ### 🔑 Gemini API Key Configuration Required
            
            The AI Chat Assistant requires a Google Gemini API key to function. 
            
            **For Streamlit Cloud (Production):**
            1. Go to your app dashboard on Streamlit Cloud
            2. Click on "⚙️ Settings" → "Secrets"
            3. Add the following configuration:
            
            ```toml
            [gemini]
            api_key = "YOUR_ACTUAL_GEMINI_API_KEY"
            
            [chat]
            rate_limit_requests = 10
            rate_limit_window = 60
            max_conversation_history = 5
            token_limit_per_query = 1000
            ```
            
            4. **Get your free API key:**
               - Visit: [Google AI Studio](https://makersuite.google.com/app/apikey)
               - Sign in with your Google account
               - Click "Create API Key"
               - Copy the key
            
            5. **Paste the key** in the secrets (replace `YOUR_ACTUAL_GEMINI_API_KEY`)
            6. **Save** the secrets
            7. Your app will automatically restart
            
            **For Local Development:**
            1. Create/edit `.streamlit/secrets.toml` in your project root
            2. Add the same configuration as above
            3. Restart your Streamlit app
            
            ---
            
            **Need Help?** Check the [AI Chat Deployment Guide](https://github.com/Tirth-1999/mays-recruiting-analytics/blob/main/docs/AI_CHAT_DEPLOYMENT.md)
            """)
        else:
            st.warning("**Unexpected Configuration Error**")
            st.info("Please check the error details above and verify your Streamlit secrets configuration.")
        
        return
    
    user = auth.get_current_user()
    
    # Initialize ChatManager with error handling
    try:
        manager = ChatManager()
    except Exception as e:
        import traceback
        st.error("⚠️ Failed to Initialize AI Chat Assistant")
        with st.expander("🔍 Initialization Error Details", expanded=True):
            st.code(f"{type(e).__name__}: {str(e) if str(e) else repr(e)}\n\nTraceback:\n{traceback.format_exc()}", language="text")
        st.info("This usually means there's a configuration issue. Please check the error details above.")
        return
    
    # Custom CSS
    st.markdown("""
    <style>
    .main .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Chrome-style tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        justify-content: center !important;
        background-color: transparent !important;
        padding: 0px 20px !important;
        border-bottom: none !important;
        margin-bottom: 30px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px !important;
        padding: 0px 32px !important;
        background-color: #f5f5f5 !important;
        border-radius: 8px 8px 0px 0px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        border-bottom: 3px solid transparent !important;
        color: #666 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #500000 !important;
        border-bottom: 3px solid #500000 !important;
    }
    
    /* Stats cards */
    .stats-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stats-value {
        font-size: 32px;
        font-weight: 700;
        color: #500000;
        margin-bottom: 8px;
    }
    
    .stats-label {
        font-size: 13px;
        font-weight: 500;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Scoped button colors - only for chat history conversation buttons */
    .stTabs [data-baseweb="tab-panel"] div[data-testid="stButton"] button[kind="secondary"]:disabled {
        background-color: #e8f5e9 !important;
        color: #2e7d32 !important;
        border: 1px solid #4caf50 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] div[data-testid="stButton"] button[kind="primary"]:not(:disabled) {
        background-color: #fff3e0 !important;
        color: #e65100 !important;
        border: 1px solid #ff9800 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Tabs directly after title (no How to Use, no divider)
    tab1, tab2, tab3 = st.tabs(["Current Conversation", "Chat History", "Settings & Privacy"])
    
    # ========================================================================
    # TAB 1: CURRENT CONVERSATION
    # ========================================================================
    with tab1:
        # Get rate limit status
        limiter = st.session_state.rate_limiter
        rate_status = limiter.check_rate_limit(user['user_id'])
        
        # Determine rate limit color and message
        if rate_status['remaining'] <= 2:
            rate_color = "#dc3545"  # Red
            rate_icon = "⚠️"
        elif rate_status['remaining'] <= 5:
            rate_color = "#ffc107"  # Yellow
            rate_icon = "⚡"
        else:
            rate_color = "#28a745"  # Green
            rate_icon = "✅"
        
        # Use columns for layout - 70/30 split
        col_header, col_buttons = st.columns([7, 3])
        
        with col_header:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 12px; border: 1px solid #e0e0e0; height: 90px; box-sizing: border-box;">
                <img src="{user['profile_picture']}" style="width: 50px; height: 50px; border-radius: 50%; border: 3px solid #500000; box-shadow: 0 2px 8px rgba(80,0,0,0.2);">
                <div style="flex: 1;">
                    <div style="font-size: 18px; font-weight: 600; color: #500000;">💬 Conversation with AI Assistant</div>
                    <div style="font-size: 13px; color: #6c757d;">Chatting as {user['name']}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 12px; color: {rate_color}; font-weight: 600;">{rate_icon} {rate_status['remaining']}/{rate_status['user_limit']} queries left</div>
                    <div style="font-size: 10px; color: #6c757d;">Resets in {rate_status['reset_seconds']}s</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_buttons:
            if st.button("❓ Help", use_container_width=True, key="help_btn"):
                st.session_state.show_help = not st.session_state.get('show_help', False)
                st.rerun()
            
            if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary", key="clear_btn"):
                manager.clear_conversation()
                st.rerun()
        
        # Show help modal if requested
        if st.session_state.get('show_help', False):
            with st.expander("📚 Quick Help Guide", expanded=True):
                st.markdown("""
                ### How to Use the AI Chat Assistant
                
                **What can I ask?**
                - 📊 **Data Queries**: "How many MBA applications in 2026?"
                - 📈 **Comparisons**: "Compare MBA vs MS ACCT enrollments"
                - 💰 **Marketing**: "What's the cost per inquiry for all programs?"
                - 🧭 **Navigation**: "Where can I see year-over-year comparisons?"
                
                **Tips for Best Results:**
                - Be specific about programs (MBA, MS ACCT, etc.)
                - Include time periods (2026, last year, etc.)
                - Ask one question at a time
                - Use follow-up questions to refine results
                
                **Example Queries:**
                - "Show me enrolled students for MBA in 2026"
                - "What's the conversion rate from inquiries to applications?"
                - "Compare marketing spend across all programs"
                - "How do I create a performance report?"
                
                **Need More Help?**
                - Check the [User Guide](docs/AI_CHAT_ASSISTANT.md) for detailed examples
                - Use the suggested queries after each response
                - Try the example queries when starting a new conversation
                
                **Rate Limits:**
                - You can send up to 10 queries per minute
                - Queries reset every 60 seconds
                - Check the header for remaining queries
                """)
                
                if st.button("Close Help", use_container_width=True):
                    st.session_state.show_help = False
                    st.rerun()
        
        # Chat messages container (no divider before this)
        messages_container = st.container(height=450, border=True)
        
        with messages_container:
            if not st.session_state.chat_messages:
                st.info("Welcome! Ask me anything about the Mays Analytics Platform.")
                
                # Show example queries on first open
                st.markdown("**💡 Try these example queries:**")
                
                example_queries = [
                    "How many MBA applications in 2026?",
                    "Compare MBA vs MS ACCT enrollments",
                    "What's the cost per inquiry for all programs?",
                    "Where can I see year-over-year comparisons?"
                ]
                
                cols = st.columns(2)
                for idx, example in enumerate(example_queries):
                    with cols[idx % 2]:
                        if st.button(f"📝 {example}", key=f"example_{idx}", use_container_width=True):
                            st.session_state.suggested_query = example
                            st.rerun()
            else:
                for msg in st.session_state.chat_messages:
                    timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%I:%M %p')
                    
                    if msg['role'] == 'user':
                        col1, col2 = st.columns([1, 20])
                        with col1:
                            st.markdown(f'<img src="{user["profile_picture"]}" style="width: 35px; height: 35px; border-radius: 50%; border: 2px solid #500000;">', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #500000 0%, #700000 100%); color: white; padding: 12px 16px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(80,0,0,0.2);">
                                <div style="margin-bottom: 5px;">{msg['content']}</div>
                                <div style="font-size: 10px; opacity: 0.8;">{timestamp}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        col1, col2 = st.columns([1, 20])
                        with col1:
                            st.markdown('<div style="width: 35px; height: 35px; border-radius: 50%; background: #500000; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">AI</div>', unsafe_allow_html=True)
                        with col2:
                            # Keep everything in one container
                            msg_container = st.container()
                            with msg_container:
                                st.write(msg['content'])
                                st.caption(f"{timestamp} • {msg.get('query_type', 'unknown')} • {msg.get('tokens_used', 0)} tokens")
                                
                                # Feedback buttons (thumbs up/down)
                                if not msg.get('error') and not msg.get('rate_limited') and msg.get('chat_id'):
                                    feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 10])
                                    
                                    msg_id = f"{msg['timestamp']}_{msg['role']}"
                                    feedback_key = f"feedback_{msg_id}"
                                    
                                    # Check if feedback already given
                                    if feedback_key not in st.session_state:
                                        st.session_state[feedback_key] = None
                                    
                                    with feedback_col1:
                                        if st.session_state[feedback_key] == 'positive':
                                            st.button("👍", key=f"thumbs_up_{msg_id}", disabled=True, use_container_width=True)
                                        else:
                                            if st.button("👍", key=f"thumbs_up_{msg_id}", use_container_width=True):
                                                st.session_state[feedback_key] = 'positive'
                                                # Save feedback to database
                                                manager.history.save_feedback(
                                                    user_id=user['user_id'],
                                                    chat_id=msg['chat_id'],
                                                    conversation_id=st.session_state.chat_conversation_id,
                                                    rating=1
                                                )
                                                st.rerun()
                                    
                                    with feedback_col2:
                                        if st.session_state[feedback_key] == 'negative':
                                            st.button("👎", key=f"thumbs_down_{msg_id}", disabled=True, use_container_width=True)
                                        else:
                                            if st.button("👎", key=f"thumbs_down_{msg_id}", use_container_width=True):
                                                st.session_state[feedback_key] = 'negative'
                                                # Save feedback to database
                                                manager.history.save_feedback(
                                                    user_id=user['user_id'],
                                                    chat_id=msg['chat_id'],
                                                    conversation_id=st.session_state.chat_conversation_id,
                                                    rating=-1
                                                )
                                                st.rerun()
                                
                                if msg.get('sql_query'):
                                    with st.expander("View SQL Query"):
                                        st.code(msg['sql_query'], language='sql')
                                
                                # Suggested queries (only for last bot message)
                                if msg == st.session_state.chat_messages[-1] and not msg.get('error'):
                                    query_type = msg.get('query_type', 'help')
                                    suggestions = manager.get_suggested_queries(query_type, limit=3)
                                    
                                    if suggestions:
                                        st.caption("💡 Try asking:")
                                        suggest_cols = st.columns(len(suggestions))
                                        for idx, suggestion in enumerate(suggestions):
                                            with suggest_cols[idx]:
                                                if st.button(suggestion, key=f"suggest_{idx}_{msg['timestamp']}", use_container_width=True):
                                                    # Add suggestion to input (we'll handle this via session state)
                                                    st.session_state.suggested_query = suggestion
                                                    st.rerun()
        
        # Input area
        input_container = st.container(border=True)
        with input_container:
            # Check if there's a suggested query to pre-fill
            default_value = st.session_state.get('suggested_query', '')
            if default_value:
                # Clear it after using
                st.session_state.suggested_query = ''
            
            with st.form(key="chat_form", clear_on_submit=True):
                col_input, col_send = st.columns([4, 1])
                with col_input:
                    user_input = st.text_input("Message", value=default_value, placeholder="Type your question here...", label_visibility="collapsed")
                with col_send:
                    submit = st.form_submit_button("Send", use_container_width=True, type="primary")
                if submit and user_input:
                    with st.spinner("Thinking..."):
                        manager.send_message(user_input, user['user_id'])
                    st.rerun()
    
    # ========================================================================
    # TAB 2: CHAT HISTORY
    # ========================================================================
    with tab2:
        # Stats cards
        stats = manager.history.get_user_stats(user['user_id'])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{stats["conversation_count"]}</div><div class="stats-label">Conversations</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{stats["total_messages"]}</div><div class="stats-label">Messages</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{stats["total_tokens"]:,}</div><div class="stats-label">Tokens Used</div></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Search and Export row
        col_search, col_export = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("🔍 Search messages", placeholder="Search across all conversations...", label_visibility="collapsed")
        with col_export:
            if st.button("📥 Export All", use_container_width=True, type="secondary"):
                try:
                    json_data = manager.history.export_all_conversations_json(user['user_id'])
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
        
        # Show search results if searching
        if search_query:
            st.markdown(f"<h3 style='text-align: center; color: #500000;'>Search Results for '{search_query}'</h3>", unsafe_allow_html=True)
            search_results = manager.history.search_messages(user['user_id'], search_query)
            
            if search_results:
                search_container = st.container(height=400, border=True)
                with search_container:
                    for result in search_results[:20]:
                        timestamp = datetime.fromisoformat(result['timestamp']).strftime('%b %d, %I:%M %p')
                        role_icon = "👤" if result['role'] == 'user' else "🤖"
                        st.markdown(f"""
                        <div style="padding: 10px; margin-bottom: 10px; background: #f8f9fa; border-radius: 8px; border-left: 3px solid #500000;">
                            <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">{role_icon} {timestamp}</div>
                            <div>{result['message'][:200]}{'...' if len(result['message']) > 200 else ''}</div>
                        </div>
                        """, unsafe_allow_html=True)
                st.info(f"Showing {min(len(search_results), 20)} of {len(search_results)} results")
            else:
                st.info("No messages found matching your search.")
            
            st.divider()
        
        if 'selected_conv_id' not in st.session_state:
            st.session_state.selected_conv_id = None
        
        conversations = manager.history.get_user_conversations(user['user_id'])
        st.markdown("<h3 style='text-align: center; color: #500000;'>Recent Conversations</h3>", unsafe_allow_html=True)
        
        history_container = st.container(height=400, border=True)
        with history_container:
            if conversations:
                for conv in conversations[:10]:
                    conv_id = conv['conversation_id']
                    started_at = datetime.fromisoformat(conv['started_at']).strftime('%b %d, %I:%M %p')
                    message_count = conv['message_count']
                    preview = manager.history.get_conversation_preview(user['user_id'], conv_id)
                    preview_text = preview[:60] + "..." if preview and len(preview) > 60 else preview or "New conversation"
                    
                    is_current = conv_id == st.session_state.chat_conversation_id
                    is_selected = conv_id == st.session_state.selected_conv_id
                    
                    # Fix: Don't use type=None, just omit the type parameter
                    if is_current:
                        if st.button(f"{preview_text}\n{started_at} • {message_count} messages", key=f"conv_{conv_id}", use_container_width=True, disabled=True, type="secondary"):
                            pass
                    elif is_selected:
                        if st.button(f"{preview_text}\n{started_at} • {message_count} messages", key=f"conv_{conv_id}", use_container_width=True, type="primary"):
                            st.session_state.selected_conv_id = conv_id
                            st.rerun()
                    else:
                        if st.button(f"{preview_text}\n{started_at} • {message_count} messages", key=f"conv_{conv_id}", use_container_width=True):
                            st.session_state.selected_conv_id = conv_id
                            st.rerun()
            else:
                st.info("No previous conversations. Start chatting to create your first one!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Load Selected", use_container_width=True, type="primary", disabled=(st.session_state.selected_conv_id is None)):
                manager.load_conversation(user['user_id'], st.session_state.selected_conv_id)
                st.session_state.selected_conv_id = None
                st.rerun()
        with col2:
            if st.button("Delete Selected", use_container_width=True, type="secondary", disabled=(st.session_state.selected_conv_id is None)):
                if st.session_state.selected_conv_id:
                    deleted = manager.history.delete_conversation(user['user_id'], st.session_state.selected_conv_id)
                    st.session_state.selected_conv_id = None
                    st.success(f"Deleted {deleted} messages")
                    st.rerun()
        with col3:
            if st.button("New Conversation", use_container_width=True):
                manager.clear_conversation()
                st.session_state.selected_conv_id = None
                st.rerun()
    
    # ========================================================================
    # TAB 3: SETTINGS & PRIVACY
    # ========================================================================
    with tab3:
        # Center-align content
        st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-panel"]:nth-child(4) {
            display: flex;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab-panel"]:nth-child(4) > div {
            max-width: 1000px;
            width: 100%;
        }
        
        .divider-fancy {
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #500000 50%, transparent 100%);
            margin: 2.5rem 0;
            opacity: 0.3;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Data Retention Section
        st.markdown("<h4 style='text-align: center; color: #500000; margin-bottom: 1.5rem;'>Data Retention</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Automatic Cleanup**")
            st.write("Conversations older than 90 days are automatically deleted.")
            
            if st.button("🧹 Run Cleanup Now", use_container_width=True, type="secondary"):
                deleted = manager.history.cleanup_old_conversations(days=90)
                if deleted > 0:
                    st.success(f"Deleted {deleted} old messages (>90 days)")
                else:
                    st.info("No old messages to delete")
        
        with col2:
            st.markdown("**Export Your Data**")
            st.write("Download all your conversations in JSON format.")
            
            try:
                json_data = manager.history.export_all_conversations_json(user['user_id'])
                st.download_button(
                    label="📥 Download All Data",
                    data=json_data,
                    file_name=f"my_chat_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
        
        # Fancy divider
        st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)
        
        # Privacy Controls Section
        st.markdown("<h4 style='text-align: center; color: #500000; margin-bottom: 1.5rem;'>Privacy Controls</h4>", unsafe_allow_html=True)
        
        st.warning("⚠️ **Warning**: The actions below are permanent and cannot be undone.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Delete All Conversations**")
            st.write("Remove all your chat history from the system.")
            
            if 'confirm_delete_all' not in st.session_state:
                st.session_state.confirm_delete_all = False
            
            if not st.session_state.confirm_delete_all:
                if st.button("🗑️ Delete All History", use_container_width=True, type="secondary"):
                    st.session_state.confirm_delete_all = True
                    st.rerun()
            else:
                st.error("Are you sure? This will delete ALL your conversations.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, Delete All", use_container_width=True, type="primary"):
                        deleted = manager.history.delete_all_user_history(user['user_id'])
                        manager.clear_conversation()
                        st.session_state.confirm_delete_all = False
                        st.success(f"Deleted {deleted} messages")
                        st.rerun()
                with col_no:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_delete_all = False
                        st.rerun()
        
        with col2:
            st.markdown("**GDPR Data Deletion**")
            st.write("Request complete deletion of your data (GDPR compliance).")
            
            if 'confirm_gdpr_delete' not in st.session_state:
                st.session_state.confirm_gdpr_delete = False
            
            if not st.session_state.confirm_gdpr_delete:
                if st.button("🚫 Request Data Deletion", use_container_width=True, type="secondary"):
                    st.session_state.confirm_gdpr_delete = True
                    st.rerun()
            else:
                st.error("⚠️ GDPR Deletion: This will permanently delete ALL your chat data.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Confirm GDPR Deletion", use_container_width=True, type="primary"):
                        result = manager.history.delete_user_data(user['user_id'])
                        manager.clear_conversation()
                        st.session_state.confirm_gdpr_delete = False
                        st.success(f"✅ Deleted {result['messages_deleted']} messages from {result['conversations_deleted']} conversations")
                        st.rerun()
                with col_no:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_gdpr_delete = False
                        st.rerun()
        
        # Fancy divider
        st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)
        
        # Usage Statistics
        st.markdown("<h4 style='text-align: center; color: #500000; margin-bottom: 1.5rem;'>Your Usage Statistics</h4>", unsafe_allow_html=True)
        
        stats = manager.history.get_user_stats(user['user_id'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{stats["conversation_count"]}</div><div class="stats-label">Conversations</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{stats["total_messages"]}</div><div class="stats-label">Messages</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{stats["total_tokens"]:,}</div><div class="stats-label">Tokens Used</div></div>', unsafe_allow_html=True)
        
        # Fancy divider
        st.markdown('<div class="divider-fancy"></div>', unsafe_allow_html=True)
        
        # Feedback Analytics Section
        st.markdown("<h4 style='text-align: center; color: #500000; margin-bottom: 1.5rem;'>Feedback Analytics</h4>", unsafe_allow_html=True)
        
        # Overall feedback stats
        feedback_stats = manager.history.get_feedback_stats(days=30)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{feedback_stats["total_feedback"]}</div><div class="stats-label">Total Feedback</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{feedback_stats["positive"]}</div><div class="stats-label">👍 Positive</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{feedback_stats["negative"]}</div><div class="stats-label">👎 Negative</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stats-card"><div class="stats-value">{feedback_stats["satisfaction_rate"]:.1f}%</div><div class="stats-label">Satisfaction Rate</div></div>', unsafe_allow_html=True)
        
        # Feedback by query type
        if feedback_stats['total_feedback'] > 0:
            st.markdown("<p style='text-align: center; font-weight: 600; color: #500000; margin-top: 2.5rem; margin-bottom: 1.5rem; font-size: 16px;'>Feedback by Query Type (Last 30 Days)</p>", unsafe_allow_html=True)
            query_type_feedback = manager.history.get_feedback_by_query_type(days=30)
            
            if query_type_feedback:
                # Create a nice card layout for each query type
                for item in query_type_feedback:
                    rate = item['satisfaction_rate']
                    
                    # Determine color based on satisfaction rate
                    if rate >= 80:
                        bg_color = "#e8f5e9"
                        border_color = "#4caf50"
                        icon = "🟢"
                    elif rate >= 60:
                        bg_color = "#fff3e0"
                        border_color = "#ff9800"
                        icon = "🟡"
                    else:
                        bg_color = "#ffebee"
                        border_color = "#f44336"
                        icon = "🔴"
                    
                    st.markdown(f"""
                    <div style="background: {bg_color}; border-left: 4px solid {border_color}; border-radius: 8px; padding: 15px 20px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                        <div style="flex: 2;">
                            <div style="font-weight: 600; color: #500000; font-size: 15px; margin-bottom: 4px;">{item['query_type'].replace('_', ' ').title()}</div>
                            <div style="font-size: 13px; color: #6c757d;">{item['total_feedback']} total responses</div>
                        </div>
                        <div style="flex: 1; text-align: center;">
                            <div style="font-size: 13px; color: #6c757d; margin-bottom: 4px;">Feedback</div>
                            <div style="font-weight: 600; color: #333;">{item['positive']} 👍 / {item['negative']} 👎</div>
                        </div>
                        <div style="flex: 1; text-align: right;">
                            <div style="font-size: 24px; font-weight: 700; color: {border_color};">{icon} {rate:.1f}%</div>
                            <div style="font-size: 11px; color: #6c757d;">Satisfaction</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No feedback data available yet.")
        else:
            st.info("No feedback received yet. Feedback will appear here once users rate responses.")


if __name__ == "__main__":
    st.set_page_config(page_title="AI Chat Assistant", layout="wide")
    render()
