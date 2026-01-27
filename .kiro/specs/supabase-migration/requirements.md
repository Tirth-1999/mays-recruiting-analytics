# Requirements: SQLite to Supabase Migration

## Executive Summary

Migrate Edulytix platform from local SQLite (`edulytix.db`) to cloud Supabase PostgreSQL to enable:
- **Persistent data** across all 8 platform pages
- **Unified database** for local and production environments  
- **Real-time user tracking** and analytics
- **Zero data loss** on deployments

**Scope**: 15 database tables, 8 platform pages, 200+ SQL queries, 6 migration scripts

---

## Problem Statement

### Current Architecture Issues

**Separate Databases Per Environment:**
```
Local Dev:     edulytix.db (on developer machine)
Production:    edulytix.db (on Streamlit Cloud container)
Result:        Completely isolated, no shared data
```

**Data Loss on Every Deployment:**
- Streamlit Cloud creates fresh container on each deploy
- Old `edulytix.db` file is deleted
- All user data, chat history, preferences lost
- Users must re-authenticate

**No Production Visibility:**
- Cannot see production users from local environment
- No analytics on real usage patterns
- Cannot debug production issues
- No way to track adoption metrics

### Impact by Platform Page

#### 1. Home Dashboard (`modules/home_dashboard.py`)
**Database Tables Used**: `admissions_metrics`, `programs`
**Queries**: 2 SELECT queries with cohort/program filters
**Impact**:
- Cannot track which cohorts/programs users view most
- Lost user filter preferences
- No analytics on dashboard usage patterns

#### 2. Executive Deep Dive (`modules/executive_deep_dive.py`)
**Database Tables Used**: `admissions_metrics`, `programs`
**Queries**: Complex SELECT with date filtering and aggregations
**Impact**:
- Cannot track which metrics executives analyze
- Lost comparison preferences
- No usage analytics for strategic decisions

#### 3. Comparison Tool (`modules/comparison_tool.py`)
**Database Tables Used**: `admissions_metrics`, `programs`
**Queries**: YoY comparison queries with multiple cohorts
**Impact**:
- Lost user comparison preferences
- Cannot track which cohorts are compared most
- No analytics on comparison patterns

#### 4. Marketing Analysis (`modules/marketing_analysis.py`)
**Database Tables Used**: `marketing_spend`, `marketing_spend_totals`, `admissions_metrics`
**Queries**: 10+ complex queries with JOINs, aggregations, ROI calculations
**Impact**:
- Cannot track ROI analysis usage
- Lost channel filter preferences
- No analytics on marketing insights accessed

#### 5. Predictive Analytics (`modules/predictive_analytics.py`)
**Database Tables Used**: `model_predictions`, `admissions_metrics`
**Queries**: ML prediction storage and retrieval
**Impact**:
- **CRITICAL**: All ML predictions lost on rebuild
- Cannot track forecast accuracy over time
- Lost model performance metrics
- No historical prediction data

#### 6. Data Explorer (`modules/database.py`)
**Database Tables Used**: ALL 15 tables (dynamic)
**Queries**: Dynamic queries based on user selection
**Impact**:
- Cannot track which tables users query most
- Lost search preferences
- No analytics on data exploration patterns
- Admin cannot see which users access sensitive tables

#### 7. AI Chat (`modules/ai_chat.py`)
**Database Tables Used**: `chat_history`, `chat_feedback`, `chat_metrics`, `users`
**Queries**: 15+ queries for conversations, feedback, search, export
**Impact**:
- **WORST UX IMPACT**: All chat history lost on rebuild
- Users lose conversation context
- Cannot track chat usage patterns
- Lost feedback ratings and comments
- No analytics on query types or performance

#### 8. Authentication (`utils/auth.py`)
**Database Tables Used**: `users`
**Queries**: User CRUD operations, role management
**Impact**:
- Users must re-authenticate after every deployment
- Lost user roles and permissions
- Cannot track login patterns
- No user adoption metrics


