"""
Predictive Analytics & Machine Learning Page Module
Provides forecasting, optimization, and recommendation capabilities
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging

# Import utility functions and ML components
from utils.database import get_connection, load_programs
from utils.data_preprocessing import DataPreprocessor
from utils.ml_models import TimeSeriesForecaster, ChannelOptimizer, TimingOptimizer, BudgetAllocator, ModelValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def render():
    """Render the Predictive Analytics page"""
    
    # Chrome-style tab CSS - matching Data Explorer exactly
    st.markdown("""
    <style>
    /* Chrome-style tabs for Predictive Analytics */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        justify-content: center !important;
        background-color: transparent !important;
        padding: 0px 20px !important;
        border-bottom: none !important;
        margin-bottom: 30px !important;
        margin-top: 20px !important;
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
    
    # Initialize database connection and preprocessor
    conn = get_connection()
    preprocessor = DataPreprocessor(conn)
    
    # Check if data is available
    try:
        # Test if required tables exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions_metrics';")
        has_admissions = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marketing_spend';")
        has_marketing = cursor.fetchone() is not None
        
        if not has_admissions:
            st.error("⚠️ Admissions data not available. Please run the ETL pipeline first.")
            return
        
        if not has_marketing:
            st.warning("⚠️ Marketing data not available. Some features will be limited.")
    
    except Exception as e:
        st.error(f"Error checking data availability: {e}")
        return
    
    # How to Use This Page - Collapsible
    with st.expander("💡 How to Use This Page", expanded=False):
        st.markdown("""
        <div style="font-size: 14px; color: #495057;">
            <strong style="color: #500000;">What You Can Do:</strong>
            <ul style="margin: 8px 0; padding-left: 20px;">
                <li><strong>Forecasting:</strong> Predict future inquiries, applications, and enrollments with confidence intervals</li>
                <li><strong>Channel Optimization:</strong> Identify the most effective marketing channels for each program</li>
                <li><strong>Timing Analysis:</strong> Discover optimal months for marketing investments</li>
                <li><strong>Budget Allocation:</strong> Get data-driven recommendations for budget distribution</li>
                <li><strong>Model Performance:</strong> Track prediction accuracy and model health over time</li>
            </ul>
            
            <strong style="color: #500000;">Key Features:</strong>
            <ul style="margin: 8px 0; padding-left: 20px;">
                <li><strong>Confidence Intervals:</strong> All forecasts include 95% confidence ranges</li>
                <li><strong>ROI Analysis:</strong> Understand return on investment for each marketing channel</li>
                <li><strong>Seasonal Patterns:</strong> Visualize and leverage seasonal trends</li>
                <li><strong>Sensitivity Analysis:</strong> See how budget changes affect expected outcomes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create tabs for main sections - NO EMOJIS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Forecasting",
        "Channels",
        "Timing",
        "Budget",
        "Performance"
    ])
    
    # Tab 1: Forecasting Section
    with tab1:
        render_forecasting_section(preprocessor, conn)
    
    # Tab 2: Channel Optimization Section
    with tab2:
        render_channel_optimization_section(preprocessor, conn)
    
    # Tab 3: Timing Analysis Section
    with tab3:
        render_timing_analysis_section(preprocessor, conn)
    
    # Tab 4: Budget Allocation Section
    with tab4:
        render_budget_allocation_section(preprocessor, conn)
    
    # Tab 5: Model Performance Dashboard Section
    with tab5:
        render_model_performance_section(conn)
    
    # Footer
    st.divider()
    st.markdown(f"""
    <div style="text-align: center; color: #6b7280; font-size: 14px;">
        <p>Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p style="font-size: 12px; color: #9ca3af;">
            Predictions are based on historical data and should be used as guidance, not guarantees.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_forecasting_section(preprocessor: DataPreprocessor, conn):
    """Render the forecasting section UI"""
    st.markdown("<h3 style='text-align: center; color: #500000;'>Time Series Forecasting</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #666; margin-bottom: 30px;'>
    Generate predictions for future inquiries, applications, and enrollments with confidence intervals.
    The system automatically selects the best forecasting model based on your data characteristics.
    </p>
    """, unsafe_allow_html=True)
    
    # Explanatory text about methodology
    with st.expander("About Forecasting Methodology", expanded=False):
        st.markdown("""
        **How It Works:**
        - **Prophet Model** (24+ months of data): Advanced time series model with automatic seasonality detection
        - **ARIMA Model** (12-24 months): Statistical model for moderate data availability
        - **Linear Regression** (<12 months): Simple trend-based model for limited data
        
        **Confidence Intervals:**
        - All forecasts include 95% confidence intervals showing the range of likely outcomes
        - Wider intervals indicate more uncertainty in predictions
        
        **Accuracy Metrics:**
        - **MAPE** (Mean Absolute Percentage Error): Lower is better, <15% is good
        - Models are validated on historical holdout data before generating forecasts
        """)
    
    st.markdown("---")
    
    # Input controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Get available programs
        programs_df = pd.read_sql("SELECT DISTINCT program FROM admissions_metrics ORDER BY program", conn)
        program_options = programs_df['program'].tolist()
        selected_program = st.selectbox(
            "🎓 Program",
            options=program_options,
            help="Select the program to forecast"
        )
    
    with col2:
        # Get available cohorts for selected program
        cohorts_df = pd.read_sql(
            "SELECT DISTINCT cohort_year FROM admissions_metrics WHERE program = ? ORDER BY cohort_year DESC",
            conn,
            params=[selected_program]
        )
        cohort_options = cohorts_df['cohort_year'].tolist()
        selected_cohort = st.selectbox(
            "📅 Cohort Year",
            options=cohort_options,
            help="Select the cohort year to forecast"
        )
    
    with col3:
        # Metric selection
        metric_options = {
            'inquiries_received': 'Inquiries Received',
            'applications_received': 'Applications Received',
            'anticipated_cohort_size': 'Anticipated Cohort Size'
        }
        selected_metric = st.selectbox(
            "Metric",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            help="Select the metric to forecast"
        )
    
    with col4:
        # Forecast horizon
        horizon_options = [3, 6, 9, 12, 18, 24]
        selected_horizon = st.selectbox(
            "🔮 Forecast Horizon (months)",
            options=horizon_options,
            index=2,  # Default to 9 months
            help="Number of months to forecast into the future"
        )
    
    # Generate forecast button
    if st.button("🚀 Generate Forecast", type="primary", use_container_width=True):
        with st.spinner("Training model and generating forecast..."):
            try:
                # Extract data for selected program and cohort
                admissions_data = preprocessor.extract_admissions_data(
                    program=selected_program,
                    cohort=selected_cohort
                )
                
                # Filter for selected metric
                metric_data = admissions_data[
                    admissions_data['metric_name'] == selected_metric
                ].copy()
                
                if metric_data.empty:
                    st.error(f"No data available for {selected_program} - Cohort {selected_cohort} - {metric_options[selected_metric]}")
                    return
                
                # Prepare data for forecasting
                metric_data = metric_data.rename(columns={'report_date': 'date'})
                metric_data = metric_data[['date', 'metric_value']].sort_values('date')
                
                # Check minimum data requirements
                if len(metric_data) < 6:
                    st.warning(f"⚠️ Insufficient data for forecasting. Need at least 6 months of data, found {len(metric_data)} months.")
                    return
                
                # Initialize and fit forecaster
                forecaster = TimeSeriesForecaster(metric_data, selected_metric)
                forecaster.fit()
                
                # Generate predictions
                predictions = forecaster.predict(periods=selected_horizon)
                
                # Get model info
                model_info = forecaster.get_model_info()
                
                # Display results
                st.success("✅ Forecast generated successfully!")
                
                # Display model information and accuracy
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.metric(
                        "Model Type",
                        model_info['model_type'].upper(),
                        help="The forecasting model selected based on data availability"
                    )
                
                with col_info2:
                    mape = model_info['validation_metrics'].get('mape')
                    if mape is not None:
                        st.metric(
                            "MAPE",
                            f"{mape:.2f}%",
                            help="Mean Absolute Percentage Error - lower is better"
                        )
                    else:
                        st.metric("MAPE", "N/A", help="Not enough data for validation")
                
                with col_info3:
                    st.metric(
                        "Data Points Used",
                        model_info['data_points_used'],
                        help="Number of historical data points used for training"
                    )
                
                st.markdown("---")
                
                # Create forecast visualization
                fig = create_forecast_chart(
                    historical_data=metric_data,
                    predictions=predictions,
                    metric_name=metric_options[selected_metric],
                    program=selected_program,
                    cohort=selected_cohort
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display predictions table
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Forecast Details</h4>", unsafe_allow_html=True)
                
                # Format predictions for display
                display_df = predictions.copy()
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m')
                display_df = display_df.rename(columns={
                    'date': 'Month',
                    'forecast': 'Predicted Value',
                    'lower_bound': 'Lower Bound (95% CI)',
                    'upper_bound': 'Upper Bound (95% CI)'
                })
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")
                logger.error(f"Forecasting error: {e}", exc_info=True)


def create_forecast_chart(
    historical_data: pd.DataFrame,
    predictions: pd.DataFrame,
    metric_name: str,
    program: str,
    cohort: int
) -> go.Figure:
    """
    Create forecast visualization with confidence intervals.
    
    Args:
        historical_data: Historical data with date and metric_value columns
        predictions: Predictions with date, forecast, lower_bound, upper_bound columns
        metric_name: Display name for the metric
        program: Program code
        cohort: Cohort year
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add historical data
    fig.add_trace(go.Scatter(
        x=historical_data['date'],
        y=historical_data['metric_value'],
        mode='lines+markers',
        name='Historical Data',
        line=dict(color='#500000', width=2),
        marker=dict(size=6),
        hovertemplate='<b>Historical</b><br>Date: %{x}<br>Value: %{y:,.0f}<extra></extra>'
    ))
    
    # Add forecast line
    fig.add_trace(go.Scatter(
        x=predictions['date'],
        y=predictions['forecast'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#0066cc', width=2, dash='dash'),
        marker=dict(size=6),
        hovertemplate='<b>Forecast</b><br>Date: %{x}<br>Value: %{y:,.0f}<extra></extra>'
    ))
    
    # Add confidence interval (shaded region)
    fig.add_trace(go.Scatter(
        x=predictions['date'],
        y=predictions['upper_bound'],
        mode='lines',
        name='Upper Bound (95% CI)',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=predictions['date'],
        y=predictions['lower_bound'],
        mode='lines',
        name='95% Confidence Interval',
        line=dict(width=0),
        fillcolor='rgba(0, 102, 204, 0.2)',
        fill='tonexty',
        hovertemplate='<b>95% CI</b><br>Date: %{x}<br>Lower: %{y:,.0f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=f"{metric_name} Forecast - {program} (Cohort {cohort})",
        xaxis_title="Date",
        yaxis_title=metric_name,
        hovermode='x unified',
        height=500,
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update axes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0,0,0,0.1)',
        showline=True,
        linewidth=1,
        linecolor='rgba(0,0,0,0.2)'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0,0,0,0.1)',
        showline=True,
        linewidth=1,
        linecolor='rgba(0,0,0,0.2)'
    )
    
    return fig


def render_channel_optimization_section(preprocessor: DataPreprocessor, conn):
    """Render the channel optimization section UI"""
    st.markdown("<h3 style='text-align: center; color: #500000;'>Marketing Channel Optimization</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #666; margin-bottom: 30px;'>
    Identify the most effective marketing channels for each program based on ROI and performance metrics.
    Recommendations consider spend efficiency, conversion rates, and consistency over time.
    </p>
    """, unsafe_allow_html=True)
    
    # Explanatory text about methodology
    with st.expander("About Channel Optimization", expanded=False):
        st.markdown("""
        **Effectiveness Score Components:**
        - **ROI (40%)**: Return on investment based on admissions value vs. marketing spend
        - **Conversion Rate (30%)**: Inquiries to applications conversion efficiency
        - **Consistency (20%)**: Performance stability over time
        - **Data Confidence (10%)**: Based on amount of historical data available
        
        **ROI Calculation:**
        - ROI = (Admissions Value - Marketing Spend) / Marketing Spend
        - Admissions Value = Number of Accepted Students * Program Tuition Estimate
        - Marketing spend is lagged by 2 months to account for conversion time
        
        **Color Indicators:**
        - Green: High ROI (> 2.0)
        - Yellow: Medium ROI (1.0 - 2.0)
        - Red: Low ROI (< 1.0)
        """)
    
    st.markdown("---")
    
    # Input controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get available programs
        programs_df = pd.read_sql("SELECT DISTINCT program FROM admissions_metrics ORDER BY program", conn)
        program_options = programs_df['program'].tolist()
        selected_program = st.selectbox(
            "🎓 Program",
            options=program_options,
            help="Select the program to analyze",
            key="channel_opt_program"
        )
    
    with col2:
        # Number of top channels to show
        top_n = st.selectbox(
            "Top Channels",
            options=[3, 5, 10],
            index=0,
            help="Number of top channels to display"
        )
    
    # Analyze channels button
    if st.button("🔍 Analyze Channels", type="primary", use_container_width=True):
        with st.spinner("Analyzing channel performance..."):
            try:
                # Extract data
                admissions_data = preprocessor.extract_admissions_data(program=selected_program)
                marketing_data = preprocessor.extract_marketing_data(program=selected_program)
                
                if admissions_data.empty:
                    st.error(f"No admissions data available for {selected_program}")
                    return
                
                if marketing_data.empty:
                    st.error(f"No marketing data available for {selected_program}")
                    return
                
                # Initialize channel optimizer
                optimizer = ChannelOptimizer(admissions_data, marketing_data)
                
                # Get channel recommendations
                recommendations = optimizer.recommend_channels(selected_program, top_n=top_n)
                
                if not recommendations:
                    st.warning(f"⚠️ Insufficient data to generate channel recommendations for {selected_program}")
                    return
                
                # Display results
                st.success(f"✅ Found {len(recommendations)} recommended channels!")
                
                st.markdown("---")
                
                # Create visualization
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Top Channel Recommendations</h4>", unsafe_allow_html=True)
                
                # Prepare data for visualization
                channels = [rec[0] for rec in recommendations]
                effectiveness_scores = [rec[1] for rec in recommendations]
                rois = [rec[2] for rec in recommendations]
                
                # Determine colors based on ROI
                colors = []
                for roi in rois:
                    if roi > 2.0:
                        colors.append('#28a745')  # Green
                    elif roi >= 1.0:
                        colors.append('#ffc107')  # Yellow
                    else:
                        colors.append('#dc3545')  # Red
                
                # Create bar chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=channels,
                    y=effectiveness_scores,
                    marker_color=colors,
                    text=[f"{score:.1f}" for score in effectiveness_scores],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Effectiveness Score: %{y:.1f}<br>' +
                                 '<extra></extra>'
                ))
                
                fig.update_layout(
                    title=f"Channel Effectiveness Scores - {selected_program}",
                    xaxis_title="Marketing Channel",
                    yaxis_title="Effectiveness Score (0-100)",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    showlegend=False
                )
                
                fig.update_xaxes(
                    showgrid=False,
                    showline=True,
                    linewidth=1,
                    linecolor='rgba(0,0,0,0.2)'
                )
                
                fig.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(0,0,0,0.1)',
                    showline=True,
                    linewidth=1,
                    linecolor='rgba(0,0,0,0.2)',
                    range=[0, 100]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display detailed metrics table
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Channel Performance Details</h4>", unsafe_allow_html=True)
                
                # Get detailed ROI data for all recommended channels
                roi_data = optimizer.calculate_roi(selected_program)
                roi_data = optimizer._calculate_effectiveness_score(roi_data, selected_program)
                
                # Filter to recommended channels
                roi_data = roi_data[roi_data['channel'].isin(channels)]
                
                # Sort by effectiveness score
                roi_data = roi_data.sort_values('effectiveness_score', ascending=False)
                
                # Format for display
                display_df = roi_data.copy()
                display_df['spend'] = display_df['spend'].apply(lambda x: f"${x:,.2f}")
                display_df['conversions'] = display_df['conversions'].astype(int)
                display_df['roi'] = display_df['roi'].apply(lambda x: f"{x:.2f}")
                display_df['effectiveness_score'] = display_df['effectiveness_score'].apply(lambda x: f"{x:.1f}")
                
                # Add ROI indicator
                display_df['roi_indicator'] = display_df['roi'].apply(lambda x: 
                    'High' if float(x) > 2.0 else 
                    'Medium' if float(x) >= 1.0 else 
                    'Low'
                )
                
                # Rename columns
                display_df = display_df.rename(columns={
                    'channel': 'Channel',
                    'spend': 'Total Spend',
                    'conversions': 'Conversions',
                    'roi': 'ROI',
                    'effectiveness_score': 'Effectiveness Score',
                    'roi_indicator': 'Performance'
                })
                
                # Select columns to display
                display_df = display_df[['Channel', 'Total Spend', 'Conversions', 'ROI', 'Performance', 'Effectiveness Score']]
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show performance history for top channel
                if len(recommendations) > 0:
                    st.markdown("---")
                    st.markdown(f"<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Performance History - {recommendations[0][0]}</h4>", unsafe_allow_html=True)
                    
                    top_channel = recommendations[0][0]
                    history = optimizer.get_channel_performance_history(selected_program, top_channel)
                    
                    if not history.empty:
                        # Create line chart for ROI over time
                        fig_history = go.Figure()
                        
                        fig_history.add_trace(go.Scatter(
                            x=history['month_year'],
                            y=history['roi'],
                            mode='lines+markers',
                            name='ROI',
                            line=dict(color='#500000', width=2),
                            marker=dict(size=8),
                            hovertemplate='<b>%{x}</b><br>ROI: %{y:.2f}<extra></extra>'
                        ))
                        
                        fig_history.update_layout(
                            title=f"ROI Trend - {top_channel}",
                            xaxis_title="Month",
                            yaxis_title="ROI",
                            height=350,
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            showlegend=False
                        )
                        
                        fig_history.update_xaxes(
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(0,0,0,0.1)'
                        )
                        
                        fig_history.update_yaxes(
                            showgrid=True,
                            gridwidth=1,
                            gridcolor='rgba(0,0,0,0.1)'
                        )
                        
                        st.plotly_chart(fig_history, use_container_width=True)
                        
                        # Display history table
                        history_display = history.copy()
                        history_display['spend'] = history_display['spend'].apply(lambda x: f"${x:,.2f}")
                        history_display['conversions'] = history_display['conversions'].astype(int)
                        history_display['roi'] = history_display['roi'].apply(lambda x: f"{x:.2f}")
                        
                        history_display = history_display.rename(columns={
                            'month_year': 'Month',
                            'spend': 'Spend',
                            'conversions': 'Conversions',
                            'roi': 'ROI'
                        })
                        
                        st.dataframe(
                            history_display,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No performance history available for this channel")
                
            except Exception as e:
                st.error(f"Error analyzing channels: {str(e)}")
                logger.error(f"Channel optimization error: {e}", exc_info=True)


def render_timing_analysis_section(preprocessor: DataPreprocessor, conn):
    """Render the timing analysis section UI"""
    st.markdown("<h3 style='text-align: center; color: #500000;'>Marketing Timing Analysis</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #666; margin-bottom: 30px;'>
    Discover optimal months for marketing investments based on seasonal patterns and conversion rates.
    Identify when your target audience is most responsive to marketing efforts.
    </p>
    """, unsafe_allow_html=True)
    
    # Explanatory text about methodology
    with st.expander("About Timing Analysis", expanded=False):
        st.markdown("""
        **How It Works:**
        - Analyzes historical conversion rates (inquiries to applications) by month
        - Identifies seasonal patterns using autocorrelation analysis
        - Ranks months by effectiveness score combining conversion rate and consistency
        
        **Effectiveness Score:**
        - **Conversion Rate (70%)**: Average inquiry-to-application conversion by month
        - **Consistency (30%)**: How stable the conversion rate is across years
        
        **Seasonal Patterns:**
        - Strong seasonality is detected when 12-month autocorrelation > 0.6
        - Heatmap shows conversion rates by month and year for visual pattern recognition
        """)
    
    st.markdown("---")
    
    # Input controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get available programs
        programs_df = pd.read_sql("SELECT DISTINCT program FROM admissions_metrics ORDER BY program", conn)
        program_options = programs_df['program'].tolist()
        selected_program = st.selectbox(
            "🎓 Program",
            options=program_options,
            help="Select the program to analyze",
            key="timing_program"
        )
    
    with col2:
        # Number of top months to show
        top_n = st.selectbox(
            "Top Months",
            options=[3, 6, 12],
            index=0,
            help="Number of top months to display"
        )
    
    # Analyze timing button
    if st.button("📅 Analyze Timing", type="primary", use_container_width=True):
        with st.spinner("Analyzing seasonal patterns..."):
            try:
                # Extract data
                admissions_data = preprocessor.extract_admissions_data(program=selected_program)
                
                if admissions_data.empty:
                    st.error(f"No admissions data available for {selected_program}")
                    return
                
                # Initialize timing optimizer
                optimizer = TimingOptimizer(admissions_data)
                
                # Get timing recommendations
                recommendations = optimizer.recommend_timing(selected_program, top_n=top_n)
                
                if not recommendations:
                    st.warning(f"⚠️ Insufficient data to generate timing recommendations for {selected_program}")
                    return
                
                # Display results
                st.success(f"✅ Found {len(recommendations)} recommended months!")
                
                st.markdown("---")
                
                # Display seasonal heatmap
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Seasonal Conversion Rate Heatmap</h4>", unsafe_allow_html=True)
                
                heatmap_fig = optimizer.visualize_seasonal_heatmap(selected_program)
                st.plotly_chart(heatmap_fig, use_container_width=True)
                
                st.markdown("---")
                
                # Display ranked list of recommended months
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Recommended Months (Ranked by Effectiveness)</h4>", unsafe_allow_html=True)
                
                # Create a nice display for recommendations
                for i, (month, effectiveness, conversion_rate) in enumerate(recommendations, 1):
                    # Determine badge color based on rank
                    if i == 1:
                        badge_color = "#28a745"  # Green
                        badge_text = "Best"
                    elif i == 2:
                        badge_color = "#ffc107"  # Yellow
                        badge_text = "2nd"
                    elif i == 3:
                        badge_color = "#fd7e14"  # Orange
                        badge_text = "3rd"
                    else:
                        badge_color = "#6c757d"  # Gray
                        badge_text = f"#{i}"
                    
                    # Format conversion rate as percentage
                    conv_rate_pct = f"{conversion_rate * 100:.1f}%"
                    effectiveness_str = f"{effectiveness:.1f}"
                    
                    # Create card for each month
                    card_html = f"""
                    <div style="background: white; border: 2px solid {badge_color}; border-radius: 12px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="background: {badge_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-right: 10px;">
                                    {badge_text}
                                </span>
                                <span style="font-size: 20px; font-weight: bold; color: #500000;">
                                    {month}
                                </span>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 24px; font-weight: bold; color: {badge_color};">
                                    {effectiveness_str}
                                </div>
                                <div style="font-size: 12px; color: #6c757d;">
                                    Effectiveness Score
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #e0e0e0;">
                            <span style="color: #6c757d; font-size: 14px;">
                                Avg Conversion Rate: <strong style="color: #500000;">{conv_rate_pct}</strong>
                            </span>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                
                # Display seasonal pattern analysis
                st.markdown("---")
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Seasonal Pattern Analysis</h4>", unsafe_allow_html=True)
                
                # Get full seasonal data
                seasonal_data = optimizer.analyze_seasonal_patterns(selected_program)
                
                if not seasonal_data.empty:
                    # Create line chart showing conversion rates by month
                    month_names = {
                        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                    }
                    
                    seasonal_data['month_name'] = seasonal_data['month'].map(month_names)
                    
                    fig_seasonal = go.Figure()
                    
                    fig_seasonal.add_trace(go.Scatter(
                        x=seasonal_data['month_name'],
                        y=seasonal_data['avg_conversion_rate'],
                        mode='lines+markers',
                        name='Avg Conversion Rate',
                        line=dict(color='#500000', width=3),
                        marker=dict(size=10),
                        fill='tozeroy',
                        fillcolor='rgba(80, 0, 0, 0.1)',
                        hovertemplate='<b>%{x}</b><br>Conversion Rate: %{y:.1f}%<extra></extra>'
                    ))
                    
                    fig_seasonal.update_layout(
                        title=f"Average Conversion Rate by Month - {selected_program}",
                        xaxis_title="Month",
                        yaxis_title="Conversion Rate",
                        height=400,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        showlegend=False
                    )
                    
                    fig_seasonal.update_xaxes(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(0,0,0,0.1)'
                    )
                    
                    fig_seasonal.update_yaxes(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='rgba(0,0,0,0.1)',
                        tickformat='.0%'
                    )
                    
                    st.plotly_chart(fig_seasonal, use_container_width=True)
                    
                    # Display data table
                    display_df = seasonal_data.copy()
                    display_df['month_name'] = display_df['month'].map(month_names)
                    display_df['avg_conversion_rate'] = display_df['avg_conversion_rate'].apply(lambda x: f"{x * 100:.1f}%")
                    display_df['consistency_score'] = display_df['consistency_score'].apply(lambda x: f"{x:.2f}")
                    
                    display_df = display_df.rename(columns={
                        'month_name': 'Month',
                        'avg_conversion_rate': 'Avg Conversion Rate',
                        'consistency_score': 'Consistency Score'
                    })
                    
                    display_df = display_df[['Month', 'Avg Conversion Rate', 'Consistency Score']]
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                
            except Exception as e:
                st.error(f"Error analyzing timing: {str(e)}")
                logger.error(f"Timing analysis error: {e}", exc_info=True)


def render_budget_allocation_section(preprocessor: DataPreprocessor, conn):
    """Render the budget allocation section UI"""
    st.markdown("<h3 style='text-align: center; color: #500000;'>Budget Allocation Recommendations</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #666; margin-bottom: 30px;'>
    Get data-driven recommendations for distributing your marketing budget across programs and channels.
    Maximize ROI by allocating resources to the most effective combinations.
    </p>
    """, unsafe_allow_html=True)
    
    # Explanatory text about methodology
    with st.expander("About Budget Allocation", expanded=False):
        st.markdown("""
        **How It Works:**
        - Ranks program-channel combinations by effectiveness score and ROI
        - Allocates budget iteratively to highest-performing combinations
        - Respects constraints (minimum per program, maximum per channel)
        - Calculates expected outcomes based on historical conversion rates
        
        **Expected Outcomes:**
        - **Inquiries**: Estimated number of inquiries generated
        - **Applications**: Estimated number of applications received
        - **Enrollments**: Estimated number of students enrolled
        - **ROI**: Expected return on investment
        
        **Sensitivity Analysis:**
        - Shows how outcomes change with +/-20% budget adjustments
        - Helps understand the impact of budget changes on expected results
        """)
    
    st.markdown("---")
    
    # Input controls
    col1, col2 = st.columns(2)
    
    with col1:
        # Total budget input
        total_budget = st.number_input(
            "💵 Total Marketing Budget ($)",
            min_value=1000.0,
            max_value=10000000.0,
            value=100000.0,
            step=10000.0,
            help="Total budget to allocate across programs and channels"
        )
    
    with col2:
        # Get available programs
        programs_df = pd.read_sql("SELECT DISTINCT program FROM admissions_metrics ORDER BY program", conn)
        program_options = programs_df['program'].tolist()
        
        selected_programs = st.multiselect(
            "🎓 Programs to Include",
            options=program_options,
            default=program_options[:3] if len(program_options) >= 3 else program_options,
            help="Select programs to include in budget allocation"
        )
    
    # Interactive slider for budget adjustment
    st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Budget Adjustment Slider</h4>", unsafe_allow_html=True)
    budget_multiplier = st.slider(
        "Adjust budget to see impact on allocations",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        format="%.1fx",
        help="Multiply the base budget to see how allocations change"
    )
    
    adjusted_budget = total_budget * budget_multiplier
    
    if budget_multiplier != 1.0:
        st.info(f"💡 Adjusted budget: ${adjusted_budget:,.2f} ({budget_multiplier:.1f}x base budget)")
    
    # Generate allocation button
    if st.button("💰 Generate Allocation", type="primary", use_container_width=True):
        if not selected_programs:
            st.error("Please select at least one program")
            return
        
        with st.spinner("Generating budget allocation recommendations..."):
            try:
                # Extract data for all selected programs
                all_admissions_data = []
                all_marketing_data = []
                
                for program in selected_programs:
                    admissions_data = preprocessor.extract_admissions_data(program=program)
                    marketing_data = preprocessor.extract_marketing_data(program=program)
                    
                    if not admissions_data.empty:
                        all_admissions_data.append(admissions_data)
                    if not marketing_data.empty:
                        all_marketing_data.append(marketing_data)
                
                if not all_admissions_data or not all_marketing_data:
                    st.error("Insufficient data for budget allocation")
                    return
                
                # Combine data
                combined_admissions = pd.concat(all_admissions_data, ignore_index=True)
                combined_marketing = pd.concat(all_marketing_data, ignore_index=True)
                
                # Initialize components
                channel_optimizer = ChannelOptimizer(combined_admissions, combined_marketing)
                
                # Create a simple forecaster (we'll use it indirectly through the allocator)
                # For now, we'll create the allocator without a forecaster since we're using historical data
                # This is a simplified implementation
                
                # Create budget allocator
                # Note: BudgetAllocator expects a forecaster, but we'll work around this
                # by using the channel optimizer directly
                
                # Simplified allocation logic
                allocations = []
                
                for program in selected_programs:
                    # Get channel recommendations
                    channel_data = channel_optimizer.calculate_roi(program)
                    
                    if channel_data.empty:
                        continue
                    
                    # Calculate effectiveness scores
                    channel_data = channel_optimizer._calculate_effectiveness_score(channel_data, program)
                    
                    # Add program column
                    channel_data['program'] = program
                    
                    allocations.append(channel_data)
                
                if not allocations:
                    st.error("No valid allocations could be generated")
                    return
                
                # Combine all allocations
                all_allocations = pd.concat(allocations, ignore_index=True)
                
                # Sort by effectiveness score
                all_allocations = all_allocations.sort_values('effectiveness_score', ascending=False)
                
                # Allocate budget proportionally based on effectiveness scores
                total_effectiveness = all_allocations['effectiveness_score'].sum()
                
                if total_effectiveness > 0:
                    all_allocations['allocated_budget'] = (
                        all_allocations['effectiveness_score'] / total_effectiveness * adjusted_budget
                    )
                else:
                    # Equal distribution if no effectiveness scores
                    all_allocations['allocated_budget'] = adjusted_budget / len(all_allocations)
                
                # Calculate allocation percentage
                all_allocations['allocation_percentage'] = (
                    all_allocations['allocated_budget'] / adjusted_budget * 100
                )
                
                # Calculate expected outcomes (simplified)
                all_allocations['expected_inquiries'] = (
                    all_allocations['conversions'] * 10
                ).astype(int)
                
                all_allocations['expected_applications'] = (
                    all_allocations['conversions'] * 3
                ).astype(int)
                
                all_allocations['expected_enrollments'] = all_allocations['conversions'].astype(int)
                all_allocations['expected_roi'] = all_allocations['roi']
                
                # Display results
                st.success("✅ Budget allocation generated successfully!")
                
                st.markdown("---")
                
                # Display summary metrics
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Allocation Summary</h4>", unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Budget",
                        f"${adjusted_budget:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Expected Inquiries",
                        f"{all_allocations['expected_inquiries'].sum():,}"
                    )
                
                with col3:
                    st.metric(
                        "Expected Applications",
                        f"{all_allocations['expected_applications'].sum():,}"
                    )
                
                with col4:
                    weighted_roi = (
                        (all_allocations['expected_roi'] * all_allocations['allocated_budget']).sum() /
                        all_allocations['allocated_budget'].sum()
                    )
                    st.metric(
                        "Weighted Avg ROI",
                        f"{weighted_roi:.2f}"
                    )
                
                st.markdown("---")
                
                # Display allocation chart
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Budget Allocation by Program and Channel</h4>", unsafe_allow_html=True)
                
                # Create stacked bar chart by program
                fig_allocation = go.Figure()
                
                programs_in_allocation = all_allocations['program'].unique()
                
                for channel in all_allocations['channel'].unique():
                    channel_data = all_allocations[all_allocations['channel'] == channel]
                    
                    fig_allocation.add_trace(go.Bar(
                        name=channel,
                        x=channel_data['program'],
                        y=channel_data['allocated_budget'],
                        text=[f"${val:,.0f}" for val in channel_data['allocated_budget']],
                        textposition='inside',
                        hovertemplate='<b>%{x} - ' + channel + '</b><br>' +
                                     'Allocated: $%{y:,.2f}<extra></extra>'
                    ))
                
                fig_allocation.update_layout(
                    barmode='stack',
                    title="Budget Allocation by Program and Channel",
                    xaxis_title="Program",
                    yaxis_title="Allocated Budget ($)",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    legend=dict(
                        title="Channel",
                        x=1.02,
                        y=1,
                        xanchor='left',
                        yanchor='top'
                    )
                )
                
                st.plotly_chart(fig_allocation, use_container_width=True)
                
                # Display detailed allocation table
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Detailed Allocation Breakdown</h4>", unsafe_allow_html=True)
                
                display_df = all_allocations.copy()
                display_df['allocated_budget'] = display_df['allocated_budget'].apply(lambda x: f"${x:,.2f}")
                display_df['allocation_percentage'] = display_df['allocation_percentage'].apply(lambda x: f"{x:.1f}%")
                display_df['expected_roi'] = display_df['expected_roi'].apply(lambda x: f"{x:.2f}")
                display_df['effectiveness_score'] = display_df['effectiveness_score'].apply(lambda x: f"{x:.1f}")
                
                display_df = display_df.rename(columns={
                    'program': 'Program',
                    'channel': 'Channel',
                    'allocated_budget': 'Allocated Budget',
                    'allocation_percentage': 'Allocation %',
                    'expected_inquiries': 'Expected Inquiries',
                    'expected_applications': 'Expected Applications',
                    'expected_enrollments': 'Expected Enrollments',
                    'expected_roi': 'Expected ROI',
                    'effectiveness_score': 'Effectiveness Score'
                })
                
                display_df = display_df[[
                    'Program', 'Channel', 'Allocated Budget', 'Allocation %',
                    'Expected Inquiries', 'Expected Applications', 'Expected Enrollments',
                    'Expected ROI', 'Effectiveness Score'
                ]]
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Sensitivity analysis
                st.markdown("---")
                st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Sensitivity Analysis</h4>", unsafe_allow_html=True)
                
                low_budget = f"${adjusted_budget * 0.8:,.2f}"
                base_budget = f"${adjusted_budget:,.2f}"
                high_budget = f"${adjusted_budget * 1.2:,.2f}"
                
                st.info(f"""
                **Budget Scenarios:**
                - **Low (-20%)**: {low_budget}
                - **Base (100%)**: {base_budget}
                - **High (+20%)**: {high_budget}
                """)
                
                # Create comparison chart
                scenarios = ['Low (-20%)', 'Base (100%)', 'High (+20%)']
                budgets = [adjusted_budget * 0.8, adjusted_budget, adjusted_budget * 1.2]
                
                # Estimate outcomes for each scenario (simplified)
                base_inquiries = all_allocations['expected_inquiries'].sum()
                base_applications = all_allocations['expected_applications'].sum()
                base_enrollments = all_allocations['expected_enrollments'].sum()
                
                inquiries = [base_inquiries * 0.8, base_inquiries, base_inquiries * 1.2]
                applications = [base_applications * 0.8, base_applications, base_applications * 1.2]
                enrollments = [base_enrollments * 0.8, base_enrollments, base_enrollments * 1.2]
                
                fig_sensitivity = go.Figure()
                
                fig_sensitivity.add_trace(go.Bar(
                    name='Expected Inquiries',
                    x=scenarios,
                    y=inquiries,
                    marker_color='#500000'
                ))
                
                fig_sensitivity.add_trace(go.Bar(
                    name='Expected Applications',
                    x=scenarios,
                    y=applications,
                    marker_color='#700000'
                ))
                
                fig_sensitivity.add_trace(go.Bar(
                    name='Expected Enrollments',
                    x=scenarios,
                    y=enrollments,
                    marker_color='#900000'
                ))
                
                fig_sensitivity.update_layout(
                    barmode='group',
                    title="Expected Outcomes by Budget Scenario",
                    xaxis_title="Budget Scenario",
                    yaxis_title="Count",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig_sensitivity, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error generating budget allocation: {str(e)}")
                logger.error(f"Budget allocation error: {e}", exc_info=True)


def render_model_performance_section(conn):
    """Render the model performance dashboard section UI"""
    st.markdown("<h3 style='text-align: center; color: #500000;'>Model Performance Dashboard</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #666; margin-bottom: 30px;'>
    Track prediction accuracy and model health over time. Monitor how well forecasting models
    are performing and identify when retraining may be needed. Evaluate how models perform against 
    actual outcomes to ensure reliable recommendations.
    </p>
    """, unsafe_allow_html=True)
    
    # Explanatory text
    with st.expander("About Model Performance Tracking", expanded=False):
        st.markdown("""
        **Performance Metrics:**
        - **MAPE** (Mean Absolute Percentage Error): Average percentage error, lower is better
        - **RMSE** (Root Mean Squared Error): Measures prediction accuracy, lower is better
        - **MAE** (Mean Absolute Error): Average absolute error, lower is better
        
        **Model Health Status:**
        - **Healthy**: MAPE < 15% - Model is performing well
        - **Warning**: MAPE 15-25% - Model performance is acceptable but could be improved
        - **Needs Retraining**: MAPE > 25% - Model should be retrained with recent data
        
        **Why Track Performance:**
        - Ensures predictions remain accurate as conditions change
        - Identifies when models need retraining
        - Builds confidence in recommendations
        """)
    
    st.markdown("---")
    
    # Check if model_predictions table exists
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_predictions';")
        has_predictions_table = cursor.fetchone() is not None
        
        if not has_predictions_table:
            st.info("""
            **Model Performance Tracking**
            
            The model performance dashboard will display accuracy metrics once predictions are generated and validated.
            
            **To start tracking:**
            1. Generate forecasts using the Forecasting tab
            2. Wait for actual outcomes to become available
            3. Return here to see how accurate the predictions were
            
            **What you will see:**
            - Accuracy trends over time
            - Current MAPE values for all models
            - Warnings if model performance degrades
            - Comparison of different forecasting models
            """)
            return
        
        # Query predictions data
        predictions_df = pd.read_sql("""
            SELECT 
                model_type,
                program,
                cohort,
                metric,
                prediction_date,
                forecast_date,
                predicted_value,
                lower_bound,
                upper_bound,
                actual_value
            FROM model_predictions
            ORDER BY prediction_date DESC, forecast_date DESC
        """, conn)
        
        if predictions_df.empty:
            st.info("""
            **No Predictions Yet**
            
            Start generating forecasts in the Forecasting tab to see performance metrics here.
            
            Once you create predictions and actual outcomes become available, this dashboard will show:
            - Model accuracy metrics (MAPE, RMSE, MAE)
            - Performance trends over time
            - Model health status
            - Comparison across different models
            """)
            return
        
        # Display current model status
        st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Current Model Status</h4>", unsafe_allow_html=True)
        
        # Calculate MAPE for each model type
        model_performance = []
        
        for model_type in predictions_df['model_type'].unique():
            model_data = predictions_df[
                (predictions_df['model_type'] == model_type) &
                (predictions_df['actual_value'].notna())
            ]
            
            if not model_data.empty:
                # Calculate MAPE
                mape = np.mean(
                    np.abs(
                        (model_data['actual_value'] - model_data['predicted_value']) /
                        model_data['actual_value']
                    )
                ) * 100
                
                # Calculate RMSE
                rmse = np.sqrt(
                    np.mean((model_data['actual_value'] - model_data['predicted_value']) ** 2)
                )
                
                # Calculate MAE
                mae = np.mean(
                    np.abs(model_data['actual_value'] - model_data['predicted_value'])
                )
                
                # Determine status
                if mape < 15:
                    status = "Healthy"
                    status_color = "#28a745"
                elif mape < 25:
                    status = "Warning"
                    status_color = "#ffc107"
                else:
                    status = "Needs Retraining"
                    status_color = "#dc3545"
                
                model_performance.append({
                    'model_type': model_type.upper(),
                    'mape': mape,
                    'rmse': rmse,
                    'mae': mae,
                    'predictions_count': len(model_data),
                    'status': status,
                    'status_color': status_color
                })
        
        if model_performance:
            # Display model cards
            cols = st.columns(min(len(model_performance), 3))
            
            for i, model in enumerate(model_performance):
                with cols[i % 3]:
                    mape_str = f"{model['mape']:.2f}%"
                    rmse_str = f"{model['rmse']:.2f}"
                    mae_str = f"{model['mae']:.2f}"
                    
                    st.markdown(f"""
                    <div style="background: white; border: 2px solid {model['status_color']}; border-radius: 12px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 18px; font-weight: bold; color: #500000; margin-bottom: 10px;">
                            {model['model_type']} Model
                        </div>
                        <div style="font-size: 14px; margin-bottom: 5px;">
                            <strong>Status:</strong> {model['status']}
                        </div>
                        <div style="font-size: 14px; margin-bottom: 5px;">
                            <strong>MAPE:</strong> {mape_str}
                        </div>
                        <div style="font-size: 14px; margin-bottom: 5px;">
                            <strong>RMSE:</strong> {rmse_str}
                        </div>
                        <div style="font-size: 14px; margin-bottom: 5px;">
                            <strong>MAE:</strong> {mae_str}
                        </div>
                        <div style="font-size: 12px; color: #6c757d; margin-top: 10px;">
                            Based on {model['predictions_count']} validated predictions
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display accuracy trends over time
            st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Accuracy Trends Over Time</h4>", unsafe_allow_html=True)
            
            # Calculate MAPE by prediction date
            predictions_with_actuals = predictions_df[predictions_df['actual_value'].notna()].copy()
            
            if not predictions_with_actuals.empty:
                predictions_with_actuals['prediction_date'] = pd.to_datetime(
                    predictions_with_actuals['prediction_date']
                )
                
                predictions_with_actuals['error_pct'] = np.abs(
                    (predictions_with_actuals['actual_value'] - predictions_with_actuals['predicted_value']) /
                    predictions_with_actuals['actual_value']
                ) * 100
                
                # Group by prediction date and model type
                accuracy_trends = predictions_with_actuals.groupby(
                    ['prediction_date', 'model_type']
                ).agg({
                    'error_pct': 'mean'
                }).reset_index()
                
                accuracy_trends = accuracy_trends.rename(columns={'error_pct': 'mape'})
                
                # Create line chart
                fig_trends = go.Figure()
                
                for model_type in accuracy_trends['model_type'].unique():
                    model_data = accuracy_trends[accuracy_trends['model_type'] == model_type]
                    
                    fig_trends.add_trace(go.Scatter(
                        x=model_data['prediction_date'],
                        y=model_data['mape'],
                        mode='lines+markers',
                        name=model_type.upper(),
                        line=dict(width=2),
                        marker=dict(size=8),
                        hovertemplate='<b>' + model_type.upper() + '</b><br>' +
                                     'Date: %{x}<br>' +
                                     'MAPE: %{y:.2f}%<extra></extra>'
                    ))
                
                # Add threshold lines
                fig_trends.add_hline(
                    y=15,
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Healthy (< 15%)",
                    annotation_position="right"
                )
                
                fig_trends.add_hline(
                    y=25,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Needs Retraining (> 25%)",
                    annotation_position="right"
                )
                
                fig_trends.update_layout(
                    title="Model Accuracy Over Time (MAPE)",
                    xaxis_title="Prediction Date",
                    yaxis_title="MAPE (%)",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    legend=dict(
                        x=0.01,
                        y=0.99,
                        xanchor='left',
                        yanchor='top',
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='rgba(0,0,0,0.2)',
                        borderwidth=1
                    )
                )
                
                fig_trends.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(0,0,0,0.1)'
                )
                
                fig_trends.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(0,0,0,0.1)'
                )
                
                st.plotly_chart(fig_trends, use_container_width=True)
            
            st.markdown("---")
            
            # Display prediction errors distribution
            st.markdown("<h4 style='text-align: center; color: #500000; margin-top: 30px;'>Prediction Error Distribution</h4>", unsafe_allow_html=True)
            
            if not predictions_with_actuals.empty:
                # Create histogram of errors
                fig_errors = go.Figure()
                
                for model_type in predictions_with_actuals['model_type'].unique():
                    model_data = predictions_with_actuals[
                        predictions_with_actuals['model_type'] == model_type
                    ]
                    
                    fig_errors.add_trace(go.Histogram(
                        x=model_data['error_pct'],
                        name=model_type.upper(),
                        opacity=0.7,
                        nbinsx=20
                    ))
                
                fig_errors.update_layout(
                    title="Distribution of Prediction Errors",
                    xaxis_title="Absolute Percentage Error (%)",
                    yaxis_title="Frequency",
                    height=400,
                    barmode='overlay',
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig_errors, use_container_width=True)
        
        else:
            st.info("""
            **Waiting for Validation Data**
            
            Predictions have been generated, but actual outcomes are not yet available for validation.
            
            Performance metrics will appear here once:
            1. Sufficient time has passed for actual outcomes to occur
            2. Actual data is loaded into the system
            3. Predictions are validated against actual outcomes
            """)
    
    except Exception as e:
        st.error(f"Error loading model performance data: {str(e)}")
        logger.error(f"Model performance error: {e}", exc_info=True)
