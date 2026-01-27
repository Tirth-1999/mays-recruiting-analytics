# Tasks: SQLite to Supabase Migration

## Overview

Complete task breakdown for migrating all 8 Edulytix pages from SQLite to Supabase PostgreSQL.

**Scope**: 15 tables, 200+ queries, 8 pages, 6 migration scripts, 2 ETL pipelines

---

## Phase 1: Supabase Setup & Configuration (15 min)

- [ ] 1.1 Create Supabase account and project
  - [ ] 1.1.1 Sign up at supabase.com
  - [ ] 1.1.2 Create new project named "mays-analytics"
  - [ ] 1.1.3 Generate strong database password and save securely
  - [ ] 1.1.4 Select region closest to users
  - [ ] 1.1.5 Wait for project initialization (2-3 minutes)

- [ ] 1.2 Run schema migration in Supabase SQL Editor
  - [ ] 1.2.1 Open Supabase dashboard → SQL Editor
  - [ ] 1.2.2 Create new query
  - [ ] 1.2.3 Copy entire contents of `supabase_schema.sql`
  - [ ] 1.2.4 Paste into SQL Editor
  - [ ] 1.2.5 Click "Run" and verify "Success. No rows returned"

- [ ] 1.3 Verify all tables and indexes created
  - [ ] 1.3.1 Go to Table Editor in Supabase dashboard
  - [ ] 1.3.2 Verify 15 tables exist: admissions_metrics, programs, marketing_spend, marketing_spend_totals, users, chat_history, chat_feedback, chat_metrics, model_predictions, metadata, marketing_campaigns, inquiry_sources
  - [ ] 1.3.3 Check each table has correct columns
  - [ ] 1.3.4 Verify indexes created (check Database → Indexes)

- [ ] 1.4 Get connection string and save securely
  - [ ] 1.4.1 Go to Project Settings → Database
  - [ ] 1.4.2 Scroll to "Connection string" section
  - [ ] 1.4.3 Select "URI" tab
  - [ ] 1.4.4 Copy connection string
  - [ ] 1.4.5 Replace `[YOUR-PASSWORD]` with actual password
  - [ ] 1.4.6 Save in password manager (DO NOT commit to Git)

- [ ] 1.5 Add SUPABASE_URL to local secrets for testing
  - [ ] 1.5.1 Open `.streamlit/secrets.toml`
  - [ ] 1.5.2 Add line: `SUPABASE_URL = "postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres"`
  - [ ] 1.5.3 Verify file is in `.gitignore`
  - [ ] 1.5.4 Save file

---

## Phase 2: Core Database Layer Updates (30 min)

- [ ] 2.1 Install psycopg2-binary dependency
  - [ ] 2.1.1 Run `pip install psycopg2-binary`
  - [ ] 2.1.2 Run `pip freeze > requirements.txt`
  - [ ] 2.1.3 Verify `psycopg2-binary==2.9.9` in requirements.txt

- [ ] 2.2 Update `utils/database.py` with dual connection support
  - [ ] 2.2.1 Add imports: `import psycopg2`, `from contextlib import contextmanager`, `from typing import Union`
  - [ ] 2.2.2 Update `get_connection()` function with PostgreSQL support and SQLite fallback
  - [ ] 2.2.3 Add `get_db_connection()` context manager
  - [ ] 2.2.4 Add `get_db_type()` helper function
  - [ ] 2.2.5 Add `check_database_health()` function
  - [ ] 2.2.6 Test locally with SQLite (remove SUPABASE_URL temporarily)
  - [ ] 2.2.7 Test locally with Supabase (add SUPABASE_URL back)

---

## Phase 3: Page-by-Page Query Updates (2-3 hours)

### 3.1 Home Dashboard (`modules/home_dashboard.py`)

- [ ] 3.1.1 Identify all SQL queries in file
  - Queries: Load admissions metrics, load programs
  - Count: 2 queries

- [ ] 3.1.2 Replace `?` with `%s` in all queries
  - Line ~40: `WHERE cohort_year = ?` → `WHERE cohort_year = %s`

- [ ] 3.1.3 Update datetime functions (if any)
  - No datetime functions in this file

- [ ] 3.1.4 Test Home Dashboard locally
  - [ ] Run app: `streamlit run main_app.py`
  - [ ] Navigate to Home Dashboard
  - [ ] Select different cohorts (2026, 2027, 2028)
  - [ ] Select different programs
  - [ ] Verify metrics display correctly
  - [ ] Check for errors in console