---

## Database Schema Analysis

### Tables Overview (15 Total)

| Table | Rows (Est) | Queries/Page | Critical? | Migration Priority |
|-------|-----------|--------------|-----------|-------------------|
| **admissions_metrics** | 2,037 | 6 pages | ✅ Yes | P0 - Core data |
| **programs** | 7 | 6 pages | ✅ Yes | P0 - Master data |
| **marketing_spend** | 76 | 1 page | ✅ Yes | P0 - Marketing |
| **marketing_spend_totals** | 90 | 1 page | ✅ Yes | P0 - Marketing |
| **users** | Variable | 2 pages | ✅ Yes | P0 - Auth |
| **chat_history** | Variable | 1 page | ✅ Yes | P0 - AI Chat |
| **chat_feedback** | Variable | 1 page | ⚠️ Medium | P1 - Feedback |
| **chat_metrics** | Variable | 1 page | ⚠️ Medium | P1 - Analytics |
| **model_predictions** | Variable | 1 page | ✅ Yes | P0 - ML |
| **metadata** | ~10 | ETL | ⚠️ Medium | P1 - System |
| **marketing_campaigns** | 0 | Future | ❌ No | P2 - Unused |
| **inquiry_sources** | 0 | Future | ❌ No | P2 - Unused |

### Query Patterns by Type

**SELECT Queries**: 180+ across all pages
- Simple filters: `WHERE cohort_year = ?`
- Complex JOINs: Marketing ROI calculations
- Aggregations: `GROUP BY`, `SUM()`, `COUNT()`
- Full table scans: Data Explorer

**INSERT Queries**: 25+ 
- User creation: `INSERT INTO users`
- Chat messages: `INSERT INTO chat_history`
- ML predictions: `INSERT INTO model_predictions`
- ETL data loading: `INSERT OR REPLACE`

**UPDATE Queries**: 10+
- User last_login: `UPDATE users SET last_login = ?`
- Metadata timestamps: `UPDATE metadata`

**DELETE Queries**: 5+
- Chat history cleanup: `DELETE FROM chat_history WHERE user_id = ?`
- User data deletion (GDPR): `DELETE FROM users WHERE user_id = ?`

### SQLite-Specific Features Used

1. **AUTOINCREMENT** (7 tables)
   - Must convert to PostgreSQL `SERIAL`
   
2. **Placeholder `?`** (200+ queries)
   - Must convert to PostgreSQL `%s`

3. **datetime('now')** and **CURRENT_TIMESTAMP** (50+ uses)
   - Must convert to PostgreSQL `NOW()`

4. **INSERT OR REPLACE** (ETL pipelines)
   - PostgreSQL equivalent: `INSERT ... ON CONFLICT ... DO UPDATE`

5. **INSERT OR IGNORE** (program loading)
   - PostgreSQL equivalent: `INSERT ... ON CONFLICT DO NOTHING`

6. **PRAGMA table_info()** (Data Explorer)
   - PostgreSQL equivalent: `information_schema.columns`

7. **sqlite_sequence** table
   - PostgreSQL uses sequences automatically

---

## Functional Requirements

### FR-1: Database Connection Management

**FR-1.1**: Dual Database Support
- System MUST support both SQLite and PostgreSQL connections
- Connection type MUST be automatically detected based on secrets configuration
- System MUST gracefully fallback to SQLite if PostgreSQL unavailable

**FR-1.2**: Environment-Based Configuration
- Production MUST use Supabase PostgreSQL (via `SUPABASE_URL` secret)
- Local development MUST default to SQLite
- Local development MAY optionally connect to Supabase for testing

**FR-1.3**: Connection Pooling
- System MUST reuse database connections efficiently
- System MUST close connections properly after use
- System MUST handle connection timeouts gracefully

