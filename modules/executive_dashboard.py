"""
Executive Dashboard Page Module
Provides high-level overview of admissions and marketing metrics for executive decision-making
"""

import streamlit as st
import streamlit.components.v1
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Import utility functions
from utils.database import get_connection, load_programs

# COHESIVE COLOR PALETTE - Every single color is completely unique
# No shades, no similar colors, all easily distinguishable
EXECUTIVE_COLORS = {
    # Admissions Metrics - 6 completely different colors
    'inquiries': '#2196F3',           # Blue
    'applications': '#FF9800',        # Orange
    'admits': '#4CAF50',              # Green
    'accepted': '#F44336',            # Red
    'enrolled': '#00BCD4',            # Cyan
    'cohort_size': '#500000',         # Texas A&M Maroon
    
    # Marketing Channels - 12 completely distinct colors
    'Google Ads': '#EA4335',          # Google Red
    'Facebook': '#1877F2',            # Facebook Blue
    'LinkedIn': '#0A66C2',            # LinkedIn Blue (darker)
    'Meta': '#9C27B0',                # Purple
    'YouTube': '#FF5722',             # Deep Orange
    'Email': '#8BC34A',               # Light Green
    'Display': '#FFC107',             # Amber/Gold
    'Search': '#673AB7',              # Deep Purple
    'Social': '#E91E63',              # Pink
    'Device ID': '#FF6F00',           # Dark Orange
    'Programmatic': '#00897B',        # Teal
    'Other': '#607D8B',               # Blue Gray
}

def get_color(key, default='#95A5A6'):
    """Get color from palette with fallback"""
    return EXECUTIVE_COLORS.get(key, default)


