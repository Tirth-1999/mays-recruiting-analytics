# EDULYTIX - Comprehensive Data Analysis & Project Understanding

## Executive Summary

After thorough analysis of all context documents and datasets, I've identified the complete data structure, business context, and project requirements for Edulytix. This document provides a detailed breakdown of what data exists, how it's structured, and its importance to the project.

---

## 1. BUSINESS CONTEXT

### What is This Project About?

**Edulytix** is a data analytics platform for **Texas A&M Mays Business School's Flex Online Programs** to:
- Track admissions funnel performance (inquiries → applications → admissions → enrollment)
- Measure marketing campaign effectiveness across multiple channels
- Forecast future enrollment numbers for budget planning
- Enable data-driven decision-making for marketing spend allocation

### Key Stakeholders
- **Shrihari Sridhar** - Senior Associate Dean (Project Sponsor)
- **Jon Jasperson** - Associate Dean for Academic Innovation (Data Provider)
- **Brooke Perry** - Marketing/Communications (Marketing Data)
- **Nate Sharp** - Leadership Team
- **Tirth Shah** - Project Lead/Developer

### Programs Being Tracked (7 Flex Online Programs)
1. **MBA** - Flex Online MBA
2. **MS ACCT** - MS Accounting
3. **MS ENLD** - MS Engineering Leadership (new program)
4. **MS HRM** - MS Human Resource Management
5. **MS MISY** - MS Management Information Systems
6. **MS MKTG** - MS Marketing
7. **MS SPBA** - MS Sport Business Analytics (newest addition)

---

## 2. DATA STRUCTURE & AVAILABILITY

### Available Datasets (6 Excel Files)

| File Name | Date Range | Purpose |
|-----------|------------|---------|
| MBS-Flex-Online-Admissions-2024-04-30.xlsx | Jan 2024 - Apr 2024 | Class of 2026 baseline |
| MBS-Flex-Online-Admissions-2024-05-31.xlsx | Jan 2024 - May 2024 | Class of 2026 tracking |
| MBS-Flex-Online-Admissions-2024-07-31.xlsx | Jan 2024 - Jul 2024 | Class of 2026 complete cycle |
| MBS-Flex-Online-Admissions-2025-07-31.xlsx | Oct 2024 - Jul 2025 | Class of 2027 tracking |
| MBS-Flex-Online-Admissions-2025-10-31.xlsx | Oct 2024 - Oct 2025 | Class of 2027 + 2028 |
| MBS-Flex-Online-Admissions-2025-10-31_New.xlsx | Oct 2025 - Present | Latest with Class of 2028 |

**Additional Marketing Data:**
- TAMU_MonthlyScorecard_2024_04.pdf - Detailed marketing campaign metrics (Impressions, Clicks, CTR, CPC by channel)

### Data Collection Timeline
- **Class of 2026**: Started tracking January 2024
- **Class of 2027**: Started tracking November 2024
- **Class of 2028**: Started tracking October 2024
- **Reporting Frequency**: Monthly (last day of each month)

---

## 3. DETAILED DATA METRICS

### A. ADMISSIONS FUNNEL METRICS (Primary KPIs)

#### 3.1 Inquiries
**Definition**: Unique individuals who contacted the program via email, text, social media, or phone
**Importance**: Top-of-funnel metric showing marketing reach effectiveness
**Data Points**: Cumulative count per program per month

#### 3.2 Application Stages
Each application goes through multiple statuses tracked in WebAdMIT (Business CAS):

