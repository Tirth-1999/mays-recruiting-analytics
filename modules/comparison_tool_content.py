"""
Comparison Tool Content - Reusable function for both standalone page and tab
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from utils.database import load_programs, load_yoy_comparison_data


def render_comparison_tool(key_prefix="comp_tool"):
    """
    Render the complete comparison tool content.
    Can be used in standalone page or as a tab.
    
    Args:
        key_prefix: Prefix for session state keys to avoid conflicts
    """
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
            # Get latest data for both cohorts
            primary_latest_date = primary_data['report_date'].max()
            primary_latest = primary_data[primary_data['report_date'] == primary_latest_date]
            
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
    else:
        st.info("💡 Please select a comparison cohort to begin the analysis.")
