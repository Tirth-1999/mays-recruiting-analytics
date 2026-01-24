"""
Home Dashboard Page Module
Extracted from main_app.py as part of Phase 3 refactoring
"""

import streamlit as st
import streamlit.components.v1
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Import utility functions
from utils.database import get_connection, load_programs


def render():
    """Render the Home Dashboard page"""
    
    # Initialize reset counter for Home filters
    if 'home_reset_count' not in st.session_state:
        st.session_state.home_reset_count = 0
    
    # Initialize funnel log scale state
    if 'home_funnel_log_scale' not in st.session_state:
        st.session_state.home_funnel_log_scale = False
    
    # Section header for filters
    # Two-column filter layout
    col_cohort, col_program = st.columns(2)
    
    with col_cohort:
        cohort_options = [2028, 2027, 2026]
        selected_cohort = st.selectbox(
            "📅 Cohort Year",
            options=cohort_options,
            index=0,
            help="Select ONE cohort year for analysis. No mixed-cohort data.",
            key=f"cohort_select_home_{st.session_state.home_reset_count}"
        )
    
    with col_program:
        # Get available programs
        programs_df = load_programs()
        program_options = ['All Programs'] + sorted(programs_df['program_code'].tolist())
        selected_program = st.selectbox(
            "🎓 Program Focus",
            options=program_options,
            index=0,
            help="Select a specific program or view all programs",
            key=f"program_select_home_{st.session_state.home_reset_count}"
        )
    
    # Load data for selected cohort
    conn = get_connection()
    query = 'SELECT * FROM admissions_metrics WHERE cohort_year = ? ORDER BY report_date, program'
    df = pd.read_sql(query, conn, params=[selected_cohort])
    df['report_date'] = pd.to_datetime(df['report_date'])
    
    # Filter by program if specific program is selected
    if selected_program != 'All Programs':
        df = df[df['program'] == selected_program]

    if not df.empty:
        # Filter out dates with no real data
        dates_with_data = df.groupby('report_date')['metric_value'].sum()
        dates_with_data = dates_with_data[dates_with_data > 0].index
        df = df[df['report_date'].isin(dates_with_data)]

        latest_date = df['report_date'].max()
        latest_data = df[df['report_date'] == latest_date]

        # Section header for current stats
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">Current Stats - Class of {}</h3>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                All metrics below are specific to the {} cohort • Last updated: {}
            </p>
        </div>
        """.format(selected_cohort, selected_cohort, latest_date.strftime('%B %d, %Y')), unsafe_allow_html=True)

        # Key Metrics Row - with truly synchronized heights using CSS Grid
        st.markdown("""
        <style>
        .metrics-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin: 20px 0;
        }
        .metric-box {
            background: white;
            padding: 1.5rem 1rem;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center !important;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .metric-box * {
            text-align: center !important;
        }
        .metric-number {
            color: #500000;
            margin: 0 auto !important;
            padding: 0 0 0 20px !important;
            font-size: 1.8rem;
            font-weight: bold;
            line-height: 1.2;
            text-align: center !important;
            width: 100%;
            display: block;
        }
        .metric-label {
            margin: 10px auto 5px auto !important;
            padding: 0 !important;
            color: #495057;
            font-weight: 600;
            font-size: 1rem;
            line-height: 1.3;
            text-align: center !important;
            width: 100%;
            display: block;
        }
        .metric-small {
            color: #6c757d;
            font-size: 0.875rem;
            text-align: center !important;
            width: 100%;
            margin: 0 auto !important;
            padding: 0 !important;
            display: block;
        }
        @media (max-width: 768px) {
            .metrics-container {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 480px) {
            .metrics-container {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        total_cohort = latest_data[latest_data['metric_name'] == 'anticipated_cohort_size']['metric_value'].sum()
        total_applications = latest_data[latest_data['metric_name'] == 'total_applications']['metric_value'].sum()
        total_inquiries = latest_data[latest_data['metric_name'] == 'inquiries_received']['metric_value'].sum()
        total_accepted = latest_data[latest_data['metric_name'] == 'admissions_accepted']['metric_value'].sum()
        conversion_rate = (total_applications / total_inquiries * 100) if total_inquiries > 0 else 0
        conversion_color = '#28a745' if conversion_rate > 30 else '#ffc107' if conversion_rate > 20 else '#dc3545'

        # Single container with all four boxes - this ensures they all have the same height
        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-box">
                <h2 class="metric-number">{int(total_cohort) if pd.notna(total_cohort) else 0}</h2>
                <p class="metric-label">Enrolled Students</p>
                <small class="metric-small">as of {latest_date.strftime('%b %d')}</small>
            </div>
            <div class="metric-box">
                <h2 class="metric-number">{int(total_applications) if pd.notna(total_applications) else 0}</h2>
                <p class="metric-label">Total Applications</p>
                <small class="metric-small">submitted</small>
            </div>
            <div class="metric-box">
                <h2 class="metric-number">{int(total_inquiries) if pd.notna(total_inquiries) else 0}</h2>
                <p class="metric-label">Total Inquiries</p>
                <small class="metric-small">received</small>
            </div>
            <div class="metric-box">
                <h2 class="metric-number" style="color: {conversion_color};">{conversion_rate:.1f}%</h2>
                <p class="metric-label">Conversion Rate</p>
                <small class="metric-small">Inquiry → Application</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # Admissions Funnel Section
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">Admissions Funnel - Class of {}</h3>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                Single-cohort analysis showing the complete application journey
            </p>
        </div>
        """.format(selected_cohort), unsafe_allow_html=True)
        
        # Log scale toggle for funnel
        col_spacer1, col_toggle, col_spacer2 = st.columns([2, 1, 2])
        with col_toggle:
            if st.button(
                f"{'Log' if st.session_state.home_funnel_log_scale else 'Linear'} Scale",
                key="toggle_log_funnel_home",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.home_funnel_log_scale = not st.session_state.home_funnel_log_scale
                st.rerun()

        funnel_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'admissions_accepted']
        funnel_labels = ['Inquiries', 'Applications', 'Offers', 'Accepted']

        funnel_data = []
        for metric in funnel_metrics:
            value = latest_data[latest_data['metric_name'] == metric]['metric_value'].sum()
            funnel_data.append(value)

        # Use bar chart instead of funnel when log scale is enabled
        if st.session_state.home_funnel_log_scale:
            fig_funnel = go.Figure(go.Bar(
                x=funnel_labels,
                y=funnel_data,
                marker={"color": ["#500000", "#700000", "#900000", "#B00000"]},
                text=funnel_data,
                texttemplate='%{text:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Count: %{y:,.0f}<extra></extra>'
            ))
            fig_funnel.update_layout(
                height=500,
                showlegend=False,
                yaxis_type='log',
                yaxis_title='Count (Log Scale)',
                xaxis_title='Stage',
                margin=dict(t=80, b=50, l=50, r=50)  # Add top margin to prevent clipping
            )
        else:
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_labels,
                x=funnel_data,
                textinfo="value+percent initial",
                marker={"color": ["#500000", "#700000", "#900000", "#B00000"]}
            ))
            fig_funnel.update_layout(height=400, showlegend=False)
        
        # Center the chart
        col_spacer1, col_chart, col_spacer2 = st.columns([0.5, 3, 0.5])
        with col_chart:
            st.plotly_chart(fig_funnel, use_container_width=True)

        st.markdown("---")

        # Program Comparison Section
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">Program Comparison</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize program filter states
        if 'prog_home_show_inquiries' not in st.session_state:
            st.session_state.prog_home_show_inquiries = True
        if 'prog_home_show_applications' not in st.session_state:
            st.session_state.prog_home_show_applications = True
        if 'prog_home_show_accepted' not in st.session_state:
            st.session_state.prog_home_show_accepted = True
        if 'prog_home_show_cohort' not in st.session_state:
            st.session_state.prog_home_show_cohort = True
        if 'prog_home_log_scale' not in st.session_state:
            st.session_state.prog_home_log_scale = False
        
        # Filter controls with custom styling
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;">
        """, unsafe_allow_html=True)
        
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
        
        with filter_col1:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_inquiries else '○'} Inquiries",
                key="toggle_inq_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_inquiries else "secondary"
            ):
                st.session_state.prog_home_show_inquiries = not st.session_state.prog_home_show_inquiries
                st.rerun()
        
        with filter_col2:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_applications else '○'} Applications",
                key="toggle_apps_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_applications else "secondary"
            ):
                st.session_state.prog_home_show_applications = not st.session_state.prog_home_show_applications
                st.rerun()
        
        with filter_col3:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_accepted else '○'} Accepted",
                key="toggle_acc_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_accepted else "secondary"
            ):
                st.session_state.prog_home_show_accepted = not st.session_state.prog_home_show_accepted
                st.rerun()
        
        with filter_col4:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_cohort else '○'} Cohort Size",
                key="toggle_cohort_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_cohort else "secondary"
            ):
                st.session_state.prog_home_show_cohort = not st.session_state.prog_home_show_cohort
                st.rerun()
        
        with filter_col5:
            if st.button(
                f"{'Log' if st.session_state.prog_home_log_scale else 'Linear'} Scale",
                key="toggle_log_prog_home",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.prog_home_log_scale = not st.session_state.prog_home_log_scale
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Simple info box for interactivity
        st.markdown("""
        <div style="background: #f0f8ff;
                    padding: 12px;
                    border-radius: 6px;
                    margin-bottom: 15px;
                    text-align: center;
                    font-size: 0.9rem;">
            💡 <strong>Interactive Chart:</strong> Use buttons above to show/hide metrics • Click legend items to toggle • Hover bars for exact values
        </div>
        """, unsafe_allow_html=True)

        program_comparison = latest_data[latest_data['metric_name'].isin([
            'inquiries_received', 'total_applications', 'admissions_accepted', 'anticipated_cohort_size'
        ])].pivot_table(
            index='program',
            columns='metric_name',
            values='metric_value',
            aggfunc='sum'
        ).fillna(0)

        if not program_comparison.empty:
            fig_comparison = go.Figure()
            
            metrics_to_plot = {
                'inquiries_received': ('Inquiries', st.session_state.prog_home_show_inquiries, '#500000'),
                'total_applications': ('Applications', st.session_state.prog_home_show_applications, '#700000'),
                'admissions_accepted': ('Accepted', st.session_state.prog_home_show_accepted, '#900000'),
                'anticipated_cohort_size': ('Cohort Size', st.session_state.prog_home_show_cohort, '#B00000')
            }
            
            for metric, (label, show_flag, color) in metrics_to_plot.items():
                if metric in program_comparison.columns and show_flag:
                    fig_comparison.add_trace(go.Bar(
                        name=label,
                        x=program_comparison.index,
                        y=program_comparison[metric],
                        marker_color=color,
                        text=program_comparison[metric],
                        texttemplate='%{text:,.0f}',
                        textposition='outside',
                        hovertemplate='<b>' + label + '</b><br>' +
                                     'Program: %{x}<br>' +
                                     'Count: %{y:,.0f}<br>' +
                                     '<extra></extra>'
                    ))
            
            fig_comparison.update_layout(
                barmode='group',
                height=500,
                xaxis_title='Program',
                yaxis_title='Count',
                yaxis_type='log' if st.session_state.prog_home_log_scale else 'linear',
                margin=dict(t=80, b=50, l=50, r=50),  # Add top margin to prevent clipping
                legend=dict(
                    x=1, y=1,
                    xanchor='right', yanchor='top',
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='rgba(0,0,0,0.2)',
                    borderwidth=1
                )
            )
            
            # Center the chart
            col_spacer1, col_chart, col_spacer2 = st.columns([0.2, 3.6, 0.2])
            with col_chart:
                st.plotly_chart(fig_comparison, use_container_width=True)
        
        st.markdown("---")
        
        # Trend Analysis Section
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">Trend Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize session state for toggle buttons
        if 'home_trend_show_apps' not in st.session_state:
            st.session_state.home_trend_show_apps = True
        if 'home_trend_show_inq' not in st.session_state:
            st.session_state.home_trend_show_inq = True
        if 'home_trend_show_inq_conv' not in st.session_state:
            st.session_state.home_trend_show_inq_conv = True
        if 'home_trend_show_app_conv' not in st.session_state:
            st.session_state.home_trend_show_app_conv = True
        
        time_series = df[df['metric_name'].isin([
            'inquiries_received', 'total_applications', 'admissions_offered'
        ])].pivot_table(
            index='report_date',
            columns='metric_name',
            values='metric_value',
            aggfunc='sum'
        ).fillna(0)
        
        if not time_series.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h4 style='text-align: center; color: #500000;'>Application & Inquiry Trends</h4>", unsafe_allow_html=True)
                
                # Toggle buttons for line selection
                st.markdown("**Select Lines to Display:**")
                filter_col1, filter_col2 = st.columns(2)
                
                with filter_col1:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_apps else '○'} Applications",
                        key="toggle_apps_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_apps else "secondary"
                    ):
                        st.session_state.home_trend_show_apps = not st.session_state.home_trend_show_apps
                        st.rerun()
                
                with filter_col2:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_inq else '○'} Inquiries",
                        key="toggle_inq_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_inq else "secondary"
                    ):
                        st.session_state.home_trend_show_inq = not st.session_state.home_trend_show_inq
                        st.rerun()
                
                fig_trend1 = go.Figure()
                
                if 'total_applications' in time_series.columns and st.session_state.home_trend_show_apps:
                    fig_trend1.add_trace(go.Scatter(
                        x=time_series.index,
                        y=time_series['total_applications'],
                        mode='lines+markers',
                        name='Applications',
                        line=dict(color='#500000', width=3),
                        marker=dict(size=8),
                        hovertemplate='<b>Applications</b><br>' +
                                     'Date: %{x}<br>' +
                                     'Count: %{y:,.0f}<br>' +
                                     '<extra></extra>'
                    ))
                
                if 'inquiries_received' in time_series.columns and st.session_state.home_trend_show_inq:
                    fig_trend1.add_trace(go.Scatter(
                        x=time_series.index,
                        y=time_series['inquiries_received'],
                        mode='lines+markers',
                        name='Inquiries',
                        line=dict(color='#B00000', width=3),
                        marker=dict(size=8),
                        hovertemplate='<b>Inquiries</b><br>' +
                                     'Date: %{x}<br>' +
                                     'Count: %{y:,.0f}<br>' +
                                     '<extra></extra>'
                    ))
                
                fig_trend1.update_layout(
                    height=400,
                    xaxis_title='Date',
                    yaxis_title='Count',
                    legend=dict(
                        x=1, y=1,
                        xanchor='right', yanchor='top',
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='rgba(0,0,0,0.2)',
                        borderwidth=1
                    )
                )
                st.plotly_chart(fig_trend1, use_container_width=True)
            
            with col2:
                st.markdown("<h4 style='text-align: center; color: #500000;'>Conversion Rates Over Time</h4>", unsafe_allow_html=True)
                
                # Toggle buttons for conversion rates
                st.markdown("**Select Conversion Metrics:**")
                conv_filter_col1, conv_filter_col2 = st.columns(2)
                
                with conv_filter_col1:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_inq_conv else '○'} Inquiry → App",
                        key="toggle_inq_conv_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_inq_conv else "secondary"
                    ):
                        st.session_state.home_trend_show_inq_conv = not st.session_state.home_trend_show_inq_conv
                        st.rerun()
                
                with conv_filter_col2:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_app_conv else '○'} App → Offer",
                        key="toggle_app_conv_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_app_conv else "secondary"
                    ):
                        st.session_state.home_trend_show_app_conv = not st.session_state.home_trend_show_app_conv
                        st.rerun()
                
                conversion_data = []
                for date in time_series.index:
                    inquiries_ts = time_series.loc[date, 'inquiries_received'] if 'inquiries_received' in time_series.columns else 0
                    applications_ts = time_series.loc[date, 'total_applications'] if 'total_applications' in time_series.columns else 0
                    offers_ts = time_series.loc[date, 'admissions_offered'] if 'admissions_offered' in time_series.columns else 0
                    
                    inquiry_conv = (applications_ts / inquiries_ts * 100) if inquiries_ts > 0 else 0
                    app_conv = (offers_ts / applications_ts * 100) if applications_ts > 0 else 0
                    
                    conversion_data.append({
                        'date': date,
                        'inquiry_conversion': inquiry_conv,
                        'application_conversion': app_conv
                    })
                
                conv_df = pd.DataFrame(conversion_data)
                
                if not conv_df.empty:
                    fig_trend2 = go.Figure()
                    
                    if st.session_state.home_trend_show_inq_conv:
                        fig_trend2.add_trace(go.Scatter(
                            x=conv_df['date'],
                            y=conv_df['inquiry_conversion'],
                            mode='lines+markers',
                            name='Inquiry → App (%)',
                            line=dict(color='#28a745', width=3),
                            marker=dict(size=8),
                            hovertemplate='<b>Inquiry to Application</b><br>' +
                                         'Date: %{x}<br>' +
                                         'Conversion Rate: %{y:.1f}%<br>' +
                                         '<extra></extra>'
                        ))
                    
                    if st.session_state.home_trend_show_app_conv:
                        fig_trend2.add_trace(go.Scatter(
                            x=conv_df['date'],
                            y=conv_df['application_conversion'],
                            mode='lines+markers',
                            name='App → Offer (%)',
                            line=dict(color='#ffc107', width=3),
                            marker=dict(size=8),
                            hovertemplate='<b>Application to Offer</b><br>' +
                                         'Date: %{x}<br>' +
                                         'Conversion Rate: %{y:.1f}%<br>' +
                                         '<extra></extra>'
                        ))
                    
                    fig_trend2.update_layout(
                        height=400,
                        xaxis_title='Date',
                        yaxis_title='Conversion Rate (%)',
                        legend=dict(
                            x=1, y=1,
                            xanchor='right', yanchor='top',
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.2)',
                            borderwidth=1
                        )
                    )
                    st.plotly_chart(fig_trend2, use_container_width=True)

    else:
        st.warning("⚠️ No data available for the selected cohort{' and program' if selected_program != 'All Programs' else ''}.")
    
    # Footer for Home page
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])
    with footer_col1:
        st.markdown(f"""
        <div class="footer-left footer-content" style="text-align: left;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
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
