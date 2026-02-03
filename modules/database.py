"""
Database/Data Explorer Page Module
Extracted from main_app.py as part of Phase 4 refactoring
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import utility functions
from utils.database import get_connection
from utils.table_display import process_table_display
from utils import auth


def render():
    """Render the Database/Data Explorer page"""
    
    # Check authentication first
    if not auth.is_authenticated():
        st.info("Please sign in to access the Data Explorer")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            auth_url = auth.get_authorization_url()
            st.link_button("Sign in with Google", auth_url, use_container_width=True, type="primary")
        return
    
    user = auth.get_current_user()
    
    # Tables to exclude from Data Explorer (sensitive data)
    # Admins can see all tables including users table
    # Regular users can see their own chat data but not other users' data
    if auth.is_admin():
        EXCLUDED_TABLES = ['sqlite_sequence']  # Only hide system tables for admins
    else:
        EXCLUDED_TABLES = [
            'users',              # Personal data (emails, names, profiles) - admin only
            'metadata',           # System metadata (update timestamps) - admin only
            'model_predictions',  # ML predictions (should be viewed via Predictive Analytics page)
            'sqlite_sequence'     # System table
        ]  # Hide sensitive tables for regular users
        # Note: chat_history, chat_feedback, chat_metrics are now visible to logged-in users
        # but queries will be filtered by user_id to show only their own data
    
    # Define searchable content for each table
    table_search_content = {
        'users': {
            'keywords': ['users', 'accounts', 'authentication', 'admin', 'roles', 'login', 'profiles'],
            'questions': [
                'Who has access to the platform?',
                'Which users have admin privileges?',
                'When did users last log in?',
                'What are the user roles?'
            ]
        },
        'metadata': {
            'keywords': ['metadata', 'system', 'updates', 'timestamps', 'etl', 'pipeline', 'last update'],
            'questions': [
                'When was the data last updated?',
                'When did the ETL pipeline last run?',
                'What is the system status?',
                'When was marketing data last refreshed?'
            ]
        },
        'model_predictions': {
            'keywords': ['predictions', 'forecasts', 'ml', 'machine learning', 'models', 'ai', 'forecast'],
            'questions': [
                'What are the enrollment predictions?',
                'How accurate are the model forecasts?',
                'What metrics are being predicted?',
                'What are the confidence intervals?'
            ]
        },
        'admissions_metrics': {
            'keywords': ['applications', 'admissions', 'inquiries', 'enrollment', 'conversion', 'cohort', 'metrics', 'performance'],
            'questions': [
                'How many applications did we receive by program and cohort?',
                'What are the conversion rates from inquiry to application?',
                'Which programs have the highest enrollment numbers?',
                'How do our metrics trend over time?'
            ]
        },
        'programs': {
            'keywords': ['programs', 'degrees', 'mba', 'masters', 'active', 'codes'],
            'questions': [
                'What programs do we currently offer?',
                'Which programs are active vs inactive?',
                'What are the program codes and full names?',
                'How are programs categorized?'
            ]
        },
        'marketing_metrics': {
            'keywords': ['marketing', 'spend', 'cost', 'channels', 'roi', 'campaigns', 'budget'],
            'questions': [
                'How much are we spending on each marketing channel?',
                'What\'s our cost per inquiry by channel?',
                'Which marketing channels are most effective?',
                'How do click-through rates compare across channels?'
            ]
        },
        'marketing_campaigns': {
            'keywords': ['campaigns', 'marketing', 'budget', 'timeline', 'targets', 'performance'],
            'questions': [
                'What marketing campaigns are currently running?',
                'Which campaigns target which programs?',
                'What are the campaign budgets and timelines?',
                'How do campaigns perform against targets?'
            ]
        },
        'marketing_spend': {
            'keywords': ['spend', 'budget', 'allocation', 'roi', 'channels', 'cost'],
            'questions': [
                'How much did we spend on each marketing channel?',
                'What\'s our monthly marketing budget allocation?',
                'Which channels have the highest ROI?',
                'How does actual spend compare to budget?'
            ]
        },
        'inquiry_sources': {
            'keywords': ['sources', 'leads', 'inquiries', 'conversion', 'quality', 'channels'],
            'questions': [
                'Where are our inquiries coming from?',
                'Which sources generate the most qualified leads?',
                'How do different sources convert to applications?',
                'What\'s the quality score by source?'
            ]
        },
        'chat_history': {
            'keywords': ['chat', 'conversations', 'ai', 'assistant', 'messages', 'queries', 'history'],
            'questions': [
                'What questions have I asked the AI assistant?',
                'What are my recent conversations?',
                'How many messages have I sent?',
                'What queries did I make?'
            ]
        },
        'chat_feedback': {
            'keywords': ['feedback', 'ratings', 'satisfaction', 'thumbs up', 'thumbs down', 'quality'],
            'questions': [
                'What feedback have I given?',
                'Which responses did I rate positively?',
                'What was my satisfaction with AI responses?',
                'How did I rate the AI assistant?'
            ]
        },
        'chat_metrics': {
            'keywords': ['metrics', 'performance', 'response time', 'tokens', 'usage', 'analytics'],
            'questions': [
                'How fast are AI responses?',
                'How many tokens have I used?',
                'What are my chat usage statistics?',
                'What is the AI performance?'
            ]
        }
    }
    
    # Initialize last refresh time in session state
    if 'data_explorer_last_refresh' not in st.session_state:
        st.session_state.data_explorer_last_refresh = datetime.now()
    
    # REFRESH BUTTON AND KEYWORD SEARCH - Side by side, aligned
    st.markdown("""
    <div style="text-align: center; margin-bottom: 10px;">
        <h4 style="color: #500000; margin-bottom: 10px;">🔍 Find Your Data</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_search, col_refresh = st.columns([4, 1])
    
    with col_search:
        keyword_search = st.text_input(
            "Search tables, questions, or data types",
            placeholder="Type keywords like 'applications', 'marketing', 'programs', 'inquiries'...",
            key="table_keyword_search",
            label_visibility="collapsed"
        )
    
    with col_refresh:
        if st.button("Refresh", use_container_width=True, type="primary"):
            st.cache_data.clear()  # Clear any cached data
            st.session_state.data_explorer_last_refresh = datetime.now()
            st.rerun()
    
    # Show last refresh time
    last_refresh = st.session_state.data_explorer_last_refresh.strftime('%b %d, %Y at %I:%M:%S %p')
    st.markdown(f"""
    <div style="text-align: center; margin: 10px 0; color: #6c757d; font-size: 13px;">
        📊 Data last refreshed: <strong>{last_refresh}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        conn = get_connection()
        
        try:
            # Get available tables
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            tables_df = pd.read_sql(tables_query, conn)
            all_tables = tables_df['name'].tolist()
            
            # Filter out excluded tables
            available_tables = [table for table in all_tables if table not in EXCLUDED_TABLES]
            
            # Filter tables based on search if provided
            if keyword_search:
                filtered_tables = []
                search_lower = keyword_search.lower()
                
                for table in available_tables:
                    if table in table_search_content:
                        content = table_search_content[table]
                        keyword_match = any(search_lower in keyword.lower() for keyword in content['keywords'])
                        question_match = any(search_lower in question.lower() for question in content['questions'])
                        table_match = search_lower in table.lower()
                        
                        if keyword_match or question_match or table_match:
                            filtered_tables.append(table)
                    elif search_lower in table.lower():
                        filtered_tables.append(table)
                
                if filtered_tables:
                    available_tables = filtered_tables
                    st.success(f"✓ Found {len(filtered_tables)} table(s) matching '{keyword_search}'")
                else:
                    st.warning(f"No tables match '{keyword_search}'. Showing all tables.")
        
        finally:
            conn.close()
            
    except Exception as e:
        st.error(f"Error accessing database: {e}")
        available_tables = []
    
    # Check if we have tables to display
    if not available_tables:
        st.warning("No tables found in the database.")
        st.info("Please ensure the ETL pipeline has been run to populate the database.")
    else:
        # Enhanced Chrome-style CSS for grouped tabs - centered and clean
        st.markdown("""
        <style>
        /* Main category tabs styling - centered */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px !important;
            justify-content: center !important;
            background-color: #f8f9fa !important;
            padding: 8px 20px !important;
            border-radius: 12px !important;
            border-bottom: none !important;
            margin-bottom: 20px !important;
            margin-top: 20px !important;
                display: flex !important;
                flex-wrap: wrap !important;
                overflow: visible !important;
                scroll-behavior: smooth !important;
                box-sizing: border-box !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px !important;
                padding: 12px 24px !important;
                background-color: white !important;
                border-radius: 8px !important;
                border: 1px solid #dee2e6 !important;
                font-weight: 500 !important;
                font-size: 15px !important;
                color: #495057 !important;
                margin: 2px !important;
                flex-shrink: 0 !important;
                white-space: nowrap !important;
                min-width: fit-content !important;
                box-sizing: border-box !important;
                transition: all 0.2s ease !important;
                cursor: pointer !important;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e9ecef !important;
                border-color: #adb5bd !important;
                color: #495057 !important;
                transform: translateY(-1px) !important;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #500000 !important;
                color: white !important;
                border-color: #500000 !important;
                box-shadow: 0 2px 8px rgba(80, 0, 0, 0.2) !important;
            }
            
            .stTabs [aria-selected="true"]:hover {
                background-color: #500000 !important;
                color: white !important;
                transform: translateY(-1px) !important;
            }
            
            /* Sub-tabs (nested) styling - centered */
            .stTabs .stTabs [data-baseweb="tab-list"] {
                background-color: #ffffff !important;
                border: 1px solid #dee2e6 !important;
                border-radius: 8px !important;
                padding: 4px !important;
                margin-bottom: 15px !important;
                margin-top: 10px !important;
                justify-content: center !important;
                flex-wrap: wrap !important;
            }
            
            .stTabs .stTabs [data-baseweb="tab"] {
                height: 40px !important;
                padding: 8px 16px !important;
                font-size: 14px !important;
                background-color: #f8f9fa !important;
                border: 1px solid #e9ecef !important;
                border-radius: 6px !important;
                color: #6c757d !important;
                margin: 2px !important;
            }
            
            .stTabs .stTabs [data-baseweb="tab"]:hover {
                background-color: #e9ecef !important;
                color: #495057 !important;
                border-color: #adb5bd !important;
                transform: none !important;
            }
            
            .stTabs .stTabs [aria-selected="true"] {
                background-color: #500000 !important;
                color: white !important;
                border-color: #500000 !important;
                box-shadow: 0 1px 4px rgba(80, 0, 0, 0.2) !important;
            }
            
            .stTabs .stTabs [aria-selected="true"]:hover {
                background-color: #500000 !important;
                color: white !important;
            }
            
            /* Responsive design */
            @media screen and (max-width: 768px) {
                .stTabs [data-baseweb="tab-list"] {
                    justify-content: center !important;
                    padding: 8px 10px !important;
                }
                
                .stTabs [data-baseweb="tab"] {
                    padding: 8px 16px !important;
                    font-size: 14px !important;
                    height: 45px !important;
                }
                
                .stTabs .stTabs [data-baseweb="tab"] {
                    padding: 6px 12px !important;
                    font-size: 13px !important;
                    height: 36px !important;
                }
            }
            
            @media screen and (max-width: 480px) {
                .stTabs [data-baseweb="tab"] {
                    padding: 6px 12px !important;
                    font-size: 13px !important;
                    height: 42px !important;
                }
                
                .stTabs .stTabs [data-baseweb="tab"] {
                    padding: 4px 8px !important;
                    font-size: 12px !important;
                    height: 32px !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Group tables by category for better organization
        table_groups = {
            'Marketing Tables': {
                'tables': ['marketing_spend', 'marketing_spend_totals', 'incremental_notes', 'marketing_data'],
                'description': 'Marketing spend data, totals, notes, and ETL tracking'
            },
            'Core Data Tables': {
                'tables': ['admissions_metrics', 'programs', 'metadata'],
                'description': 'Admissions funnel data, program definitions, and system metadata'
            },
            'AI Chat Tables': {
                'tables': ['chat_history', 'chat_feedback', 'chat_metrics'],
                'description': 'AI assistant conversations, feedback, and performance metrics'
            },
            'System Tables': {
                'tables': ['users', 'model_predictions'],
                'description': 'User management and ML prediction results'
            }
        }
        
        # Filter available tables by groups and user permissions
        filtered_groups = {}
        for group_name, group_info in table_groups.items():
            group_tables = [table for table in group_info['tables'] 
                          if table in available_tables]
            if group_tables:  # Only show groups that have available tables
                filtered_groups[group_name] = {
                    'tables': group_tables,
                    'description': group_info['description']
                }
        
        # Create main category tabs
        if filtered_groups:
            main_tabs = st.tabs(list(filtered_groups.keys()))
            
            for i, (group_name, group_info) in enumerate(filtered_groups.items()):
                with main_tabs[i]:
                    st.markdown(f"""
                    <div style="background: #f8f9fa;
                                padding: 15px 20px;
                                border-radius: 10px;
                                margin-bottom: 20px;
                                text-align: center;">
                        <h4 style="margin: 0; color: #500000;">{group_name}</h4>
                        <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">{group_info['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create sub-tabs for tables within this group
                    group_tables = group_info['tables']
                    
                    # Create display names for sub-tabs
                    sub_tab_labels = []
                    for table in group_tables:
                        display_name = table.replace('_', ' ').title()
                        name_mapping = {
                            'Marketing Spend': 'Spend',
                            'Marketing Spend Totals': 'Totals',
                            'Incremental Notes': 'Notes',
                            'Marketing Data': 'Processing Logs',
                            'Admissions Metrics': 'Admissions',
                            'Programs': 'Programs',
                            'Metadata': 'Metadata',
                            'Chat History': 'History',
                            'Chat Feedback': 'Feedback',
                            'Chat Metrics': 'Metrics',
                            'Users': 'Users',
                            'Model Predictions': 'Predictions'
                        }
                        display_name = name_mapping.get(display_name, display_name)
                        sub_tab_labels.append(display_name)
                    
                    # Create sub-tabs
                    sub_tabs = st.tabs(sub_tab_labels)
                    
                    for j, table in enumerate(group_tables):
                        with sub_tabs[j]:
                            # Add table-specific info
                            st.markdown(f"""
                            <div style="background: white;
                                        padding: 10px 15px;
                                        border-radius: 8px;
                                        margin-bottom: 15px;
                                        border: 1px solid #dee2e6;
                                        text-align: center;">
                                <strong>Table:</strong> <code>{table}</code>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Handle chat tables with user filtering
                            conn_display = get_connection()
                            try:
                                if table in ['chat_history', 'chat_feedback', 'chat_metrics']:
                                    if not auth.is_admin():
                                        st.info(f"Showing your personal {table.replace('_', ' ')} data")
                                        process_table_display(conn_display, table, user_filter={'user_id': user['user_id']})
                                    else:
                                        st.info(f"Admin view: Showing all {table.replace('_', ' ')} data")
                                        process_table_display(conn_display, table)
                                else:
                                    # Other tables show all data
                                    process_table_display(conn_display, table)
                            finally:
                                conn_display.close()
        else:
            st.warning("No tables available for your user role.")