### 3.2 Executive Deep Dive (`modules/executive_deep_dive.py`)

- [ ] 3.2.1 Identify all SQL queries in file
  - Queries: Load cohort data with date filtering, load programs
  - Count: 2-3 queries

- [ ] 3.2.2 Replace `?` with `%s` in all queries
  - Search for all `?` placeholders
  - Replace with `%s`

- [ ] 3.2.3 Update datetime functions (if any)
  - Check for `datetime('now')` → `NOW()`
  - Check for `CURRENT_TIMESTAMP` → `NOW()`

- [ ] 3.2.4 Test Executive Deep Dive locally
  - [ ] Navigate to Executive Deep Dive page
  - [ ] Test all 4 tabs: Overview, Program Deep Dive, Cohort Trends, Funnel Analysis
  - [ ] Select different cohorts and programs
  - [ ] Verify charts render correctly
  - [ ] Check for errors in console

### 3.3 Comparison Tool (`modules/comparison_tool.py`)

- [ ] 3.3.1 Identify all SQL queries in file
  - Queries: YoY comparison with multiple cohorts
  - Count: 2-3 queries

- [ ] 3.3.2 Replace `?` with `%s` in all queries
  - Search for `IN (?, ?)` patterns
  - Replace with `IN (%s, %s)`

- [ ] 3.3.3 Update datetime functions (if any)
  - Check for datetime functions

- [ ] 3.3.4 Test Comparison Tool locally
  - [ ] Navigate to Comparison Tool page
  - [ ] Select two different cohorts
  - [ ] Select different programs
  - [ ] Verify comparison metrics display
  - [ ] Verify charts render correctly
  - [ ] Check for errors in console

### 3.4 Marketing Analysis (`modules/marketing_analysis.py`)

- [ ] 3.4.1 Identify all SQL queries in file
  - Queries: Marketing spend, totals, admissions metrics, ROI calculations
  - Count: 10+ queries (MOST COMPLEX PAGE)

- [ ] 3.4.2 Replace `?` with `%s` in all queries
  - Search for all `?` placeholders
  - Pay special attention to JOIN queries
  - Update aggregation queries

- [ ] 3.4.3 Update datetime functions (if any)
  - Check for datetime functions in date filtering

- [ ] 3.4.4 Test Marketing Analysis locally
  - [ ] Navigate to Marketing Analysis page
  - [ ] Test all 5 tabs: Overview, Channel Performance, ROI Analysis, Timing Analysis, Budget Allocation
  - [ ] Apply different filters (program, channel, date range)
  - [ ] Verify spend data displays correctly
  - [ ] Verify ROI calculations are accurate
  - [ ] Check for errors in console

### 3.5 Predictive Analytics (`modules/predictive_analytics.py`)

- [ ] 3.5.1 Identify all SQL queries in file
  - Queries: Model predictions storage and retrieval
  - Count: 5+ queries

- [ ] 3.5.2 Replace `?` with `%s` in all queries
  - Update INSERT queries for predictions
  - Update SELECT queries for forecast retrieval

- [ ] 3.5.3 Update datetime functions
  - Check for `datetime('now')` in prediction timestamps
  - Replace with `NOW()`

- [ ] 3.5.4 Test Predictive Analytics locally
  - [ ] Navigate to Predictive Analytics page
  - [ ] Test all 5 tabs: Time Series Forecasting, Channel Optimization, Timing Analysis, Budget Allocation, Model Performance
  - [ ] Generate new predictions
  - [ ] Verify predictions are stored in database
  - [ ] Verify predictions display correctly
  - [ ] Check for errors in console

### 3.6 Data Explorer (`modules/database.py`)

- [ ] 3.6.1 Identify all SQL queries in file
  - Queries: Dynamic table queries, schema queries, search queries
  - Count: 10+ queries (DYNAMIC QUERIES)

- [ ] 3.6.2 Replace `?` with `%s` in all queries
  - Update dynamic query generation
  - Update search queries with LIKE patterns

- [ ] 3.6.3 Update PRAGMA queries for PostgreSQL
  - Replace `PRAGMA table_info([table])` with PostgreSQL equivalent:
    ```sql
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = %s
    ```

- [ ] 3.6.4 Test Data Explorer locally
  - [ ] Navigate to Data Explorer page
  - [ ] Test viewing all 15 tables
  - [ ] Test search functionality
  - [ ] Test filtering and sorting
  - [ ] Verify table statistics display
  - [ ] Check for errors in console