| Metric | Definition | Business Importance |
|--------|------------|---------------------|
| **Applications - In Progress** | Created account, selected program, not yet submitted | Shows interest level; dynamic metric (can decrease if prospects abandon) |
| **Applications - Received** | Paid and submitted but missing required documents | Indicates serious intent; revenue generated |
| **Applications - Complete** | All documents submitted and ready for review | Ready for admissions decision |
| **Applications - Manual** | Requires manual processing (special cases) | Quality control checkpoint |
| **Applications - Verified** | Coursework/GPA verified by Liaison | Final validation before decision |
| **Applications - On Hold** | Issues detected (duplicate, payment, conduct) | Risk management metric |
| **Applications - Undelivered** | Returned for corrections | Data quality indicator |
| **Applications - Deferral** | Carried over from previous cycle | Retention metric |

#### 3.3 Admissions Decisions

| Metric | Definition | Business Importance |
|--------|------------|---------------------|
| **Pre-Admissions** | Completed pre-application & interview, invited to apply formally | Qualified lead pool |
| **Offered Admission** | Formal admission offers extended | Acceptance capacity planning |
| **Denied Admission** | Applications rejected | Quality standards metric |
| **Accepted Offers** | Students confirmed intent to enroll | **CRITICAL: Revenue projection** |
| **Declined Offers** | Students rejected admission offer | Competitor analysis signal |
| **Deferred to Next Year** | Accepted but postponed enrollment | Future cohort planning |
| **Deferred from Last Year** | Previous year deferrals now enrolling | Cohort size adjustment |
| **Moved to Another Mays Program** | Transferred to different program | Internal conversion tracking |
| **Application Withdrawn** | Student withdrew from consideration | Attrition analysis |

#### 3.4 **ANTICIPATED COHORT SIZE** (Most Important Metric)
**Definition**: Expected number of students starting the program
**Calculation**: Accepted Offers + Deferred from Last Year - Deferred to Next Year
**Business Importance**: 
- Direct revenue forecast (tuition × cohort size)
- Faculty/resource allocation
- Program viability assessment
- Budget planning for next fiscal year

---

### B. MARKETING CAMPAIGN METRICS

#### Marketing Channels Tracked

| Channel | Metrics | Business Importance |
|---------|---------|---------------------|
| **Meta (Facebook/Instagram)** | Impressions, Clicks, CTR | Social media reach; younger demographics |
| **LinkedIn** | Impressions, Clicks, CTR, CPC | Professional audience; MBA/MS programs |
| **Google Paid Search (SEM)** | Impressions, Clicks, CTR, CPC | High-intent searches; conversion driver |
| **Display Ads** | Impressions, Clicks, CTR | Brand awareness; retargeting |
| **YouTube** | Impressions, Clicks, CTR | Video engagement; storytelling |
| **Contextual Display** | Impressions, Clicks, CTR | Content-based targeting |
| **List-Based Display** | Impressions, Clicks, CTR | Targeted audience lists |
| **Digital OOH (Out-of-Home)** | Impressions | Brand awareness (billboards, transit) |
| **Retargeting** | Impressions, Clicks, CTR | Re-engage previous visitors |

#### Key Marketing KPIs
- **CTR (Click-Through Rate)**: Clicks ÷ Impressions (benchmark: 0.16% for Meta, 0.53% for LinkedIn, 6.41% for Search)
- **CPC (Cost Per Click)**: Total spend ÷ Clicks (benchmark: $1.87 for Search, $4.91 for LinkedIn)
- **Impressions**: Total ad views
- **Clicks**: Total ad clicks

#### Marketing Data Gaps
⚠️ **CRITICAL MISSING DATA**: Marketing spend by channel
- Context emails mention this data is being requested from Ologie (marketing agency)
- Need: Monthly spend by channel (Meta, LinkedIn, Google, etc.)
- Need: Program-level spend vs. overall awareness spend
- This is essential for ROI analysis and budget optimization

---

## 4. DATA EVOLUTION & STRUCTURE

### Sheet Structure in Excel Files