**Acceptance Criteria**:
- [ ] `get_connection()` returns PostgreSQL connection when `SUPABASE_URL` present
- [ ] `get_connection()` returns SQLite connection when `SUPABASE_URL` absent
- [ ] Connection failures trigger fallback to SQLite with warning message
- [ ] All connections are properly closed after use

### FR-2: Query Compatibility Across All Pages

**FR-2.1**: Home Dashboard Queries
- All cohort filtering queries MUST work with PostgreSQL
- Program loading queries MUST work with PostgreSQL
- Date range filtering MUST work with PostgreSQL

**FR-2.2**: Executive Deep Dive Queries
- Complex date filtering MUST work with PostgreSQL
- Multi-program aggregations MUST work with PostgreSQL
- Trend analysis queries MUST work with PostgreSQL

**FR-2.3**: Comparison Tool Queries
- YoY comparison queries MUST work with PostgreSQL
- Multi-cohort JOINs MUST work with PostgreSQL
- Statistical calculations MUST work with PostgreSQL

**FR-2.4**: Marketing Analysis Queries
- Marketing spend aggregations MUST work with PostgreSQL
- ROI calculation queries MUST work with PostgreSQL
- Channel performance queries MUST work with PostgreSQL
- Spend validation queries MUST work with PostgreSQL

**FR-2.5**: Predictive Analytics Queries
- ML prediction storage MUST work with PostgreSQL
- Forecast retrieval queries MUST work with PostgreSQL
- Model performance queries MUST work with PostgreSQL

**FR-2.6**: Data Explorer Queries
- Dynamic table queries MUST work with PostgreSQL
- Table schema queries MUST work with PostgreSQL
- Search queries MUST work with PostgreSQL
- Table statistics MUST work with PostgreSQL

**FR-2.7**: AI Chat Queries
- Chat message storage MUST work with PostgreSQL
- Conversation retrieval MUST work with PostgreSQL
- Feedback storage MUST work with PostgreSQL
- Search queries MUST work with PostgreSQL
- Export queries MUST work with PostgreSQL

**FR-2.8**: Authentication Queries
- User creation MUST work with PostgreSQL
- User lookup MUST work with PostgreSQL
- Role management MUST work with PostgreSQL
- Last login updates MUST work with PostgreSQL

**Acceptance Criteria**:
- [ ] All 200+ queries updated to PostgreSQL syntax
- [ ] All placeholder `?` replaced with `%s`
- [ ] All `datetime('now')` replaced with `NOW()`
- [ ] All `CURRENT_TIMESTAMP` replaced with `NOW()`
- [ ] Query results identical between SQLite and PostgreSQL
- [ ] No breaking changes to application logic


### FR-3: ETL Pipeline Compatibility

**FR-3.1**: Admissions Data ETL (`etl_pipeline.py`)
- Table creation queries MUST work with PostgreSQL
- `INSERT OR REPLACE` MUST be converted to PostgreSQL upsert
- Batch insert operations MUST work with PostgreSQL
- Metadata updates MUST work with PostgreSQL

**FR-3.2**: Marketing Data ETL (`marketing_etl.py`)
- Marketing table creation MUST work with PostgreSQL
- Spend data upserts MUST work with PostgreSQL
- Totals calculation MUST work with PostgreSQL
- Data validation queries MUST work with PostgreSQL

**Acceptance Criteria**:
- [ ] ETL pipelines run successfully with PostgreSQL
- [ ] Data integrity maintained during ETL
- [ ] No duplicate records created
- [ ] Metadata timestamps updated correctly

### FR-4: Migration Scripts Compatibility

**FR-4.1**: All 6 migration scripts MUST be updated:
1. `add_users_table.py` - User authentication table
2. `add_user_roles.py` - Role column addition
3. `add_chat_history_table.py` - Chat conversation storage
4. `add_chat_indexes.py` - Performance indexes
5. `add_feedback_table.py` - Feedback ratings
6. `add_model_predictions_table.py` - ML predictions