### 3.7 AI Chat (`modules/ai_chat.py`)

- [ ] 3.7.1 Identify all SQL queries in file
  - Queries: Chat history CRUD, feedback, search, export
  - Count: 15+ queries (CRITICAL FOR UX)

- [ ] 3.7.2 Replace `?` with `%s` in all queries
  - Update INSERT queries for chat messages
  - Update SELECT queries for conversation retrieval
  - Update feedback queries
  - Update search queries

- [ ] 3.7.3 Update datetime functions
  - Replace `datetime('now')` with `NOW()` in timestamp columns
  - Replace `CURRENT_TIMESTAMP` with `NOW()`

- [ ] 3.7.4 Test AI Chat locally
  - [ ] Navigate to AI Chat page
  - [ ] Send test messages
  - [ ] Verify messages are saved to database
  - [ ] Verify conversation history displays
  - [ ] Test search functionality
  - [ ] Test feedback (thumbs up/down)
  - [ ] Test export functionality
  - [ ] Check for errors in console

### 3.8 Authentication (`utils/auth.py`)

- [ ] 3.8.1 Identify all SQL queries in file
  - Queries: User CRUD, role management, login tracking
  - Count: 8+ queries

- [ ] 3.8.2 Replace `?` with `%s` in all queries
  - Update user creation queries
  - Update user lookup queries
  - Update last_login update queries

- [ ] 3.8.3 Update datetime functions
  - Replace `datetime('now')` with `NOW()` in created_at, last_login
  - Replace `CURRENT_TIMESTAMP` with `NOW()`

- [ ] 3.8.4 Test Authentication locally
  - [ ] Test Google OAuth login
  - [ ] Verify user is created in database
  - [ ] Check Supabase dashboard for new user
  - [ ] Test logout
  - [ ] Test re-login (should update last_login)
  - [ ] Check for errors in console

---

## Phase 4: ETL Pipeline Updates (30 min)

### 4.1 Admissions Data ETL (`etl_pipeline.py`)

- [ ] 4.1.1 Update table creation queries
  - Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`
  - Replace `CURRENT_TIMESTAMP` with `NOW()`

- [ ] 4.1.2 Update INSERT OR REPLACE queries
  - PostgreSQL equivalent: `INSERT ... ON CONFLICT ... DO UPDATE`
  - Example:
    ```sql
    INSERT INTO admissions_metrics (report_date, program, cohort_year, metric_name, metric_value)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (report_date, program, cohort_year, metric_name)
    DO UPDATE SET metric_value = EXCLUDED.metric_value
    ```

- [ ] 4.1.3 Replace `?` with `%s` in all queries

- [ ] 4.1.4 Update metadata queries
  - Replace `datetime('now')` with `NOW()`

- [ ] 4.1.5 Test ETL pipeline
  - [ ] Run `python etl_pipeline.py`
  - [ ] Verify data loads successfully
  - [ ] Check Supabase dashboard for data
  - [ ] Verify no duplicate records
  - [ ] Check for errors

### 4.2 Marketing Data ETL (`marketing_etl.py`)

- [ ] 4.2.1 Update table creation queries
  - Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`
  - Replace `CURRENT_TIMESTAMP` with `NOW()`

- [ ] 4.2.2 Update INSERT OR REPLACE queries
  - Convert to PostgreSQL ON CONFLICT syntax

- [ ] 4.2.3 Replace `?` with `%s` in all queries

- [ ] 4.2.4 Update metadata queries
  - Replace `datetime('now')` with `NOW()`

- [ ] 4.2.5 Test marketing ETL
  - [ ] Run `python marketing_etl.py`
  - [ ] Verify marketing data loads
  - [ ] Check Supabase dashboard for data
  - [ ] Verify totals match
  - [ ] Check for errors

---

## Phase 5: Migration Scripts Updates (30 min)

- [ ] 5.1 Update `migrations/add_users_table.py`
  - [ ] 5.1.1 Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`
  - [ ] 5.1.2 Replace `CURRENT_TIMESTAMP` with `NOW()`
  - [ ] 5.1.3 Test migration script locally

- [ ] 5.2 Update `migrations/add_user_roles.py`
  - [ ] 5.2.1 Replace `?` with `%s` in queries
  - [ ] 5.2.2 Test migration script locally

- [ ] 5.3 Update `migrations/add_chat_history_table.py`
  - [ ] 5.3.1 Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`
  - [ ] 5.3.2 Replace `CURRENT_TIMESTAMP` with `NOW()`
  - [ ] 5.3.3 Test migration script locally

