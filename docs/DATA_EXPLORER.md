# Data Explorer

[← Back to Documentation](README.md)

---

## Overview

The Data Explorer provides professional data exploration with advanced filtering and export capabilities, organized into logical categories for better user experience.

## Features

### Organized Table Categories

#### Marketing Tables
- **Spend**: Individual channel spend by month (marketing_spend)
- **Totals**: Program-level aggregated totals (marketing_spend_totals)
- **Notes**: Marketing strategy notes (incremental_notes)
- **Processing Logs**: ETL processing metadata (marketing_data)

#### Core Data Tables
- **Admissions**: Main admissions funnel data (admissions_metrics)
- **Programs**: Program definitions and mapping (programs)
- **Metadata**: System metadata and timestamps (metadata)

#### AI Chat Tables
- **History**: User conversations with AI assistant (chat_history)
- **Feedback**: User ratings and feedback (chat_feedback)
- **Metrics**: AI performance metrics (chat_metrics)

#### System Tables
- **Users**: User authentication and profiles (users)
- **Predictions**: ML forecasting results (model_predictions)

### Advanced Filtering
- **Column Selection**: Multi-select columns to display
- **Row Limits**: 10, 25, 50, 100, 500, All
- **Sort Options**: Any column, ascending/descending
- **Text Search**: Filter across all columns
- **Real-time Updates**: Instant filtering

### Data Analysis
- **Quick Statistics**: Count, mean, std, min, max, quartiles
- **CSV Export**: Download filtered data
- **Interactive Display**: Pagination support
- **Data Availability**: Clear indicators

## How to Use

1. **Select Category**: Click main tab for desired category (Marketing, Core Data, AI Chat, System)
2. **Select Table**: Click sub-tab for specific table within category
3. **Read Description**: Understand table purpose and structure
4. **Configure Filters**:
   - Select columns to display
   - Set row limit
   - Choose sort column and direction
   - Enter search text
5. **View Data**: Interactive table with pagination
6. **Export**: Download as CSV for analysis

## Navigation Structure

The Data Explorer uses a two-level navigation system:
- **Level 1**: Category tabs (Marketing Tables, Core Data Tables, etc.)
- **Level 2**: Table sub-tabs within each category

This organization reduces cognitive load and makes it easier to find related data.

## Tips

- Start with the appropriate category for your analysis needs
- Use column selection to focus on relevant data
- Text search works across all columns
- Export filtered data for offline analysis
- Review table descriptions for context
- Categories group related tables for logical exploration

---

[← Back to Documentation](README.md)