**FR-4.2**: Migration Script Requirements
- All `AUTOINCREMENT` MUST be converted to `SERIAL`
- All `datetime('now')` MUST be converted to `NOW()`
- All `CURRENT_TIMESTAMP` MUST be converted to `NOW()`
- All indexes MUST be created correctly
- All foreign keys MUST be maintained

**Acceptance Criteria**:
- [ ] All migration scripts run successfully with PostgreSQL
- [ ] Tables created with correct schema
- [ ] Indexes created for performance
- [ ] Foreign key constraints enforced

### FR-5: Data Migration (Optional)

**FR-5.1**: Export Existing Data
- System MUST export all tables from local SQLite
- System MUST preserve data types and relationships
- System MUST handle NULL values correctly
- System MUST export in PostgreSQL-compatible format

**FR-5.2**: Import to Supabase
- System MUST import data to PostgreSQL tables
- System MUST verify data integrity after import
- System MUST validate row counts match
- System MUST handle duplicate records gracefully

**Acceptance Criteria**:
- [ ] All tables exported successfully
- [ ] All data imported to Supabase
- [ ] Row counts match between SQLite and PostgreSQL
- [ ] Data integrity verified (no corruption)

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1**: Query Response Time
- 95% of queries MUST complete in < 500ms
- 99% of queries MUST complete in < 1000ms
- No query SHOULD take > 5 seconds

**NFR-1.2**: Connection Overhead
- Connection establishment MUST be < 100ms
- Connection pooling MUST reduce overhead
- Cached connections MUST be reused

**NFR-1.3**: Page Load Time
- Home Dashboard MUST load in < 3 seconds
- Executive Deep Dive MUST load in < 3 seconds
- Marketing Analysis MUST load in < 4 seconds (complex queries)
- AI Chat MUST load in < 2 seconds
- Data Explorer MUST load in < 2 seconds

**Acceptance Criteria**:
- [ ] Performance testing shows < 500ms for 95% of queries
- [ ] No performance degradation vs SQLite
- [ ] Page load times meet requirements

### NFR-2: Reliability

**NFR-2.1**: Uptime
- Database MUST be available 99.9% of time
- System MUST gracefully degrade if database unavailable
- System MUST automatically recover from transient failures

**NFR-2.2**: Data Consistency
- ACID compliance MUST be maintained
- No data corruption during migration
- Transactions MUST be properly committed/rolled back

**NFR-2.3**: Error Handling
- Connection errors MUST be caught and logged
- Query errors MUST be caught and logged
- User-friendly error messages MUST be displayed
- System MUST not crash on database errors

**Acceptance Criteria**:
- [ ] Database uptime > 99.9%
- [ ] No data corruption incidents
- [ ] All errors handled gracefully
- [ ] Users see helpful error messages

### NFR-3: Security

**NFR-3.1**: Connection Security
- All connections MUST use SSL/TLS encryption
- Credentials MUST be stored in secrets (not code)
- No credentials MUST be in version control

**NFR-3.2**: Access Control
- Admin users MUST have access to all tables
- Regular users MUST NOT access sensitive tables
- Users MUST only see their own chat history
- Row-level security SHOULD be implemented (future)

**NFR-3.3**: Data Privacy
- User data MUST be protected
- GDPR compliance MUST be maintained
- Users MUST be able to delete their data

**Acceptance Criteria**:
- [ ] All connections use SSL/TLS
- [ ] No credentials in Git
- [ ] Access control enforced
- [ ] User data protected

### NFR-4: Scalability

**NFR-4.1**: User Capacity
- System MUST support 1000+ concurrent users
- System MUST handle 10,000+ database rows
- System MUST scale within free tier limits (500MB)

**NFR-4.2**: Query Optimization
- Indexes MUST be on frequently queried columns
- JOINs MUST be efficient
- Full table scans MUST be minimized