- [ ] 5.4 Update `migrations/add_chat_indexes.py`
  - [ ] 5.4.1 Verify index syntax compatible with PostgreSQL
  - [ ] 5.4.2 Test migration script locally

- [ ] 5.5 Update `migrations/add_feedback_table.py`
  - [ ] 5.5.1 Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`
  - [ ] 5.5.2 Replace `CURRENT_TIMESTAMP` with `NOW()`
  - [ ] 5.5.3 Test migration script locally

- [ ] 5.6 Update `migrations/add_model_predictions_table.py`
  - [ ] 5.6.1 Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`
  - [ ] 5.6.2 Replace `CURRENT_TIMESTAMP` with `NOW()`
  - [ ] 5.6.3 Test migration script locally

---

## Phase 6: Comprehensive Local Testing (1 hour)

### 6.1 Test with SQLite (Default Fallback)

- [ ] 6.1.1 Remove SUPABASE_URL from `.streamlit/secrets.toml`
- [ ] 6.1.2 Run app: `streamlit run main_app.py`
- [ ] 6.1.3 Verify app connects to SQLite
- [ ] 6.1.4 Test all 8 pages work correctly
- [ ] 6.1.5 Verify no errors in console

### 6.2 Test with Supabase (Production Simulation)

- [ ] 6.2.1 Add SUPABASE_URL back to `.streamlit/secrets.toml`
- [ ] 6.2.2 Run app: `streamlit run main_app.py`
- [ ] 6.2.3 Verify app connects to Supabase
- [ ] 6.2.4 Test all 8 pages systematically:

**Home Dashboard**:
- [ ] 6.2.4.1 Select different cohorts
- [ ] 6.2.4.2 Select different programs
- [ ] 6.2.4.3 Verify metrics display
- [ ] 6.2.4.4 Verify charts render

**Executive Deep Dive**:
- [ ] 6.2.4.5 Test all 4 tabs
- [ ] 6.2.4.6 Verify data loads
- [ ] 6.2.4.7 Verify charts render

**Comparison Tool**:
- [ ] 6.2.4.8 Compare two cohorts
- [ ] 6.2.4.9 Verify metrics display
- [ ] 6.2.4.10 Verify charts render

**Marketing Analysis**:
- [ ] 6.2.4.11 Test all 5 tabs
- [ ] 6.2.4.12 Verify spend data
- [ ] 6.2.4.13 Verify ROI calculations

**Predictive Analytics**:
- [ ] 6.2.4.14 Test all 5 tabs
- [ ] 6.2.4.15 Generate predictions
- [ ] 6.2.4.16 Verify predictions saved

**Data Explorer**:
- [ ] 6.2.4.17 View all tables
- [ ] 6.2.4.18 Test search
- [ ] 6.2.4.19 Test filtering

**AI Chat**:
- [ ] 6.2.4.20 Send test messages
- [ ] 6.2.4.21 Verify history persists
- [ ] 6.2.4.22 Test feedback
- [ ] 6.2.4.23 Test search

**Authentication**:
- [ ] 6.2.4.24 Test login
- [ ] 6.2.4.25 Verify user in Supabase
- [ ] 6.2.4.26 Test logout

- [ ] 6.2.5 Check Supabase dashboard
  - [ ] 6.2.5.1 Verify user created
  - [ ] 6.2.5.2 Verify chat messages saved
  - [ ] 6.2.5.3 Verify predictions saved
  - [ ] 6.2.5.4 Check table row counts

### 6.3 Performance Testing

- [ ] 6.3.1 Measure query response times
  - [ ] Use browser DevTools Network tab
  - [ ] Record response times for each page
  - [ ] Verify 95% < 500ms

- [ ] 6.3.2 Test with multiple tabs open
  - [ ] Open 5+ browser tabs
  - [ ] Navigate different pages simultaneously
  - [ ] Verify no connection errors

---

## Phase 7: GitHub Actions Keep-Alive Setup (15 min)

- [ ] 7.1 Create GitHub Actions workflow file
  - [ ] 7.1.1 Create `.github/workflows/keep-supabase-alive.yml`
  - [ ] 7.1.2 Add workflow content (see design doc)
  - [ ] 7.1.3 Configure cron schedule: `0 2 */5 * *` (every 5 days at 2 AM)
  - [ ] 7.1.4 Add manual trigger option: `workflow_dispatch`

