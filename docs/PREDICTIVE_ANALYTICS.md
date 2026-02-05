# Predictive Analytics

[← Back to Documentation](README.md)

---

## Overview

The Predictive Analytics page provides intelligent marketing insights with three focused analysis tools: Channel Performance, Timing Intelligence, and Budget Allocation. Each tool delivers actionable recommendations with clean, professional visualizations.

## Navigation

The page features three sub-tabs accessible from the top navigation:
- **Channel Performance**: Identify top-performing channels with ROI forecasting
- **Timing Intelligence**: Discover optimal timing for channel investments
- **Budget Allocation**: Get data-driven budget distribution recommendations

---

## Channel Performance

### Purpose
Identify which marketing channels deliver the best results and forecast expected outcomes based on investment scenarios.

### Interface Layout

#### Investment Filters
- **Monthly Investment Amount**: Set investment level ($1,000 - $50,000)
- **Investment Duration**: Choose timeframe (1, 3, 6, or 12 months)

#### Top 3 Channel Investment Forecasts
Each channel is displayed in a clean white card containing:
- **Channel Name**: Ranked by effectiveness (#1, #2, #3)
- **Monthly Forecast**: Expected outcomes per month
- **Total Forecast**: Cumulative outcomes over investment duration
- **ROI**: Return on investment multiplier
- **Confidence**: Prediction confidence percentage
- **Recommendation**: Color-coded guidance (Recommended/Consider/Caution)

#### Channel Comparison Table
Comprehensive table showing:
- Total Spend
- Attributed Outcomes
- Efficiency (Outcomes per dollar)
- Effectiveness Score
- Consistency Score
- Performance Rating

### How to Use

1. **Set Investment Parameters**
   - Enter your planned monthly investment amount
   - Select the investment duration

2. **Review Top Channels**
   - Examine the top 3 channels ranked by effectiveness
   - Compare metrics: forecast, ROI, and confidence
   - Read the recommendation for each channel

3. **Analyze Comparison Table**
   - Review all channels side-by-side
   - Identify efficiency and consistency patterns
   - Use performance ratings to guide decisions

### Interpretation Guide

**Recommendation Types:**
- **Recommended** (Green): High efficiency (>0.01), invest with confidence
- **Consider** (Blue): Moderate efficiency (0.005-0.01), viable option
- **Caution** (Yellow): Lower efficiency (<0.005), requires careful evaluation

**Key Metrics:**
- **Effectiveness Score**: Composite metric combining efficiency and consistency
- **Consistency Score**: Reliability of channel performance over time
- **ROI**: Expected return per dollar invested

---

## Timing Intelligence

### Purpose
Discover the optimal timing for channel investments by analyzing seasonal patterns and month-specific effectiveness.

### Interface Layout

#### Channel-Timing Effectiveness Matrix
Interactive heatmap showing:
- **Channels** (Y-axis): All marketing channels
- **Months** (X-axis): January through December
- **Color Coding**: Green (high effectiveness) to Red (low effectiveness)
- **Hover Details**: Exact effectiveness scores

#### Investment Filters
- **Monthly Investment Amount**: Set investment level ($1,000 - $25,000)
- **Forecast Period**: Choose horizon (3, 6, or 12 months)

#### Top 5 Channel Opportunities
Each opportunity is displayed in a clean white card containing:
- **Channel & Month**: Specific timing recommendation
- **Seasonal Badge**: Peak Season or High Season indicator (if applicable)
- **Expected Outcomes**: Prominently displayed forecast
- **Recommendation**: Investment guidance with expected results

### How to Use

1. **Analyze the Heatmap**
   - Identify green cells (high effectiveness periods)
   - Look for patterns across channels
   - Note seasonal trends

2. **Set Investment Parameters**
   - Enter your planned monthly investment
   - Select the forecast period

3. **Review Top Opportunities**
   - Examine the top 5 month-channel combinations
   - Note seasonal indicators (Peak/High Season)
   - Compare expected outcomes

4. **Plan Your Calendar**
   - Schedule campaigns during high-effectiveness periods
   - Allocate more budget to peak seasons
   - Avoid low-effectiveness months

### Interpretation Guide

**Seasonal Indicators:**
- **Peak Season**: January-March (1.2x multiplier)
- **High Season**: September-October (1.1x multiplier)
- **Standard**: Other months (1.0x multiplier)

**Effectiveness Scores:**
- **>0.5**: Excellent timing, highly recommended
- **0.2-0.5**: Good timing, consider investing
- **<0.2**: Lower effectiveness, use caution

---

## Budget Allocation

### Purpose
Generate optimal budget distribution across channels and months to maximize ROI and expected outcomes.

### Interface Layout

#### Budget Filters
- **Total Budget**: Set total marketing budget ($5,000 - $500,000)
- **Planning Period**: Choose timeframe (3, 6, 9, or 12 months)

#### Generate Button
Single "Generate Budget Allocation" button to create recommendations

#### Recommended Budget Allocation
After generation, displays:
- **Summary Metrics**: Total Allocated, Expected Outcomes, Average ROI
- **Allocation Table**: Detailed breakdown by channel and month
- **Key Recommendations**: Top 3 strategic insights

### How to Use

1. **Set Budget Parameters**
   - Enter your total marketing budget
   - Select the planning period

2. **Generate Allocation**
   - Click "Generate Budget Allocation"
   - Wait for optimization to complete

3. **Review Summary Metrics**
   - Check total allocated amount
   - Review expected outcomes
   - Note average ROI

4. **Analyze Allocation Table**
   - Review budget distribution by channel
   - Note recommended months for each channel
   - Compare effectiveness scores and ROI

5. **Apply Key Recommendations**
   - Read the top 3 strategic insights
   - Note primary investment recommendation
   - Review expected returns and budget utilization

### Interpretation Guide

**Allocation Strategy:**
- Budget is distributed proportionally based on effectiveness scores
- Higher effectiveness channels receive larger allocations
- Timing is optimized for each channel

**Key Metrics:**
- **Allocated Budget**: Dollar amount assigned to each channel-month
- **Expected Outcomes**: Forecasted results (inquiries/applications)
- **Effectiveness Score**: Performance rating (0-1 scale)
- **ROI**: Expected return multiplier

---

## Data Requirements

### Minimum Data
- **Admissions Data**: 6+ months of historical metrics
- **Marketing Data**: 6+ months of spend by channel
- **Matched Periods**: Overlapping date ranges for both datasets

### Optimal Data
- **12+ months**: Better seasonal pattern detection
- **Multiple Programs**: Cross-program insights
- **Complete Records**: All channels and months populated

---

## Best Practices

### Channel Performance
- Review forecasts monthly to track accuracy
- Test different investment scenarios
- Focus on channels with high consistency scores
- Balance ROI with strategic goals

### Timing Intelligence
- Plan campaigns 2-3 months in advance
- Allocate extra budget to peak seasons
- Monitor heatmap for emerging patterns
- Combine timing with channel insights

### Budget Allocation
- Run multiple scenarios with different budgets
- Review sensitivity to budget changes
- Align allocations with strategic priorities
- Update quarterly as data evolves

### General Tips
- **Start Small**: Test recommendations with pilot budgets
- **Track Results**: Compare actual vs. predicted outcomes
- **Iterate**: Refine based on performance data
- **Combine Insights**: Use all three tools together for comprehensive strategy

---

## Understanding the Analytics

### How Effectiveness is Calculated
Effectiveness scores combine multiple factors:
- **Spend Efficiency**: Outcomes per dollar spent
- **Consistency**: Reliability across time periods
- **Attribution**: Direct correlation between spend and outcomes
- **Recency**: Recent performance weighted higher

### Confidence Levels
Confidence percentages indicate prediction reliability:
- **70-100%**: High confidence, strong historical patterns
- **50-70%**: Moderate confidence, some variability
- **<50%**: Lower confidence, limited data or high variability

### ROI Calculations
ROI represents expected return on investment:
- **>2.0x**: Excellent return
- **1.5-2.0x**: Good return
- **1.0-1.5x**: Moderate return
- **<1.0x**: Below breakeven

---

## Troubleshooting

### No Data Available
- Ensure admissions data is loaded (run ETL pipeline)
- Verify marketing spend data exists
- Check program name matching between datasets

### Low Confidence Scores
- Increase historical data range
- Verify data quality and completeness
- Consider seasonal variations

### Unexpected Recommendations
- Review underlying data for anomalies
- Check for recent changes in marketing strategy
- Verify date ranges are correct

---

## Technical Notes

### Model Architecture
- **Channel Optimizer**: Calculates ROI and effectiveness by channel
- **Timing Analyzer**: Identifies seasonal patterns and optimal periods
- **Budget Allocator**: Optimizes distribution using effectiveness scores

### Update Frequency
- Recommendations update when filters change
- Data refreshes when ETL pipeline runs
- Historical patterns recalculate with new data

### Performance
- Analysis runs in real-time for selected filters
- Large datasets may take 2-3 seconds to process
- Results are cached for faster subsequent views

---

[← Back to Documentation](README.md)
