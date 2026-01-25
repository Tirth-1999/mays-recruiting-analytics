# AI Chatbot Assistant - Implementation Tasks

## Overview
Implementation tasks for the AI-powered chatbot assistant feature. Tasks are organized by phase and follow the requirements and design specifications.

**Feature**: AI Chatbot Assistant  
**Status**: Ready for Implementation  
**Estimated Duration**: 8 weeks  
**Priority**: High

---

## Phase 1: MVP with Gemini (Week 1-2)

### 1. Project Setup & Dependencies
- [ ] 1.1 Install required Python packages
  - `google-generativeai` for Gemini API
  - `chromadb` for vector storage
  - `sentence-transformers` for embeddings
  - `streamlit-chat` or `streamlit-extras` for chat UI components
- [ ] 1.2 Update `requirements.txt` with new dependencies
- [ ] 1.3 Create `.streamlit/secrets.toml.template` entry for Gemini API key
- [ ] 1.4 Add Gemini API key to Streamlit Cloud secrets

### 2. Database Migration
- [ ] 2.1 Create migration script `migrations/add_chat_history_table.py`
  - Create `chat_history` table with schema from design doc
  - Add indexes for user_id, conversation_id, timestamp
  - Add foreign key constraint to users table
- [ ] 2.2 Run migration on local database
- [ ] 2.3 Test migration rollback functionality
- [ ] 2.4 Document migration in `docs/TECHNICAL_GUIDE.md`

### 3. Backend Utilities - Gemini Client
- [ ] 3.1 Create `utils/ai_chat/` directory structure
- [ ] 3.2 Implement `utils/ai_chat/gemini_client.py`
  - GeminiClient class with API configuration
  - generate() method for text generation
  - Token counting functionality
  - Error handling and retry logic
  - Rate limiting (15 requests/minute for free tier)
- [ ] 3.3 Write unit tests for GeminiClient
- [ ] 3.4 Test API connection with sample prompts

### 4. Backend Utilities - Vector Store
- [ ] 4.1 Implement `utils/ai_chat/vector_store.py`
  - Initialize ChromaDB persistent client
  - Create schema_collection for database schema
  - Implement add_schema_embedding() method
  - Implement search_schema() method for semantic search
  - Add error handling for ChromaDB operations
- [ ] 4.2 Create schema embedding script
  - Extract schema from edulytix.db
  - Generate embeddings using sentence-transformers
  - Store in ChromaDB with metadata
- [ ] 4.3 Test semantic search with sample queries
- [ ] 4.4 Write unit tests for vector store operations

### 5. Backend Utilities - Query Processing
- [ ] 5.1 Implement `utils/ai_chat/prompts.py`
  - DATA_QUERY_PROMPT template
  - NAVIGATION_PROMPT template
  - HELP_PROMPT template
  - CONVERSATIONAL_PROMPT template
- [ ] 5.2 Implement `utils/ai_chat/sql_generator.py`
  - classify_query() function
  - generate_sql() function using Gemini
  - validate_sql() for security checks
  - execute_sql() with error handling
  - format_results() for response formatting
- [ ] 5.3 Write unit tests for query classification
- [ ] 5.4 Write unit tests for SQL validation
- [ ] 5.5 Test SQL generation with sample queries

### 6. Backend Utilities - Chat History
- [ ] 6.1 Implement `utils/ai_chat/chat_history.py`
  - ChatHistory class with database operations
  - save_message() method
  - get_conversation() method
  - get_user_conversations() method
  - delete_conversation() method
  - get_conversation_context() for RAG
- [ ] 6.2 Write unit tests for chat history operations
- [ ] 6.3 Test conversation retrieval and context building

### 7. UI Components - Floating Chat Button
- [ ] 7.1 Design chat button HTML/CSS
  - 60px circular button with maroon gradient
  - Chat icon (white)
  - Hover effects and animations
  - Position: bottom-right, 20px above back-to-top
  - Z-index: 999998