- [ ] 7.2 Add GitHub secrets
  - [ ] 7.2.1 Go to GitHub repo → Settings → Secrets and variables → Actions
  - [ ] 7.2.2 Add `SUPABASE_URL` (project URL from Supabase dashboard)
  - [ ] 7.2.3 Add `SUPABASE_ANON_KEY` (from Supabase dashboard → Settings → API)

- [ ] 7.3 Test workflow
  - [ ] 7.3.1 Go to Actions tab in GitHub
  - [ ] 7.3.2 Select "Keep Supabase Alive" workflow
  - [ ] 7.3.3 Click "Run workflow" → "Run workflow"
  - [ ] 7.3.4 Wait for completion (should be < 1 minute)
  - [ ] 7.3.5 Verify successful execution (green checkmark)
  - [ ] 7.3.6 Check Supabase logs for ping

---

## Phase 8: Production Deployment (30 min)

- [ ] 8.1 Add secrets to Streamlit Cloud
  - [ ] 8.1.1 Go to app.streamlit.io
  - [ ] 8.1.2 Select your app
  - [ ] 8.1.3 Click Settings (⚙️) → Secrets
  - [ ] 8.1.4 Add: `SUPABASE_URL = "postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres"`
  - [ ] 8.1.5 Click "Save"

- [ ] 8.2 Deploy to production
  - [ ] 8.2.1 Commit all changes: `git add -A`
  - [ ] 8.2.2 Create commit: `git commit -m "feat: Migrate to Supabase PostgreSQL"`
  - [ ] 8.2.3 Push to GitHub: `git push origin main`
  - [ ] 8.2.4 Wait for Streamlit Cloud rebuild (2-5 minutes)
  - [ ] 8.2.5 Monitor deployment logs for errors

- [ ] 8.3 Verify production connection
  - [ ] 8.3.1 Open production app URL
  - [ ] 8.3.2 Check browser console for connection messages
  - [ ] 8.3.3 Verify no error messages
  - [ ] 8.3.4 Check database type (should be PostgreSQL)

- [ ] 8.4 Test production functionality
  - [ ] 8.4.1 Test user authentication
    - [ ] Sign in with Google
    - [ ] Verify user appears in Supabase dashboard
    - [ ] Check user_id, email, name, role

  - [ ] 8.4.2 Test all 8 pages (same as local testing)
    - [ ] Home Dashboard
    - [ ] Executive Deep Dive
    - [ ] Comparison Tool
    - [ ] Marketing Analysis
    - [ ] Predictive Analytics
    - [ ] Data Explorer
    - [ ] AI Chat (CRITICAL - test chat history persistence)
    - [ ] Documentation & Help

  - [ ] 8.4.3 Test chat history persistence
    - [ ] Send test message in AI Chat
    - [ ] Close browser
    - [ ] Reopen production app
    - [ ] Verify chat history still visible
    - [ ] Check Supabase dashboard for chat_history records

  - [ ] 8.4.4 Test across multiple sessions
    - [ ] Open app in incognito window
    - [ ] Sign in as different user
    - [ ] Verify separate chat histories
    - [ ] Verify data isolation

---

## Phase 9: Data Migration (Optional - 30 min)

- [ ] 9.1* Export data from local SQLite
  - [ ] 9.1.1* Create export script (see design doc)
  - [ ] 9.1.2* Export all tables to CSV
  - [ ] 9.1.3* Verify export completeness
  - [ ] 9.1.4* Check for data integrity

- [ ] 9.2* Import data to Supabase
  - [ ] 9.2.1* Use Supabase Table Editor → Import CSV
  - [ ] 9.2.2* Or use direct SQL insert script
  - [ ] 9.2.3* Verify row counts match
  - [ ] 9.2.4* Verify data integrity (spot check records)

---

## Phase 10: Monitoring & Validation (30 min)

- [ ] 10.1 Set up monitoring
  - [ ] 10.1.1 Monitor Supabase dashboard for usage
    - [ ] Check Database → Usage
    - [ ] Verify storage < 500MB
    - [ ] Verify bandwidth < 5GB/month

  - [ ] 10.1.2 Check for errors in logs
    - [ ] Supabase → Logs → Postgres Logs
    - [ ] Look for connection errors
    - [ ] Look for query errors

  - [ ] 10.1.3 Verify GitHub Actions runs successfully
    - [ ] Check Actions tab
    - [ ] Verify keep-alive runs every 5 days
    - [ ] Set up email notifications for failures