**Acceptance Criteria**:
- [ ] System handles 1000+ concurrent users
- [ ] Database size < 500MB (free tier)
- [ ] Queries optimized with indexes

### NFR-5: Maintainability

**NFR-5.1**: Code Quality
- Clear separation of database logic
- Reusable connection functions
- Well-documented code changes
- Consistent coding patterns

**NFR-5.2**: Testing
- Unit tests for database functions
- Integration tests for queries
- Rollback plan documented and tested

**Acceptance Criteria**:
- [ ] Code follows best practices
- [ ] Tests cover critical paths
- [ ] Documentation complete

### NFR-6: Cost

**NFR-6.1**: Free Tier Compliance
- Database storage MUST stay < 500MB
- Bandwidth MUST stay < 5GB/month
- No paid features required

**Acceptance Criteria**:
- [ ] Usage within free tier limits
- [ ] No unexpected costs

---

## User Stories

### US-1: Platform Administrator

**US-1.1**: View Production Users
```
As a platform administrator,
I want to see all users who have logged into the production app,
So that I can track adoption and user engagement.

Acceptance Criteria:
- Can view all production users in Supabase dashboard
- User data includes: name, email, role, last login, created date
- Can filter and search users
- User count is accurate and real-time
```

**US-1.2**: Track User Activity Across All Pages
```
As a platform administrator,
I want to track user activity across all 8 pages,
So that I can understand which features are most valuable.

Acceptance Criteria:
- Can see which pages users visit most
- Can see which filters/options users select
- Can see chat usage patterns
- Can see data exploration patterns
```

**US-1.3**: Analyze ML Prediction Accuracy
```
As a platform administrator,
I want to track ML prediction accuracy over time,
So that I can improve forecasting models.

Acceptance Criteria:
- All predictions stored in database
- Can compare predictions vs actuals
- Can track model performance metrics
- Historical data preserved across deployments
```

### US-2: Developer

**US-2.1**: Develop Locally with SQLite
```
As a developer,
I want to continue using SQLite for local development,
So that I don't need internet connection or cloud setup for testing.

Acceptance Criteria:
- App works locally without Supabase credentials
- Falls back to SQLite automatically
- Can test features offline
- Local SQLite data is independent from production
```

**US-2.2**: Test with Production Data
```
As a developer,
I want to optionally connect to Supabase locally,
So that I can test with real production data when needed.

Acceptance Criteria:
- Can add Supabase URL to local secrets
- App connects to Supabase when credentials present
- Can switch between SQLite and Supabase easily
- No code changes needed to switch databases
```

**US-2.3**: Debug Production Issues
```
As a developer,
I want to query production database from local environment,
So that I can debug issues without deploying.

Acceptance Criteria:
- Can connect to production database locally
- Can run queries against production data
- Can view user chat history for debugging
- Can test fixes before deploying
```

### US-3: End User

**US-3.1**: Persistent Chat History
```
As a user,
I want my AI chat history to persist across app updates,
So that I can reference previous conversations.

Acceptance Criteria:
- Chat history survives deployments
- Can access previous conversations
- Can search chat history
- Can export conversations
```

**US-3.2**: Persistent Authentication
```
As a user,
I want to stay logged in across app updates,
So that I don't have to re-authenticate frequently.

Acceptance Criteria:
- Login persists across deployments
- User preferences are saved
- Profile information remains intact
- No re-authentication required after updates
```

**US-3.3**: Reliable Data Access
```
As a user,
I want fast and reliable access to all platform features,
So that I have a smooth experience.

Acceptance Criteria:
- Query response time < 500ms for 95% of requests
- No connection timeouts under normal load
- Graceful error handling if database unavailable
- Clear error messages if issues occur
```

---

## Success Criteria