- [ ] 7.2 Implement authentication gate
  - Check `auth.is_authenticated()` before showing button
  - Hide button for unauthenticated users
  - Show tooltip "Sign in to use chat" on hover (optional)
- [ ] 7.3 Add click handler to open chat window
- [ ] 7.4 Test button on desktop and mobile

### 8. UI Components - Chat Window
- [ ] 8.1 Design chat window overlay
  - 400px × 600px on desktop
  - Full screen on mobile
  - Maroon gradient header matching platform theme
  - Scrollable message area
  - Input field with send button
- [ ] 8.2 Implement chat window header
  - User profile picture and name from OAuth
  - Clear conversation button
  - Close button
- [ ] 8.3 Implement message display area
  - User messages (right-aligned, light background)
  - Bot messages (left-aligned, white background)
  - Timestamps on each message
  - Copy button on bot responses
  - Auto-scroll to latest message
- [ ] 8.4 Implement input area
  - Text input field with placeholder
  - Send button (disabled when empty)
  - Enter key to send
  - Typing indicator while processing
- [ ] 8.5 Test chat window responsiveness

### 9. Main Chat Module
- [ ] 9.1 Create `modules/ai_chat.py`
  - render() function as main entry point
  - ChatManager class for state management
  - Integration with all utility modules
- [ ] 9.2 Implement authentication check
  - Use `auth.is_authenticated()` and `auth.get_current_user()`
  - Show sign-in prompt for unauthenticated users
  - Display user greeting for authenticated users
- [ ] 9.3 Implement message handling
  - Capture user input
  - Call QueryProcessor
  - Display bot response
  - Save to chat history
- [ ] 9.4 Implement session state management
  - Current conversation_id
  - Message history
  - Chat window open/closed state
- [ ] 9.5 Add error handling and user feedback
  - Show error messages for API failures
  - Display helpful suggestions for ambiguous queries
  - Handle rate limiting gracefully

### 10. Integration & Testing
- [ ] 10.1 Integrate chat module into `main_app.py`
  - Add chat button to all pages
  - Ensure consistent positioning
  - Test with existing OAuth flow
- [ ] 10.2 End-to-end testing
  - Test simple data queries ("How many MBA applications?")
  - Test with different programs and date ranges
  - Test error handling (invalid queries, API failures)
  - Test authentication gate (signed in vs signed out)
- [ ] 10.3 Performance testing
  - Measure response times
  - Check token usage per query
  - Test with multiple concurrent users (if possible)
- [ ] 10.4 User acceptance testing
  - Test with real users
  - Gather feedback on UI/UX
  - Identify common query patterns

### 11. Documentation
- [ ] 11.1 Update `docs/TECHNICAL_GUIDE.md`
  - Add AI Chat section
  - Document architecture and components
  - Explain query processing pipeline
- [ ] 11.2 Create user guide in `docs/AI_CHAT_GUIDE.md`
  - How to use the chat feature
  - Example queries
  - Tips for getting best results
- [ ] 11.3 Update `README.md`
  - Add AI Chat to features list
  - Add screenshot or demo GIF
- [ ] 11.4 Update `docs/CHANGELOG.md`
  - Add Phase 1 MVP release notes

---

## Phase 2: Chat History & Persistence (Week 3)

### 12. Chat History UI
- [ ] 12.1 Design conversation list sidebar
  - Show all user conversations
  - Display conversation preview (first message)
  - Show timestamp and message count
  - Highlight active conversation
- [ ] 12.2 Implement conversation switching
  - Click to load previous conversation
  - Maintain context when switching
  - Update UI to show loaded conversation
- [ ] 12.3 Add conversation management actions
  - Delete conversation button (with confirmation)
  - Clear all history button (with confirmation)
  - Rename conversation (optional)
- [ ] 12.4 Test conversation persistence
  - Create multiple conversations
  - Switch between conversations
  - Verify data integrity

### 13. Search & Export
- [ ] 13.1 Implement chat history search
  - Search input field in chat window
  - Search across all user conversations
  - Highlight matching messages
  - Filter by date range (optional)
