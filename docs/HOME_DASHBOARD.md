# 🏠 Home Dashboard

[← Back to Main](../README.md) | [Next: Executive Deep Dive →](EXECUTIVE_DEEP_DIVE.md)

---

## Overview

The Home Dashboard provides a quick overview of cohort performance with key metrics and trends. It's your starting point for understanding overall admissions performance.

## Features

### 📊 Current Stats
Display real-time metrics for the selected cohort:
- **Enrolled Students**: Total anticipated cohort size
- **Total Applications**: All applications submitted
- **Total Inquiries**: All inquiries received
- **Conversion Rate**: Inquiry → Application percentage with color-coded indicators

### 🎯 Admissions Funnel
Visual representation of the complete admissions journey:
- **6-Stage Funnel**: Inquiries → Applications → Complete Apps → Offers → Accepted → Enrolled
- **Linear/Log Scale Toggle**: Switch between scales for better visualization
- **Interactive Chart**: Hover for exact values and percentages
- **Percentage of Initial**: Shows conversion at each stage

### 📈 Program Comparison
Side-by-side performance across all 7 programs:
- **Toggle Metrics**: Show/hide Inquiries, Applications, Accepted, Cohort Size
- **Log Scale Option**: Better visualization for wide-ranging values
- **Color-Coded Bars**: Maroon gradient for visual distinction
- **Grouped Display**: Easy comparison across programs

### 📉 Trend Analysis
Track performance over time with dual charts:

**Application & Inquiry Trends:**
- Multi-line time series chart
- Toggle buttons to show/hide metrics
- Hover for exact values and dates
- Identify growth patterns

**Conversion Rates Over Time:**
- Inquiry → Application conversion
- Application → Offer conversion
- Track effectiveness changes
- Spot seasonal patterns

## How to Use

### Step 1: Select Filters
```
📅 Cohort Year: Choose Class of 2026, 2027, or 2028
🎓 Program Focus: Select specific program or "All Programs"
```

### Step 2: Review Key Metrics
- Check the 4 metric cards at the top
- Note the conversion rate color (Green = Good, Yellow = Fair, Red = Needs Attention)
- Compare against historical benchmarks

### Step 3: Analyze Funnel
- Review the admissions funnel for drop-off points
- Toggle log scale if values vary widely
- Identify stages needing improvement

### Step 4: Compare Programs
- Use toggle buttons to focus on specific metrics
- Enable log scale for better comparison
- Identify top and bottom performers

### Step 5: Examine Trends
- Toggle metrics on/off to focus analysis
- Look for seasonal patterns
- Compare conversion rates over time

## Configuration

### Filter Options
```python
cohort_options = [2028, 2027, 2026]
program_options = ['All Programs', 'MBA', 'MS ACCT', 'MS ENLD', 
                   'MS HRM', 'MS MISY', 'MS MKTG', 'MS SPBA']
```

### Chart Options
- **Linear/Log Scale**: Toggle for funnel and program comparison
- **Metric Visibility**: Toggle individual metrics on/off
- **Interactive Hover**: Automatic on all charts
- **Data Labels**: Show exact values on charts

### Color Scheme
```python
# Conversion Rate Colors
Green (#28a745): > 30% (Excellent)
Yellow (#ffc107): 20-30% (Good)
Red (#dc3545): < 20% (Needs Improvement)

# Chart Colors
Maroon (#500000): Primary data
Dark Maroon (#700000): Secondary data
Light Maroon (#B00000): Tertiary data
```

## Tips & Best Practices

### For Quick Analysis
1. Start with "All Programs" to see overall performance
2. Check conversion rate first - it's the key indicator
3. Use funnel to identify bottlenecks
4. Compare current cohort to previous years

### For Deep Dive
1. Filter by specific program
2. Enable log scale if needed
3. Toggle metrics to focus on specific areas
4. Review trends for patterns

### For Presentations
1. Use print button to export
2. Take screenshots of key charts
3. Note the "Last Updated" timestamp
4. Include conversion rate context

## Common Questions

**Q: Why is my conversion rate low?**
A: Check the funnel to see where drop-off occurs. Low conversion could indicate:
- Marketing targeting issues (if drop-off at inquiry stage)
- Application complexity (if drop-off at application stage)
- Competitive offers (if drop-off at acceptance stage)

**Q: How do I compare cohorts?**
A: Use the Comparison Tool page for detailed year-over-year analysis.

**Q: What's the difference between linear and log scale?**
A: Linear scale shows actual values. Log scale compresses large values, making it easier to compare when values vary widely (e.g., 10 vs 1000).

**Q: Can I export the data?**
A: Yes, use the print button or visit the Data Explorer page for CSV export.

## Related Pages

- **📊 Executive Deep Dive**: Comprehensive cohort analysis with 4 tabs
- **🔄 Comparison Tool**: Year-over-year cohort comparisons
- **📢 Marketing Analysis**: Marketing spend and ROI tracking
- **🗄️ Data Explorer**: Raw data access and export
- **🔮 Predictive Analytics**: Forecasting and ML recommendations

## Technical Details

### Data Source
```sql
SELECT * FROM admissions_metrics 
WHERE cohort_year = ? 
ORDER BY report_date, program
```

### Metrics Calculated
```python
conversion_rate = (total_applications / total_inquiries) * 100
funnel_stages = [inquiries, applications, complete, offers, accepted, enrolled]
program_metrics = [inquiries, applications, accepted, cohort_size]
```

### Performance
- **Load Time**: < 2 seconds for typical dataset
- **Refresh Rate**: Real-time (updates on filter change)
- **Cache**: Enabled for database queries (TTL: 300 seconds)

---

**Home Dashboard Guide** • Version 4.0 • Last Updated: January 23, 2026

[← Back to Main](../README.md) | [Next: Executive Deep Dive →](EXECUTIVE_DEEP_DIVE.md)