- [ ] 10.2 Performance validation
  - [ ] 10.2.1 Check query response times in production
    - [ ] Use browser DevTools
    - [ ] Record response times for each page
    - [ ] Verify 95% < 500ms

  - [ ] 10.2.2 Monitor for slow queries
    - [ ] Supabase → Database → Query Performance
    - [ ] Identify slow queries (> 1s)
    - [ ] Optimize if needed

  - [ ] 10.2.3 Verify no performance degradation
    - [ ] Compare with SQLite baseline
    - [ ] Check page load times
    - [ ] Check user experience

- [ ] 10.3 User validation
  - [ ] 10.3.1 Verify production users are tracked
    - [ ] Check Supabase → Table Editor → users
    - [ ] Verify new users appear
    - [ ] Verify last_login updates

  - [ ] 10.3.2 Check user login history
    - [ ] Query users table
    - [ ] Check created_at and last_login timestamps
    - [ ] Verify role assignments

  - [ ] 10.3.3 Verify chat history persists
    - [ ] Check chat_history table
    - [ ] Verify messages from multiple users
    - [ ] Verify conversation_id grouping

  - [ ] 10.3.4 Test across multiple sessions
    - [ ] Have multiple users test simultaneously
    - [ ] Verify data isolation
    - [ ] Verify no conflicts

---

## Success Criteria

### Phase Completion Checklist

**Phase 1 - Setup**: ✅
- [ ] Supabase project created
- [ ] All 15 tables visible in dashboard
- [ ] Connection string obtained

**Phase 2 - Core Layer**: ✅
- [ ] `get_connection()` works with both databases
- [ ] Fallback to SQLite works
- [ ] No import errors

**Phase 3 - Query Updates**: ✅
- [ ] All 200+ queries updated
- [ ] All 8 pages work with PostgreSQL
- [ ] No syntax errors

**Phase 4 - ETL**: ✅
- [ ] Both ETL pipelines work
- [ ] Data loads successfully
- [ ] No duplicate records

**Phase 5 - Migrations**: ✅
- [ ] All 6 migration scripts updated
- [ ] Scripts run successfully
- [ ] Tables created correctly

**Phase 6 - Local Testing**: ✅
- [ ] App works with SQLite
- [ ] App works with Supabase
- [ ] All features work correctly

**Phase 7 - Keep-Alive**: ✅
- [ ] GitHub Actions workflow created
- [ ] Workflow runs successfully
- [ ] Supabase stays active

**Phase 8 - Production**: ✅
- [ ] Production connects to Supabase
- [ ] New users appear in dashboard
- [ ] No errors in production

**Phase 9 - Data Migration**: ✅ (Optional)
- [ ] Data exported from SQLite
- [ ] Data imported to Supabase
- [ ] Data integrity verified

**Phase 10 - Monitoring**: ✅
- [ ] Usage within free tier
- [ ] Performance meets requirements
- [ ] Users tracked successfully

---

## Rollback Checkpoints

**Checkpoint 1**: After Phase 2
- Can rollback by removing psycopg2 import
- SQLite still works

**Checkpoint 2**: After Phase 6
- Can rollback by not deploying to production
- Local changes can be reverted

**Checkpoint 3**: After Phase 8
- Can rollback by removing SUPABASE_URL from secrets
- App falls back to SQLite automatically

---

## Time Estimates

| Phase | Estimated Time | Actual Time |
|-------|---------------|-------------|
| 1. Setup | 15 min | |
| 2. Core Layer | 30 min | |
| 3. Query Updates | 2-3 hours | |
| 4. ETL | 30 min | |
| 5. Migrations | 30 min | |
| 6. Local Testing | 1 hour | |
| 7. Keep-Alive | 15 min | |
| 8. Production | 30 min | |
| 9. Data Migration | 30 min (optional) | |
| 10. Monitoring | 30 min | |
| **Total** | **6-8 hours** | |

---

**Document Version**: 2.0  
**Created**: January 26, 2026  
**Status**: Ready for Execution  
**Pages Covered**: 8/8 (100%)  
**Tables Covered**: 15/15 (100%)  
**Queries to Update**: 200+  
**Migration Scripts**: 6  
**ETL Pipelines**: 2