- [ ] 13.2 Implement export functionality
  - Export single conversation to JSON
  - Export all history to JSON
  - Export to CSV format (optional)
  - Add download button in chat header
- [ ] 13.3 Test search and export
  - Search for specific keywords
  - Verify export file format
  - Test with large conversation history

### 14. Conversation Threading
- [ ] 14.1 Implement conversation grouping
  - Auto-generate conversation_id for new chats
  - Group related messages by conversation_id
  - Display conversation title (first user message)
- [ ] 14.2 Add "New Conversation" button
  - Start fresh conversation
  - Generate new conversation_id
  - Clear current message history in UI
- [ ] 14.3 Test conversation threading
  - Create multiple conversations
  - Verify messages are grouped correctly
  - Test conversation_id generation

### 15. Data Retention & Cleanup
- [ ] 15.1 Implement automatic cleanup script
  - Delete conversations older than 90 days (configurable)
  - Soft delete: mark as deleted, purge after 30 days
  - Run as scheduled task or on-demand
- [ ] 15.2 Add user privacy controls
  - Allow users to delete their data
  - Implement GDPR-compliant data deletion
  - Add confirmation dialogs
- [ ] 15.3 Test cleanup functionality
  - Verify old conversations are deleted
  - Test soft delete and purge
  - Ensure user data isolation

---

## Phase 3: Navigation Intelligence (Week 4)

### 16. Platform Knowledge Base
- [ ] 16.1 Create platform knowledge embeddings
  - Document all 6 platform pages (Home, Executive, Comparison, Marketing, Data Explorer, Predictive)
  - Include page descriptions, use cases, filters, metrics
  - Generate embeddings and store in ChromaDB
- [ ] 16.2 Create `platform_knowledge_collection` in ChromaDB
  - Store page metadata
  - Store filter descriptions
  - Store common workflows
- [ ] 16.3 Test semantic search for platform knowledge
  - Query: "Where can I compare programs?" → Comparison Tool
  - Query: "How do I see marketing ROI?" → Marketing Analysis

### 17. Navigation Query Handler
- [ ] 17.1 Implement navigation query detection
  - Update classify_query() to detect navigation queries
  - Keywords: "where", "which page", "how do i", "navigate"
- [ ] 17.2 Implement page recommendation logic
  - Retrieve relevant page from ChromaDB
  - Generate step-by-step instructions
  - Include filter suggestions
- [ ] 17.3 Format navigation responses
  - **Recommended Page**: [Page Name]
  - **Why**: [Explanation]
  - **Steps**: [Numbered list]
  - **Filters to Apply**: [List]
- [ ] 17.4 Test navigation queries
  - "Where can I see year-over-year comparisons?"
  - "How do I analyze marketing effectiveness?"
  - "Which page shows forecasts?"

### 18. Deep Linking (Optional)
- [ ] 18.1* Implement deep linking to pages
  - Generate URLs with pre-applied filters
  - Example: `/Executive_Deep_Dive?program=MBA&cohort=2025`
- [ ] 18.2* Add clickable links in chat responses
  - Use st.markdown with links
  - Open in same tab or new tab (user preference)
- [ ] 18.3* Test deep linking
  - Verify links navigate correctly
  - Test with different filter combinations

### 19. Workflow Guidance
- [ ] 19.1 Create common workflow templates
  - "How to create a program performance report"
  - "How to analyze marketing ROI"
  - "How to forecast enrollments"
- [ ] 19.2 Implement workflow query detection
  - Keywords: "how to", "create report", "analyze"
- [ ] 19.3 Generate step-by-step workflow guides
  - Multi-step instructions
  - Page navigation
  - Filter application
  - Interpretation tips
- [ ] 19.4 Test workflow guidance
  - "How do I create a report for MBA performance?"
  - "Walk me through analyzing marketing effectiveness"

---

## Phase 4: Enhanced RAG Pipeline (Week 5-6)