### Migration Success (Must Have - P0)
1. ✅ All 15 tables created in Supabase PostgreSQL
2. ✅ All 200+ SQL queries updated to PostgreSQL syntax
3. ✅ All 8 pages work identically with PostgreSQL
4. ✅ Local development works with SQLite fallback
5. ✅ Production connects to Supabase successfully
6. ✅ New users appear in Supabase dashboard
7. ✅ Chat history persists across deployments
8. ✅ ML predictions persist across deployments
9. ✅ No data loss during migration
10. ✅ GitHub Actions keep-alive configured

### User Experience Success (Should Have - P1)
1. ✅ Users don't notice any changes
2. ✅ No re-authentication required
3. ✅ App loads in < 3 seconds
4. ✅ No error messages for users
5. ✅ All features work as before

### Developer Experience Success (Should Have - P1)
1. ✅ Local development unchanged
2. ✅ Clear documentation available
3. ✅ Easy to switch between databases
4. ✅ Debugging tools available
5. ✅ Rollback plan documented

### Performance Success (Should Have - P1)
1. ✅ 95% of queries < 500ms
2. ✅ 99% of queries < 1000ms
3. ✅ No performance degradation vs SQLite
4. ✅ Page load times meet requirements

---

## Out of Scope

### Not Included in This Migration
1. ❌ Row-level security (RLS) implementation
2. ❌ Database replication/clustering
3. ❌ Advanced monitoring/alerting
4. ❌ Automated backups (Supabase handles this)
5. ❌ Performance optimization beyond basic indexes
6. ❌ Migration of historical data (optional)
7. ❌ Multi-region deployment
8. ❌ Custom database functions/triggers
9. ❌ Real-time subscriptions
10. ❌ GraphQL API

---

## Risks & Mitigation

### Risk 1: Data Loss During Migration
**Probability**: Low  
**Impact**: High  
**Mitigation**:
- Test migration on copy of database first
- Verify data integrity after migration
- Keep SQLite backup until migration verified
- Rollback plan documented

### Risk 2: Query Compatibility Issues
**Probability**: Medium  
**Impact**: Medium  
**Mitigation**:
- Comprehensive testing of all queries
- Automated tests for critical paths
- Gradual rollout (test locally first)
- Quick rollback to SQLite if needed

### Risk 3: Performance Degradation
**Probability**: Low  
**Impact**: Medium  
**Mitigation**:
- Performance testing before deployment
- Indexes on critical columns
- Connection pooling
- Monitor query times

### Risk 4: Supabase Auto-Pause
**Probability**: High (without mitigation)  
**Impact**: High  
**Mitigation**:
- GitHub Actions keep-alive workflow
- UptimeRobot monitoring
- Clear documentation for manual restore
- Alerts if project paused

### Risk 5: Cost Overruns
**Probability**: Low  
**Impact**: Low  
**Mitigation**:
- Monitor usage in Supabase dashboard
- Stay within free tier limits
- Alerts if approaching limits
- Optimization if needed

---

## Timeline Estimate

| Phase | Duration | Description |
|-------|----------|-------------|
| Setup | 15 min | Create Supabase project, run schema |
| Core Layer | 30 min | Update connection logic |
| Query Updates | 2-3 hours | Update all 200+ queries across 8 pages |
| Migration Scripts | 30 min | Update 6 migration scripts |
| ETL Updates | 30 min | Update 2 ETL pipelines |
| Local Testing | 1 hour | Test all pages with both databases |
| Keep-Alive | 15 min | GitHub Actions setup |
| Production | 30 min | Deploy and verify |
| Data Migration | 30 min | Optional - migrate existing data |
| Monitoring | 30 min | Validate and monitor |
| **Total** | **6-8 hours** | Complete migration |

---

**Document Version**: 2.0  
**Created**: January 26, 2026  
**Updated**: January 26, 2026  
**Status**: Ready for Design Phase  
**Owner**: Platform Team  
**Pages Covered**: 8/8 (100%)  
**Tables Covered**: 15/15 (100%)  
**Queries Analyzed**: 200+
