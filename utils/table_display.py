"""
Table display utility functions for Mays Analytics Platform
Functions for displaying and filtering database tables in Data Explorer
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def process_table_display(conn, selected_table, user_filter=None):
    """
    Helper function to display table data with filtering options - styled like Marketing Analysis
    
    Args:
        conn: Database connection
        selected_table: Name of the table to display
        user_filter: Optional dict with column:value pairs to filter data (e.g., {'user_id': 123})
    """
    try:
        # Table descriptions - what questions each table can help answer
        table_descriptions = {
            'admissions_metrics': {
                'icon': '📊',
                'title': 'Admissions Performance Data',
                'questions': [
                    'How many applications did we receive by program and cohort?',
                    'What are the conversion rates from inquiry to application?',
                    'Which programs have the highest enrollment numbers?',
                    'How do our metrics trend over time?'
                ]
            },
            'programs': {
                'icon': '🎓',
                'title': 'Program Information',
                'questions': [
                    'What programs do we currently offer?',
                    'Which programs are active vs inactive?',
                    'What are the program codes and full names?',
                    'How are programs categorized?'
                ]
            },
            'marketing_metrics': {
                'icon': '📈',
                'title': 'Marketing Performance Data',
                'questions': [
                    'How much are we spending on each marketing channel?',
                    'What\'s our cost per inquiry by channel?',
                    'Which marketing channels are most effective?',
                    'How do click-through rates compare across channels?'
                ]
            },
            'marketing_campaigns': {
                'icon': '📢',
                'title': 'Campaign Management Data',
                'questions': [
                    'What marketing campaigns are currently running?',
                    'Which campaigns target which programs?',
                    'What are the campaign budgets and timelines?',
                    'How do campaigns perform against targets?'
                ]
            },
            'marketing_spend': {
                'icon': '💰',
                'title': 'Marketing Budget & Spend',
                'questions': [
                    'How much did we spend on each marketing channel?',
                    'What\'s our monthly marketing budget allocation?',
                    'Which channels have the highest ROI?',
                    'How does actual spend compare to budget?'
                ]
            },
            'inquiry_sources': {
                'icon': '🔍',
                'title': 'Lead Source Analysis',
                'questions': [
                    'Where are our inquiries coming from?',
                    'Which sources generate the most qualified leads?',
                    'How do different sources convert to applications?',
                    'What\'s the quality score by source?'
                ]
            },
            'chat_history': {
                'icon': '💬',
                'title': 'AI Chat Conversation History',
                'questions': [
                    'What questions have I asked the AI assistant?',
                    'What are my recent conversations?',
                    'How many messages have I sent?',
                    'What responses did I receive?'
                ]
            },
            'chat_feedback': {
                'icon': '👍',
                'title': 'AI Chat Feedback & Ratings',
                'questions': [
                    'What feedback have I given to AI responses?',
                    'Which responses did I rate positively?',
                    'What was my satisfaction with the AI?',
                    'How did I rate different query types?'
                ]
            },
            'chat_metrics': {
                'icon': '📊',
                'title': 'AI Chat Performance Metrics',
                'questions': [
                    'How fast are AI responses?',
                    'How many tokens have I used?',
                    'What are my chat usage statistics?',
                    'What is the AI performance over time?'
                ]
            },
            'sqlite_sequence': {
                'icon': '⚙️',
                'title': 'System Table',
                'questions': [
                    'Internal SQLite sequence information',
                    'Auto-incrementing field management'
                ]
            },
            'marketing_data': {
                'icon': '📊',
                'title': 'Marketing ETL State Tracking',
                'questions': [
                    'What marketing data has been processed?',
                    'When was the last ETL update?',
                    'Which fiscal years have been loaded?',
                    'What programs and channels are tracked?'
                ]
            },
            'incremental_notes': {
                'icon': '📝',
                'title': 'Marketing Incremental Notes',
                'questions': [
                    'What incremental spend changes were made?',
                    'Which programs had budget adjustments?',
                    'What are the reasons for spend increases?',
                    'How are channels being optimized?'
                ]
            },
            'marketing_spend_totals': {
                'icon': '💰',
                'title': 'Marketing Spend Totals',
                'questions': [
                    'What are the total monthly spends by program?',
                    'How do program budgets compare?',
                    'What are the spending trends over time?',
                    'Which months had the highest investment?'
                ]
            },
            'metadata': {
                'icon': '🔧',
                'title': 'System Metadata',
                'questions': [
                    'When was data last updated?',
                    'What is the system configuration?',
                    'What are the data refresh timestamps?'
                ]
            },
            'model_predictions': {
                'icon': '🔮',
                'title': 'AI Model Predictions',
                'questions': [
                    'What are the forecasted enrollment numbers?',
                    'Which programs are predicted to grow?',
                    'What are the confidence intervals?',
                    'How accurate are the predictions?'
                ]
            },
            'users': {
                'icon': '👥',
                'title': 'User Management',
                'questions': [
                    'Who has access to the system?',
                    'What are the user roles and permissions?',
                    'When did users last log in?'
                ]
            }
        }
        
        # Show formatted table description with darker background (matching Marketing Analysis)
        if selected_table in table_descriptions:
            desc = table_descriptions[selected_table]
            
            # Create individual question boxes
            question_boxes = ''.join([
                f'''<div style="background: white;
                            padding: 15px 20px;
                            border-radius: 6px;
                            margin: 8px 0;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                            flex: 1;
                            min-width: 0;">
                    <p style="margin: 0; color: #495057; font-size: 14px; line-height: 1.5;">{q}</p>
                </div>'''
                for q in desc['questions']
            ])
            
            st.markdown(f"""
            <div style="text-align: center;
                        padding: 20px;
                        background: #e9ecef;
                        border-radius: 8px;
                        margin: 20px 0;">
                <h4 style="color: #500000; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    {desc['title']}
                </h4>
                <p style="margin: 0 0 15px 0; color: #495057; font-weight: 600; font-size: 15px;">
                    💡 What questions can this table help answer?
                </p>
                <div style="display: flex;
                            flex-direction: column;
                            gap: 8px;
                            max-width: 800px;
                            margin: 0 auto;">
                    {question_boxes}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center;
                        padding: 15px;
                        background: #e9ecef;
                        border-radius: 8px;
                        margin: 20px 0;">
                <strong style="color: #500000;">📋 Table:</strong> <code>{selected_table}</code><br>
                <em style="color: #6c757d;">Explore the data to understand what insights it can provide.</em>
            </div>
            """, unsafe_allow_html=True)
        
        # Get table info
        table_info_query = f"PRAGMA table_info({selected_table})"
        table_info = pd.read_sql(table_info_query, conn)
        
        # Build query with user filter if provided
        if user_filter:
            where_clauses = [f"{col} = ?" for col in user_filter.keys()]
            where_sql = " WHERE " + " AND ".join(where_clauses)
            filter_values = tuple(user_filter.values())
            
            count_query = f"SELECT COUNT(*) as count FROM {selected_table}{where_sql}"
            row_count = pd.read_sql(count_query, conn, params=filter_values)['count'].iloc[0]
            
            data_query = f"SELECT * FROM {selected_table}{where_sql}"
        else:
            count_query = f"SELECT COUNT(*) as count FROM {selected_table}"
            row_count = pd.read_sql(count_query, conn)['count'].iloc[0]
            
            data_query = f"SELECT * FROM {selected_table}"
            filter_values = None
        
        # Show row count centered
        st.markdown(f"""
        <div style="text-align: center; margin: 15px 0; color: #6c757d;">
            <strong>{row_count:,}</strong> total rows in this table
        </div>
        """, unsafe_allow_html=True)
        
        # Show table schema in expander
        with st.expander("📋 View Table Schema"):
            st.dataframe(table_info[['name', 'type', 'notnull', 'pk']], use_container_width=True)
        
        # FILTERS SECTION with header
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">Filter & Explore Data</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Get all data first to enable filtering
        if filter_values:
            full_data = pd.read_sql(data_query, conn, params=filter_values)
        else:
            full_data = pd.read_sql(data_query, conn)
        
        if not full_data.empty:
            # Create filter columns
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                # Column filter
                columns = ['All Columns'] + list(full_data.columns)
                selected_columns = st.multiselect(
                    "📋 Select Columns", 
                    columns, 
                    default=['All Columns'],
                    key=f"columns_{selected_table}"
                )
                
                if 'All Columns' in selected_columns or not selected_columns:
                    display_data = full_data.copy()
                else:
                    display_data = full_data[selected_columns].copy()
            
            with filter_col2:
                # Row limit
                row_limit = st.number_input(
                    "📊 Row Limit", 
                    min_value=10, 
                    max_value=1000, 
                    value=100, 
                    step=10,
                    key=f"limit_{selected_table}"
                )
            
            with filter_col3:
                # Sort options
                sort_columns = ['None'] + list(full_data.columns)
                sort_by = st.selectbox("🔄 Sort By", sort_columns, key=f"sort_{selected_table}")
            
            # Sort order on new row if sort is selected
            if sort_by != 'None':
                sort_order = st.radio(
                    "Sort Order", 
                    ['Ascending', 'Descending'], 
                    horizontal=True,
                    key=f"order_{selected_table}"
                )
            else:
                sort_order = 'Ascending'
            
            # Text search filter - FULL WIDTH
            search_term = st.text_input(
                "🔍 Search in all columns",
                placeholder="Type to search across all columns (case-insensitive)...",
                key=f"search_{selected_table}"
            )
            
            # Apply filters
            filtered_data = display_data.copy()
            
            # Apply search filter
            if search_term:
                try:
                    # Search across all string columns
                    string_columns = filtered_data.select_dtypes(include=['object']).columns
                    if len(string_columns) > 0:
                        search_mask = filtered_data[string_columns].astype(str).apply(
                            lambda x: x.str.contains(search_term, case=False, na=False)
                        ).any(axis=1)
                        filtered_data = filtered_data[search_mask]
                except Exception as e:
                    st.warning(f"Search error: {str(e)}")
            
            # Apply sorting
            if sort_by != 'None' and sort_by in filtered_data.columns:
                try:
                    ascending = sort_order == 'Ascending'
                    filtered_data = filtered_data.sort_values(by=sort_by, ascending=ascending)
                except Exception as e:
                    st.warning(f"Sort error: {str(e)}")
            
            # Apply row limit
            filtered_data = filtered_data.head(row_limit)
            
            # DATA DISPLAY SECTION with header
            st.markdown("""
            <div style="text-align: center;
                        padding: 15px;
                        background: #e9ecef;
                        border-radius: 8px;
                        margin: 20px 0;">
                <h3 style="color: #500000; margin: 0; font-size: 20px;">Data Table</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Showing {len(filtered_data):,} of {len(full_data):,} rows**")
            
            with col2:
                # Download filtered data
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv_data,
                    f"{selected_table}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True,
                    key=f"download_{selected_table}"
                )
            
            # Display the data table
            st.dataframe(filtered_data, use_container_width=True, height=500)
            
            # Quick stats for numeric columns
            numeric_columns = filtered_data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                with st.expander("📈 Quick Statistics (Numeric Columns)"):
                    stats_data = filtered_data[numeric_columns].describe()
                    st.dataframe(stats_data, use_container_width=True)
        
        else:
            st.info(f"Table '{selected_table}' is empty.")
            
    except Exception as e:
        st.error(f"Error loading table data: {str(e)}")
        st.info("Please check if the table exists and contains valid data.")
