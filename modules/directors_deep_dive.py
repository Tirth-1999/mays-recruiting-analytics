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

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
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
        """, unsafe_allow_html=True)
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Load data based on selection
    current_data = load_cohort_data(selected_cohort)

    # Apply program filter if selected
    if selected_program_filter != "All Programs":
        current_data = current_data[current_data['program'] == selected_program_filter]

    if current_data.empty:
        st.error(f"❌ No data available for Class of {selected_cohort}" + 
                 (f" - {selected_program_filter}" if selected_program_filter != "All Programs" else ""))
        st.info("💡 Try selecting a different cohort/program or check the database")
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

        # Calculate comprehensive metrics
        inquiries = latest_data[latest_data['metric_name'] == 'inquiries_received']['metric_value'].fillna(0).sum()
        applications = latest_data[latest_data['metric_name'] == 'total_applications']['metric_value'].fillna(0).sum()
        offers = latest_data[latest_data['metric_name'] == 'admissions_offered']['metric_value'].fillna(0).sum()
        accepted = latest_data[latest_data['metric_name'] == 'admissions_accepted']['metric_value'].fillna(0).sum()
        enrolled = latest_data[latest_data['metric_name'] == 'anticipated_cohort_size']['metric_value'].fillna(0).sum()
        in_progress = latest_data[latest_data['metric_name'] == 'applications_in_progress']['metric_value'].fillna(0).sum()
        complete = latest_data[latest_data['metric_name'] == 'applications_complete']['metric_value'].fillna(0).sum()
        
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
        
        # Comprehensive KPI Grid using CSS Grid
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
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        @media (max-width: 1200px) {
            .full-metrics-container {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        @media (max-width: 768px) {
            .full-metrics-container {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 480px) {
            .full-metrics-container {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="full-metrics-container">
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem; padding-left: 20px;">{int(inquiries)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Inquiries</p>
                <small style="color: #6c757d; font-size: 0.8rem;">Total received</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem; padding-left: 20px;">{int(applications)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Applications</p>
                <small style="color: {'#28a745' if conversion_1 > 30 else '#ffc107' if conversion_1 > 20 else '#dc3545'}; font-size: 0.8rem;">{conversion_1:.1f}% conv.</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem; padding-left: 20px;">{int(in_progress)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">In Progress</p>
                <small style="color: #6c757d; font-size: 0.8rem;">Applications</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem; padding-left: 20px;">{int(complete)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Complete</p>
                <small style="color: #6c757d; font-size: 0.8rem;">Applications</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem; padding-left: 20px;">{int(offers)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Offers</p>
                <small style="color: #6c757d; font-size: 0.8rem;">{conversion_2:.1f}% rate</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem; padding-left: 20px;">{int(enrolled)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Enrolled</p>
                <small style="color: {'#28a745' if yield_rate > 70 else '#ffc107' if yield_rate > 50 else '#dc3545'}; font-size: 0.8rem;">{yield_rate:.1f}% yield</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
        ).fillna(0).reset_index()
        
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
            
            # Divider between charts
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Performance metrics radar chart - FULL WIDTH
            st.markdown("<h4 style='text-align: center; color: #500000;'>Performance Radar</h4>", unsafe_allow_html=True)
            
            metrics = ['Inquiry Conversion', 'Application Completion', 'Selectivity', 'Yield Rate', 'Overall Efficiency']
            values = [
                conversion_1,
                (complete / applications * 100) if applications > 0 else 0,
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
                height=500,
                margin=dict(t=50, b=50, l=80, r=80)
            )
            st.plotly_chart(fig, use_container_width=True)
            
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
            st.markdown("**📊 Select Metrics to Display:**")
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
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
            
            # Multi-line time series
            time_series = current_data.pivot_table(
                index='report_date',
                columns='metric_name',
                values='metric_value',
                aggfunc='sum'
            ).fillna(0)
            
            if not time_series.empty:
                fig = go.Figure()
                
                key_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'anticipated_cohort_size']
                colors = ['#500000', '#700000', '#900000', '#B00000']
                metric_labels = ['Inquiries Received', 'Total Applications', 'Admissions Offered', 'Anticipated Cohort Size']
                show_flags = [st.session_state.exec_full_show_inq, st.session_state.exec_full_show_apps, st.session_state.exec_full_show_offers, st.session_state.exec_full_show_cohort]
                
                for i, (metric, label, show_flag) in enumerate(zip(key_metrics, metric_labels, show_flags)):
                    if metric in time_series.columns and show_flag:
                        fig.add_trace(go.Scatter(
                            x=time_series.index,
                            y=time_series[metric],
                            mode='lines+markers',
                            name=label,
                            line=dict(color=colors[i], width=3),
                            marker=dict(size=8),
                            hovertemplate='<b>' + label + '</b><br>' +
                                         'Date: %{x}<br>' +
                                         'Count: %{y:,.0f}<br>' +
                                         '<extra></extra>'
                        ))
                
                fig.update_layout(
                    title='Key Metrics Trends Over Time - Interactive View',
                    height=500,
                    xaxis_title='Date',
                    yaxis_title='Count',
                    legend=dict(
                        x=1, y=1,
                        xanchor='right', yanchor='top',
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='rgba(0,0,0,0.3)',
                        borderwidth=1
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Growth rate analysis
                st.markdown("<h4 style='text-align: center; color: #500000;'>📊 Growth Rate Analysis</h4>", unsafe_allow_html=True)
                
                growth_data = []
                for metric in key_metrics:
                    if metric in time_series.columns and len(time_series) > 1:
                        values = time_series[metric].values
                        if len(values) >= 2 and values[-2] > 0:
                            growth_rate = ((values[-1] - values[-2]) / values[-2] * 100)
                            growth_data.append({
                                'Metric': metric.replace('_', ' ').title(),
                                'Growth Rate (%)': growth_rate,
                                'Latest Value': values[-1],
                                'Previous Value': values[-2]
                            })
                
                if growth_data:
                    growth_df = pd.DataFrame(growth_data)
                    st.dataframe(
                        growth_df.style.format({
                            'Growth Rate (%)': '{:+.1f}%',
                            'Latest Value': '{:.0f}',
                            'Previous Value': '{:.0f}'
                        }).background_gradient(subset=['Growth Rate (%)'], cmap='RdYlGn'),
                        use_container_width=True
                    )
        
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
            ).fillna(0)
            
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
                    if st.button(
                        f"📊 {st.session_state.exec_app_chart_type}",
                        key="toggle_chart_type_app",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_app_chart_type = 'Bar' if st.session_state.exec_app_chart_type == 'Line' else 'Line'
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
                        # Line chart with data labels
                        for i, metric in enumerate(selected_app_metrics):
                            if metric in program_time_series.columns:
                                metric_display = metric.replace('_', ' ').title()
                                fig_app.add_trace(go.Scatter(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    mode='lines+markers+text',
                                    name=metric_display,
                                    line=dict(color=app_colors[i % len(app_colors)], width=3),
                                    marker=dict(size=8),
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
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
                                metric_display = metric.replace('_', ' ').title()
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
                        title='Applications Metrics Over Time',
                        height=600,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        yaxis_type='log' if st.session_state.exec_app_log else 'linear',
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=-0.35,
                            xanchor='center',
                            x=0.5,
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.3)',
                            borderwidth=1,
                            font=dict(size=11),
                            itemwidth=30
                        ),
                        margin=dict(b=180, t=50, l=40, r=40)
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
                    if st.button(
                        f"📊 {st.session_state.exec_adm_chart_type}",
                        key="toggle_chart_type_adm",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_adm_chart_type = 'Bar' if st.session_state.exec_adm_chart_type == 'Line' else 'Line'
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
                        # Line chart with data labels
                        for i, metric in enumerate(selected_adm_metrics):
                            if metric in program_time_series.columns:
                                metric_display = metric.replace('_', ' ').title()
                                fig_adm.add_trace(go.Scatter(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    mode='lines+markers+text',
                                    name=metric_display,
                                    line=dict(color=adm_colors[i % len(adm_colors)], width=3),
                                    marker=dict(size=8),
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
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
                                metric_display = metric.replace('_', ' ').title()
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
                        title='Admissions Metrics Over Time',
                        height=600,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        yaxis_type='log' if st.session_state.exec_adm_log else 'linear',
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=-0.35,
                            xanchor='center',
                            x=0.5,
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.3)',
                            borderwidth=1,
                            font=dict(size=11),
                            itemwidth=30
                        ),
                        margin=dict(b=180, t=50, l=40, r=40)
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

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

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

                    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

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
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px 15px; border-radius: 6px; margin: 15px 0;">
                            <p style="margin: 0; color: #856404; font-size: 14px;">
                                ℹ️ <strong>Note:</strong> The following metrics were excluded from comparison as they have no data for either cohort: <strong>{excluded_list}</strong>
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