### 20. Conversation Memory
- [x] 20.1 Implement conversation context retrieval
  - Get last 5 exchanges from chat_history
  - Format as context for prompt
  - Include in Gemini API call
- [x] 20.2 Implement reference resolution
  - Detect pronouns and references ("it", "that", "same")
  - Resolve to previous entities (programs, metrics, dates)
  - Update query with resolved references
- [x] 20.3 Test conversation memory
  - Query 1: "How many MBA applications?"
  - Query 2: "What about ACCT?" (should understand context)
  - Query 3: "Show me the same for 2024" (should remember metric)
- [x] 20.4 Add context indicators in responses
  - "Based on your previous question about MBA..."
  - "Continuing from our discussion of applications..."

### 21. Complex Query Support
- [x] 21.1 Enhance SQL generation for joins
  - Support queries joining admissions_metrics + marketing_spend
  - Example: "What's the cost per enrollment for MBA?"
- [x] 21.2 Implement aggregation support
  - SUM, AVG, COUNT, MIN, MAX
  - GROUP BY for program, cohort, date
  - HAVING clauses for filtering aggregates
- [x] 21.3 Implement comparison queries
  - Year-over-year comparisons
  - Program-to-program comparisons
  - Growth rate calculations
- [x] 21.4 Test complex queries
  - "Compare MBA applications between 2024 and 2025"
  - "Which program has the highest conversion rate?"
  - "What's the average cost per inquiry across all programs?"

### 22. Schema Intelligence
- [x] 22.1 Enhance schema embeddings
  - Add column descriptions and data types
  - Include sample values for reference
  - Add relationship information (foreign keys)
- [x] 22.2 Implement smart schema retrieval
  - Retrieve only relevant tables/columns for query
  - Use semantic search to find best matches
  - Limit context to reduce token usage
- [x] 22.3 Add schema validation
  - Verify generated SQL uses valid tables/columns
  - Check for typos and suggest corrections
  - Validate data types in WHERE clauses
- [x] 22.4 Test schema intelligence
  - Query with business terms: "enrollments" → metric_name = 'Enrolled'
  - Query with abbreviations: "MBA" → program_code = 'MBA'
  - Query with synonyms: "applications" = "apps" = "applicants"

### 23. Query Pattern Recognition
- [x] 23.1 Implement query pattern caching
  - Identify common query patterns
  - Cache SQL templates for patterns
  - Substitute parameters for new queries
- [x] 23.2 Create pattern library
  - "How many [metric] for [program]?"
  - "What's the [metric] for [program] in [year]?"
  - "Compare [metric] between [program1] and [program2]"
- [x] 23.3 Implement pattern matching
  - Extract parameters from user query
  - Match to cached pattern
  - Generate SQL from template
- [x] 23.4 Test pattern recognition
  - Measure response time improvement
  - Verify accuracy of pattern matching
  - Test with variations of common queries

---

## Phase 5: Optimization (Week 7)

### 24. Token Optimization
- [x] 24.1 Implement prompt compression
  - Remove unnecessary whitespace
  - Use abbreviations where safe
  - Limit schema context to essentials
- [ ] 24.2 Implement response streaming (if supported)
  - Stream tokens as they're generated
  - Display partial responses in real-time
  - Improve perceived response time
- [x] 24.3 Optimize conversation context
  - Summarize old messages instead of full text
  - Limit to last 5 exchanges (configurable)
  - Remove redundant information
- [x] 24.4 Measure token usage
  - Log tokens per query
  - Calculate average and percentiles
  - Identify high-token queries for optimization

### 25. Response Caching
- [x] 25.1 Implement query result caching
  - Cache SQL query results for 5 minutes
  - Use query hash as cache key
  - Invalidate cache on data updates (optional)
- [x] 25.2 Implement response caching
  - Cache full bot responses for identical queries
  - Use LRU cache with 100 entry limit
  - Include timestamp in cached responses
- [x] 25.3 Test caching effectiveness
  - Measure cache hit rate
  - Verify response time improvement
  - Test cache invalidation

