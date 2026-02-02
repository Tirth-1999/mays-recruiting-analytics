"""
Director's Deep Dive Page Module
Provides detailed program-specific analysis with trends and comparative insights
"""

import streamlit as st
import streamlit.components.v1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Import utility functions
from utils.database import get_connection, load_programs, load_cohort_data, load_yoy_comparison_data


def render():
    """Render the Director's Deep Dive page"""
    
    # Section header for filters
    # Two-column filter layout
    col_cohort, col_program = st.columns(2)

    with col_cohort:
        cohort_options = [2028, 2027, 2026]
        selected_cohort = st.selectbox(
            "📅 Primary Cohort",
            options=cohort_options,
            index=0,
            help="Select primary cohort for analysis"
        )

    with col_program:
        programs_df = load_programs()
        program_options = ["All Programs"] + sorted(programs_df['program_name'].tolist())
        selected_program_filter = st.selectbox(
            "🎓 Program Focus",
            options=program_options,
            help="Filter by specific program"
        )
    
    # How to Use This Section - Collapsible
    with st.expander("💡 How to Use This Section", expanded=False):
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 14px; color: #495057;">
            <div>
                <strong style="color: #500000;">📊 Navigation & Filters:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Primary Cohort:</strong> Select the class year you want to analyze</li>
                    <li><strong>Program Focus:</strong> Filter by specific program or view all programs</li>
                    <li><strong>Four Tabs:</strong> Navigate between Performance, Trends, Programs, and Data Tables</li>
                </ul>
            </div>
            <div>
                <strong style="color: #500000;">🎯 Interactive Features:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Toggle Buttons:</strong> Show/hide specific metrics on charts</li>
                    <li><strong>Log Scale:</strong> Switch between linear and logarithmic scales for better visualization</li>
                    <li><strong>Hover Details:</strong> Move mouse over charts for exact values and insights</li>
                    <li><strong>Export Data:</strong> Download tables and charts for further analysis</li>
                </ul>
            </div>
        </div>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px; margin-bottom: 10px; text-align: center; border: 1px solid #e9ecef;">
            <strong style="color: #495057;">📸 State Snapshot Data:</strong>
            <p style="margin: 8px 0 0 0; color: #6c757d; font-size: 14px; line-height: 1.4;">
                Data represents point-in-time snapshots. Fewer complete applications than offers indicates natural funnel progression.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Load data based on selection
    current_data = load_cohort_data(selected_cohort)

    # Apply program filter if selected
    if selected_program_filter != "All Programs":
        current_data = current_data[current_data['program'] == selected_program_filter]
    if current_data.empty:
        # Handle no data case with better messaging
        if selected_program_filter != "All Programs":
            # Specific program selected but no data available
            st.markdown(f"""
            <div style="text-align: center;
                        padding: 40px 20px;
                        background: #fff3cd;
                        border: 2px solid #ffeaa7;
                        border-radius: 12px;
                        margin: 40px 0;">
                <h2 style="color: #856404; margin: 0 0 15px 0; font-size: 24px;">
                    📊 No Data Available
                </h2>
                <p style="color: #856404; font-size: 18px; margin: 0 0 10px 0; font-weight: 500;">
                    There is no data available for <strong>{selected_program_filter}</strong> in Class of {selected_cohort}.
                </p>
                <p style="color: #6c757d; font-size: 14px; margin: 0; line-height: 1.5;">
                    This program may not be offered for this cohort, or data collection may not have started yet.<br>
                    Try selecting "All Programs" or a different cohort year to see available data.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # All programs selected but no data for entire cohort
            st.markdown(f"""
            <div style="text-align: center;
                        padding: 40px 20px;
                        background: #f8d7da;
                        border: 2px solid #f5c6cb;
                        border-radius: 12px;
                        margin: 40px 0;">
                <h2 style="color: #721c24; margin: 0 0 15px 0; font-size: 24px;">
                    📊 No Data Available
                </h2>
                <p style="color: #721c24; font-size: 18px; margin: 0 0 10px 0; font-weight: 500;">
                    There is no data available for Class of {selected_cohort}.
                </p>
                <p style="color: #6c757d; font-size: 14px; margin: 0; line-height: 1.5;">
                    This cohort may not have started yet, or data collection may be in progress.<br>
                    Try selecting a different cohort year to see available data.
                </p>
            </div>
            """, unsafe_allow_html=True)
        return  # Exit early, don't show empty charts
    else:
        # Find the latest date with complete data
        # For each date, check if we have inquiries_received for all programs
        date_completeness = []
        for date in current_data['report_date'].unique():
            date_df = current_data[current_data['report_date'] == date]
            # Check if we have inquiries_received metric for this date
            inquiries_df = date_df[date_df['metric_name'] == 'inquiries_received']
            total_value = date_df['metric_value'].sum()
            num_programs_with_inquiries = len(inquiries_df)
            
            date_completeness.append({
                'date': date,
                'total_value': total_value,
                'num_programs': num_programs_with_inquiries
            })
        
        completeness_df = pd.DataFrame(date_completeness)
        
        # Get the maximum number of programs with inquiries (baseline for complete data)
        max_programs = completeness_df['num_programs'].max()
        
        # Find dates with non-zero data AND complete program coverage
        complete_dates = completeness_df[
            (completeness_df['total_value'] > 0) & 
            (completeness_df['num_programs'] == max_programs)
        ]['date']
        
        if len(complete_dates) > 0:
            # Use the latest date with complete data
            latest_date = complete_dates.max()
            latest_data = current_data[current_data['report_date'] == latest_date]
        else:
            # Fallback: use latest date with non-zero data
            nonzero_dates = completeness_df[completeness_df['total_value'] > 0]['date']
            if len(nonzero_dates) > 0:
                latest_date = nonzero_dates.max()
                latest_data = current_data[current_data['report_date'] == latest_date]
            else:
                # All dates have zero values - use the latest date anyway
                latest_date = current_data['report_date'].max()
                latest_data = current_data[current_data['report_date'] == latest_date]

        # Calculate comprehensive metrics using latest available value for each metric
        def get_latest_metric_value(metric_name):
            metric_data = current_data[current_data['metric_name'] == metric_name]
            if not metric_data.empty:
                return metric_data.loc[metric_data['report_date'].idxmax(), 'metric_value']
            return 0
        
        inquiries = get_latest_metric_value('inquiries_received')
        applications = get_latest_metric_value('total_applications')
        offers = get_latest_metric_value('admissions_offered')
        accepted = get_latest_metric_value('admissions_accepted')
        enrolled = get_latest_metric_value('anticipated_cohort_size')
        deferred_from_last = get_latest_metric_value('admissions_deferred_from_last')
        in_progress = get_latest_metric_value('applications_in_progress')
        complete = get_latest_metric_value('applications_complete')
        
        # Calculate conversion rates
        conversion_1 = (applications / inquiries * 100) if inquiries > 0 else 0
        conversion_2 = (offers / applications * 100) if applications > 0 else 0
        yield_rate = (accepted / offers * 100) if offers > 0 else 0
        overall_conversion = (enrolled / inquiries * 100) if inquiries > 0 else 0

        # FULL DEEP DIVE - Most comprehensive analysis with advanced metrics
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">Full Deep Dive - Class of {}</h3>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                Complete analytics suite with advanced insights and predictive analysis
            </p>
        </div>
        """.format(selected_cohort), unsafe_allow_html=True)
        
        # Comprehensive KPI Grid using CSS Grid with responsive font sizing
        st.markdown("""
        <style>
        .full-metrics-container {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 1rem;
            margin: 20px 0;
        }
        .full-metric-box {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center !important;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 120px;
        }
        .full-metric-box * {
            text-align: center !important;
        }
        .full-metric-number {
            color: #500000 !important;
            margin: 0 !important;
            padding: 0 0 0 15px !important;
            font-size: clamp(1rem, 1.8vw + 0.5rem, 1.8rem) !important;
            font-weight: bold !important;
            line-height: 1.1 !important;
            text-align: center !important;
            width: 100% !important;
            display: block !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-sizing: border-box !important;
            text-indent: 0 !important;
            letter-spacing: 0 !important;
        }
        .full-metric-label {
            margin: 8px auto 3px auto !important;
            padding: 0 5px !important;
            color: #495057 !important;
            font-weight: 500 !important;
            font-size: clamp(0.75rem, 1.2vw + 0.3rem, 0.9rem) !important;
            line-height: 1.2 !important;
            text-align: center !important;
            width: 100% !important;
            display: block !important;
        }
        .full-metric-small {
            color: #6c757d !important;
            font-size: clamp(0.65rem, 1vw + 0.25rem, 0.8rem) !important;
            text-align: center !important;
            margin: 0 !important;
        }
        
        /* Adjust for narrower screens (sidebar open on laptop) */
        @media (max-width: 1400px) {
            .full-metrics-container {
                grid-template-columns: repeat(3, 1fr);
                gap: 0.8rem;
            }
            .full-metric-number {
                font-size: clamp(0.9rem, 1.5vw + 0.4rem, 1.5rem) !important;
            }
            .full-metric-label {
                font-size: clamp(0.7rem, 1vw + 0.25rem, 0.85rem) !important;
            }
            .full-metric-small {
                font-size: clamp(0.6rem, 0.9vw + 0.2rem, 0.75rem) !important;
            }
        }
        
        /* Tablet portrait */
        @media (max-width: 900px) {
            .full-metrics-container {
                grid-template-columns: repeat(2, 1fr);
            }
            .full-metric-number {
                font-size: clamp(1.2rem, 2vw + 0.5rem, 1.8rem) !important;
            }
            .full-metric-label {
                font-size: clamp(0.8rem, 1.3vw + 0.3rem, 0.95rem) !important;
            }
            .full-metric-small {
                font-size: clamp(0.7rem, 1.1vw + 0.25rem, 0.8rem) !important;
            }
        }
        
        /* Mobile */
        @media (max-width: 768px) {
            .full-metrics-container {
                grid-template-columns: 1fr;
            }
            .full-metric-number {
                font-size: clamp(1.5rem, 3vw + 0.5rem, 2rem) !important;
            }
            .full-metric-label {
                font-size: clamp(0.9rem, 2vw + 0.3rem, 1.1rem) !important;
            }
            .full-metric-small {
                font-size: clamp(0.8rem, 1.5vw + 0.3rem, 0.9rem) !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get additional metrics for comprehensive view
        applications_received = get_latest_metric_value('applications_received')
        applications_manual = get_latest_metric_value('applications_manual')
        applications_verified = get_latest_metric_value('applications_verified')
        applications_on_hold = get_latest_metric_value('applications_on_hold')
        applications_undelivered = get_latest_metric_value('applications_undelivered')
        applications_deferral = get_latest_metric_value('applications_deferral')
        
        admissions_denied = get_latest_metric_value('admissions_denied')
        admissions_declined = get_latest_metric_value('admissions_declined')
        admissions_deferred_to_next = get_latest_metric_value('admissions_deferred_to_next')
        admissions_withdrawn = get_latest_metric_value('admissions_withdrawn')
        admissions_moved_to_other = get_latest_metric_value('admissions_moved_to_other')
        
        st.markdown(f"""
        <div class="full-metrics-container">
            <div class="full-metric-box">
                <h2 class="full-metric-number">{int(inquiries)}</h2>
                <p class="full-metric-label">Inquiries</p>
                <small class="full-metric-small">Total received</small>
            </div>
            <div class="full-metric-box">
                <h2 class="full-metric-number">{int(applications)}</h2>
                <p class="full-metric-label">Applications</p>
                <small class="full-metric-small" style="color: {'#28a745' if conversion_1 > 30 else '#ffc107' if conversion_1 > 20 else '#dc3545'} !important;">{conversion_1:.1f}% conv.</small>
            </div>
            <div class="full-metric-box">
                <h2 class="full-metric-number">{int(in_progress)}</h2>
                <p class="full-metric-label">In Progress</p>
                <small class="full-metric-small">Applications</small>
            </div>
            <div class="full-metric-box">
                <h2 class="full-metric-number">{int(complete)}</h2>
                <p class="full-metric-label">Complete</p>
                <small class="full-metric-small">Applications</small>
            </div>
            <div class="full-metric-box">
                <h2 class="full-metric-number">{int(offers)}</h2>
                <p class="full-metric-label">Offers</p>
                <small class="full-metric-small">{conversion_2:.1f}% rate</small>
            </div>
            <div class="full-metric-box">
                <h2 class="full-metric-number">{int(enrolled)}</h2>
                <p class="full-metric-label">Enrolled</p>
                <small class="full-metric-small" style="color: {'#28a745' if yield_rate > 70 else '#ffc107' if yield_rate > 50 else '#dc3545'} !important;">{yield_rate:.1f}% yield</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add comprehensive metrics breakdown section
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # Add consistent spacing above expandable sections
        st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
        
        # Create expandable sections for detailed metrics
        col1, col2 = st.columns(2)
        
        # Add CSS styles once for both tables
        st.markdown("""
        <style>
        .metric-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 14px;
        }
        .metric-table th {
            background: #500000;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
        }
        .metric-table td {
            padding: 10px 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        .metric-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        .metric-number {
            font-weight: 600;
            color: #500000;
            text-align: right;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with col1:
            with st.expander("**Application Status Breakdown**", expanded=False):
                st.markdown(f"""
                <table class="metric-table">
                    <thead>
                        <tr>
                            <th>Application Status</th>
                            <th style="text-align: right;">Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Total Applications</td>
                            <td class="metric-number">{int(applications):,}</td>
                        </tr>
                        <tr>
                            <td>In Progress</td>
                            <td class="metric-number">{int(in_progress):,}</td>
                        </tr>
                        <tr>
                            <td>Complete</td>
                            <td class="metric-number">{int(complete):,}</td>
                        </tr>
                        <tr>
                            <td>Received</td>
                            <td class="metric-number">{int(applications_received):,}</td>
                        </tr>
                        <tr>
                            <td>Manual Review</td>
                            <td class="metric-number">{int(applications_manual):,}</td>
                        </tr>
                        <tr>
                            <td>Verified</td>
                            <td class="metric-number">{int(applications_verified):,}</td>
                        </tr>
                        <tr>
                            <td>On Hold</td>
                            <td class="metric-number">{int(applications_on_hold):,}</td>
                        </tr>
                        <tr>
                            <td>Undelivered</td>
                            <td class="metric-number">{int(applications_undelivered):,}</td>
                        </tr>
                        <tr>
                            <td>Deferral</td>
                            <td class="metric-number">{int(applications_deferral):,}</td>
                        </tr>
                    </tbody>
                </table>
                """, unsafe_allow_html=True)
        
        with col2:
            with st.expander("**Admissions Decision Breakdown**", expanded=False):
                st.markdown(f"""
                <table class="metric-table">
                    <thead>
                        <tr>
                            <th>Admissions Decision</th>
                            <th style="text-align: right;">Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Offers Made</td>
                            <td class="metric-number">{int(offers):,}</td>
                        </tr>
                        <tr>
                            <td>Accepted</td>
                            <td class="metric-number">{int(accepted):,}</td>
                        </tr>
                        <tr>
                            <td>Denied</td>
                            <td class="metric-number">{int(admissions_denied):,}</td>
                        </tr>
                        <tr>
                            <td>Declined by Student</td>
                            <td class="metric-number">{int(admissions_declined):,}</td>
                        </tr>
                        <tr>
                            <td>Deferred to Next Cohort</td>
                            <td class="metric-number">{int(admissions_deferred_to_next):,}</td>
                        </tr>
                        <tr>
                            <td>Deferred from Previous</td>
                            <td class="metric-number">{int(deferred_from_last):,}</td>
                        </tr>
                        <tr>
                            <td>Moved to Other Program</td>
                            <td class="metric-number">{int(admissions_moved_to_other):,}</td>
                        </tr>
                        <tr>
                            <td>Withdrawn</td>
                            <td class="metric-number">{int(admissions_withdrawn):,}</td>
                        </tr>
                        <tr style="background: #e8f5e8; font-weight: 600;">
                            <td><strong>Final Enrolled</strong></td>
                            <td class="metric-number" style="color: #28a745;"><strong>{int(enrolled):,}</strong></td>
                        </tr>
                    </tbody>
                </table>
                """, unsafe_allow_html=True)

        # Add consistent spacing below expandable sections
        st.markdown("<div style='margin: 0px 0;'></div>", unsafe_allow_html=True)

        # Advanced Analytics Tabs
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # Chrome-style tabs CSS (same as Marketing Analysis)
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
        
        # Prepare complete_data for use across tabs (needed for Data Tables and Advanced Insights)
        complete_data = current_data.pivot_table(
            index=['report_date', 'program'],
            columns='metric_name',
            values='metric_value',
            aggfunc='sum'
        ).reset_index()  # No fillna - preserve actual data patterns
        
        # Tab content using native Streamlit tabs (Chrome-style)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Performance Analysis", "Trend Analysis", "Program Deep Dive", "Data Tables", "Comparison Tool"])
        
        with tab1:
            # Complete conversion funnel with log scale toggle - FULL WIDTH
            st.markdown("<h4 style='text-align: center; color: #500000;'>Complete Conversion Funnel</h4>", unsafe_allow_html=True)
            
            # Initialize log scale state for full deep dive funnel
            if 'exec_full_funnel_log' not in st.session_state:
                st.session_state.exec_full_funnel_log = False
            
            # Log scale toggle button - centered
            col_spacer1, col_toggle, col_spacer2 = st.columns([2, 1, 2])
            with col_toggle:
                toggle_label = "📊 Linear Scale" if st.session_state.exec_full_funnel_log else "📊 Log Scale"
                if st.button(
                    toggle_label,
                    key="toggle_log_full_funnel",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_funnel_log else "secondary"
                ):
                    st.session_state.exec_full_funnel_log = not st.session_state.exec_full_funnel_log
                    st.rerun()
            
            funnel_data = [inquiries, applications, complete, offers, accepted, enrolled]
            funnel_labels = ['Inquiries', 'Applications', 'Complete Apps', 'Offers', 'Accepted', 'Enrolled']
            
            if st.session_state.exec_full_funnel_log:
                # Use bar chart with log scale
                fig = go.Figure(go.Bar(
                    x=funnel_labels,
                    y=funnel_data,
                    marker={"color": ["#500000", "#600000", "#700000", "#800000", "#900000", "#B00000"]},
                    text=funnel_data,
                    texttemplate='%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Count: %{y:,.0f}<extra></extra>'
                ))
                fig.update_layout(
                    height=500,
                    showlegend=False,
                    yaxis_type='log',
                    yaxis_title='Count (Log Scale)',
                    xaxis_title='Stage',
                    margin=dict(t=80, b=50, l=80, r=80)
                )
            else:
                # Use funnel chart
                fig = go.Figure(go.Funnel(
                    y=funnel_labels,
                    x=funnel_data,
                    textinfo="value+percent initial",
                    marker={"color": ["#500000", "#600000", "#700000", "#800000", "#900000", "#B00000"]}
                ))
                fig.update_layout(
                    height=500,
                    margin=dict(t=50, b=50, l=80, r=80)
                )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add note about deferred students if applicable
            if deferred_from_last > 0:
                st.markdown(f"""
                <div style="text-align: center; margin: 20px 0; padding: 8px 15px; background: #f8f9fa; border-radius: 6px;">
                    <small style="color: #6c757d; font-size: 14px;">
                        Note: {int(deferred_from_last)} student(s) deferred from previous cohort joined this class.
                    </small>
                </div>
                """, unsafe_allow_html=True)
            
            # Divider between charts
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Performance metrics radar chart - WITH PROFESSIONAL DROPDOWN EXPLANATION
            st.markdown("<h4 style='text-align: center; color: #500000;'>Performance Radar</h4>", unsafe_allow_html=True)
            
            # Add helpful note about chart interactivity
            st.markdown("""
            <div style="background: #f0f8ff; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center; font-size: 0.85rem;">
                💡 <strong>Interactive Chart:</strong> Use toolbar to zoom, pan, or reset view • Double-click to auto-scale • Hover for exact values
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate current values for display
            app_completion_rate = (complete / applications * 100) if applications > 0 else 0
            
            # Add JavaScript to detect screen width and store in session state
            st.markdown("""
            <script>
            const width = window.innerWidth;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: width}, '*');
            </script>
            """, unsafe_allow_html=True)
            
            # Use a single column layout that will naturally stack on smaller screens
            # Streamlit automatically handles responsive behavior
            st.markdown("""
            <style>
            /* Force columns to stack at 1400px breakpoint */
            @media (max-width: 1400px) {
                [data-testid="column"] {
                    width: 100% !important;
                    flex: 100% !important;
                    max-width: 100% !important;
                }
            }
            
            /* Remove gaps between expanders to make them look like a single widget */
            div[data-testid="stExpander"] {
                margin-bottom: 0px !important;
                border-bottom: none !important;
            }
            div[data-testid="stExpander"]:first-of-type {
                border-top-left-radius: 8px !important;
                border-top-right-radius: 8px !important;
            }
            div[data-testid="stExpander"]:last-of-type {
                border-bottom-left-radius: 8px !important;
                border-bottom-right-radius: 8px !important;
                border-bottom: 1px solid #e0e0e0 !important;
            }
            
            /* Responsive spacing - only add top margin on larger screens */
            @media (min-width: 1401px) {
                .radar-explanation-spacer {
                    height: 120px;
                }
            }
            @media (max-width: 1400px) {
                .radar-explanation-spacer {
                    height: 20px;
                }
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create two columns: radar chart on left, explanation on right
            radar_col, explanation_col = st.columns([1.3, 1], gap="large")
            
            with radar_col:
                metrics = ['Inquiry Conversion', 'Application Completion', 'Selectivity', 'Yield Rate', 'Overall Efficiency']
                values = [
                    conversion_1,
                    app_completion_rate,
                    conversion_2,
                    yield_rate,
                    overall_conversion
                ]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=metrics,
                    fill='toself',
                    name='Performance',
                    line_color='#500000',
                    fillcolor='rgba(80, 0, 0, 0.3)'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    height=600,
                    margin=dict(t=50, b=50, l=80, r=120)
                )
                
                # Enhanced config with better zoom controls
                config = {
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['resetScale2d'],
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'performance_radar',
                        'height': 600,
                        'width': 800,
                        'scale': 1
                    }
                }
                
                st.plotly_chart(fig, use_container_width=True, config=config)
            
            with explanation_col:
                # Add vertical spacing to center the widget (responsive)
                st.markdown("<div class='radar-explanation-spacer'></div>", unsafe_allow_html=True)
                
                # Metric 1: Inquiry Conversion
                with st.expander("**Inquiry Conversion**", expanded=False):
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 8px; margin-bottom: 15px;">
                        <div style="font-size: 36px; font-weight: 700; color: #500000;">{conversion_1:.1f}%</div>
                        <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">Current Performance</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <tr style="background: #f8f9fa;">
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Formula</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-family: 'Courier New', monospace;">(Applications ÷ Inquiries) × 100</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Meaning</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">Percentage of inquiries that convert to applications. Higher values indicate effective engagement.</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                
                # Metric 2: Application Completion
                with st.expander("**Application Completion**", expanded=False):
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 8px; margin-bottom: 15px;">
                        <div style="font-size: 36px; font-weight: 700; color: #500000;">{app_completion_rate:.1f}%</div>
                        <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">Current Performance</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <tr style="background: #f8f9fa;">
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Formula</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-family: 'Courier New', monospace;">(Complete Apps ÷ Total Apps) × 100</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Meaning</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">Percentage of started applications that are completed. Indicates application process efficiency.</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                
                # Metric 3: Selectivity
                with st.expander("**Selectivity**", expanded=False):
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 8px; margin-bottom: 15px;">
                        <div style="font-size: 36px; font-weight: 700; color: #500000;">{conversion_2:.1f}%</div>
                        <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">Current Performance</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <tr style="background: #f8f9fa;">
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Formula</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-family: 'Courier New', monospace;">(Offers ÷ Applications) × 100</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Meaning</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">Percentage of applications that receive offers. Reflects admission standards and competitiveness.</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                
                # Metric 4: Yield Rate
                with st.expander("**Yield Rate**", expanded=False):
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 8px; margin-bottom: 15px;">
                        <div style="font-size: 36px; font-weight: 700; color: #500000;">{yield_rate:.1f}%</div>
                        <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">Current Performance</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <tr style="background: #f8f9fa;">
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Formula</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-family: 'Courier New', monospace;">(Accepted ÷ Offers) × 100</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Meaning</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">Percentage of offers that are accepted. Indicates program attractiveness and competitiveness.</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
                
                # Metric 5: Overall Efficiency
                with st.expander("**Overall Efficiency**", expanded=False):
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); border-radius: 8px; margin-bottom: 15px;">
                        <div style="font-size: 36px; font-weight: 700; color: #500000;">{overall_conversion:.1f}%</div>
                        <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">Current Performance</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <tr style="background: #f8f9fa;">
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Formula</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-family: 'Courier New', monospace;">(Enrolled ÷ Inquiries) × 100</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: 600; color: #500000;">Meaning</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">End-to-end conversion from inquiry to enrollment. Measures overall funnel effectiveness.</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)
            
            # Add Correlation Matrix and Performance Benchmarks to Performance Analysis
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Correlation analysis - full width with better color scale
            st.markdown("<h4 style='text-align: center; color: #500000;'>Correlation Matrix</h4>", unsafe_allow_html=True)
            
            if not complete_data.empty:
                numeric_data = complete_data.select_dtypes(include=[np.number])
                if len(numeric_data.columns) > 1:
                    correlation_matrix = numeric_data.corr()
                    
                    # Use green (high correlation) to red (low correlation) color scale
                    fig = px.imshow(
                        correlation_matrix,
                        labels=dict(color="Correlation"),
                        color_continuous_scale=[[0, '#dc3545'], [0.5, '#ffc107'], [1, '#28a745']],  # Red -> Yellow -> Green
                        aspect="auto",
                        zmin=-1,
                        zmax=1
                    )
                    fig.update_layout(
                        title="Correlation Matrix (Green = High Correlation, Red = Low Correlation)",
                        height=600,
                        width=1000
                    )
                    
                    # Center the chart
                    col_spacer1, col_chart, col_spacer2 = st.columns([0.2, 3, 0.2])
                    with col_chart:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Add dynamic explanation dropdown - centered
                    col_exp_spacer1, col_exp_content, col_exp_spacer2 = st.columns([0.2, 3, 0.2])
                    with col_exp_content:
                        with st.expander("How to Use This Section", expanded=False):
                            # Generate dynamic insights based on correlation values
                            insights_html = []
                            
                            # Find key correlations (if columns exist)
                            key_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 
                                         'admissions_accepted', 'anticipated_cohort_size']
                            
                            available_metrics = [m for m in key_metrics if m in correlation_matrix.columns]
                            
                            if len(available_metrics) >= 2:
                                # Find strongest positive correlations
                                for i, metric1 in enumerate(available_metrics):
                                    for metric2 in available_metrics[i+1:]:
                                        corr_value = correlation_matrix.loc[metric1, metric2]
                                        if abs(corr_value) > 0.7:  # Strong correlation
                                            metric1_clean = metric1.replace('_', ' ').title()
                                            metric2_clean = metric2.replace('_', ' ').title()
                                            
                                            if corr_value > 0.7:
                                                insights_html.append(f"<p style='margin: 10px 0; font-size: 14px; color: #495057; line-height: 1.6; text-align: center;'><strong style='color: #28a745;'>Strong Positive Link:</strong> {metric1_clean} and {metric2_clean} move together ({corr_value:.2f}). When one increases, the other typically does too.</p>")
                                            elif corr_value < -0.7:
                                                insights_html.append(f"<p style='margin: 10px 0; font-size: 14px; color: #495057; line-height: 1.6; text-align: center;'><strong style='color: #dc3545;'>Inverse Relationship:</strong> {metric1_clean} and {metric2_clean} move in opposite directions ({corr_value:.2f}). This may indicate a bottleneck.</p>")
                            
                            # Build the complete HTML
                            html_content = """<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
<h5 style="color: #500000; margin-top: 0; text-align: center;">Understanding the Correlation Matrix</h5>
<div style="margin-bottom: 20px;">
<strong style="color: #500000; display: block; text-align: center;">What It Shows:</strong>
<p style="margin: 5px 0; font-size: 14px; color: #495057; line-height: 1.6; text-align: center;">This matrix reveals how different metrics relate to each other. Each cell shows the correlation between two metrics, ranging from -1 (perfect inverse relationship) to +1 (perfect positive relationship).</p>
</div>
<div style="margin-bottom: 20px;">
<strong style="color: #500000; display: block; text-align: center;">Color Guide:</strong>
<ul style="margin: 5px 0; font-size: 14px; color: #495057; line-height: 1.6; list-style-position: inside; text-align: center; list-style-type: none;">
<li><span style="color: #28a745; font-weight: 600;">Green (0.7 to 1.0)</span>: Strong positive correlation - metrics move together</li>
<li><span style="color: #ffc107; font-weight: 600;">Yellow (0.3 to 0.7)</span>: Moderate correlation - some relationship exists</li>
<li><span style="color: #dc3545; font-weight: 600;">Red (-1.0 to 0.3)</span>: Weak or negative correlation - metrics don't move together</li>
</ul>
</div>
<div style="margin-bottom: 20px;">
<strong style="color: #500000; display: block; text-align: center;">How to Use This:</strong>
<ol style="margin: 5px 0; font-size: 14px; color: #495057; line-height: 1.6; text-align: left; max-width: 800px; margin-left: auto; margin-right: auto;">
<li><strong>Identify Leading Indicators:</strong> Strong correlations help predict future outcomes. If inquiries strongly correlate with enrollments, early inquiry numbers forecast final results.</li>
<li><strong>Spot Bottlenecks:</strong> Weak correlations between sequential stages (e.g., applications to offers) may indicate process issues.</li>
<li><strong>Validate Strategies:</strong> Check if marketing spend correlates with inquiries, or if program changes impact conversion rates.</li>
<li><strong>Benchmark Health:</strong> Healthy programs show predictable patterns. Unusual correlations flag areas needing attention.</li>
</ol>
</div>"""
                            
                            # Add dynamic insights if any were found
                            if insights_html:
                                html_content += """<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
<strong style="color: #500000; display: block; text-align: center;">Key Insights from Your Data:</strong>
</div>"""
                                html_content += "".join(insights_html[:3])  # Show top 3 insights
                            else:
                                html_content += """<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 15px;">
<p style="margin: 0; font-size: 14px; color: #856404; line-height: 1.6; text-align: center;"><strong>Tip:</strong> Look for dark green cells to find your strongest predictive relationships. These are the metrics you should monitor most closely for forecasting.</p>
</div>"""
                            
                            html_content += "</div>"
                            
                            st.markdown(html_content, unsafe_allow_html=True)
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Performance benchmarks - full width stretched layout with center alignment
            st.markdown("<h4 style='text-align: center; color: #500000;'>Performance Benchmarks</h4>", unsafe_allow_html=True)
            
            # Add CSS to center-align metrics while preserving styling
            st.markdown("""
            <style>
            [data-testid="stMetric"] {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            [data-testid="stMetricLabel"] {
                display: flex;
                justify-content: center;
                width: 100%;
            }
            [data-testid="stMetricLabel"] > div {
                text-align: center;
            }
            [data-testid="stMetricValue"] {
                display: flex;
                justify-content: center;
                width: 100%;
            }
            [data-testid="stMetricDelta"] {
                display: flex;
                justify-content: center;
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)
            
            benchmarks = {
                'Inquiry Conversion': {'value': conversion_1, 'benchmark': 30, 'unit': '%'},
                'Yield Rate': {'value': yield_rate, 'benchmark': 60, 'unit': '%'},
                'Application Completion': {'value': (complete / applications * 100) if applications > 0 else 0, 'benchmark': 80, 'unit': '%'}
            }
            
            # Use columns with no gap and custom spacing
            col1, col2, col3 = st.columns([1, 1, 1])
            for idx, (metric, data) in enumerate(benchmarks.items()):
                with [col1, col2, col3][idx]:
                    performance = "🟢 Above" if data['value'] > data['benchmark'] else "🟡 At" if abs(data['value'] - data['benchmark']) < 5 else "🔴 Below"
                    st.metric(
                        metric,
                        f"{data['value']:.1f}{data['unit']}",
                        f"{performance} benchmark ({data['benchmark']}{data['unit']})"
                    )
        
        with tab2:
            # Initialize session state for toggle buttons
            if 'exec_full_show_inq' not in st.session_state:
                st.session_state.exec_full_show_inq = True
            if 'exec_full_show_apps' not in st.session_state:
                st.session_state.exec_full_show_apps = True
            if 'exec_full_show_offers' not in st.session_state:
                st.session_state.exec_full_show_offers = True
            if 'exec_full_show_cohort' not in st.session_state:
                st.session_state.exec_full_show_cohort = True
            
            # Toggle buttons for metric selection
            metric_col1, metric_col2, metric_col3, metric_col4, scale_col = st.columns([1, 1, 1, 1, 1])
            
            with metric_col1:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_inq else '○'} Inquiries",
                    key="toggle_inq_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_inq else "secondary"
                ):
                    st.session_state.exec_full_show_inq = not st.session_state.exec_full_show_inq
                    st.rerun()
            
            with metric_col2:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_apps else '○'} Applications",
                    key="toggle_apps_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_apps else "secondary"
                ):
                    st.session_state.exec_full_show_apps = not st.session_state.exec_full_show_apps
                    st.rerun()
            
            with metric_col3:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_offers else '○'} Offers",
                    key="toggle_offers_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_offers else "secondary"
                ):
                    st.session_state.exec_full_show_offers = not st.session_state.exec_full_show_offers
                    st.rerun()
            
            with metric_col4:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_cohort else '○'} Cohort Size",
                    key="toggle_cohort_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_cohort else "secondary"
                ):
                    st.session_state.exec_full_show_cohort = not st.session_state.exec_full_show_cohort
                    st.rerun()
            
            # Initialize scale type state
            if 'exec_full_scale_type' not in st.session_state:
                st.session_state.exec_full_scale_type = 'Linear'
            
            with scale_col:
                scale_options = ['Linear', 'Log', 'Square Root']
                current_scale = st.session_state.exec_full_scale_type
                next_scale_idx = (scale_options.index(current_scale) + 1) % len(scale_options)
                next_scale = scale_options[next_scale_idx]
                
                if st.button(
                    f"📊 {current_scale}",
                    key="toggle_scale_full",
                    use_container_width=True,
                    type="secondary",
                    help=f"Click to switch to {next_scale} scale"
                ):
                    st.session_state.exec_full_scale_type = next_scale
                    st.rerun()
            
            # Multi-line time series - only use actual reported data (no fillna)
            time_series = current_data.pivot_table(
                index='report_date',
                columns='metric_name',
                values='metric_value',
                aggfunc='sum'
            )  # No fillna - preserve natural data endpoints
            
            if not time_series.empty:
                fig = go.Figure()
                
                key_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'anticipated_cohort_size']
                colors = ['#500000', '#700000', '#900000', '#B00000']
                metric_labels = ['Inquiries Received', 'Total Applications', 'Admissions Offered', 'Anticipated Cohort Size']
                show_flags = [st.session_state.exec_full_show_inq, st.session_state.exec_full_show_apps, st.session_state.exec_full_show_offers, st.session_state.exec_full_show_cohort]
                
                for i, (metric, label, show_flag) in enumerate(zip(key_metrics, metric_labels, show_flags)):
                    if metric in time_series.columns and show_flag:
                        # Apply scale transformation to y values
                        y_values = time_series[metric]
                        
                        if st.session_state.exec_full_scale_type == 'Log':
                            # For log scale, replace zeros with small value to avoid log(0)
                            y_values = y_values.replace(0, 0.1)
                        elif st.session_state.exec_full_scale_type == 'Square Root':
                            # Apply square root transformation
                            y_values = np.sqrt(y_values)
                        
                        fig.add_trace(go.Scatter(
                            x=time_series.index,
                            y=y_values,
                            mode='lines+markers',
                            name=label,
                            line=dict(color=colors[i], width=3),
                            marker=dict(size=8),
                            hovertemplate='<b>' + label + '</b><br>' +
                                         'Date: %{x}<br>' +
                                         'Count: %{y:,.0f}<br>' +
                                         '<extra></extra>'
                        ))
                
                # Set y-axis type and title based on scale
                if st.session_state.exec_full_scale_type == 'Log':
                    yaxis_type = 'log'
                    yaxis_title = 'Count (Log Scale)'
                elif st.session_state.exec_full_scale_type == 'Square Root':
                    yaxis_type = 'linear'
                    yaxis_title = 'Count (Square Root Scale)'
                else:
                    yaxis_type = 'linear'
                    yaxis_title = 'Count'
                
                fig.update_layout(
                    title={
                        'text': f'Key Metrics Trends Over Time - {st.session_state.exec_full_scale_type} Scale',
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    height=500,
                    xaxis_title='Date',
                    yaxis_title=yaxis_title,
                    yaxis_type=yaxis_type,
                    legend=dict(
                        orientation='h',
                        x=0.5,
                        y=1.12,
                        xanchor='center',
                        yanchor='top',
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='rgba(0,0,0,0.3)',
                        borderwidth=1
                    ),
                    margin=dict(t=120, b=50, l=80, r=80)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Growth rate analysis
                st.markdown("<h4 style='text-align: center; color: #500000;'>Growth Rate Analysis</h4>", unsafe_allow_html=True)
                
                # Add helpful hint explaining the growth rate analysis
                st.markdown("""
                <div style="background: #f0f8ff;
                            padding: 12px;
                            border-radius: 6px;
                            margin-bottom: 15px;
                            text-align: center;
                            font-size: 0.9rem;">
                    💡 <strong>Tip:</strong> Compares first vs. last data point for the fiscal year • 🟢 Positive growth • 🔴 Decline • 🟡 Moderate change
                </div>
                """, unsafe_allow_html=True)
                
                growth_data = []
                for metric in key_metrics:
                    if metric in time_series.columns:
                        # Get all values for this metric
                        values = time_series[metric].values
                        dates = time_series.index
                        
                        # Find all non-zero values to get the actual data range
                        non_zero_indices = [i for i, v in enumerate(values) if v > 0]
                        
                        if len(non_zero_indices) >= 2:
                            # Use the FIRST and LAST non-zero values (start vs end of fiscal year)
                            first_idx = non_zero_indices[0]  # First data point
                            last_idx = non_zero_indices[-1]  # Last data point
                            first_val = float(values[first_idx])
                            last_val = float(values[last_idx])
                            first_date = dates[first_idx]
                            last_date = dates[last_idx]
                        elif len(non_zero_indices) == 1:
                            # Only one data point - no growth calculation possible
                            continue
                        elif len(values) >= 2:
                            # Fall back to first and last values even if zero
                            first_val = float(values[0])
                            last_val = float(values[-1])
                            first_date = dates[0]
                            last_date = dates[-1]
                        else:
                            continue  # Not enough data points
                        
                        # Calculate growth rate from start to end of period
                        if first_val > 0:
                            growth_rate = ((last_val - first_val) / first_val * 100)
                        elif last_val > 0 and first_val == 0:
                            growth_rate = 100.0  # Growth from zero
                        else:
                            growth_rate = 0.0  # Both zero
                        
                        # Add to growth data
                        growth_data.append({
                            'Metric': metric.replace('_', ' ').title(),
                            'Growth Rate (%)': growth_rate,
                            'End Value': last_val,
                            'Start Value': first_val,
                            'End Date': last_date.strftime('%b %Y'),
                            'Start Date': first_date.strftime('%b %Y')
                        })
                
                if growth_data:
                    growth_df = pd.DataFrame(growth_data)
                    
                    # Apply color styling with proper gradient
                    styled_df = growth_df.style.format({
                        'Growth Rate (%)': '{:+.1f}%',
                        'End Value': '{:.0f}',
                        'Start Value': '{:.0f}'
                    }).background_gradient(
                        subset=['Growth Rate (%)'], 
                        cmap='RdYlGn',
                        vmin=-50,  # Red for large declines
                        vmax=50    # Green for large growth
                    )
                    
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.info("📊 Growth rate analysis requires at least two time periods with data. Please check back when more data is available.")
        
        with tab3:
            # Define metric categories
            applications_metrics = [
                'inquiries_received', 'applications_in_progress', 'applications_received', 
                'applications_complete', 'applications_manual', 'applications_verified', 
                'applications_on_hold', 'applications_undelivered', 'applications_deferral', 
                'total_applications', 'admissions_pre_admission'
            ]
            
            admissions_metrics = [
                'admissions_offered', 'admissions_denied', 'admissions_accepted', 
                'admissions_declined', 'admissions_deferred_to_next', 'admissions_deferred_from_last', 
                'admissions_moved_to_other', 'admissions_withdrawn', 'anticipated_cohort_size'
            ]
            
            # Get time series data for all programs
            program_time_series = current_data.pivot_table(
                index='report_date',
                columns='metric_name',
                values='metric_value',
                aggfunc='sum'
            )  # No fillna - preserve natural data endpoints
            
            # Function to clean up metric names for shorter legends
            def clean_metric_name(metric_name):
                """Clean up metric names for shorter, cleaner legends"""
                # Convert to title case first
                display_name = metric_name.replace('_', ' ').title()
                
                # Remove redundant prefixes for cleaner legends
                prefixes_to_remove = [
                    'Applications ', 'Admissions ', 'Anticipated ', 'Total '
                ]
                
                for prefix in prefixes_to_remove:
                    if display_name.startswith(prefix):
                        display_name = display_name[len(prefix):]
                        break
                
                # Handle special cases for even cleaner names
                replacements = {
                    'Cohort Size': 'Enrolled',
                    'In Progress': 'In Progress',
                    'Received': 'Received',
                    'Complete': 'Complete',
                    'Manual': 'Manual Review',
                    'Verified': 'Verified',
                    'On Hold': 'On Hold',
                    'Undelivered': 'Undelivered',
                    'Deferral': 'Deferral',
                    'Offered': 'Offered',
                    'Denied': 'Denied',
                    'Accepted': 'Accepted',
                    'Declined': 'Declined',
                    'Deferred To Next': 'Deferred Out',
                    'Deferred From Last': 'Deferred In',
                    'Moved To Other': 'Moved',
                    'Withdrawn': 'Withdrawn'
                }
                
                return replacements.get(display_name, display_name)
            
            if not program_time_series.empty:
                # ===== APPLICATIONS SECTION =====
                st.markdown("<h4 style='text-align: center; color: #500000;'>📝 Applications Metrics</h4>", unsafe_allow_html=True)
                
                # Initialize session state for applications filter
                if 'exec_app_metrics_reset' not in st.session_state:
                    st.session_state.exec_app_metrics_reset = 0
                
                # Initialize log scale state for applications
                if 'exec_app_log' not in st.session_state:
                    st.session_state.exec_app_log = False
                
                # Initialize chart type state for applications
                if 'exec_app_chart_type' not in st.session_state:
                    st.session_state.exec_app_chart_type = 'Line'
                
                available_app_metrics = [m for m in applications_metrics if m in program_time_series.columns]
                
                app_reset_suffix = f"_{st.session_state.exec_app_metrics_reset}"
                app_state_key = f'selected_app_metrics{app_reset_suffix}'
                
                if app_state_key not in st.session_state:
                    st.session_state[app_state_key] = available_app_metrics.copy()
                
                current_app_selection = st.session_state[app_state_key]
                
                if len(current_app_selection) == len(available_app_metrics):
                    app_summary_text = "All application metrics"
                elif len(current_app_selection) == 0:
                    app_summary_text = "No metrics selected"
                elif len(current_app_selection) == 1:
                    app_summary_text = current_app_selection[0].replace('_', ' ').title()
                else:
                    app_summary_text = f"{len(current_app_selection)} metrics selected"
                
                # Layout: 60% for filter, 20% for chart type, 20% for log scale button
                col_filter, col_chart_type, col_button = st.columns([3, 1, 1])
                
                with col_filter:
                    with st.popover(app_summary_text, use_container_width=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✓ All", key=f"app_all{app_reset_suffix}", use_container_width=True, type="primary"):
                                st.session_state.exec_app_metrics_reset += 1
                                new_app_key = f'selected_app_metrics_{st.session_state.exec_app_metrics_reset}'
                                st.session_state[new_app_key] = available_app_metrics.copy()
                                st.rerun()
                        with col_b:
                            if st.button("✗ Clear", key=f"app_clear{app_reset_suffix}", use_container_width=True, type="secondary"):
                                st.session_state.exec_app_metrics_reset += 1
                                new_app_key = f'selected_app_metrics_{st.session_state.exec_app_metrics_reset}'
                                st.session_state[new_app_key] = []
                                st.rerun()
                        
                        st.divider()
                        
                        for idx, metric in enumerate(available_app_metrics):
                            is_checked = metric in st.session_state[app_state_key]
                            metric_display = metric.replace('_', ' ').title()
                            new_value = st.checkbox(
                                metric_display, 
                                value=is_checked, 
                                key=f"app_cb_{idx}{app_reset_suffix}"
                            )
                            
                            if new_value != is_checked:
                                if new_value:
                                    if metric not in st.session_state[app_state_key]:
                                        st.session_state[app_state_key].append(metric)
                                else:
                                    if metric in st.session_state[app_state_key]:
                                        st.session_state[app_state_key].remove(metric)
                                st.rerun()
                
                with col_chart_type:
                    # Show what you can switch TO, not what you currently have
                    next_chart_type = 'Bar' if st.session_state.exec_app_chart_type == 'Line' else 'Line'
                    if st.button(
                        f"📊 {next_chart_type}",
                        key="toggle_chart_type_app",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_app_chart_type = next_chart_type
                        st.rerun()
                
                with col_button:
                    if st.button(
                        f"📈 {'Log' if st.session_state.exec_app_log else 'Linear'}",
                        key="toggle_log_app",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_app_log = not st.session_state.exec_app_log
                        st.rerun()
                
                selected_app_metrics = st.session_state.get(app_state_key, available_app_metrics)
                
                # Applications chart
                if len(selected_app_metrics) > 0:
                    fig_app = go.Figure()
                    
                    # Color palette for applications
                    app_colors = ['#500000', '#700000', '#900000', '#B00000', '#D00000', '#F00000', 
                                 '#FF4444', '#FF6666', '#FF8888', '#FFAAAA', '#FFCCCC']
                    
                    if st.session_state.exec_app_chart_type == 'Line':
                        # Line chart with data labels - filter out zeros to avoid vertical lines
                        for i, metric in enumerate(selected_app_metrics):
                            if metric in program_time_series.columns:
                                metric_display = clean_metric_name(metric)
                                
                                # Filter out zero values for line charts to avoid vertical lines
                                metric_data = program_time_series[metric]
                                non_zero_mask = metric_data > 0
                                filtered_dates = program_time_series.index[non_zero_mask]
                                filtered_values = metric_data[non_zero_mask]
                                
                                if len(filtered_values) > 0:  # Only add trace if there's data
                                    fig_app.add_trace(go.Scatter(
                                        x=filtered_dates,
                                        y=filtered_values,
                                        mode='lines+markers+text',
                                        name=metric_display,
                                        line=dict(color=app_colors[i % len(app_colors)], width=3),
                                        marker=dict(size=8),
                                        text=[f'{int(val)}' for val in filtered_values],
                                        textposition='top center',
                                        textfont=dict(size=10, color=app_colors[i % len(app_colors)]),
                                        hovertemplate=f'<b>{metric_display}</b><br>' +
                                                     'Date: %{x}<br>' +
                                                     'Value: %{y:,.0f}<br>' +
                                                     '<extra></extra>'
                                    ))
                    else:
                        # Bar chart (grouped)
                        for i, metric in enumerate(selected_app_metrics):
                            if metric in program_time_series.columns:
                                metric_display = clean_metric_name(metric)
                                fig_app.add_trace(go.Bar(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    name=metric_display,
                                    marker_color=app_colors[i % len(app_colors)],
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
                                    textposition='outside',
                                    textfont=dict(size=10),
                                    hovertemplate=f'<b>{metric_display}</b><br>' +
                                                 'Date: %{x}<br>' +
                                                 'Value: %{y:,.0f}<br>' +
                                                 '<extra></extra>'
                                ))
                        fig_app.update_layout(barmode='group')
                    
                    fig_app.update_layout(
                        title={
                            'text': 'Applications Metrics Over Time',
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        height=600,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        yaxis_type='log' if st.session_state.exec_app_log else 'linear',
                        legend=dict(
                            orientation='h',
                            x=0.5,
                            y=1.15,
                            xanchor='center',
                            yanchor='top',
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.3)',
                            borderwidth=1,
                            font=dict(size=10),
                            itemwidth=30,
                            tracegroupgap=5
                        ),
                        margin=dict(b=50, t=150, l=40, r=40)
                    )
                    st.plotly_chart(fig_app, use_container_width=True)
                else:
                    st.info("💡 Please select at least one application metric to display.")
                
                # ===== ADMISSIONS SECTION =====
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown("<h4 style='text-align: center; color: #500000;'>🎓 Admissions Metrics</h4>", unsafe_allow_html=True)
                
                # Initialize session state for admissions filter
                if 'exec_adm_metrics_reset' not in st.session_state:
                    st.session_state.exec_adm_metrics_reset = 0
                
                # Initialize log scale state for admissions
                if 'exec_adm_log' not in st.session_state:
                    st.session_state.exec_adm_log = False
                
                # Initialize chart type state for admissions
                if 'exec_adm_chart_type' not in st.session_state:
                    st.session_state.exec_adm_chart_type = 'Line'
                
                available_adm_metrics = [m for m in admissions_metrics if m in program_time_series.columns]
                
                adm_reset_suffix = f"_{st.session_state.exec_adm_metrics_reset}"
                adm_state_key = f'selected_adm_metrics{adm_reset_suffix}'
                
                if adm_state_key not in st.session_state:
                    st.session_state[adm_state_key] = available_adm_metrics.copy()
                
                current_adm_selection = st.session_state[adm_state_key]
                
                if len(current_adm_selection) == len(available_adm_metrics):
                    adm_summary_text = "All admission metrics"
                elif len(current_adm_selection) == 0:
                    adm_summary_text = "No metrics selected"
                elif len(current_adm_selection) == 1:
                    adm_summary_text = current_adm_selection[0].replace('_', ' ').title()
                else:
                    adm_summary_text = f"{len(current_adm_selection)} metrics selected"
                
                # Layout: 60% for filter, 20% for chart type, 20% for log scale button
                col_filter_adm, col_chart_type_adm, col_button_adm = st.columns([3, 1, 1])
                
                with col_filter_adm:
                    with st.popover(adm_summary_text, use_container_width=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✓ All", key=f"adm_all{adm_reset_suffix}", use_container_width=True, type="primary"):
                                st.session_state.exec_adm_metrics_reset += 1
                                new_adm_key = f'selected_adm_metrics_{st.session_state.exec_adm_metrics_reset}'
                                st.session_state[new_adm_key] = available_adm_metrics.copy()
                                st.rerun()
                        with col_b:
                            if st.button("✗ Clear", key=f"adm_clear{adm_reset_suffix}", use_container_width=True, type="secondary"):
                                st.session_state.exec_adm_metrics_reset += 1
                                new_adm_key = f'selected_adm_metrics_{st.session_state.exec_adm_metrics_reset}'
                                st.session_state[new_adm_key] = []
                                st.rerun()
                        
                        st.divider()
                        
                        for idx, metric in enumerate(available_adm_metrics):
                            is_checked = metric in st.session_state[adm_state_key]
                            metric_display = metric.replace('_', ' ').title()
                            new_value = st.checkbox(
                                metric_display, 
                                value=is_checked, 
                                key=f"adm_cb_{idx}{adm_reset_suffix}"
                            )
                            
                            if new_value != is_checked:
                                if new_value:
                                    if metric not in st.session_state[adm_state_key]:
                                        st.session_state[adm_state_key].append(metric)
                                else:
                                    if metric in st.session_state[adm_state_key]:
                                        st.session_state[adm_state_key].remove(metric)
                                st.rerun()
                
                with col_chart_type_adm:
                    # Show what you can switch TO, not what you currently have
                    next_chart_type = 'Bar' if st.session_state.exec_adm_chart_type == 'Line' else 'Line'
                    if st.button(
                        f"📊 {next_chart_type}",
                        key="toggle_chart_type_adm",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_adm_chart_type = next_chart_type
                        st.rerun()
                
                with col_button_adm:
                    if st.button(
                        f"📈 {'Log' if st.session_state.exec_adm_log else 'Linear'}",
                        key="toggle_log_adm",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_adm_log = not st.session_state.exec_adm_log
                        st.rerun()
                
                selected_adm_metrics = st.session_state.get(adm_state_key, available_adm_metrics)
                
                # Admissions chart
                if len(selected_adm_metrics) > 0:
                    fig_adm = go.Figure()
                    
                    # Color palette for admissions (different shades)
                    adm_colors = ['#003366', '#004488', '#0055AA', '#0066CC', '#0077EE', 
                                 '#3399FF', '#5AADFF', '#7AC1FF', '#99D5FF']
                    
                    if st.session_state.exec_adm_chart_type == 'Line':
                        # Line chart with data labels - filter out zeros to avoid vertical lines
                        for i, metric in enumerate(selected_adm_metrics):
                            if metric in program_time_series.columns:
                                metric_display = clean_metric_name(metric)
                                
                                # Filter out zero values for line charts to avoid vertical lines
                                metric_data = program_time_series[metric]
                                non_zero_mask = metric_data > 0
                                filtered_dates = program_time_series.index[non_zero_mask]
                                filtered_values = metric_data[non_zero_mask]
                                
                                if len(filtered_values) > 0:  # Only add trace if there's data
                                    fig_adm.add_trace(go.Scatter(
                                        x=filtered_dates,
                                        y=filtered_values,
                                        mode='lines+markers+text',
                                        name=metric_display,
                                        line=dict(color=adm_colors[i % len(adm_colors)], width=3),
                                        marker=dict(size=8),
                                        text=[f'{int(val)}' for val in filtered_values],
                                        textposition='top center',
                                        textfont=dict(size=10, color=adm_colors[i % len(adm_colors)]),
                                        hovertemplate=f'<b>{metric_display}</b><br>' +
                                                     'Date: %{x}<br>' +
                                                     'Value: %{y:,.0f}<br>' +
                                                     '<extra></extra>'
                                    ))
                    else:
                        # Bar chart (grouped)
                        for i, metric in enumerate(selected_adm_metrics):
                            if metric in program_time_series.columns:
                                metric_display = clean_metric_name(metric)
                                fig_adm.add_trace(go.Bar(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    name=metric_display,
                                    marker_color=adm_colors[i % len(adm_colors)],
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
                                    textposition='outside',
                                    textfont=dict(size=10),
                                    hovertemplate=f'<b>{metric_display}</b><br>' +
                                                 'Date: %{x}<br>' +
                                                 'Value: %{y:,.0f}<br>' +
                                                 '<extra></extra>'
                                ))
                        fig_adm.update_layout(barmode='group')
                    
                    fig_adm.update_layout(
                        title={
                            'text': 'Admissions Metrics Over Time',
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        height=600,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        yaxis_type='log' if st.session_state.exec_adm_log else 'linear',
                        legend=dict(
                            orientation='h',
                            x=0.5,
                            y=1.15,
                            xanchor='center',
                            yanchor='top',
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.3)',
                            borderwidth=1,
                            font=dict(size=10),
                            itemwidth=30,
                            tracegroupgap=5
                        ),
                        margin=dict(b=50, t=150, l=40, r=40)
                    )
                    st.plotly_chart(fig_adm, use_container_width=True)
                else:
                    st.info("💡 Please select at least one admission metric to display.")
        
        with tab4:
            # Data Tables
            st.markdown("<h4 style='text-align: center; color: #500000;'>📊 Complete Dataset</h4>", unsafe_allow_html=True)
            st.dataframe(complete_data, use_container_width=True, height=400)
            
            # Summary statistics
            st.markdown("<h4 style='text-align: center; color: #500000;'>📈 Summary Statistics</h4>", unsafe_allow_html=True)
            numeric_cols = complete_data.select_dtypes(include=[np.number]).columns
            summary_stats = complete_data[numeric_cols].describe()
            st.dataframe(summary_stats.round(2), use_container_width=True)
            
            # Download options - centered and full width
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_complete = complete_data.to_csv(index=False)
                st.download_button(
                    "📥 Download Complete Data",
                    csv_complete,
                    f"complete_data_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col2:
                csv_summary = summary_stats.to_csv()
                st.download_button(
                    "📥 Download Summary Stats",
                    csv_summary,
                    f"summary_stats_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col3:
                # Create executive summary report
                exec_summary = pd.DataFrame({
                    'Metric': ['Total Inquiries', 'Total Applications', 'Total Offers', 'Total Enrolled', 'Conversion Rate', 'Yield Rate'],
                    'Value': [inquiries, applications, offers, enrolled, f"{conversion_1:.1f}%", f"{yield_rate:.1f}%"]
                })
                csv_exec = exec_summary.to_csv(index=False)
                st.download_button(
                    "📥 Download Executive Summary",
                    csv_exec,
                    f"executive_summary_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        with tab5:
            # Comparison Tool - Cohort-to-Cohort Analysis
            key_prefix = "exec_dive_comp"
            
            # Cohort selection filters
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**🎓 Primary Cohort**")
                cohort_options = [2028, 2027, 2026]
                primary_cohort = st.selectbox(
                    "Primary Cohort",
                    options=cohort_options,
                    index=0,
                    key=f"{key_prefix}_primary",
                    label_visibility="collapsed"
                )

            with col2:
                st.markdown("**🔄 Comparison Cohort**")
                comparison_cohorts = [c for c in cohort_options if c != primary_cohort]
                if comparison_cohorts:
                    comparison_cohort = st.selectbox(
                        "Comparison Cohort",
                        options=comparison_cohorts,
                        key=f"{key_prefix}_secondary",
                        label_visibility="collapsed"
                    )
                else:
                    st.warning("No other cohorts available for comparison")
                    comparison_cohort = None

            with col3:
                st.markdown("**📚 Program Filter**")
                programs_df = load_programs()
                program_options = ['All Programs'] + sorted(programs_df['program_name'].tolist())
                program_filter_comp = st.selectbox(
                    "Program Filter",
                    options=program_options,
                    key=f"{key_prefix}_program",
                    label_visibility="collapsed"
                )

            # How to Use - Collapsible
            with st.expander("💡 How to Use This Comparison Tool", expanded=False):
                st.markdown("""
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 14px; color: #495057;">
                    <div>
                        <strong style="color: #500000;">📊 Step-by-Step Guide:</strong>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li><strong>Select Cohorts:</strong> Choose primary and comparison cohorts using filters above</li>
                            <li><strong>Filter by Program:</strong> Select specific program or view all programs combined</li>
                            <li><strong>Explore Time Series:</strong> Click metric selector to visualize trends over time</li>
                            <li><strong>View Data Tables:</strong> Click "Show Data Table" for detailed program breakdowns</li>
                        </ul>
                    </div>
                    <div>
                        <strong style="color: #500000;">🎯 Key Features:</strong>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li><strong>Percentage Changes:</strong> Full-width bar chart showing growth/decline metrics</li>
                            <li><strong>Comprehensive Table:</strong> Detailed comparison with variance metrics</li>
                            <li><strong>Export Options:</strong> Download comparison tables or individual cohort data</li>
                            <li><strong>Visual Indicators:</strong> Green = growth, Red = decline, hover for exact values</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Load comparison data
            if comparison_cohort:
                comp_data = load_yoy_comparison_data(primary_cohort, comparison_cohort)
                primary_data = comp_data[comp_data['cohort_year'] == primary_cohort]
                secondary_data = comp_data[comp_data['cohort_year'] == comparison_cohort]

                # Apply program filter
                if program_filter_comp != "All Programs":
                    primary_data = primary_data[primary_data['program'] == program_filter_comp]
                    secondary_data = secondary_data[secondary_data['program'] == program_filter_comp]

                if not primary_data.empty and not secondary_data.empty:
                    # Get latest data with non-zero values for both cohorts
                    # Primary cohort
                    primary_dates_with_data = primary_data.groupby('report_date')['metric_value'].sum()
                    primary_dates_with_nonzero = primary_dates_with_data[primary_dates_with_data > 0].index
                    if len(primary_dates_with_nonzero) > 0:
                        primary_latest_date = primary_dates_with_nonzero.max()
                    else:
                        primary_latest_date = primary_data['report_date'].max()
                    primary_latest = primary_data[primary_data['report_date'] == primary_latest_date]

                    # Secondary cohort
                    secondary_dates_with_data = secondary_data.groupby('report_date')['metric_value'].sum()
                    secondary_dates_with_nonzero = secondary_dates_with_data[secondary_dates_with_data > 0].index
                    if len(secondary_dates_with_nonzero) > 0:
                        secondary_latest_date = secondary_dates_with_nonzero.max()
                    else:
                        secondary_latest_date = secondary_data['report_date'].max()
                    secondary_latest = secondary_data[secondary_data['report_date'] == secondary_latest_date]

                    program_scope = f" - {program_filter_comp}" if program_filter_comp != "All Programs" else ""

                    # Display comparison header
                    st.markdown(f"""
                    <div style="text-align: center;
                                padding: 15px;
                                background: #e9ecef;
                                border-radius: 8px;
                                margin: 20px 0;">
                        <h3 style="color: #500000; margin: 0; font-size: 20px;">
                            Comparing: Class of {primary_cohort} vs Class of {comparison_cohort}{program_scope}
                        </h3>
                        <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                            Primary: {primary_latest_date.strftime('%B %d, %Y')} | Comparison: {secondary_latest_date.strftime('%B %d, %Y')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Calculate metrics for both cohorts
                    primary_metrics = primary_latest.groupby('metric_name')['metric_value'].sum()
                    secondary_metrics = secondary_latest.groupby('metric_name')['metric_value'].sum()

                    # Create comprehensive comparison dataframe
                    yoy_comparison = pd.DataFrame({
                        f'Class of {primary_cohort}': primary_metrics,
                        f'Class of {comparison_cohort}': secondary_metrics
                    }).fillna(0)

                    yoy_comparison['Absolute Change'] = yoy_comparison[f'Class of {primary_cohort}'] - yoy_comparison[f'Class of {comparison_cohort}']

                    # Calculate % Change with proper handling of edge cases
                    def calculate_pct_change(row):
                        primary_val = row[f'Class of {primary_cohort}']
                        comparison_val = row[f'Class of {comparison_cohort}']

                        if primary_val == 0 and comparison_val == 0:
                            return 0.0
                        if comparison_val == 0 and primary_val > 0:
                            return np.nan
                        if primary_val == 0 and comparison_val > 0:
                            return -100.0
                        return ((primary_val / comparison_val) - 1) * 100

                    yoy_comparison['% Change'] = yoy_comparison.apply(calculate_pct_change, axis=1).round(1)

                    # Calculate variance metrics
                    yoy_comparison['Mean'] = yoy_comparison[[f'Class of {primary_cohort}', f'Class of {comparison_cohort}']].mean(axis=1)
                    yoy_comparison['Variance'] = (
                        ((yoy_comparison[f'Class of {primary_cohort}'] - yoy_comparison['Mean']) ** 2 + 
                         (yoy_comparison[f'Class of {comparison_cohort}'] - yoy_comparison['Mean']) ** 2) / 2
                    )
                    yoy_comparison['Std Deviation'] = np.sqrt(yoy_comparison['Variance'])
                    yoy_comparison['Coefficient of Variation'] = np.where(
                        yoy_comparison['Mean'] != 0,
                        (yoy_comparison['Std Deviation'] / yoy_comparison['Mean']) * 100,
                        0
                    ).round(2)

                    # Add performance indicators
                    def get_performance_indicator(row):
                        pct_change = row['% Change']
                        primary_val = row[f'Class of {primary_cohort}']
                        comparison_val = row[f'Class of {comparison_cohort}']

                        if comparison_val == 0 and primary_val > 0:
                            return '🟢 New Metric - Strong Growth (No Base Year Data)'
                        if primary_val == 0 and comparison_val > 0:
                            return '🔴 Complete Decline (Metric Discontinued)'
                        if pct_change > 15:
                            return '🟢 Strong Growth'
                        elif pct_change > 5:
                            return '🟡 Moderate Growth'
                        elif pct_change >= -5:
                            return '➡️ Stable'
                        else:
                            return '🔴 Decline'

                    yoy_comparison['Performance Indicator'] = yoy_comparison.apply(get_performance_indicator, axis=1)

                    # Filter out metrics where BOTH cohorts have zero values
                    metrics_with_data = yoy_comparison[
                        (yoy_comparison[f'Class of {primary_cohort}'] != 0) | 
                        (yoy_comparison[f'Class of {comparison_cohort}'] != 0)
                    ]

                    excluded_metrics = yoy_comparison[
                        (yoy_comparison[f'Class of {primary_cohort}'] == 0) & 
                        (yoy_comparison[f'Class of {comparison_cohort}'] == 0)
                    ].index.tolist()

                    yoy_comparison = metrics_with_data.copy()

                    # Initialize session state for time series metrics filter
                    reset_key = f'{key_prefix}_ts_metrics_reset'
                    if reset_key not in st.session_state:
                        st.session_state[reset_key] = 0

                    # Metric selector for time series
                    all_metrics = sorted(primary_data['metric_name'].unique())
                    available_metrics = [m for m in all_metrics if m in yoy_comparison.index]

                    ts_reset_suffix = f"_{st.session_state[reset_key]}"
                    ts_state_key = f'{key_prefix}_selected_ts_metrics{ts_reset_suffix}'

                    # Set default selection
                    default_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'anticipated_cohort_size']
                    default_selection = [m for m in default_metrics if m in available_metrics]
                    if not default_selection:
                        default_selection = available_metrics[:4] if len(available_metrics) >= 4 else available_metrics

                    if ts_state_key not in st.session_state:
                        st.session_state[ts_state_key] = default_selection.copy()

                    current_ts_selection = st.session_state[ts_state_key]

                    # Create summary text for popover button
                    if len(current_ts_selection) == len(available_metrics):
                        ts_summary_text = "All metrics selected"
                    elif len(current_ts_selection) == 0:
                        ts_summary_text = "No metrics selected - Click to select"
                    elif len(current_ts_selection) == 1:
                        ts_summary_text = current_ts_selection[0].replace('_', ' ').title()
                    else:
                        ts_summary_text = f"{len(current_ts_selection)} metrics selected"

                    # Custom popover dropdown
                    with st.popover(f"📊 {ts_summary_text}", use_container_width=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✓ All", key=f"{key_prefix}_ts_all{ts_reset_suffix}", use_container_width=True, type="primary"):
                                st.session_state[reset_key] += 1
                                new_ts_key = f'{key_prefix}_selected_ts_metrics_{st.session_state[reset_key]}'
                                st.session_state[new_ts_key] = available_metrics.copy()
                                st.rerun()
                        with col_b:
                            if st.button("✗ Clear", key=f"{key_prefix}_ts_clear{ts_reset_suffix}", use_container_width=True, type="secondary"):
                                st.session_state[reset_key] += 1
                                new_ts_key = f'{key_prefix}_selected_ts_metrics_{st.session_state[reset_key]}'
                                st.session_state[new_ts_key] = []
                                st.rerun()

                        st.divider()

                        for idx, metric in enumerate(available_metrics):
                            is_checked = metric in st.session_state[ts_state_key]
                            metric_display = metric.replace('_', ' ').title()
                            new_value = st.checkbox(
                                metric_display, 
                                value=is_checked, 
                                key=f"{key_prefix}_ts_cb_{idx}{ts_reset_suffix}"
                            )

                            if new_value != is_checked:
                                if new_value:
                                    if metric not in st.session_state[ts_state_key]:
                                        st.session_state[ts_state_key].append(metric)
                                else:
                                    if metric in st.session_state[ts_state_key]:
                                        st.session_state[ts_state_key].remove(metric)
                                st.rerun()

                    selected_ts_metrics = st.session_state.get(ts_state_key, default_selection)

                    if selected_ts_metrics:
                        for idx, metric in enumerate(selected_ts_metrics):
                            # Properly aggregate data by date
                            primary_ts = primary_data[primary_data['metric_name'] == metric].groupby('report_date')['metric_value'].sum().reset_index().sort_values('report_date')
                            secondary_ts = secondary_data[secondary_data['metric_name'] == metric].groupby('report_date')['metric_value'].sum().reset_index().sort_values('report_date')

                            # Keep original data for drill-down
                            primary_detail = primary_data[primary_data['metric_name'] == metric].sort_values(['report_date', 'program'])
                            secondary_detail = secondary_data[secondary_data['metric_name'] == metric].sort_values(['report_date', 'program'])

                            if not primary_ts.empty or not secondary_ts.empty:
                                # Display metric name as section header
                                st.markdown(f"""
                                <div style="text-align: center;
                                            padding: 10px;
                                            background: #e9ecef;
                                            border-radius: 6px;
                                            margin: 15px 0 10px 0;">
                                    <h4 style="color: #500000; margin: 0; font-size: 16px;">{metric.replace('_', ' ').title()}</h4>
                                </div>
                                """, unsafe_allow_html=True)

                                # Side-by-side comparison
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(f"<p style='text-align: center; font-weight: bold; color: #500000;'>Class of {primary_cohort}</p>", unsafe_allow_html=True)
                                    if not primary_ts.empty:
                                        fig_primary = go.Figure()
                                        fig_primary.add_trace(go.Scatter(
                                            x=primary_ts['report_date'],
                                            y=primary_ts['metric_value'],
                                            mode='lines+markers+text',
                                            name=f'Class of {primary_cohort}',
                                            line=dict(color='#500000', width=4),
                                            marker=dict(size=12, symbol='circle'),
                                            text=[f'{int(val):,}' for val in primary_ts['metric_value']],
                                            textposition='top center',
                                            textfont=dict(size=10, color='#500000'),
                                            hovertemplate='<b>%{x|%b %d, %Y}</b><br>Value: %{y:,.0f}<extra></extra>',
                                            showlegend=False
                                        ))

                                        fig_primary.update_layout(
                                            height=350,
                                            xaxis_title='Date',
                                            yaxis_title='Count',
                                            xaxis=dict(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor='#500000', linewidth=2),
                                            yaxis=dict(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor='#500000', linewidth=2),
                                            plot_bgcolor='#fafafa',
                                            margin=dict(t=40, b=60, l=60, r=40)
                                        )
                                        st.plotly_chart(fig_primary, use_container_width=True, key=f"{key_prefix}_primary_{metric}_{idx}")
                                    else:
                                        st.info("No data available")

                                with col2:
                                    st.markdown(f"<p style='text-align: center; font-weight: bold; color: #B00000;'>Class of {comparison_cohort}</p>", unsafe_allow_html=True)
                                    if not secondary_ts.empty:
                                        fig_secondary = go.Figure()
                                        fig_secondary.add_trace(go.Scatter(
                                            x=secondary_ts['report_date'],
                                            y=secondary_ts['metric_value'],
                                            mode='lines+markers+text',
                                            name=f'Class of {comparison_cohort}',
                                            line=dict(color='#B00000', width=4),
                                            marker=dict(size=12, symbol='diamond'),
                                            text=[f'{int(val):,}' for val in secondary_ts['metric_value']],
                                            textposition='top center',
                                            textfont=dict(size=10, color='#B00000'),
                                            hovertemplate='<b>%{x|%b %d, %Y}</b><br>Value: %{y:,.0f}<extra></extra>',
                                            showlegend=False
                                        ))

                                        fig_secondary.update_layout(
                                            height=350,
                                            xaxis_title='Date',
                                            yaxis_title='Count',
                                            xaxis=dict(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor='#B00000', linewidth=2),
                                            yaxis=dict(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor='#B00000', linewidth=2),
                                            plot_bgcolor='#fafafa',
                                            margin=dict(t=40, b=60, l=60, r=40)
                                        )
                                        st.plotly_chart(fig_secondary, use_container_width=True, key=f"{key_prefix}_secondary_{metric}_{idx}")
                                    else:
                                        st.info("No data available")

                                # Centered button for this metric
                                col_left, col_center, col_right = st.columns([2, 1, 2])
                                with col_center:
                                    table_key = f"{key_prefix}_table_visible_{metric}_{idx}"
                                    if table_key not in st.session_state:
                                        st.session_state[table_key] = False

                                    button_label = "Hide Data Table" if st.session_state[table_key] else "📊 Show Data Table"
                                    if st.button(button_label, key=f"{key_prefix}_btn_metric_{metric}_{idx}", use_container_width=True):
                                        st.session_state[table_key] = not st.session_state[table_key]
                                        st.rerun()

                                # Data tables with expandable rows
                                if st.session_state.get(table_key, False):
                                    col1, col2 = st.columns(2)

                                    with col1:
                                        if not primary_ts.empty:
                                            st.markdown("**📋 Data Details (Click to expand by program)**")
                                            for date_idx, row in primary_ts.iterrows():
                                                date_val = pd.to_datetime(row['report_date'])
                                                total_val = int(row['metric_value'])
                                                date_str = date_val.strftime('%b %d, %Y')
                                                date_details = primary_detail[primary_detail['report_date'] == row['report_date']]

                                                with st.expander(f"📅 {date_str} - Total: {total_val:,}"):
                                                    if not date_details.empty:
                                                        breakdown = date_details[['program', 'metric_value']].copy()
                                                        breakdown.columns = ['Program', 'Value']
                                                        breakdown['Value'] = breakdown['Value'].astype(int)
                                                        st.dataframe(
                                                            breakdown.style.set_properties(**{'text-align': 'center', 'font-size': '13px'}).set_table_styles([
                                                                {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#500000'), ('color', 'white'), ('font-weight', 'bold')]}
                                                            ]),
                                                            use_container_width=True,
                                                            hide_index=True
                                                        )
                                                    else:
                                                        st.info("No program breakdown available")

                                    with col2:
                                        if not secondary_ts.empty:
                                            st.markdown("**📋 Data Details (Click to expand by program)**")
                                            for date_idx, row in secondary_ts.iterrows():
                                                date_val = pd.to_datetime(row['report_date'])
                                                total_val = int(row['metric_value'])
                                                date_str = date_val.strftime('%b %d, %Y')
                                                date_details = secondary_detail[secondary_detail['report_date'] == row['report_date']]

                                                with st.expander(f"📅 {date_str} - Total: {total_val:,}"):
                                                    if not date_details.empty:
                                                        breakdown = date_details[['program', 'metric_value']].copy()
                                                        breakdown.columns = ['Program', 'Value']
                                                        breakdown['Value'] = breakdown['Value'].astype(int)
                                                        st.dataframe(
                                                            breakdown.style.set_properties(**{'text-align': 'center', 'font-size': '13px'}).set_table_styles([
                                                                {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#B00000'), ('color', 'white'), ('font-weight', 'bold')]}
                                                            ]),
                                                            use_container_width=True,
                                                            hide_index=True
                                                        )
                                                    else:
                                                        st.info("No program breakdown available")
                    else:
                        st.info("💡 Select at least one metric to view time series comparison.")

                    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

                    # Percentage Change Analysis
                    st.markdown("""
                    <div style="text-align: center; padding: 15px; background: #e9ecef; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #500000; margin: 0; font-size: 20px;">Percentage Change Analysis</h3>
                        <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">Compare performance changes across all metrics</p>
                    </div>
                    """, unsafe_allow_html=True)

                    change_data = yoy_comparison['% Change'].dropna()
                    colors = ['#28a745' if x > 0 else '#dc3545' if x < 0 else '#6c757d' for x in change_data.values]

                    max_val = change_data.max()
                    min_val = change_data.min()
                    y_range_padding = max(abs(max_val), abs(min_val)) * 0.2

                    fig = go.Figure(go.Bar(
                        x=change_data.index,
                        y=change_data.values,
                        marker_color=colors,
                        text=[f'{x:+.1f}%' for x in change_data.values],
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>Change: %{y:+.1f}%<extra></extra>'
                    ))

                    fig.update_layout(
                        height=550,
                        xaxis_title='Metrics',
                        yaxis_title='% Change',
                        yaxis=dict(range=[min_val - y_range_padding, max_val + y_range_padding]),
                        showlegend=False,
                        margin=dict(t=60, b=100, l=60, r=60)
                    )
                    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=2)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

                    # Show note about excluded metrics
                    if excluded_metrics:
                        excluded_list = ', '.join([m.replace('_', ' ').title() for m in excluded_metrics])
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 15px 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e9ecef;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px; text-align: center;">
                                <strong>Note:</strong> The following metrics were excluded from comparison as they have no data for either cohort: <strong style="color: #495057;">{excluded_list}</strong>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Comprehensive Comparison Table
                    st.markdown("""
                    <div style="text-align: center; padding: 15px; background: #e9ecef; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #500000; margin: 0; font-size: 20px;">Comprehensive Comparison Table with Variance Metrics</h3>
                        <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">Detailed comparison with statistical variance analysis</p>
                    </div>
                    """, unsafe_allow_html=True)

                    enhanced_comparison = yoy_comparison.copy()
                    if 'Mean' in enhanced_comparison.columns:
                        enhanced_comparison = enhanced_comparison.drop(columns=['Mean'])

                    display_df = enhanced_comparison.copy().round(2)

                    styled_df = display_df.style.format({
                        f'Class of {primary_cohort}': '{:.0f}',
                        f'Class of {comparison_cohort}': '{:.0f}',
                        'Absolute Change': '{:+.0f}',
                        '% Change': lambda x: 'N/A' if pd.isna(x) else f'{x:+.1f}%',
                        'Variance': '{:.1f}',
                        'Std Deviation': '{:.1f}',
                        'Coefficient of Variation': '{:.1f}%'
                    }).background_gradient(subset=['Coefficient of Variation'], cmap='YlOrRd')

                    st.dataframe(styled_df, use_container_width=True, height=500)

                    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

                    # Export buttons
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        csv_comparison = enhanced_comparison.to_csv()
                        st.download_button(
                            "📥 Download Comparison Table",
                            csv_comparison,
                            f"comparison_{primary_cohort}_vs_{comparison_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv",
                            use_container_width=True
                        )

                    with col2:
                        csv_primary = primary_data.to_csv(index=False)
                        st.download_button(
                            f"📥 Download {primary_cohort} Data",
                            csv_primary,
                            f"cohort_{primary_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv",
                            use_container_width=True
                        )

                    with col3:
                        csv_secondary = secondary_data.to_csv(index=False)
                        st.download_button(
                            f"📥 Download {comparison_cohort} Data",
                            csv_secondary,
                            f"cohort_{comparison_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv",
                            use_container_width=True
                        )

                else:
                    st.warning("⚠️ No data available for the selected cohorts and program filter combination.")
                    st.info("💡 Try selecting different cohorts or adjusting the program filter.")
    
    # Footer for Director's Deep Dive page
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])
    with footer_col1:
        st.markdown(f"""
        <div class="footer-left footer-content" style="text-align: left;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">📊 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """, unsafe_allow_html=True)
    with footer_col2:
        st.markdown("""
        <div class="footer-center footer-content" style="text-align: center;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;"></p>
        </div>
        """, unsafe_allow_html=True)
    with footer_col3:
        st.markdown("""
        <div class="footer-right footer-content" style="text-align: right;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">💡 Use buttons above to switch views</p>
        </div>
        """, unsafe_allow_html=True)

