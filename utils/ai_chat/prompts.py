"""
Prompt templates for AI chatbot assistant
"""

DATA_QUERY_PROMPT = """SQL expert for Mays Analytics Platform.

Schema: {schema_context}

Question: {user_question}
Context: {conversation_history}

Generate SQLite query. Return ONLY SQL, no markdown/explanations.

Rules:
- Use proper table/column names
- WHERE clauses for filtering
- Dates as 'YYYY-MM-DD'
- LIMIT 100 max
- Aggregations: SUM, AVG, COUNT, MIN, MAX with GROUP BY
- HAVING for filtered aggregates
- Use full program names (Flex Online MBA, Flex Online MS Accounting, etc.)
- ORDER BY for readability
- JOINs for multi-table queries
- Growth: ((new-old)/old)*100

SQL:"""

NAVIGATION_PROMPT = """Guide for Mays Analytics Platform.

Pages: {platform_knowledge}

Question: {user_question}

Recommend best page with navigation steps (under 200 words).

Format:
**Page**: [Name]
**Why**: [One sentence]
**Steps**:
1. [Action]
2. [Action]
3. [Action]
**Filters**: [List]
**Results**: [Brief description]"""

HELP_PROMPT = """Assistant for Mays Analytics Platform.

Info: {platform_knowledge}

Question: {user_question}

Provide clear explanation (under 150 words). Be practical and actionable."""

CONVERSATIONAL_PROMPT = """Friendly AI for Mays Analytics Platform.

Context: {conversation_history}

Message: {user_question}

Respond naturally (under 100 words). Guide data questions to be specific. Keep brief and friendly."""

# Schema context template for data queries (compressed)
SCHEMA_CONTEXT_TEMPLATE = """Tables:
1. admissions_metrics: program(TEXT), cohort_year(INT), metric_name(TEXT), metric_value(REAL), report_date(TEXT)
   Programs: Flex Online MBA, Flex Online MS Accounting, Flex Online MS Human Resource Management, 
             Flex Online MS Management Information Systems, Flex Online MS Marketing, 
             Flex Online MS Entrepreneurial Leadership, Flex Online AI in Business Program
   Metrics: inquiries_received, total_applications, admits, enrolled, deposits, confirmed
2. marketing_spend: program(TEXT), channel(TEXT), amount(REAL), spend_date(TEXT), fiscal_year(TEXT)
   Programs: Same as admissions_metrics, plus "General Awareness"
3. programs: program_code(TEXT), program_name(TEXT), is_active(INT)
   Maps short codes (MBA, MS ACCT, etc.) to full names (Flex Online MBA, etc.)
4. model_predictions: program_code(TEXT), cohort_year(INT), metric_name(TEXT), predicted_value(REAL), confidence_lower(REAL), confidence_upper(REAL)

Notes:
- Metrics are lowercase_with_underscores
- "applications"→'total_applications', "inquiries"→'inquiries_received'
- Use ORDER BY report_date DESC for latest data
- Always use full program names in WHERE clauses (e.g., WHERE program = 'Flex Online MBA')
- User may use short codes (MBA, MS ACCT) - convert to full names using programs table or mapping
"""

# Platform knowledge for navigation queries
PLATFORM_KNOWLEDGE = """
**Platform Pages:**

Page 1: Executive Dashboard
- Purpose: High-level overview of all programs
- Best For: Quick snapshot, executive summary, overall trends
- Filters: Cohort year
- Metrics: Total inquiries, applications, admits, enrolled
- Use When: Need big picture view of all programs

Page 2: Director's Deep Dive
- Purpose: Detailed program-specific analysis
- Best For: Deep analysis of single program, trend identification
- Filters: Program, cohort year, date range
- Metrics: Program funnel, conversion rates, time-series trends
- Use When: Analyzing specific program performance

Page 3: Comparison Tool
- Purpose: Year-over-year and program comparisons
- Best For: Comparative analysis, identifying growth/decline
- Filters: Two cohorts or two programs
- Metrics: Percentage changes, variance, growth rates
- Use When: Comparing performance across time or programs

Page 4: Marketing Analysis
- Purpose: Marketing spend and ROI analysis
- Best For: Marketing effectiveness, budget decisions
- Filters: Program, fiscal year, channel
- Metrics: Spend by channel, cost per inquiry/application, ROI
- Use When: Evaluating marketing effectiveness

Page 5: Data Explorer
- Purpose: Raw data access with flexible filtering
- Best For: Custom analysis, data export
- Filters: All dimensions
- Metrics: All available metrics in tables
- Use When: Need raw data or custom analysis

Page 6: Predictive Analytics
- Purpose: ML-powered forecasting
- Best For: Future planning, trend prediction
- Filters: Program, forecast horizon
- Metrics: Predicted enrollments, confidence intervals
- Use When: Planning for future or forecasting

**Common Workflows:**

Workflow 1: Create Program Performance Report
- Pages: Director's Deep Dive → Data Explorer
- Steps: Select program → Choose cohort → Review metrics → Export data
- Best For: Comprehensive program analysis

Workflow 2: Analyze Marketing ROI
- Pages: Marketing Analysis
- Steps: Select program → Choose fiscal year → Review channels → Calculate ROI
- Best For: Marketing effectiveness evaluation

Workflow 3: Year-over-Year Comparison
- Pages: Comparison Tool
- Steps: Select two cohorts → Choose metrics → Review changes → Export
- Best For: Trend analysis and growth tracking

Workflow 4: Forecast Enrollments
- Pages: Predictive Analytics
- Steps: Select program → Choose horizon → Review predictions → Compare with history
- Best For: Future planning and projections
"""