#### Sheet 1: "All Programs"
- **Purpose**: Executive dashboard view
- **Structure**: Cross-program comparison for current month
- **Columns**: One column per program (MBA, MS ACCT, MS HRM, etc.)
- **Rows**: All metrics (inquiries through campaign metrics)
- **Evolution**: Latest files show 3 cohorts side-by-side (Class '26, '27, '28)

#### Sheet 2: "Awareness" (New in 2025 files)
- **Purpose**: Overall brand awareness campaigns (not program-specific)
- **Structure**: Same as individual program sheets
- **Importance**: Tracks top-of-funnel marketing before program selection

#### Sheets 3-9: Individual Program Sheets
- **Purpose**: Month-by-month tracking for each program
- **Structure**: 
  - Columns: Monthly snapshots (Jan 2024, Feb 2024, Mar 2024, etc.)
  - Rows: All metrics
- **Importance**: Time-series data for trend analysis and forecasting

#### Sheet 10: "Metric Definitions"
- **Purpose**: Data dictionary
- **Source**: WebAdMIT (Business CAS) definitions
- **Importance**: Ensures consistent interpretation

---

## 5. DATA QUALITY & OBSERVATIONS

### Strengths
✅ **Consistent Structure**: All files follow same format
✅ **Comprehensive Funnel**: Tracks entire journey from inquiry to enrollment
✅ **Multi-Program**: Enables cross-program comparison
✅ **Historical Data**: 18+ months of data for Class of 2026
✅ **Marketing Integration**: Campaign metrics alongside admissions data

### Gaps & Challenges
⚠️ **Missing Marketing Spend Data**: Cannot calculate ROI without cost data
⚠️ **Incomplete Historical Data**: Class of 2026 only starts from Jan 2024 (missing earlier months)
⚠️ **Sparse Marketing Data**: Many months show "NaN" for campaign metrics
⚠️ **New Programs**: MS ENLD and MS SPBA have limited historical data
⚠️ **Inconsistent Tracking**: Some programs started tracking at different times

### Data Patterns Observed
1. **Seasonal Trends**: Applications spike in certain months (likely before semester starts)
2. **Conversion Rates Vary**: MBA has higher inquiry-to-application conversion than MS programs
3. **Marketing Effectiveness**: Google Search has 12.45% CTR (2x industry benchmark)
4. **Cohort Sizes**: Range from 5 (MS ACCT) to 22 (MS HRM) for Class of 2028

---

## 6. HOW THIS DATA SUPPORTS EDULYTIX GOALS

### Goal 1: Data Visualization Dashboard
**Data Available**:
- ✅ Historical trends (inquiries, applications, admissions over time)
- ✅ Conversion rates at each funnel stage
- ✅ Program-by-program comparison
- ✅ Marketing channel performance (CTR, impressions, clicks)
- ⚠️ Marketing ROI (need spend data)

**Visualizations Needed**:
- Funnel charts (inquiries → applications → admissions → enrollment)
- Time-series line charts (monthly trends)
- Heatmaps (program performance comparison)
- Channel performance bar charts (CTR, CPC by channel)
- Cohort size projections

### Goal 2: Predictive Forecasting
**Data Available**:
- ✅ 18+ months of historical data for Class of 2026
- ✅ 12+ months for Class of 2027
- ✅ 2+ months for Class of 2028
- ✅ Seasonal patterns visible

**Forecasting Opportunities**:
- Predict anticipated cohort size 1-6 months ahead
- Forecast application volume by program
- Estimate marketing campaign impact on inquiries
- Project revenue based on enrollment forecasts

**Challenges**:
- Limited data for newer programs (MS ENLD, MS SPBA)
- Marketing data gaps may affect accuracy
- Need to account for external factors (economy, competition)

### Goal 3: AI Chatbot Integration
**Sample Queries the Data Can Answer**:
1. "What was our total marketing spend last year?" (need spend data)
2. "How many applications did MBA receive in October 2025?" ✅
3. "What's the conversion rate from inquiry to application for MS HRM?" ✅
4. "Which marketing channel has the best CTR?" ✅
5. "What's the anticipated cohort size for Class of 2028?" ✅
6. "How does MS MISY's performance compare to MS MKTG?" ✅
7. "What's the trend in MBA inquiries over the past 6 months?" ✅
8. "How many students deferred from last year?" ✅
9. "What's the acceptance rate for MS ACCT?" ✅
10. "Which program has the highest application completion rate?" ✅

---

## 7. TECHNICAL RECOMMENDATIONS

### Database Schema Design

#### Table 1: `programs`
```sql
- program_id (PK)
- program_code (MBA, MS_ACCT, MS_HRM, etc.)
- program_name
- start_date
- is_active
```

#### Table 2: `cohorts`
```sql
- cohort_id (PK)
- cohort_year (2026, 2027, 2028)
- start_date
- end_date
```

#### Table 3: `admissions_metrics` (Monthly snapshots)
```sql
- metric_id (PK)
- program_id (FK)
- cohort_id (FK)
- report_date (last day of month)
- inquiries_received
- applications_in_progress
- applications_received
- applications_complete
- applications_manual
- applications_verified
- applications_on_hold
- applications_undelivered
- applications_deferral
- total_applications
- admissions_pre_admission
- admissions_offered
- admissions_denied
- admissions_accepted
- admissions_declined
- admissions_deferred_to_next
- admissions_deferred_from_last
- admissions_moved_to_other
- admissions_withdrawn
- anticipated_cohort_size
```

#### Table 4: `marketing_campaigns`
```sql
- campaign_id (PK)
- program_id (FK) -- NULL for awareness campaigns
- cohort_id (FK)
- report_date
- channel (Meta, LinkedIn, Google, etc.)
- campaign_name
- impressions
- clicks
- ctr
- cpc
- total_spend (TO BE ADDED)
```

#### Table 5: `marketing_channels`
```sql
- channel_id (PK)
- channel_name
- channel_type (paid_social, paid_search, display, video, ooh)
- industry_benchmark_ctr
- industry_benchmark_cpc
```

### Data Pipeline Architecture

```
Source Data (Excel Files)
    ↓
ETL Process (Python/Pandas)
    ↓
Data Validation & Cleaning
    ↓
PostgreSQL Database
    ↓
    ├→ Power BI / Tableau (Dashboards)
    ├→ Python ML Models (Forecasting)
    └→ API Layer (Chatbot Integration)
```

### ETL Considerations
1. **Data Cleaning**: Handle "- NA -", NaN, and inconsistent date formats
2. **Deduplication**: Ensure no duplicate monthly records
3. **Validation**: Check for logical inconsistencies (e.g., accepted > offered)
4. **Incremental Loads**: Only update changed/new data
5. **Audit Trail**: Track when data was loaded and from which file

---

## 8. FORECASTING MODEL APPROACH

### Recommended Models by Use Case

#### Use Case 1: Anticipated Cohort Size Prediction
**Model**: ARIMA or Prophet (time-series)
**Features**: 
- Historical cohort sizes
- Month of year (seasonality)
- Program type
- Marketing spend (when available)

#### Use Case 2: Inquiry-to-Application Conversion
**Model**: Logistic Regression or Random Forest
**Features**:
- Program characteristics
- Marketing channel mix
- Historical conversion rates
- Seasonal factors

#### Use Case 3: Marketing Channel Effectiveness
**Model**: Multi-touch Attribution Model
**Features**:
- Channel impressions/clicks
- Spend by channel
- Time lag between campaign and application
- Program-specific response rates

### Validation Strategy
- **Train/Test Split**: 80/20 (use most recent data for testing)
- **Cross-Validation**: Time-series cross-validation (respect temporal order)
- **Metrics**: MAPE (Mean Absolute Percentage Error), RMSE
- **Baseline**: Compare against naive forecast (last year's numbers)

---

## 9. DASHBOARD MOCKUP REQUIREMENTS

### Executive Dashboard (High-Level)
**Widgets**:
1. Total Anticipated Cohort Size (all programs) - Big Number
2. YoY Growth % - Big Number with trend arrow
3. Funnel Visualization (inquiries → applications → admissions → enrollment)
4. Program Performance Comparison - Bar chart
5. Marketing Channel ROI - Bubble chart (CTR vs CPC vs Spend)
6. Monthly Trend - Line chart (last 12 months)

### Program-Specific Dashboard
**Widgets**:
1. Program Cohort Size Forecast - Line chart with confidence intervals
2. Application Funnel - Sankey diagram
3. Conversion Rates - Gauge charts
4. Marketing Attribution - Stacked bar chart
5. Month-over-Month Change - Table with sparklines

### Marketing Dashboard
**Widgets**:
1. Spend by Channel - Pie chart
2. Channel Performance - Table (CTR, CPC, Clicks, Conversions)
3. Campaign Timeline - Gantt chart
4. ROI by Program - Heatmap
5. Benchmark Comparison - Bullet charts (actual vs industry benchmark)

---

## 10. IMPLEMENTATION TIMELINE (REVISED)

### Phase 1: Data Foundation (Weeks 1-3)
- Week 1: Database schema design & setup
- Week 2: ETL pipeline development (Excel → Database)
- Week 3: Data validation & quality checks

### Phase 2: Dashboard Development (Weeks 4-7)
- Week 4: Executive dashboard (Power BI/Tableau)
- Week 5: Program-specific dashboards
- Week 6: Marketing dashboard
- Week 7: User testing & refinement

### Phase 3: Forecasting Models (Weeks 8-10)
- Week 8: Data preparation & feature engineering
- Week 9: Model development & training
- Week 10: Model validation & integration

### Phase 4: AI Chatbot (Weeks 11-13)
- Week 11: API development (query database)
- Week 12: GPT integration & query templates
- Week 13: Testing & refinement

### Phase 5: Integration & Deployment (Weeks 14-16)
- Week 14: Full system integration
- Week 15: UAT with stakeholders
- Week 16: Deployment & training

**Total Timeline**: 16 weeks (4 months) with 2-3 developers

---

## 11. CRITICAL SUCCESS FACTORS

### Must-Haves
1. ✅ **Accurate Data Pipeline**: No data loss or corruption during ETL
2. ⚠️ **Marketing Spend Data**: Essential for ROI analysis (currently missing)
3. ✅ **Real-Time Updates**: Monthly data refresh process
4. ✅ **User-Friendly Dashboards**: Non-technical users must be able to navigate
5. ✅ **Reliable Forecasts**: ±10% accuracy for cohort size predictions

### Nice-to-Haves
- Automated email reports
- Mobile-responsive dashboards
- What-if scenario planning tool
- Integration with CRM systems
- Predictive alerts (e.g., "MBA applications trending below target")

---

## 12. RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Marketing spend data not available | High | Build dashboard without ROI initially; add later when data arrives |
| Limited historical data for new programs | Medium | Use ensemble models; weight predictions toward similar programs |
| Data quality issues in source files | High | Implement robust validation; flag anomalies for manual review |
| Stakeholder scope creep | Medium | Stick to 10-15 chatbot queries; document future enhancements |
| Forecast accuracy concerns | High | Set realistic expectations; show confidence intervals; compare to baseline |

---

## CONCLUSION

The available data is **comprehensive and well-structured** for building Edulytix. The admissions funnel data is complete and consistent, enabling robust dashboards and forecasting. The main gap is **marketing spend data**, which is critical for ROI analysis but can be added later without blocking the project.

**Recommended Next Steps**:
1. Confirm database technology (PostgreSQL recommended)
2. Request marketing spend data from Brooke Perry/Ologie
3. Set up development environment
4. Begin ETL pipeline development
5. Schedule weekly check-ins with stakeholders

This project is **highly feasible** within the 4-6 month timeline with a 2-3 person team.
