"""
Marketing Analysis Page Module
Extracted from main_app.py as part of Phase 7 refactoring
"""

import streamlit as st
import streamlit.components.v1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import utility functions
from utils.database import get_connection, normalize_program_name


def render():
    """Render the Marketing Analysis page"""
    
    # Check if marketing data is available
    conn = get_connection()
    
    # Test if marketing tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marketing_spend';")
    has_marketing_spend = cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marketing_spend_totals';")
    has_marketing_totals = cursor.fetchone() is not None
    
    has_data = has_marketing_spend and has_marketing_totals
    
    if not has_data:
        st.warning("⚠️ Marketing data not yet available")
        st.info("""
        ### 🚧 Marketing Spend Dashboard
        
        Run `python3 marketing_etl.py` to load marketing spend data.
        
        **What you'll see here:**
        - 📊 Spend by program and channel
        - 💰 Monthly spend trends
        - 📈 Channel performance comparison
        - 🎯 Fiscal year breakdown
        - 📝 Incremental spend notes
        """)
    else:
        # Load data from new tables
        spend_df = pd.read_sql("""
            SELECT 
                program,
                channel,
                fiscal_year,
                month_date,
                spend_amount,
                extra_notes
            FROM marketing_spend
            ORDER BY month_date DESC, program, channel
        """, conn)
        
        # Convert dates
        spend_df['month_date'] = pd.to_datetime(spend_df['month_date'])
        
        # Add normalized program names for matching
        spend_df['program_normalized'] = spend_df['program'].apply(normalize_program_name)
        
        # GLOBAL FILTERS - Applied to all tabs
        st.markdown("""
        <style>
        /* Section headers with centered styling */
        .section-header {
            text-align: center;
            padding: 12px;
            background: #e9ecef;
            border-radius: 8px;
            margin: 20px 0 15px 0;
        }
        .section-header h3 {
            margin: 0;
            color: #500000;
            font-size: 20px;
        }
        
        /* Style bordered containers with gradient background */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stHorizontalBlock"]) {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
            padding: 15px !important;
            border-radius: 8px !important;
        }
        
        /* Equal-sized buttons */
        div[data-testid="stButton"] button {
            width: 100% !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            font-size: 12px !important;
            padding: 8px 4px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize independent reset counters for each filter
        if 'fy_reset_count' not in st.session_state:
            st.session_state.fy_reset_count = 0
        if 'prog_reset_count' not in st.session_state:
            st.session_state.prog_reset_count = 0
        if 'chan_reset_count' not in st.session_state:
            st.session_state.chan_reset_count = 0
        
        col1, col2, col3 = st.columns(3)
        
        # FISCAL YEAR MULTI-SELECT
        with col1:
            fiscal_years_list_global = sorted(spend_df['fiscal_year'].unique().tolist())
            
            # Use independent reset counter for fiscal year
            fy_reset_suffix = f"_{st.session_state.fy_reset_count}"
            fy_state_key_global = f'selected_fy_global{fy_reset_suffix}'
            
            if fy_state_key_global not in st.session_state:
                st.session_state[fy_state_key_global] = fiscal_years_list_global.copy()
            
            current_fy_selection_global = st.session_state[fy_state_key_global]
            
            if len(current_fy_selection_global) == len(fiscal_years_list_global):
                fy_summary_text_global = "All fiscal years"
            elif len(current_fy_selection_global) == 0:
                fy_summary_text_global = "No fiscal years selected"
            elif len(current_fy_selection_global) == 1:
                fy_summary_text_global = str(current_fy_selection_global[0])
            else:
                fy_summary_text_global = f"{len(current_fy_selection_global)} fiscal years"
            
            st.markdown("**📅 Fiscal Year**")
            
            with st.popover(fy_summary_text_global, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key=f"fy_all_global{fy_reset_suffix}", use_container_width=True, type="primary"):
                        st.session_state.fy_reset_count += 1
                        new_fy_key_global = f'selected_fy_global_{st.session_state.fy_reset_count}'
                        st.session_state[new_fy_key_global] = fiscal_years_list_global.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key=f"fy_clear_global{fy_reset_suffix}", use_container_width=True, type="secondary"):
                        st.session_state.fy_reset_count += 1
                        new_fy_key_global = f'selected_fy_global_{st.session_state.fy_reset_count}'
                        st.session_state[new_fy_key_global] = []
                        st.rerun()
                
                st.divider()
                
                for idx, fy in enumerate(fiscal_years_list_global):
                    is_checked = fy in st.session_state[fy_state_key_global]
                    new_value = st.checkbox(
                        str(fy), 
                        value=is_checked, 
                        key=f"fy_cb_{idx}_global{fy_reset_suffix}"
                    )
                    
                    if new_value != is_checked:
                        if new_value:
                            if fy not in st.session_state[fy_state_key_global]:
                                st.session_state[fy_state_key_global].append(fy)
                        else:
                            if fy in st.session_state[fy_state_key_global]:
                                st.session_state[fy_state_key_global].remove(fy)
                        st.rerun()
        
        selected_fy_global = st.session_state.get(fy_state_key_global, fiscal_years_list_global)
        
        fy_filtered_global = spend_df.copy()
        if len(selected_fy_global) > 0:
            fy_filtered_global = fy_filtered_global[fy_filtered_global['fiscal_year'].isin(selected_fy_global)]
        else:
            fy_filtered_global = fy_filtered_global.head(0)
        
        # PROGRAM MULTI-SELECT
        with col2:
            programs_list_global = sorted(fy_filtered_global['program'].unique().tolist())
            
            # Use independent reset counter for programs
            prog_reset_suffix = f"_{st.session_state.prog_reset_count}"
            prog_state_key_global = f'selected_programs_global{prog_reset_suffix}'
            
            if prog_state_key_global not in st.session_state:
                st.session_state[prog_state_key_global] = programs_list_global.copy()
            
            # Auto-update: Remove programs that are no longer available due to fiscal year filter changes
            current_prog_selection_global = st.session_state[prog_state_key_global]
            valid_programs = [prog for prog in current_prog_selection_global if prog in programs_list_global]
            
            # If the available programs changed, update the selection to only valid ones
            if set(valid_programs) != set(current_prog_selection_global):
                st.session_state[prog_state_key_global] = valid_programs if valid_programs else programs_list_global.copy()
                current_prog_selection_global = st.session_state[prog_state_key_global]
            
            if len(current_prog_selection_global) == len(programs_list_global):
                prog_summary_text_global = "All programs"
            elif len(current_prog_selection_global) == 0:
                prog_summary_text_global = "No programs selected"
            elif len(current_prog_selection_global) == 1:
                prog_summary_text_global = current_prog_selection_global[0]
            else:
                prog_summary_text_global = f"{len(current_prog_selection_global)} programs"
            
            st.markdown("**🎓 Program**")
            
            with st.popover(prog_summary_text_global, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key=f"prog_all_global{prog_reset_suffix}", use_container_width=True, type="primary"):
                        st.session_state.prog_reset_count += 1
                        new_prog_key_global = f'selected_programs_global_{st.session_state.prog_reset_count}'
                        st.session_state[new_prog_key_global] = programs_list_global.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key=f"prog_clear_global{prog_reset_suffix}", use_container_width=True, type="secondary"):
                        st.session_state.prog_reset_count += 1
                        new_prog_key_global = f'selected_programs_global_{st.session_state.prog_reset_count}'
                        st.session_state[new_prog_key_global] = []
                        st.rerun()
                
                st.divider()
                
                for idx, program in enumerate(programs_list_global):
                    is_checked = program in st.session_state[prog_state_key_global]
                    new_value = st.checkbox(
                        program, 
                        value=is_checked, 
                        key=f"prog_cb_{idx}_global{prog_reset_suffix}"
                    )
                    
                    if new_value != is_checked:
                        if new_value:
                            if program not in st.session_state[prog_state_key_global]:
                                st.session_state[prog_state_key_global].append(program)
                        else:
                            if program in st.session_state[prog_state_key_global]:
                                st.session_state[prog_state_key_global].remove(program)
                        st.rerun()
        
        selected_programs_global = st.session_state.get(prog_state_key_global, programs_list_global)
        
        program_filtered_global = fy_filtered_global.copy()
        if len(selected_programs_global) > 0:
            program_filtered_global = program_filtered_global[program_filtered_global['program'].isin(selected_programs_global)]
        else:
            program_filtered_global = program_filtered_global.head(0)
        
        # CHANNEL MULTI-SELECT
        with col3:
            channels_list_global = sorted(program_filtered_global['channel'].unique().tolist())
            
            # Use independent reset counter for channels
            chan_reset_suffix = f"_{st.session_state.chan_reset_count}"
            chan_state_key_global = f'selected_channels_global{chan_reset_suffix}'
            
            if chan_state_key_global not in st.session_state:
                st.session_state[chan_state_key_global] = channels_list_global.copy()
            
            # Auto-update: Remove channels that are no longer available due to upstream filter changes
            current_chan_selection_global = st.session_state[chan_state_key_global]
            valid_channels = [ch for ch in current_chan_selection_global if ch in channels_list_global]
            
            # If the available channels changed, update the selection to only valid ones
            if set(valid_channels) != set(current_chan_selection_global):
                st.session_state[chan_state_key_global] = valid_channels if valid_channels else channels_list_global.copy()
                current_chan_selection_global = st.session_state[chan_state_key_global]
            
            if len(current_chan_selection_global) == len(channels_list_global):
                chan_summary_text_global = "All channels"
            elif len(current_chan_selection_global) == 0:
                chan_summary_text_global = "No channels selected"
            elif len(current_chan_selection_global) == 1:
                chan_summary_text_global = current_chan_selection_global[0]
            else:
                chan_summary_text_global = f"{len(current_chan_selection_global)} channels"
            
            st.markdown("**📢 Channel**")
            
            with st.popover(chan_summary_text_global, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key=f"chan_all_global{chan_reset_suffix}", use_container_width=True, type="primary"):
                        st.session_state.chan_reset_count += 1
                        new_chan_key_global = f'selected_channels_global_{st.session_state.chan_reset_count}'
                        st.session_state[new_chan_key_global] = channels_list_global.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key=f"chan_clear_global{chan_reset_suffix}", use_container_width=True, type="secondary"):
                        st.session_state.chan_reset_count += 1
                        new_chan_key_global = f'selected_channels_global_{st.session_state.chan_reset_count}'
                        st.session_state[new_chan_key_global] = []
                        st.rerun()
                
                st.divider()
                
                for idx, channel in enumerate(channels_list_global):
                    is_checked = channel in st.session_state[chan_state_key_global]
                    new_value = st.checkbox(
                        channel, 
                        value=is_checked, 
                        key=f"chan_cb_{idx}_global{chan_reset_suffix}"
                    )
                    
                    if new_value != is_checked:
                        if new_value:
                            if channel not in st.session_state[chan_state_key_global]:
                                st.session_state[chan_state_key_global].append(channel)
                        else:
                            if channel in st.session_state[chan_state_key_global]:
                                st.session_state[chan_state_key_global].remove(channel)
                        st.rerun()
        
        selected_channels_global = st.session_state.get(chan_state_key_global, channels_list_global)
        
        # Apply all global filters to create the master filtered dataset
        filtered_spend_global = spend_df.copy()
        
        if len(selected_fy_global) > 0:
            filtered_spend_global = filtered_spend_global[filtered_spend_global['fiscal_year'].isin(selected_fy_global)]
        else:
            filtered_spend_global = filtered_spend_global.head(0)
        
        if len(selected_programs_global) > 0:
            filtered_spend_global = filtered_spend_global[filtered_spend_global['program'].isin(selected_programs_global)]
        else:
            filtered_spend_global = filtered_spend_global.head(0)
        
        if len(selected_channels_global) > 0:
            filtered_spend_global = filtered_spend_global[filtered_spend_global['channel'].isin(selected_channels_global)]
        else:
            filtered_spend_global = filtered_spend_global.head(0)
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # How to Use This Analysis - Collapsible
        with st.expander("💡 How to Use This Analysis", expanded=False):
            st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 14px; color: #495057;">
                <div>
                    <strong style="color: #500000;">📊 What You Can Discover:</strong>
                    <ul style="margin: 8px 0; padding-left: 20px;">
                        <li><strong>Spend Analysis:</strong> Track marketing investments by channel and program</li>
                        <li><strong>Channel Performance:</strong> Compare effectiveness across different marketing channels</li>
                        <li><strong>Trend Tracking:</strong> Monitor spending patterns over time and fiscal years</li>
                        <li><strong>ROI Insights:</strong> Understand cost per inquiry and conversion metrics</li>
                    </ul>
                </div>
                <div>
                    <strong style="color: #500000;">🎯 Interactive Features:</strong>
                    <ul style="margin: 8px 0; padding-left: 20px;">
                        <li><strong>Multi-Select Filters:</strong> Choose fiscal years, programs, and channels</li>
                        <li><strong>Dynamic Charts:</strong> Click legend items to toggle data series on/off</li>
                        <li><strong>Hover Details:</strong> Move mouse over charts for exact values and breakdowns</li>
                        <li><strong>Data Export:</strong> Download filtered data for further analysis</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # Chrome-style CSS for tabs with always-visible scrollbar when needed
        st.markdown("""
        <style>
        /* Chrome-style tabs - Base styles */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px !important;
            justify-content: center !important;
            background-color: transparent !important;
            padding: 0px 20px !important;
            border-bottom: none !important;
            margin-bottom: 30px !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            scroll-behavior: smooth !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: thin !important;
            scrollbar-color: #500000 #f0f0f0 !important;
            box-sizing: border-box !important;
        }
        
        /* Always show scrollbar when content overflows */
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            height: 10px !important;
            display: block !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
            background: #f0f0f0 !important;
            border-radius: 5px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
            background: #500000 !important;
            border-radius: 5px !important;
            min-width: 50px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
            background: #700000 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 45px !important;
            padding: 0px 32px !important;
            background-color: #f5f5f5 !important;
            border-radius: 8px 8px 0px 0px !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            border: none !important;
            border-bottom: 3px solid transparent !important;
            color: #666 !important;
            margin-bottom: -2px !important;
            flex-shrink: 0 !important;
            white-space: nowrap !important;
            min-width: fit-content !important;
            box-sizing: border-box !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: #500000 !important;
            border-bottom: 3px solid #500000 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e8e8e8 !important;
            color: #500000 !important;
        }
        
        .stTabs [aria-selected="true"]:hover {
            background-color: white !important;
        }
        
        /* Tablet adjustments - switch to left-aligned */
        @media screen and (max-width: 1024px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 15px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 24px !important;
                font-size: 14px !important;
            }
            
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                height: 12px !important;
            }
        }
        
        /* Mobile adjustments - left-aligned */
        @media screen and (max-width: 768px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 10px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 20px !important;
                font-size: 13px !important;
                height: 42px !important;
            }
        }
        
        /* Small mobile adjustments - left-aligned */
        @media screen and (max-width: 480px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 10px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 16px !important;
                font-size: 12px !important;
                height: 40px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # TABS - Now using globally filtered data
        overview_tab, advanced_tab, channel_tab, notes_tab = st.tabs(["📊 Overview", "🔬 Advanced Analytics", "📢 Channel Analytics", "📝 Incremental Notes"])
        
        with overview_tab:
            # Use globally filtered data
            filtered_spend = filtered_spend_global.copy()
            
            if filtered_spend.empty:
                st.warning("⚠️ No data matches the selected filters")
            else:
                # Try to load admissions data for ROI metrics
                try:
                    admissions_df = pd.read_sql("""
                        SELECT 
                            report_date,
                            program,
                            metric_name,
                            metric_value
                        FROM admissions_metrics
                        WHERE metric_name IN ('inquiries_received', 'applications_received', 'admissions_accepted')
                    """, conn)
                    
                    # Normalize admissions program names
                    admissions_df['program_normalized'] = admissions_df['program'].apply(normalize_program_name)
                    admissions_df['report_date'] = pd.to_datetime(admissions_df['report_date'])
                    admissions_df['month_date'] = admissions_df['report_date'].dt.to_period('M').dt.to_timestamp()
                    
                    # Pivot admissions data
                    admissions_pivot = admissions_df.pivot_table(
                        index=['month_date', 'program_normalized'],
                        columns='metric_name',
                        values='metric_value',
                        aggfunc='sum'
                    ).reset_index()
                    
                    # Aggregate marketing spend by month and normalized program
                    monthly_spend_norm = filtered_spend.groupby(['month_date', 'program_normalized']).agg({
                        'spend_amount': 'sum'
                    }).reset_index()
                    
                    # Merge on normalized program names
                    roi_df = pd.merge(
                        monthly_spend_norm,
                        admissions_pivot,
                        on=['month_date', 'program_normalized'],
                        how='inner'
                    )
                    
                    has_roi_data = not roi_df.empty
                    
                    if has_roi_data:
                        # Calculate ROI metrics
                        roi_df['CPI'] = roi_df.apply(lambda x: x['spend_amount'] / x['inquiries_received'] if x['inquiries_received'] > 0 else 0, axis=1)
                        roi_df['CPA'] = roi_df.apply(lambda x: x['spend_amount'] / x['applications_received'] if x['applications_received'] > 0 else 0, axis=1)
                        roi_df['CPAd'] = roi_df.apply(lambda x: x['spend_amount'] / x['admissions_accepted'] if x['admissions_accepted'] > 0 else 0, axis=1)
                        roi_df['Conversion_Rate'] = roi_df.apply(lambda x: (x['applications_received'] / x['inquiries_received'] * 100) if x['inquiries_received'] > 0 else 0, axis=1)
                    else:
                        # Debug: Show why no match
                        if len(monthly_spend_norm) > 0 and len(admissions_pivot) > 0:
                            with st.expander("🔍 Debug: Why are metrics showing N/A?", expanded=False):
                                st.markdown("**Marketing Data Programs:**")
                                st.write(sorted(monthly_spend_norm['program_normalized'].unique().tolist()))
                                st.markdown("**Admissions Data Programs:**")
                                st.write(sorted(admissions_pivot['program_normalized'].unique().tolist()))
                                st.info("💡 If your selected program doesn't appear in both lists, that's why metrics show N/A. The program names need to match between marketing and admissions data.")
                except Exception as e:
                    has_roi_data = False
                    with st.expander("⚠️ Debug: Error loading admissions data", expanded=False):
                        st.error(f"Error: {str(e)}")
                        st.info("This usually means the admissions_metrics table is empty or doesn't exist. Run the ETL pipeline to populate it.")
                
                # KEY METRICS SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>💰 Marketing Performance Overview</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if has_roi_data:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Spend", f"${filtered_spend['spend_amount'].sum():,.2f}")
                    with col2:
                        avg_cpi = roi_df[roi_df['CPI'] > 0]['CPI'].mean()
                        st.metric("Avg Cost per Inquiry", f"${avg_cpi:,.2f}" if pd.notna(avg_cpi) and avg_cpi > 0 else "N/A")
                    with col3:
                        avg_cpa = roi_df[roi_df['CPA'] > 0]['CPA'].mean()
                        st.metric("Avg Cost per Application", f"${avg_cpa:,.2f}" if pd.notna(avg_cpa) and avg_cpa > 0 else "N/A")
                    with col4:
                        avg_conv = roi_df[roi_df['Conversion_Rate'] > 0]['Conversion_Rate'].mean()
                        st.metric("Avg Conversion Rate", f"{avg_conv:.1f}%" if pd.notna(avg_conv) and avg_conv > 0 else "N/A")
                else:
                    # Fallback to basic metrics if no ROI data
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Spend", f"${filtered_spend['spend_amount'].sum():,.2f}")
                    with col2:
                        st.metric("Programs", filtered_spend['program'].nunique())
                    with col3:
                        st.metric("Channels", filtered_spend['channel'].nunique())
                    with col4:
                        avg_spend = filtered_spend.groupby('channel')['spend_amount'].sum().mean()
                        st.metric("Avg per Channel", f"${avg_spend:,.2f}")
                
                st.divider()
                
                # SPEND BY PROGRAM SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>📊 Spend by Program</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container_prog = st.container(border=True)
                
                with filter_container_prog:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        available_programs = sorted(filtered_spend['program'].unique().tolist())
                        if st.button("✓ All", key="overview_prog_all", use_container_width=True):
                            for program in available_programs:
                                st.session_state[f"overview_prog_check_{program}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="overview_prog_none", use_container_width=True):
                            for program in available_programs:
                                st.session_state[f"overview_prog_check_{program}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'overview_prog_log_scale' not in st.session_state:
                            st.session_state.overview_prog_log_scale = False
                        if st.button("📊 " + ("Log" if not st.session_state.overview_prog_log_scale else "Linear"), 
                                   key="overview_prog_log_toggle", use_container_width=True):
                            st.session_state.overview_prog_log_scale = not st.session_state.overview_prog_log_scale
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Program toggle buttons - FORCE multi-row layout
                    num_programs = len(available_programs)
                    programs_per_row = 4  # Force 4 buttons per row
                    
                    overview_prog_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_programs, programs_per_row):
                        row_end = min(row_start + programs_per_row, num_programs)
                        row_programs = available_programs[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_programs))
                        
                        for idx, program in enumerate(row_programs):
                            with row_cols[idx]:
                                if f"overview_prog_check_{program}" not in st.session_state:
                                    st.session_state[f"overview_prog_check_{program}"] = True
                                
                                is_selected = st.session_state[f"overview_prog_check_{program}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {program}" if is_selected else program
                                
                                if st.button(button_label, key=f"overview_prog_btn_{program}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"overview_prog_check_{program}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"overview_prog_check_{program}"]:
                                    overview_prog_selected.append(program)
                
                # Filter and display chart
                if overview_prog_selected:
                    chart1_data = filtered_spend[filtered_spend['program'].isin(overview_prog_selected)]
                    program_spend = chart1_data.groupby('program')['spend_amount'].sum().sort_values(ascending=False)
                    
                    fig = px.bar(x=program_spend.index, y=program_spend.values,
                               labels={'x': 'Program', 'y': 'Total Spend ($)'},
                               color=program_spend.values, color_continuous_scale='RdYlGn_r',
                               log_y=st.session_state.overview_prog_log_scale)
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, key="overview_prog_chart")
                else:
                    st.info("No programs selected. Click '✓ All' to select all programs.")
                
                st.divider()
                
                # SPEND BY CHANNEL SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>📢 Spend by Channel</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container_chan = st.container(border=True)
                
                with filter_container_chan:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        available_channels = sorted(filtered_spend['channel'].unique().tolist())
                        if st.button("✓ All", key="overview_chan_all", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"overview_chan_check_{channel}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="overview_chan_none", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"overview_chan_check_{channel}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'overview_chan_chart_type' not in st.session_state:
                            st.session_state.overview_chan_chart_type = "Pie"
                        if st.button("📊 " + st.session_state.overview_chan_chart_type, 
                                   key="overview_chan_type_toggle", use_container_width=True):
                            st.session_state.overview_chan_chart_type = "Bar" if st.session_state.overview_chan_chart_type == "Pie" else "Pie"
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Channel toggle buttons - FORCE multi-row layout
                    num_channels = len(available_channels)
                    channels_per_row = 4  # Force 4 buttons per row
                    
                    overview_chan_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_channels, channels_per_row):
                        row_end = min(row_start + channels_per_row, num_channels)
                        row_channels = available_channels[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_channels))
                        
                        for idx, channel in enumerate(row_channels):
                            with row_cols[idx]:
                                if f"overview_chan_check_{channel}" not in st.session_state:
                                    st.session_state[f"overview_chan_check_{channel}"] = True
                                
                                is_selected = st.session_state[f"overview_chan_check_{channel}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {channel}" if is_selected else channel
                                
                                if st.button(button_label, key=f"overview_chan_btn_{channel}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"overview_chan_check_{channel}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"overview_chan_check_{channel}"]:
                                    overview_chan_selected.append(channel)
                
                # Filter and display chart
                if overview_chan_selected:
                    chart2_data = filtered_spend[filtered_spend['channel'].isin(overview_chan_selected)]
                    channel_spend = chart2_data.groupby('channel')['spend_amount'].sum().sort_values(ascending=False)
                    
                    if st.session_state.overview_chan_chart_type == "Pie":
                        fig = px.pie(values=channel_spend.values, names=channel_spend.index,
                                   title='Spend Distribution by Channel')
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                    else:
                        fig = px.bar(x=channel_spend.index, y=channel_spend.values,
                                   labels={'x': 'Channel', 'y': 'Total Spend ($)'},
                                   color=channel_spend.values, color_continuous_scale='RdYlGn_r')
                        fig.update_layout(showlegend=False)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True, key="overview_chan_chart")
                else:
                    st.info("No channels selected. Click '✓ All' to select all channels.")
        
        with advanced_tab:
            # Use globally filtered data
            filtered_spend_adv = filtered_spend_global.copy()
            
            if filtered_spend_adv.empty:
                st.warning("⚠️ No data matches the selected filters")
            else:
                try:
                    # Load admissions data
                    admissions_df = pd.read_sql("""
                        SELECT 
                            report_date,
                            program,
                            metric_name,
                            metric_value
                        FROM admissions_metrics
                        WHERE metric_name IN ('inquiries_received', 'applications_received', 'admissions_accepted')
                    """, conn)
                    
                    # Normalize admissions program names
                    admissions_df['program_normalized'] = admissions_df['program'].apply(normalize_program_name)
                    admissions_df['report_date'] = pd.to_datetime(admissions_df['report_date'])
                    admissions_df['month_date'] = admissions_df['report_date'].dt.to_period('M').dt.to_timestamp()
                    
                    # Pivot admissions data
                    admissions_pivot = admissions_df.pivot_table(
                        index=['month_date', 'program_normalized'],
                        columns='metric_name',
                        values='metric_value',
                        aggfunc='sum'
                    ).reset_index()
                    
                    # Aggregate marketing spend by month and normalized program
                    monthly_spend_norm = filtered_spend_adv.groupby(['month_date', 'program_normalized']).agg({
                        'spend_amount': 'sum'
                    }).reset_index()
                    
                    # Merge on normalized program names
                    roi_df = pd.merge(
                        monthly_spend_norm,
                        admissions_pivot,
                        on=['month_date', 'program_normalized'],
                        how='inner'
                    )
                    
                    if not roi_df.empty and len(roi_df) > 0:
                        # Calculate ROI metrics
                        roi_df['CPI'] = roi_df.apply(lambda x: x['spend_amount'] / x['inquiries_received'] if x['inquiries_received'] > 0 else 0, axis=1)
                        roi_df['CPA'] = roi_df.apply(lambda x: x['spend_amount'] / x['applications_received'] if x['applications_received'] > 0 else 0, axis=1)
                        roi_df['CPAd'] = roi_df.apply(lambda x: x['spend_amount'] / x['admissions_accepted'] if x['admissions_accepted'] > 0 else 0, axis=1)
                        roi_df['Conversion_Rate'] = roi_df.apply(lambda x: (x['applications_received'] / x['inquiries_received'] * 100) if x['inquiries_received'] > 0 else 0, axis=1)
                        
                        # ROI SUMMARY SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>💰 ROI Summary</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            avg_cpi = roi_df[roi_df['CPI'] > 0]['CPI'].mean()
                            st.metric("Avg Cost per Inquiry", f"${avg_cpi:,.2f}" if avg_cpi > 0 else "N/A")
                        with col2:
                            avg_cpa = roi_df[roi_df['CPA'] > 0]['CPA'].mean()
                            st.metric("Avg Cost per Application", f"${avg_cpa:,.2f}" if avg_cpa > 0 else "N/A")
                        with col3:
                            avg_cpad = roi_df[roi_df['CPAd'] > 0]['CPAd'].mean()
                            st.metric("Avg Cost per Admission", f"${avg_cpad:,.2f}" if avg_cpad > 0 else "N/A")
                        with col4:
                            avg_conv = roi_df[roi_df['Conversion_Rate'] > 0]['Conversion_Rate'].mean()
                            st.metric("Avg Conversion Rate", f"{avg_conv:.1f}%" if avg_conv > 0 else "N/A")
                        
                        st.divider()
                        
                        # PROGRAM SPEND BY CHANNEL SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>📊 Program Spend by Channel</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("*See which channels each program invests in*")
                        
                        # Aggregate spend by program and channel
                        program_channel_spend = filtered_spend_adv.groupby(['program_normalized', 'channel'])['spend_amount'].sum().reset_index()
                        
                        if not program_channel_spend.empty:
                            # Create grouped bar chart
                            fig_grouped = px.bar(
                                program_channel_spend,
                                x='program_normalized',
                                y='spend_amount',
                                color='channel',
                                title='Marketing Spend by Program and Channel',
                                labels={'program_normalized': 'Program', 'spend_amount': 'Spend ($)', 'channel': 'Channel'},
                                barmode='group',  # Use 'stack' for stacked bars
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            fig_grouped.update_layout(
                                height=450,
                                xaxis_title="Program",
                                yaxis_title="Spend ($)",
                                legend_title="Channel",
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig_grouped, use_container_width=True, key="program_channel_grouped")
                            
                            # Add toggle for stacked view
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if 'barmode_stacked' not in st.session_state:
                                    st.session_state.barmode_stacked = False
                                if st.button("📊 Toggle Stack/Group", key="toggle_barmode"):
                                    st.session_state.barmode_stacked = not st.session_state.barmode_stacked
                                    st.rerun()
                            with col2:
                                st.caption("Click to switch between grouped (side-by-side) and stacked (cumulative) view")
                            
                            # Show stacked version if toggled
                            if st.session_state.barmode_stacked:
                                fig_stacked = px.bar(
                                    program_channel_spend,
                                    x='program_normalized',
                                    y='spend_amount',
                                    color='channel',
                                    title='Marketing Spend by Program and Channel (Stacked)',
                                    labels={'program_normalized': 'Program', 'spend_amount': 'Spend ($)', 'channel': 'Channel'},
                                    barmode='stack',
                                    color_discrete_sequence=px.colors.qualitative.Set3
                                )
                                fig_stacked.update_layout(
                                    height=450,
                                    xaxis_title="Program",
                                    yaxis_title="Spend ($)",
                                    legend_title="Channel",
                                    hovermode='x unified'
                                )
                                st.plotly_chart(fig_stacked, use_container_width=True, key="program_channel_stacked")
                        
                        st.divider()
                        
                        # CHANNEL PERFORMANCE BY PROGRAM SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>🔗 Channel Performance by Program</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("*Discover which channels drive the most admissions for each program*")
                        
                        # Aggregate spend and admissions by program and channel
                        channel_program_data = filtered_spend_adv.groupby(['program_normalized', 'channel']).agg({
                            'spend_amount': 'sum'
                        }).reset_index()
                        
                        # Merge with admissions data
                        admissions_by_program = admissions_df.groupby('program_normalized').agg({
                            'metric_value': 'sum'
                        }).reset_index()
                        admissions_by_program.columns = ['program_normalized', 'total_admissions']
                        
                        # For correlation, we need channel-level admissions
                        # Since we don't have channel-level admissions, we'll calculate efficiency metrics
                        channel_program_merged = pd.merge(
                            channel_program_data,
                            admissions_by_program,
                            on='program_normalized',
                            how='left'
                        )
                        
                        # Calculate spend share per channel within each program
                        program_totals = channel_program_merged.groupby('program_normalized')['spend_amount'].sum().reset_index()
                        program_totals.columns = ['program_normalized', 'program_total_spend']
                        
                        channel_program_merged = pd.merge(
                            channel_program_merged,
                            program_totals,
                            on='program_normalized'
                        )
                        
                        channel_program_merged['spend_share'] = (
                            channel_program_merged['spend_amount'] / channel_program_merged['program_total_spend'] * 100
                        )
                        
                        # Create pivot table for heatmap
                        heatmap_data = channel_program_merged.pivot_table(
                            index='channel',
                            columns='program_normalized',
                            values='spend_share',
                            fill_value=0
                        )
                        
                        if not heatmap_data.empty:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Heatmap showing spend share
                                fig_heatmap = px.imshow(
                                    heatmap_data,
                                    labels=dict(x="Program", y="Channel", color="Spend Share (%)"),
                                    title="Channel Spend Share by Program",
                                    color_continuous_scale='RdYlGn',
                                    aspect='auto'
                                )
                                fig_heatmap.update_layout(height=400)
                                st.plotly_chart(fig_heatmap, use_container_width=True, key="channel_program_heatmap")
                            
                            with col2:
                                # Show top channel per program
                                top_channels = channel_program_merged.loc[
                                    channel_program_merged.groupby('program_normalized')['spend_amount'].idxmax()
                                ][['program_normalized', 'channel', 'spend_amount', 'spend_share']]
                                
                                st.markdown("**Top Channel per Program:**")
                                for _, row in top_channels.iterrows():
                                    st.markdown(f"**{row['program_normalized']}**: {row['channel']} ({row['spend_share']:.1f}% of program spend)")
                        
                        st.divider()
                        
                        # SPEND VS OUTCOMES TREND SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>📈 Spend vs Outcomes Trend</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        monthly_trends = roi_df.groupby('month_date').agg({
                            'spend_amount': 'sum',
                            'inquiries_received': 'sum',
                            'applications_received': 'sum',
                            'admissions_accepted': 'sum'
                        }).reset_index()
                        
                        if len(monthly_trends) > 1:
                            # Create subplots with shared x-axis
                            from plotly.subplots import make_subplots
                            
                            fig = make_subplots(
                                rows=2, cols=1,
                                subplot_titles=('Marketing Spend Over Time', 'Outcomes Over Time'),
                                vertical_spacing=0.15,
                                row_heights=[0.4, 0.6]
                            )
                            
                            # Top chart: Spend
                            fig.add_trace(
                                go.Bar(x=monthly_trends['month_date'], y=monthly_trends['spend_amount'],
                                      name='Spend ($)', marker_color='lightcoral'),
                                row=1, col=1
                            )
                            
                            # Bottom chart: Outcomes
                            fig.add_trace(
                                go.Scatter(x=monthly_trends['month_date'], y=monthly_trends['inquiries_received'],
                                          name='Inquiries', mode='lines+markers',
                                          line=dict(color='blue', width=3), marker=dict(size=10)),
                                row=2, col=1
                            )
                            fig.add_trace(
                                go.Scatter(x=monthly_trends['month_date'], y=monthly_trends['applications_received'],
                                          name='Applications', mode='lines+markers',
                                          line=dict(color='green', width=3), marker=dict(size=10)),
                                row=2, col=1
                            )
                            fig.add_trace(
                                go.Scatter(x=monthly_trends['month_date'], y=monthly_trends['admissions_accepted'],
                                          name='Admissions', mode='lines+markers',
                                          line=dict(color='purple', width=3), marker=dict(size=10)),
                                row=2, col=1
                            )
                            
                            fig.update_xaxes(title_text="Month", row=2, col=1)
                            fig.update_yaxes(title_text="Spend ($)", row=1, col=1)
                            fig.update_yaxes(title_text="Count", row=2, col=1)
                            
                            fig.update_layout(
                                height=650,
                                hovermode='x unified',
                                showlegend=True,
                                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                                margin=dict(b=100)  # Add bottom margin for legend
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key="adv_trend_chart")
                        
                        st.divider()
                        
                        # DETAILED ROI METRICS SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>📋 Detailed ROI Metrics by Program</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Calculate program_roi for the table
                        program_roi = roi_df.groupby('program_normalized').agg({
                            'spend_amount': 'sum',
                            'inquiries_received': 'sum',
                            'applications_received': 'sum',
                            'admissions_accepted': 'sum',
                            'CPI': 'mean',
                            'CPA': 'mean',
                            'CPAd': 'mean'
                        }).reset_index()
                        
                        display_table = program_roi.round(2).sort_values('CPAd')
                        st.dataframe(
                            display_table.style.background_gradient(
                                subset=['CPI', 'CPA', 'CPAd'], cmap='RdYlGn_r'
                            ).format({
                                'spend_amount': '${:,.2f}',
                                'inquiries_received': '{:.0f}',
                                'applications_received': '{:.0f}',
                                'admissions_accepted': '{:.0f}',
                                'CPI': '${:,.2f}',
                                'CPA': '${:,.2f}',
                                'CPAd': '${:,.2f}'
                            }),
                            use_container_width=True
                        )
                    else:
                        st.warning("⚠️ No matching data between marketing spend and admissions for selected filters")
                        st.info("Try selecting 'All' for broader results, or check that both marketing and admissions data exist for the selected programs.")
                
                except Exception as e:
                    st.error(f"Error loading ROI analytics: {str(e)}")
                    st.info("Ensure admissions data is loaded by running the ETL pipeline.")
        
        with channel_tab:
            # Use globally filtered data
            filtered_spend_chan = filtered_spend_global.copy()
            
            if filtered_spend_chan.empty:
                st.warning("⚠️ No data matches the selected filters")
            else:
                # Get available channels for per-chart filters
                available_channels = sorted(filtered_spend_chan['channel'].unique().tolist())
                
                # KEY METRICS SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>💰 Key Metrics</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Spend", f"${filtered_spend_chan['spend_amount'].sum():,.2f}")
                with col2:
                    st.metric("Channels", filtered_spend_chan['channel'].nunique())
                with col3:
                    st.metric("Programs", filtered_spend_chan['program'].nunique())
                with col4:
                    avg_spend = filtered_spend_chan.groupby('channel')['spend_amount'].sum().mean()
                    st.metric("Avg per Channel", f"${avg_spend:,.2f}")
                
                st.divider()
                
                # CHART 1 - Spend Distribution
                st.markdown("""
                <div class="section-header">
                    <h3>📊 Spend Distribution by Channel</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container = st.container(border=True)
                
                with filter_container:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("✓ All", key="chart1_all", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart1_check_{channel}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="chart1_none", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart1_check_{channel}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'chart1_log_scale' not in st.session_state:
                            st.session_state.chart1_log_scale = False
                        if st.button("📊 " + ("Log" if not st.session_state.chart1_log_scale else "Linear"), 
                                   key="chart1_log_toggle", use_container_width=True):
                            st.session_state.chart1_log_scale = not st.session_state.chart1_log_scale
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Channel toggle buttons - FORCE multi-row layout
                    num_channels = len(available_channels)
                    channels_per_row = 4  # Force 4 buttons per row
                    
                    chart1_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_channels, channels_per_row):
                        row_end = min(row_start + channels_per_row, num_channels)
                        row_channels = available_channels[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_channels))
                        
                        for idx, channel in enumerate(row_channels):
                            with row_cols[idx]:
                                if f"chart1_check_{channel}" not in st.session_state:
                                    st.session_state[f"chart1_check_{channel}"] = True
                                
                                is_selected = st.session_state[f"chart1_check_{channel}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {channel}" if is_selected else channel
                                
                                if st.button(button_label, key=f"chart1_btn_{channel}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"chart1_check_{channel}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"chart1_check_{channel}"]:
                                    chart1_selected.append(channel)
                
                # Filter and display chart
                if chart1_selected:
                    chart1_data = filtered_spend_chan[filtered_spend_chan['channel'].isin(chart1_selected)]
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        channel_totals = chart1_data.groupby('channel')['spend_amount'].sum().sort_values(ascending=False)
                        fig = px.bar(x=channel_totals.index, y=channel_totals.values,
                                   labels={'x': 'Channel', 'y': 'Total Spend ($)'},
                                   title='Total Spend by Channel',
                                   color=channel_totals.values,
                                   color_continuous_scale='RdYlGn_r',
                                   log_y=st.session_state.chart1_log_scale)
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key="channel_bar_chart")
                    
                    with col2:
                        fig = px.pie(values=channel_totals.values, names=channel_totals.index,
                                   title='Channel Spend Share')
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True, key="channel_pie_chart")
                else:
                    st.info("No channels selected. Click '✓ Select All' to select all channels.")
                
                st.divider()
                
                # CHART 2 - Trend Chart
                st.markdown("""
                <div class="section-header">
                    <h3>📈 Channel Spend Trends</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container2 = st.container(border=True)
                
                with filter_container2:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("✓ All", key="chart2_all", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart2_check_{channel}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="chart2_none", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart2_check_{channel}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'chart2_log_scale' not in st.session_state:
                            st.session_state.chart2_log_scale = False
                        if st.button("📊 " + ("Log" if not st.session_state.chart2_log_scale else "Linear"), 
                                   key="chart2_log_toggle", use_container_width=True):
                            st.session_state.chart2_log_scale = not st.session_state.chart2_log_scale
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Channel toggle buttons - FORCE multi-row layout (same as Chart 1)
                    num_channels = len(available_channels)
                    channels_per_row = 4  # Force 4 buttons per row
                    
                    chart2_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_channels, channels_per_row):
                        row_end = min(row_start + channels_per_row, num_channels)
                        row_channels = available_channels[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_channels))
                        
                        for idx, channel in enumerate(row_channels):
                            with row_cols[idx]:
                                if f"chart2_check_{channel}" not in st.session_state:
                                    st.session_state[f"chart2_check_{channel}"] = True
                                
                                is_selected = st.session_state[f"chart2_check_{channel}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {channel}" if is_selected else channel
                                
                                if st.button(button_label, key=f"chart2_btn_{channel}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"chart2_check_{channel}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"chart2_check_{channel}"]:
                                    chart2_selected.append(channel)
                
                # Filter and display chart
                if chart2_selected:
                    chart2_data = filtered_spend_chan[filtered_spend_chan['channel'].isin(chart2_selected)]
                    monthly_channel = chart2_data.groupby(['month_date', 'channel'])['spend_amount'].sum().reset_index()
                    
                    if not monthly_channel.empty:
                        fig = px.line(monthly_channel, x='month_date', y='spend_amount', color='channel',
                                    title='Monthly Spend by Channel',
                                    labels={'month_date': 'Month', 'spend_amount': 'Spend ($)', 'channel': 'Channel'},
                                    markers=True,
                                    log_y=st.session_state.chart2_log_scale)
                        fig.update_layout(height=450, hovermode='x unified')
                        st.plotly_chart(fig, use_container_width=True, key="channel_trend_chart")
                else:
                    st.info("No channels selected. Click '✓ Select All' to select all channels.")
                
                st.divider()
                
                # CHART 3: Summary Table (NO FILTERS)
                st.markdown("""
                <div class="section-header">
                    <h3>📋 Channel Performance Summary</h3>
                </div>
                """, unsafe_allow_html=True)
                
                channel_spend_summary = filtered_spend_chan.groupby('channel').agg({
                    'spend_amount': 'sum',
                    'program': 'nunique',
                    'month_date': 'nunique'
                }).reset_index()
                channel_spend_summary.columns = ['Channel', 'Total Spend', 'Programs', 'Months']
                
                st.dataframe(
                    channel_spend_summary.sort_values('Total Spend', ascending=False).style.background_gradient(
                        subset=['Total Spend'], cmap='RdYlGn_r'
                    ).format({
                        'Total Spend': '${:,.2f}'
                    }),
                    use_container_width=True
                )
        
        with notes_tab:
            # Use globally filtered data
            notes_filtered = filtered_spend_global.copy()
            notes_filtered['month_name'] = notes_filtered['month_date'].dt.strftime('%B %Y')
            
            # Extract notes
            notes_df = notes_filtered[notes_filtered['extra_notes'].notna()].copy()
            unique_notes = []
            
            if not notes_df.empty:
                for _, row in notes_df.iterrows():
                    try:
                        import json
                        notes_list = json.loads(row['extra_notes'])
                        for note in notes_list:
                            note_key = f"{row['program']}_{row['month_date'].strftime('%Y-%m')}_{note[:50]}"
                            if not any(existing['key'] == note_key for existing in unique_notes):
                                unique_notes.append({
                                    'key': note_key,
                                    'program': row['program'],
                                    'month': row['month_date'].strftime('%B %Y'),
                                    'year': row['month_date'].year,
                                    'month_num': row['month_date'].month,
                                    'fiscal_year': row['fiscal_year'],
                                    'note': note
                                })
                    except:
                        pass
            
            if unique_notes:
                notes_display_df = pd.DataFrame(unique_notes)
                notes_display_df = notes_display_df.sort_values(['year', 'month_num'], ascending=[False, False])
                
                # NOTES SECTION HEADER
                st.markdown("""
                <div class="section-header">
                    <h3>📋 Incremental Notes</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Found {len(notes_display_df)} notes**")
                
                # Scrollable container
                notes_container = st.container(height=450)
                with notes_container:
                    for i, (_, note_row) in enumerate(notes_display_df.iterrows()):
                        with st.expander(f"📅 {note_row['program']} - {note_row['month']} ({note_row['fiscal_year']})", expanded=(i < 3)):
                            st.markdown(f"**Note:** {note_row['note']}")
            else:
                st.info("No notes available for selected filters.")
    
    # Footer for Marketing Analysis page
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])
    with footer_col1:
        st.markdown(f"""
        <div class="footer-left footer-content" style="text-align: left;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">📊 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """, unsafe_allow_html=True)
    with footer_col2:
        st.components.v1.html("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%; min-height: 60px;">
            <button onclick="window.top.print()" 
                    style="background-color: white;
                           color: #500000;
                           border: 2px solid #e0e0e0;
                           border-radius: 8px;
                           padding: 0.6rem 1.2rem;
                           font-size: 0.95rem;
                           font-weight: 600;
                           cursor: pointer;
                           transition: all 0.3s ease;
                           width: 100%;
                           min-height: 45px;
                           font-family: 'Source Sans Pro', sans-serif;"
                    onmouseover="this.style.backgroundColor='#e9ecef'; this.style.borderColor='#500000';"
                    onmouseout="this.style.backgroundColor='white'; this.style.borderColor='#e0e0e0';">
                🖨️ Print Page
            </button>
        </div>
        """, height=70)
    with footer_col3:
        st.markdown("""
        <div class="footer-right footer-content" style="text-align: right;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">💡 Use buttons above to switch views</p>
        </div>
        """, unsafe_allow_html=True)