def render():
    """Render the Executive Dashboard page"""
    
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
        program_options = ['All Programs'] + sorted(programs_df['program_name'].tolist())
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
        
        # Check if we have any data after filtering
        if len(dates_with_data) > 0:
            df = df[df['report_date'].isin(dates_with_data)]
            latest_date = df['report_date'].max()
            latest_data = df[df['report_date'] == latest_date]
        else:
            # No data available - show message
            df = pd.DataFrame()  # Empty dataframe
    
    # Check if we have data to display
    if not df.empty:
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
        
        # Use maroon palette for funnel (gradient from dark to light)
        funnel_colors = ['#500000', '#700000', '#900000', '#B00000']  # Dark maroon to lighter maroon

        funnel_data = []
        for metric in funnel_metrics:
            value = latest_data[latest_data['metric_name'] == metric]['metric_value'].sum()
            funnel_data.append(value)

        # Use bar chart instead of funnel when log scale is enabled
        if st.session_state.home_funnel_log_scale:
            fig_funnel = go.Figure(go.Bar(
                x=funnel_labels,
                y=funnel_data,
                marker={"color": funnel_colors},
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
                marker={"color": funnel_colors}
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
        
        # Independent filters for Program Comparison section
        st.markdown("**Filters for Program Comparison**")
        
        # Load all cohort data (not just selected_cohort)
        all_cohorts_query = 'SELECT * FROM admissions_metrics ORDER BY report_date, program'
        all_cohorts_df = pd.read_sql(all_cohorts_query, conn)
        all_cohorts_df['report_date'] = pd.to_datetime(all_cohorts_df['report_date'])
        
        # Initialize session state for program comparison filters
        if 'prog_comparison_cohort_selection' not in st.session_state:
            st.session_state.prog_comparison_cohort_selection = sorted(all_cohorts_df['cohort_year'].unique().tolist())
        if 'prog_comparison_program_selection' not in st.session_state:
            st.session_state.prog_comparison_program_selection = sorted(all_cohorts_df['program'].unique().tolist())
        
        col_cohort_filter, col_prog_filter = st.columns(2)
        
        # Cohort Filter
        with col_cohort_filter:
            cohorts_list = sorted(all_cohorts_df['cohort_year'].unique().tolist())
            
            if len(st.session_state.prog_comparison_cohort_selection) == len(cohorts_list):
                cohort_summary = "All cohorts"
            elif len(st.session_state.prog_comparison_cohort_selection) == 0:
                cohort_summary = "No cohorts selected"
            elif len(st.session_state.prog_comparison_cohort_selection) == 1:
                cohort_summary = f"Class of {st.session_state.prog_comparison_cohort_selection[0]}"
            else:
                cohort_summary = f"{len(st.session_state.prog_comparison_cohort_selection)} cohorts"
            
            st.markdown("**📅 Cohort Year**")
            with st.popover(cohort_summary, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key="prog_comp_cohort_all", use_container_width=True, type="primary"):
                        st.session_state.prog_comparison_cohort_selection = cohorts_list.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key="prog_comp_cohort_clear", use_container_width=True, type="secondary"):
                        st.session_state.prog_comparison_cohort_selection = []
                        st.rerun()
                
                st.divider()
                
                for idx, cohort in enumerate(cohorts_list):
                    is_checked = cohort in st.session_state.prog_comparison_cohort_selection
                    new_value = st.checkbox(f"Class of {cohort}", value=is_checked, key=f"prog_comp_cohort_cb_{idx}")
                    
                    if new_value != is_checked:
                        if new_value:
                            if cohort not in st.session_state.prog_comparison_cohort_selection:
                                st.session_state.prog_comparison_cohort_selection.append(cohort)
                        else:
                            if cohort in st.session_state.prog_comparison_cohort_selection:
                                st.session_state.prog_comparison_cohort_selection.remove(cohort)
                        st.rerun()
        
        # Program Filter
        with col_prog_filter:
            # Filter by cohort first
            cohort_filtered_df = all_cohorts_df[all_cohorts_df['cohort_year'].isin(st.session_state.prog_comparison_cohort_selection)] if len(st.session_state.prog_comparison_cohort_selection) > 0 else all_cohorts_df.head(0)
            programs_list = sorted(cohort_filtered_df['program'].unique().tolist()) if not cohort_filtered_df.empty else []
            
            # Update program selection to only include valid programs
            valid_programs = [p for p in st.session_state.prog_comparison_program_selection if p in programs_list]
            if set(valid_programs) != set(st.session_state.prog_comparison_program_selection):
                st.session_state.prog_comparison_program_selection = valid_programs if valid_programs else programs_list.copy()
            
            if len(st.session_state.prog_comparison_program_selection) == len(programs_list):
                prog_summary = "All programs"
            elif len(st.session_state.prog_comparison_program_selection) == 0:
                prog_summary = "No programs selected"
            elif len(st.session_state.prog_comparison_program_selection) == 1:
                prog_summary = st.session_state.prog_comparison_program_selection[0].replace('Flex Online ', '').replace('MS ', '')
            else:
                prog_summary = f"{len(st.session_state.prog_comparison_program_selection)} programs"
            
            st.markdown("**🎓 Program**")
            with st.popover(prog_summary, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key="prog_comp_prog_all", use_container_width=True, type="primary"):
                        st.session_state.prog_comparison_program_selection = programs_list.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key="prog_comp_prog_clear", use_container_width=True, type="secondary"):
                        st.session_state.prog_comparison_program_selection = []
                        st.rerun()
                
                st.divider()
                
                for idx, prog in enumerate(programs_list):
                    is_checked = prog in st.session_state.prog_comparison_program_selection
                    prog_display = prog.replace('Flex Online ', '').replace('MS ', '')
                    new_value = st.checkbox(prog_display, value=is_checked, key=f"prog_comp_prog_cb_{idx}")
                    
                    if new_value != is_checked:
                        if new_value:
                            if prog not in st.session_state.prog_comparison_program_selection:
                                st.session_state.prog_comparison_program_selection.append(prog)
                        else:
                            if prog in st.session_state.prog_comparison_program_selection:
                                st.session_state.prog_comparison_program_selection.remove(prog)
                        st.rerun()
        
        # Apply filters to get comparison data
        filtered_comparison_df = all_cohorts_df.copy()
        if len(st.session_state.prog_comparison_cohort_selection) > 0:
            filtered_comparison_df = filtered_comparison_df[filtered_comparison_df['cohort_year'].isin(st.session_state.prog_comparison_cohort_selection)]
        else:
            filtered_comparison_df = filtered_comparison_df.head(0)
        
        if len(st.session_state.prog_comparison_program_selection) > 0:
            filtered_comparison_df = filtered_comparison_df[filtered_comparison_df['program'].isin(st.session_state.prog_comparison_program_selection)]
        else:
            filtered_comparison_df = filtered_comparison_df.head(0)
        
        # Get latest data for each program-cohort combination, then aggregate
        if not filtered_comparison_df.empty:
            # Get latest date for each program-cohort combination
            latest_dates = filtered_comparison_df.groupby(['program', 'cohort_year'])['report_date'].max().reset_index()
            filtered_latest_data = filtered_comparison_df.merge(latest_dates, on=['program', 'cohort_year', 'report_date'])
        else:
            filtered_latest_data = pd.DataFrame()
        
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
        
        # Check if we have data after filtering
        if filtered_latest_data.empty:
            st.warning("⚠️ No data available for the selected filters. Please adjust your selections.")
        else:
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

            program_comparison = filtered_latest_data[filtered_latest_data['metric_name'].isin([
                'inquiries_received', 'total_applications', 'admissions_accepted', 'anticipated_cohort_size'
            ])].pivot_table(
                index='program',
                columns='metric_name',
                values='metric_value',
                aggfunc='sum'
            ).fillna(0)

            if not program_comparison.empty:
                fig_comparison = go.Figure()
                
                # Use cohesive color palette
                metrics_to_plot = {
                    'inquiries_received': ('Inquiries', st.session_state.prog_home_show_inquiries, get_color('inquiries')),
                    'total_applications': ('Applications', st.session_state.prog_home_show_applications, get_color('applications')),
                    'admissions_accepted': ('Accepted', st.session_state.prog_home_show_accepted, get_color('accepted')),
                    'anticipated_cohort_size': ('Cohort Size', st.session_state.prog_home_show_cohort, get_color('cohort_size'))
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
                
                # Calculate y-axis range to prevent clipping
                if not st.session_state.prog_home_log_scale:
                    # Get max value across all visible metrics
                    max_values = []
                    for metric, (label, show_flag, color) in metrics_to_plot.items():
                        if metric in program_comparison.columns and show_flag:
                            max_values.append(program_comparison[metric].max())
                    
                    if max_values:
                        max_y = max(max_values)
                        # Add 20% padding to prevent clipping
                        y_range = [0, max_y * 1.20]
                    else:
                        y_range = None
                else:
                    y_range = None
                
                fig_comparison.update_layout(
                    barmode='group',
                    height=500,
                    xaxis_title='Program',
                    yaxis_title='Count',
                    yaxis_type='log' if st.session_state.prog_home_log_scale else 'linear',
                    yaxis_range=y_range,
                    margin=dict(t=120, b=80, l=60, r=60),  # Increased margins for better spacing
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
                        line=dict(color=get_color('applications'), width=3),
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
                        line=dict(color=get_color('inquiries'), width=3),
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
                            line=dict(color=get_color('inquiries'), width=3),
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
                            line=dict(color=get_color('applications'), width=3),
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
        # No data available - show helpful message
        # Check if this is a valid program that exists but has no data
        programs_query = 'SELECT program_name FROM programs WHERE is_active = 1'
        all_programs = pd.read_sql(programs_query, conn)
        
        if selected_program != 'All Programs' and selected_program in all_programs['program_name'].values:
            # Program exists but has no data for this cohort
            st.markdown("""
            <div style="text-align: center;
                        padding: 40px;
                        background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
                        border-radius: 12px;
                        border: 2px solid #ffc107;
                        margin: 40px 0;">
                <div style="font-size: 64px; margin-bottom: 20px;">🚀</div>
                <h3 style="color: #500000; margin: 0 0 15px 0;">Program Tracked - No Enrollment Data Yet</h3>
                <p style="color: #6c757d; font-size: 16px; line-height: 1.6; max-width: 600px; margin: 0 auto;">
                    <strong>{}</strong> is an active program in our system for <strong>Class of {}</strong>,
                    but enrollment activity hasn't started yet.
                    <br><br>
                    This typically means:
                </p>
                <ul style="color: #6c757d; font-size: 14px; text-align: left; max-width: 500px; margin: 20px auto; line-height: 1.8;">
                    <li>The program is newly launched and recruiting will begin soon</li>
                    <li>Marketing campaigns are being planned or in early stages</li>
                    <li>Data collection will start once inquiries are received</li>
                </ul>
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px auto; max-width: 500px; border-left: 4px solid #ffc107;">
                    <p style="color: #856404; font-size: 14px; margin: 0; text-align: left;">
                        <strong>💡 Note:</strong> The program is configured and ready to track data. 
                        Check back after marketing campaigns launch or try viewing other cohort years.
                    </p>
                </div>
            </div>
            """.format(selected_program, selected_cohort), unsafe_allow_html=True)
        else:
            # Generic no data message
            st.markdown("""
            <div style="text-align: center;
                        padding: 40px;
                        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                        border-radius: 12px;
                        border: 2px dashed #dee2e6;
                        margin: 40px 0;">
                <div style="font-size: 64px; margin-bottom: 20px;">📊</div>
                <h3 style="color: #500000; margin: 0 0 15px 0;">No Data Available</h3>
                <p style="color: #6c757d; font-size: 16px; line-height: 1.6; max-width: 600px; margin: 0 auto;">
                    There is currently no enrollment data for <strong>Class of {}</strong>{}.
                    <br><br>
                    This could mean:
                </p>
                <ul style="color: #6c757d; font-size: 14px; text-align: left; max-width: 500px; margin: 20px auto; line-height: 1.8;">
                    <li>Programs haven't started recruiting for this cohort yet</li>
                    <li>Data collection is in progress</li>
                    <li>The cohort year may not be active</li>
                </ul>
                <p style="color: #6c757d; font-size: 14px; margin-top: 20px;">
                    Try selecting a different cohort year or program from the sidebar.
                </p>
            </div>
            """.format(
                selected_cohort,
                f" for <strong>{selected_program}</strong>" if selected_program != 'All Programs' else ""
            ), unsafe_allow_html=True)
    
    # Marketing Insights Section (High-Level Overview)
    st.markdown("---")
    
    # Build the subtitle dynamically
    if selected_program != 'All Programs':
        subtitle = f"High-level marketing spend overview for {selected_program}"
    else:
        subtitle = "High-level marketing spend overview"
    
    st.markdown(f"""
    <div style="text-align: center;
                padding: 15px;
                background: #e9ecef;
                border-radius: 8px;
                margin: 20px 0;">
        <h3 style="color: #500000; margin: 0; font-size: 20px;">Marketing Insights</h3>
        <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if marketing data exists
    marketing_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='marketing_spend';"
    cursor = conn.cursor()
    cursor.execute(marketing_query)
    has_marketing = cursor.fetchone() is not None
    
    if has_marketing:
        # Load marketing data - filter by selected program if specific program is chosen
        if selected_program != 'All Programs':
            marketing_df = pd.read_sql("""
                SELECT program, channel, spend_amount, fiscal_year, month_date
                FROM marketing_spend
                WHERE program = ?
                ORDER BY month_date DESC
            """, conn, params=[selected_program])
        else:
            # Include all programs including General Awareness
            marketing_df = pd.read_sql("""
                SELECT program, channel, spend_amount, fiscal_year, month_date
                FROM marketing_spend
                ORDER BY month_date DESC
            """, conn)
        
        if not marketing_df.empty:
            # Independent filters for Marketing Insights section
            st.markdown("**Filters for Marketing Insights**")
            
            # Initialize session state for marketing filters
            if 'marketing_insights_fy_selection' not in st.session_state:
                st.session_state.marketing_insights_fy_selection = sorted(marketing_df['fiscal_year'].unique().tolist())
            if 'marketing_insights_prog_selection' not in st.session_state:
                st.session_state.marketing_insights_prog_selection = sorted(marketing_df['program'].unique().tolist())
            
            col_fy, col_prog = st.columns(2)
            
            # Fiscal Year Filter
            with col_fy:
                fiscal_years_list = sorted(marketing_df['fiscal_year'].unique().tolist())
                
                if len(st.session_state.marketing_insights_fy_selection) == len(fiscal_years_list):
                    fy_summary = "All fiscal years"
                elif len(st.session_state.marketing_insights_fy_selection) == 0:
                    fy_summary = "No fiscal years selected"
                elif len(st.session_state.marketing_insights_fy_selection) == 1:
                    fy_summary = str(st.session_state.marketing_insights_fy_selection[0])
                else:
                    fy_summary = f"{len(st.session_state.marketing_insights_fy_selection)} fiscal years"
                
                st.markdown("**📅 Fiscal Year**")
                with st.popover(fy_summary, use_container_width=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✓ All", key="mkt_fy_all", use_container_width=True, type="primary"):
                            st.session_state.marketing_insights_fy_selection = fiscal_years_list.copy()
                            st.rerun()
                    with col_b:
                        if st.button("✗ Clear", key="mkt_fy_clear", use_container_width=True, type="secondary"):
                            st.session_state.marketing_insights_fy_selection = []
                            st.rerun()
                    
                    st.divider()
                    
                    for idx, fy in enumerate(fiscal_years_list):
                        is_checked = fy in st.session_state.marketing_insights_fy_selection
                        new_value = st.checkbox(str(fy), value=is_checked, key=f"mkt_fy_cb_{idx}")
                        
                        if new_value != is_checked:
                            if new_value:
                                if fy not in st.session_state.marketing_insights_fy_selection:
                                    st.session_state.marketing_insights_fy_selection.append(fy)
                            else:
                                if fy in st.session_state.marketing_insights_fy_selection:
                                    st.session_state.marketing_insights_fy_selection.remove(fy)
                            st.rerun()
            
            # Program Filter
            with col_prog:
                # Filter by fiscal year first
                fy_filtered_df = marketing_df[marketing_df['fiscal_year'].isin(st.session_state.marketing_insights_fy_selection)] if len(st.session_state.marketing_insights_fy_selection) > 0 else marketing_df.head(0)
                programs_list = sorted(fy_filtered_df['program'].unique().tolist()) if not fy_filtered_df.empty else []
                
                # Update program selection to only include valid programs
                valid_programs = [p for p in st.session_state.marketing_insights_prog_selection if p in programs_list]
                if set(valid_programs) != set(st.session_state.marketing_insights_prog_selection):
                    st.session_state.marketing_insights_prog_selection = valid_programs if valid_programs else programs_list.copy()
                
                if len(st.session_state.marketing_insights_prog_selection) == len(programs_list):
                    prog_summary = "All programs"
                elif len(st.session_state.marketing_insights_prog_selection) == 0:
                    prog_summary = "No programs selected"
                elif len(st.session_state.marketing_insights_prog_selection) == 1:
                    prog_summary = st.session_state.marketing_insights_prog_selection[0].replace('Flex Online ', '').replace('MS ', '')
                else:
                    prog_summary = f"{len(st.session_state.marketing_insights_prog_selection)} programs"
                
                st.markdown("**🎓 Program**")
                with st.popover(prog_summary, use_container_width=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✓ All", key="mkt_prog_all", use_container_width=True, type="primary"):
                            st.session_state.marketing_insights_prog_selection = programs_list.copy()
                            st.rerun()
                    with col_b:
                        if st.button("✗ Clear", key="mkt_prog_clear", use_container_width=True, type="secondary"):
                            st.session_state.marketing_insights_prog_selection = []
                            st.rerun()
                    
                    st.divider()
                    
                    for idx, prog in enumerate(programs_list):
                        is_checked = prog in st.session_state.marketing_insights_prog_selection
                        prog_display = prog.replace('Flex Online ', '').replace('MS ', '')
                        new_value = st.checkbox(prog_display, value=is_checked, key=f"mkt_prog_cb_{idx}")
                        
                        if new_value != is_checked:
                            if new_value:
                                if prog not in st.session_state.marketing_insights_prog_selection:
                                    st.session_state.marketing_insights_prog_selection.append(prog)
                            else:
                                if prog in st.session_state.marketing_insights_prog_selection:
                                    st.session_state.marketing_insights_prog_selection.remove(prog)
                            st.rerun()
            
            # Apply filters to marketing data
            filtered_marketing_df = marketing_df.copy()
            if len(st.session_state.marketing_insights_fy_selection) > 0:
                filtered_marketing_df = filtered_marketing_df[filtered_marketing_df['fiscal_year'].isin(st.session_state.marketing_insights_fy_selection)]
            else:
                filtered_marketing_df = filtered_marketing_df.head(0)
            
            if len(st.session_state.marketing_insights_prog_selection) > 0:
                filtered_marketing_df = filtered_marketing_df[filtered_marketing_df['program'].isin(st.session_state.marketing_insights_prog_selection)]
            else:
                filtered_marketing_df = filtered_marketing_df.head(0)
            
            # Check if we have data after filtering
            if filtered_marketing_df.empty:
                st.warning("⚠️ No marketing data available for the selected filters. Please adjust your selections.")
            else:
                # Key Marketing Metrics (using filtered data)
                total_spend = filtered_marketing_df['spend_amount'].sum()
                
                # Count programs (exclude General Awareness from program count)
                program_list = filtered_marketing_df['program'].unique()
                num_programs = len([p for p in program_list if p != 'General Awareness'])
                has_general_awareness = 'General Awareness' in program_list
                
                num_channels = filtered_marketing_df['channel'].nunique()
                avg_spend_per_program = total_spend / num_programs if num_programs > 0 else 0
            
            # Display metrics in a grid
            st.markdown("""
            <style>
            .marketing-metrics-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 1rem;
                margin: 20px 0;
            }
            .marketing-metric-box {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            }
            .marketing-metric-number {
                color: #500000;
                font-size: 1.8rem;
                font-weight: bold;
                margin: 0;
            }
            .marketing-metric-label {
                color: #6c757d;
                font-size: 0.9rem;
                margin: 0.5rem 0 0 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="marketing-metric-box">
                    <div class="marketing-metric-number">${total_spend:,.0f}</div>
                    <div class="marketing-metric-label">Total Marketing Spend</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="marketing-metric-box">
                    <div class="marketing-metric-number">{num_programs}</div>
                    <div class="marketing-metric-label">Programs Marketed</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="marketing-metric-box">
                    <div class="marketing-metric-number">{num_channels}</div>
                    <div class="marketing-metric-label">Marketing Channels</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="marketing-metric-box">
                    <div class="marketing-metric-number">${avg_spend_per_program:,.0f}</div>
                    <div class="marketing-metric-label">Avg Spend/Program</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Two charts side by side with better spacing
            col_chart1, col_chart2 = st.columns([1.2, 0.8])
            
            with col_chart1:
                st.markdown("**Spend by Program & Channel**")
                
                # Create stacked bar chart showing channel breakdown per program
                program_channel_spend = filtered_marketing_df.groupby(['program', 'channel'])['spend_amount'].sum().reset_index()
                
                # Shorten program names for better display
                program_channel_spend['program_short'] = program_channel_spend['program'].str.replace('Flex Online ', '').str.replace('MS ', '')
                
                fig_prog = go.Figure()
                
                # Get unique channels and programs
                channels = program_channel_spend['channel'].unique()
                programs = program_channel_spend['program_short'].unique()
                
                # Calculate totals for each program (for top labels)
                program_totals = program_channel_spend.groupby('program_short')['spend_amount'].sum()
                
                # Add a trace for each channel (stacked bars)
                for idx, channel in enumerate(channels):
                    channel_data = program_channel_spend[program_channel_spend['channel'] == channel]
                    
                    # Create a full list with zeros for programs that don't have this channel
                    y_values = []
                    for prog in programs:
                        prog_data = channel_data[channel_data['program_short'] == prog]
                        if len(prog_data) > 0:
                            y_values.append(prog_data['spend_amount'].values[0])
                        else:
                            y_values.append(0)
                    
                    # Only show total on the last trace (top of stack)
                    if idx == len(channels) - 1:
                        text_values = [f'${program_totals[prog]:,.0f}' for prog in programs]
                        textposition = 'outside'
                    else:
                        text_values = ['' for _ in programs]
                        textposition = 'none'
                    
                    fig_prog.add_trace(go.Bar(
                        name=channel,
                        x=programs,
                        y=y_values,
                        marker_color=get_color(channel),
                        text=text_values,
                        textposition=textposition,
                        hovertemplate='<b>%{fullData.name}</b><br>Program: %{x}<br>Spend: $%{y:,.0f}<extra></extra>'
                    ))
                
                fig_prog.update_layout(
                    barmode='stack',
                    height=500,
                    xaxis_title='',
                    yaxis_title='Spend ($)',
                    margin=dict(t=100, b=100, l=70, r=40),  # Increased top margin for labels
                    xaxis={
                        'tickangle': -45,
                        'tickfont': {'size': 11}
                    },
                    yaxis={
                        'tickformat': '$,.0f',
                        'range': [0, program_totals.max() * 1.15]  # Add 15% space above for labels
                    },
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='rgba(0,0,0,0.2)',
                        borderwidth=1
                    )
                )
                st.plotly_chart(fig_prog, use_container_width=True)
            
            with col_chart2:
                st.markdown("**Spend by Channel**")
                channel_spend = filtered_marketing_df.groupby('channel')['spend_amount'].sum().sort_values(ascending=False)
                
                # Use the cohesive color palette
                colors_list = [get_color(ch) for ch in channel_spend.index]
                
                fig_chan = go.Figure(data=[
                    go.Pie(
                        labels=channel_spend.index, 
                        values=channel_spend.values,
                        marker=dict(colors=colors_list),
                        textinfo='label+percent',
                        textposition='auto',
                        hovertemplate='<b>%{label}</b><br>Spend: $%{value:,.0f}<br>%{percent}<extra></extra>'
                    )
                ])
                fig_chan.update_layout(
                    height=500,
                    margin=dict(t=40, b=40, l=20, r=20),
                    showlegend=False
                )
                st.plotly_chart(fig_chan, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Link to full marketing analysis
            st.info("💡 **Tip**: Visit the **Marketing Analysis** page for detailed ROI metrics, channel performance, and budget allocation insights.")
        else:
            st.info("📊 Marketing data is being collected. Check back soon for insights.")
    else:
        st.info("📊 Marketing data not yet available. Run the marketing ETL pipeline to load data.")
    
    # Footer for Executive Dashboard page
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
