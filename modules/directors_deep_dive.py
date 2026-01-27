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
from utils.database import get_connection, load_programs, load_cohort_data
from utils.data_processing import generate_insights


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
        # Get latest data for current cohort
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
            # Comparison Tool integrated as a tab
            from modules.comparison_tool_content import render_comparison_tool
            render_comparison_tool(key_prefix="exec_dive_comp")
    
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