### 26. Rate Limiting
- [x] 26.1 Implement per-user rate limiting
  - 10 queries per minute per user
  - Store request timestamps in memory or Redis
  - Return helpful error message when limit exceeded
- [x] 26.2 Implement global rate limiting
  - 100 queries per minute across all users
  - Protect against API quota exhaustion
  - Queue requests if possible
- [x] 26.3 Add rate limit indicators in UI
  - Show remaining queries in chat header
  - Display countdown timer when limited
  - Suggest waiting time
- [x] 26.4 Test rate limiting
  - Simulate rapid queries
  - Verify limits are enforced
  - Test error messages

### 27. Performance Tuning
- [x] 27.1 Optimize database queries
  - Add indexes for common query patterns
  - Use query explain to identify slow queries
  - Optimize JOIN operations
- [ ] 27.2 Implement async processing
  - Use asyncio for parallel operations
  - Retrieve schema and context concurrently
  - Non-blocking API calls
- [ ] 27.3 Optimize ChromaDB operations
  - Batch embedding operations
  - Tune search parameters (n_results, distance threshold)
  - Consider in-memory mode for small datasets
- [x] 27.4 Load testing
  - Simulate 10 concurrent users
  - Measure response times under load
  - Identify bottlenecks

---

## Phase 6: Polish & Testing (Week 8)

### 28. UI/UX Refinements
- [ ] 28.1 Improve chat window animations
  - Smooth open/close transitions
  - Message fade-in animations
  - Typing indicator animation
- [ ] 28.2 Add keyboard shortcuts
  - Esc to close chat window
  - Ctrl+K to open chat (optional)
  - Up arrow to edit last message (optional)
- [ ] 28.3 Improve mobile experience
  - Full-screen chat on mobile
  - Touch-friendly buttons
  - Swipe to close (optional)
- [ ] 28.4 Add accessibility features
  - ARIA labels for screen readers
  - Keyboard navigation
  - High contrast mode support

### 29. Error Handling Improvements
- [x] 29.1 Enhance error messages
  - Provide specific, actionable feedback
  - Suggest alternative phrasings
  - Include examples of supported queries
- [ ] 29.2 Implement fallback strategies
  - Retry with simplified prompt on failure
  - Fall back to simpler query if complex fails
  - Offer manual navigation as last resort
- [ ] 29.3 Add error logging
  - Log all errors with context
  - Include user_id, query, error type
  - Monitor error rates in production
- [ ] 29.4 Test error scenarios
  - Invalid queries
  - API failures
  - Database errors
  - Rate limit exceeded

### 30. User Feedback Integration
- [x] 30.1 Add feedback buttons on responses
  - Thumbs up/down on each bot response
  - Optional comment field
  - Store feedback in database
- [x] 30.2 Implement feedback analysis
  - Track response satisfaction rate
  - Identify problematic query types
  - Use feedback to improve prompts
- [x] 30.3 Add suggested queries
  - Show example queries on first open
  - Suggest related queries after response
  - Learn from popular queries

### 31. Documentation & Examples
- [x] 31.1 Create comprehensive user guide
  - How to use chat feature
  - Example queries for each use case
  - Tips for getting best results
  - Troubleshooting common issues
- [x] 31.2 Add in-app help
  - Help button in chat header
  - Quick tips on first use
  - Contextual help based on query type
- [ ] 31.3 Create video tutorial (optional)
  - Screen recording of common workflows
  - Embed in documentation
  - Share with users

### 32. Production Deployment
- [ ] 32.1 Update deployment checklist
  - Add AI Chat deployment steps
  - Include API key setup
  - Document ChromaDB persistence
- [ ] 32.2 Deploy to Streamlit Cloud
  - Push code to GitHub
  - Update Streamlit secrets
  - Verify ChromaDB persistence
  - Test OAuth integration
- [ ] 32.3 Monitor production metrics
  - Query volume and response times
  - Error rates and types
  - Token usage and costs
  - User adoption rate
- [ ] 32.4 Create rollback plan
  - Document rollback procedure
  - Test rollback in staging
  - Prepare communication for users

### 33. Version Release
- [ ] 33.1 Update version to 5.3
  - Update `version.py`
  - Update `README.md` (version badge, What's New, Version History)
  - Update `docs/README.md` (add v5.3 section)
  - Update `docs/CHANGELOG.md` (add v5.3 entry, update Development Timeline and Summary)
- [ ] 33.2 Create git tag and push
  - Create tag `v5.3`
  - Push to GitHub
  - Create GitHub release with notes
- [ ] 33.3 Announce release
  - Email to stakeholders
  - Update platform announcement banner (optional)
  - Share demo video or screenshots

---

## Testing Checklist

### Functional Testing
- [ ] Authentication gate works correctly
- [ ] Chat button shows/hides based on auth status
- [ ] User can send messages and receive responses
- [ ] Simple data queries return correct results
- [ ] Complex queries with joins work correctly
- [ ] Navigation queries provide helpful guidance
- [ ] Help queries explain platform features
- [ ] Conversation history is saved and retrieved
- [ ] Users can search their chat history
- [ ] Users can export chat history
- [ ] Users can delete conversations
- [ ] Rate limiting prevents abuse
- [ ] Error messages are helpful and actionable

### Security Testing
- [ ] SQL injection attempts are blocked
- [ ] Users can only access their own chat history
- [ ] API keys are not exposed in responses
- [ ] Input sanitization prevents malicious queries
- [ ] Generated SQL is validated before execution
- [ ] Authentication is required for all chat operations

### Performance Testing
- [ ] Response time < 3 seconds for 80% of queries
- [ ] Response time < 5 seconds for 95% of queries
- [ ] Token usage < 1000 tokens per query (average)
- [ ] Chat history loads in < 1 second
- [ ] System handles 10 concurrent users
- [ ] Caching improves response times
- [ ] Rate limiting doesn't impact normal usage

### Usability Testing
- [ ] Chat interface is intuitive and easy to use
- [ ] Users can find the chat button easily
- [ ] Error messages help users rephrase queries
- [ ] Responses are clear and well-formatted
- [ ] Mobile experience is smooth and responsive
- [ ] Keyboard shortcuts work as expected
- [ ] Accessibility features work with screen readers

---

## Success Criteria

### Phase 1 (MVP)
- ✅ Chat feature is accessible to authenticated users
- ✅ Users can ask simple data queries and get correct answers
- ✅ Response time < 3 seconds for simple queries
- ✅ Chat history is saved to database
- ✅ UI matches platform design (maroon gradient theme)

### Phase 2 (Chat History)
- ✅ Users can view and search their chat history
- ✅ Users can export chat history to JSON
- ✅ Conversations are organized and threaded
- ✅ Users can delete conversations

### Phase 3 (Navigation)
- ✅ Users can ask navigation questions and get helpful guidance
- ✅ System recommends correct page for user's need
- ✅ Step-by-step instructions are clear and actionable

### Phase 4 (Enhanced RAG)
- ✅ System remembers context from previous messages
- ✅ Complex queries with joins and aggregations work
- ✅ System resolves references ("it", "that", "same")
- ✅ Query accuracy > 90%

### Phase 5 (Optimization)
- ✅ Token usage < 1000 tokens per query (average)
- ✅ Caching improves response times by 30%+
- ✅ Rate limiting prevents abuse without impacting UX
- ✅ System handles 10+ concurrent users

### Phase 6 (Polish)
- ✅ User satisfaction > 80% (based on feedback)
- ✅ Error rate < 10%
- ✅ Documentation is comprehensive and helpful
- ✅ Production deployment is stable

---

## Notes

- Tasks marked with `*` are optional and can be skipped if time is limited
- Each phase should be completed and tested before moving to the next
- User feedback should be gathered after Phase 1 and incorporated into later phases
- Token usage and costs should be monitored throughout development
- Security testing should be performed at every phase

---

**Document Version**: 1.0  
**Created**: January 25, 2026  
**Status**: Ready for Execution
