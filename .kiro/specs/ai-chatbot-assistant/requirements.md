# AI Chatbot Assistant - Requirements Document

## Feature Overview
An intelligent AI chatbot assistant that enables program directors and stakeholders to query the Mays Analytics Platform database using natural language. The chatbot will understand questions, convert them to SQL queries, retrieve data, and provide formatted, concise answers with context.

## Target Users
- **Program Directors**: Quick access to program-specific metrics
- **Admissions Staff**: Real-time insights on applications and enrollments
- **Marketing Team**: Campaign performance and ROI analysis
- **Executive Leadership**: High-level strategic insights

## Core Objectives
1. **Natural Language Understanding**: Convert user questions to accurate database queries
2. **Database Intelligence**: Deep understanding of schema, relationships, and data patterns
3. **RAG Pipeline**: Retrieve relevant context and provide accurate, formatted responses
4. **Token Efficiency**: Minimize token usage while maintaining response quality
5. **Fast Response Time**: Sub-3 second response time for most queries
6. **Memory Layer**: Maintain conversation context for follow-up questions

---

## User Stories

### US-1: Basic Query Interaction
**As a** program director  
**I want to** ask questions in natural language about my program's metrics  
**So that** I can quickly get insights without navigating through dashboards

**Acceptance Criteria:**
- AC-1.1: User can type questions in a chat interface
- AC-1.2: System understands common query patterns (e.g., "How many applications for MBA?")
- AC-1.3: System returns accurate data from the database
- AC-1.4: Response time is under 3 seconds for simple queries
- AC-1.5: Responses are formatted in a clear, readable manner

### US-2: Database Schema Understanding
**As a** user  
**I want to** ask questions without knowing the exact table/column names  
**So that** I can get answers using business terminology

**Acceptance Criteria:**
- AC-2.1: System maps business terms to database schema (e.g., "enrollments" → metric_name = 'Enrolled')
- AC-2.2: System understands program abbreviations (MBA, ACCT, MKTG, etc.)
- AC-2.3: System recognizes date formats and time periods
- AC-2.4: System handles synonyms (e.g., "applications" = "apps" = "applicants")
- AC-2.5: System provides helpful suggestions when query is ambiguous

### US-3: Complex Query Handling
**As a** marketing analyst  
**I want to** ask multi-dimensional questions  
**So that** I can analyze trends and correlations

**Acceptance Criteria:**
- AC-3.1: System handles queries with multiple filters (program, date range, cohort)
- AC-3.2: System can perform aggregations (sum, average, count, growth rate)
- AC-3.3: System can compare metrics across programs or time periods
- AC-3.4: System can join data from multiple tables (admissions + marketing spend)
- AC-3.5: System provides context when data is incomplete or unavailable

### US-4: Conversation Memory
**As a** user  
**I want to** ask follow-up questions without repeating context  
**So that** I can have a natural conversation flow

**Acceptance Criteria:**
- AC-4.1: System remembers previous queries in the conversation
- AC-4.2: System understands references like "show me the same for ACCT"
- AC-4.3: System maintains context for at least 5 previous exchanges
- AC-4.4: User can clear conversation history
- AC-4.5: System indicates when it's using previous context

### US-5: Response Formatting
**As a** user  
**I want to** receive well-formatted, concise responses  
**So that** I can quickly understand the insights

**Acceptance Criteria:**
- AC-5.1: Numerical data is formatted with proper separators (1,234 not 1234)
- AC-5.2: Percentages are shown with 1-2 decimal places
- AC-5.3: Dates are formatted consistently (e.g., "Jan 2025")
- AC-5.4: Responses include relevant context (e.g., "as of Dec 2025")
- AC-5.5: Large result sets are summarized with key highlights
- AC-5.6: Responses use bullet points or tables when appropriate

### US-6: Error Handling & Guidance
**As a** user  
**I want to** receive helpful feedback when my question can't be answered  
**So that** I can rephrase or understand limitations

**Acceptance Criteria:**
- AC-6.1: System explains why a query couldn't be answered
- AC-6.2: System suggests alternative phrasings or related queries
- AC-6.3: System indicates when data is not available for requested time period
- AC-6.4: System provides examples of supported query types
- AC-6.5: System handles SQL errors gracefully without exposing technical details

### US-7: Token Optimization
**As a** system administrator  
**I want to** minimize token usage per query  
**So that** we can reduce API costs and improve response speed

**Acceptance Criteria:**
- AC-7.1: System uses efficient prompts (< 500 tokens for context)
- AC-7.2: System retrieves only relevant schema information
- AC-7.3: System limits data samples to necessary rows
- AC-7.4: System uses streaming responses when possible
- AC-7.5: System caches common query patterns

### US-8: Quick Metrics Access
**As a** program director  
**I want to** get instant answers to common questions  
**So that** I can make quick decisions

**Acceptance Criteria:**
- AC-8.1: System recognizes common query patterns (e.g., "latest numbers")
- AC-8.2: System provides pre-computed metrics when available
- AC-8.3: System suggests related metrics after answering
- AC-8.4: System can provide comparisons to previous periods automatically
- AC-8.5: System highlights significant changes or trends

### US-9: Navigation Assistance
**As a** user  
**I want to** get guidance on which page and filters to use for specific tasks  
**So that** I can efficiently navigate the platform to create reports

**Acceptance Criteria:**
- AC-9.1: System understands all platform pages (Home, Executive, Comparison, Marketing, Data Explorer, Predictive)
- AC-9.2: System can recommend the best page for user's specific need
- AC-9.3: System provides step-by-step navigation instructions
- AC-9.4: System suggests appropriate filters to apply (program, date range, cohort)
- AC-9.5: System explains what each page is designed for
- AC-9.6: System can guide users to generate specific reports
- AC-9.7: System provides clickable links or clear directions to navigate

### US-10: Authentication Gate & Access Control
**As a** platform administrator  
**I want to** restrict chat access to authenticated users only  
**So that** we can track usage and maintain security

**Acceptance Criteria:**
- AC-10.1: Chat feature is only accessible after Google OAuth authentication
- AC-10.2: Unauthenticated users see a "Sign in to use Chat" message
- AC-10.3: System uses existing OAuth implementation (v5.2)
- AC-10.4: System leverages existing `users` table for user identification
- AC-10.5: System greets users by name from their OAuth profile
- AC-10.6: Chat button is hidden/disabled for unauthenticated users

### US-11: Chat History & Persistence
**As a** returning user  
**I want to** access my previous chat conversations  
**So that** I can continue where I left off and maintain context

**Acceptance Criteria:**
- AC-11.1: Chat history is stored per user account (linked to user_id)
- AC-11.2: Users can view previous conversations in chronological order
- AC-11.3: Users can search through their chat history
- AC-11.4: Users can resume previous conversations
- AC-11.5: Users can delete individual conversations or entire history
- AC-11.6: Chat history is stored securely in the database
- AC-11.7: Users can export their chat history (JSON or CSV)
- AC-11.8: System maintains conversation threading (groups related messages)

### US-12: Platform Knowledge Base
**As a** user  
**I want to** ask questions about platform features and capabilities  
**So that** I can learn how to use the platform effectively

**Acceptance Criteria:**
- AC-12.1: System has knowledge of all platform pages and their purposes
- AC-12.2: System can explain available filters and their effects
- AC-12.3: System can describe available metrics and calculations
- AC-12.4: System provides examples of common workflows
- AC-12.5: System can answer "how do I..." questions
- AC-12.6: System references documentation when appropriate

---

## Technical Requirements

### TR-1: Database Integration
- TR-1.1: Read-only access to SQLite database
- TR-1.2: Support for all existing tables (admissions_metrics, marketing_spend, programs, etc.)
- TR-1.3: Efficient query execution (< 1 second for most queries)
- TR-1.4: Connection pooling for concurrent users

### TR-2: LLM Integration
- TR-2.1: Support for Google Gemini (free tier for testing)
- TR-2.2: Alternative support for OpenAI GPT-4/3.5-turbo
- TR-2.3: Alternative support for Claude
- TR-2.4: Configurable model selection based on query complexity
- TR-2.5: API key management through Streamlit secrets
- TR-2.6: Fallback to alternative models if primary fails

### TR-3: RAG Pipeline & Vector Database
- TR-3.1: Schema embedding and vector storage
- TR-3.2: Semantic search for relevant schema elements
- TR-3.3: Context retrieval from previous queries
- TR-3.4: Dynamic prompt construction based on query type
- TR-3.5: Support for multiple vector database options:
  - **ChromaDB**: Embedded, free, simple setup (recommended for MVP)
  - **Pinecone**: Cloud-based, scalable, free tier available
  - **Supabase Vector**: PostgreSQL-based, free tier, good for production
  - **Weaviate**: Open-source, self-hosted or cloud
  - **Qdrant**: High-performance, free tier available

### TR-4: Authentication & User Management
- TR-4.1: **Use existing Google OAuth 2.0 implementation** (v5.2)
- TR-4.2: Leverage existing `users` table (user_id, google_id, email, name, profile_picture_url, role)
- TR-4.3: Check authentication status using `auth.is_authenticated()`
- TR-4.4: Get user info using `auth.get_current_user()`
- TR-4.5: No additional authentication system needed
- TR-4.6: Chat feature gated behind authentication check

### TR-5: Chat History Storage
- TR-5.1: New `chat_history` table in existing SQLite database
- TR-5.2: Schema: `chat_id`, `user_id` (FK to users), `conversation_id`, `message`, `role` (user/assistant), `timestamp`, `tokens_used`
- TR-5.3: Conversation threading and organization by `conversation_id`
- TR-5.4: Search functionality across chat history
- TR-5.5: Export chat history (JSON or CSV format)
- TR-5.6: Automatic cleanup of old conversations (configurable retention, default 90 days)
- TR-5.7: Soft delete for user privacy (mark as deleted, actual deletion after 30 days)

### TR-6: Platform Navigation Knowledge
- TR-6.1: Embedded knowledge base of all platform pages
- TR-6.2: Page descriptions and use cases
- TR-6.3: Available filters per page
- TR-6.4: Common workflows and examples
- TR-6.5: Deep linking to specific pages with pre-applied filters
### TR-7: UI/UX Requirements
- TR-7.1: Chat interface integrated into main application
- TR-7.2: Floating chat button (bottom-right corner, positioned near back-to-top button)
- TR-7.3: Expandable/collapsible chat window (overlay, doesn't shift content)
- TR-7.4: Message history display with scrolling
- TR-7.5: Typing indicators during processing
- TR-7.6: Copy response functionality
- TR-7.7: Clear conversation button
- TR-7.8: **Authentication gate**: Show "Sign in to use Chat" for unauthenticated users
- TR-7.9: User profile display in chat header (name, profile picture from OAuth)
- TR-7.10: Navigation suggestions with clickable links
- TR-7.11: Chat button hidden/disabled when not authenticated
- TR-7.12: Smooth animations matching platform design (maroon gradient theme)

### TR-8: Performance Requirements
- TR-8.1: Response time < 3 seconds for 80% of queries
- TR-8.2: Response time < 5 seconds for 95% of queries
- TR-8.3: Support for 10+ concurrent users
- TR-8.4: Token usage < 1000 tokens per query (average)
- TR-8.5: Chat history loading < 1 second

### TR-9: Security & Privacy
- TR-9.1: **Leverage existing OAuth security** (no additional auth needed)
- TR-9.2: Query logging for debugging (anonymized, user_id only)
- TR-9.3: Rate limiting to prevent abuse (10 queries/minute per user)
- TR-9.4: Input sanitization to prevent SQL injection
- TR-9.5: API key encryption and secure storage (Streamlit secrets)
- TR-9.6: HTTPS for all communications (Streamlit Cloud default)
- TR-9.7: Chat history accessible only to owning user (user_id check)
- TR-9.8: GDPR compliance for data deletion requests (soft delete + purge)

---

## Database Schema Context

### Key Tables
1. **admissions_metrics**: Core metrics (inquiries, applications, admits, enrolled)
2. **marketing_spend**: Marketing channel spend by program and month
3. **programs**: Active program list with codes
4. **model_predictions**: ML forecasting results
5. **marketing_campaigns**: Campaign tracking data
6. **users** (existing): User authentication via Google OAuth (user_id, google_id, email, name, profile_picture_url, role, created_at, last_login)
7. **chat_history** (new): Stored conversations per user

### Common Metrics
- Inquiries, Applications, Admits, Enrolled, Deposits, Confirmed
- Conversion rates, Growth rates, ROI metrics

### Programs
- MBA, MS ACCT, MS HRM, MS MISY, MS MKTG, MS ENLD, MS SPBA

### Date Ranges
- Admissions data: Jan 2024 - Dec 2025
- Marketing spend: FY25 Year 1

---

## Platform Pages Knowledge Base

### Page 1: Home Dashboard
**Purpose**: High-level overview of all programs and key metrics  
**Best For**: Quick snapshot, executive summary, overall trends  
**Available Filters**: Cohort year  
**Key Metrics**: Total inquiries, applications, admits, enrolled across all programs  
**When to Use**: "Show me overall performance" or "What's the big picture?"

### Page 2: Executive Deep Dive
**Purpose**: Detailed program-specific analysis with trends  
**Best For**: Deep analysis of single program, trend identification  
**Available Filters**: Program, cohort year, date range  
**Key Metrics**: Program-specific funnel, conversion rates, time-series trends  
**When to Use**: "Analyze MBA performance" or "Show me ACCT trends"

### Page 3: Comparison Tool
**Purpose**: Year-over-year and program-to-program comparisons  
**Best For**: Comparative analysis, identifying winners/losers  
**Available Filters**: Two cohorts or two programs, metrics selection  
**Key Metrics**: Percentage changes, variance, statistical comparisons  
**When to Use**: "Compare 2024 vs 2025" or "Which program is growing fastest?"

### Page 4: Marketing Analysis
**Purpose**: Marketing spend, channel performance, ROI analysis  
**Best For**: Marketing effectiveness, budget allocation decisions  
**Available Filters**: Program, fiscal year, channel, date range  
**Key Metrics**: Spend by channel, cost per inquiry/application, ROI  
**When to Use**: "How effective is our Google Ads?" or "What's our marketing ROI?"

### Page 5: Data Explorer
**Purpose**: Raw data access with flexible filtering  
**Best For**: Custom analysis, data export, detailed investigation  
**Available Filters**: All dimensions (program, cohort, date, metric)  
**Key Metrics**: All available metrics in tabular format  
**When to Use**: "I need raw data" or "Export specific metrics"

### Page 6: Predictive Analytics
**Purpose**: ML-powered forecasting and predictions  
**Best For**: Future planning, budget forecasting, trend prediction  
**Available Filters**: Program, forecast horizon, model type  
**Key Metrics**: Predicted inquiries/applications/enrollments, confidence intervals  
**When to Use**: "What will enrollment be next year?" or "Forecast MBA applications"

---

## Example Queries to Support

### Simple Data Queries
- "How many applications for MBA in 2025?"
- "What's the latest enrollment count for ACCT?"
- "Show me marketing spend for MKTG program"

### Comparative Queries
- "Compare MBA applications between 2024 and 2025"
- "Which program has the highest conversion rate?"
- "Show me ROI for all marketing channels"

### Trend Queries
- "What's the growth trend for MBA applications?"
- "How has marketing spend changed over time?"
- "Show me enrollment trends for all programs"

### Complex Queries
- "What's the cost per enrollment for MBA Google Ads?"
- "Which marketing channel has the best ROI for ACCT?"
- "Show me programs with declining applications"

### Navigation & Guidance Queries
- "Where can I see year-over-year comparisons?"
- "How do I create a report for MBA performance?"
- "Which page should I use to analyze marketing effectiveness?"
- "Show me how to filter by date range"
- "I want to forecast next year's enrollments, where do I go?"
- "What filters are available on the Executive Deep Dive page?"
- "Help me navigate to the comparison tool"
- "How do I export data?"

### Platform Knowledge Queries
- "What does the Home Dashboard show?"
- "What's the difference between Executive Dive and Comparison Tool?"
- "What metrics are available?"
- "How do I use the predictive analytics page?"
- "What programs are tracked in the system?"

---

## Out of Scope (Phase 1)

- ❌ Data modification or updates through chat
- ❌ Automated report generation or PDF export from chat
- ❌ Email notifications or alerts
- ❌ Multi-user collaboration features (shared chats)
- ❌ Voice input/output
- ❌ Integration with external data sources
- ❌ Custom dashboard creation from chat
- ❌ Direct filter application (chat guides, user applies manually)

---

## Success Metrics

### Quantitative
- **Response Accuracy**: > 90% of queries return correct data
- **Response Time**: < 3 seconds average
- **Token Efficiency**: < 1000 tokens per query average
- **User Adoption**: 50%+ of users try chatbot within first week
- **Query Success Rate**: > 85% of queries successfully answered

### Qualitative
- Users report chatbot is "helpful" or "very helpful"
- Users prefer chatbot over manual dashboard navigation for quick queries
- Reduced support requests for basic data questions

---

## Dependencies

### External Services
- **Google Gemini API** (primary - free tier for testing)
- OpenAI API (optional alternative)
- Claude API (optional alternative)
- Vector database service (see options below)

### Vector Database Options (Ranked by Recommendation)
1. **ChromaDB** (Recommended for MVP)
   - ✅ Embedded, no external service needed
   - ✅ Free and open-source
   - ✅ Simple setup
   - ✅ Good for development and small-scale production
   - ❌ Limited scalability for very large datasets

2. **Supabase Vector**
   - ✅ PostgreSQL-based (familiar)
   - ✅ Free tier available (500MB)
   - ✅ Good for production
   - ✅ Integrated with Supabase auth (bonus!)
   - ❌ Requires external service setup

3. **Pinecone**
   - ✅ Cloud-based, highly scalable
   - ✅ Free tier (1 index, 100K vectors)
   - ✅ Excellent performance
   - ❌ Requires external account
   - ❌ Limited free tier

4. **Qdrant**
   - ✅ High-performance
   - ✅ Free tier available (1GB cluster)
   - ✅ Good API
   - ❌ Requires external service

5. **Weaviate**
   - ✅ Open-source
   - ✅ Self-hosted or cloud
   - ❌ More complex setup
   - ❌ Steeper learning curve

### Python Libraries
- `google-generativeai` for Gemini integration
- `langchain` or `llama-index` for RAG pipeline
- `chromadb` for vector storage (recommended)
- `streamlit-chat` or `streamlit-extras` for chat UI
- `sentence-transformers` for embeddings
- **No additional auth libraries needed** (using existing OAuth)

### Infrastructure
- Existing SQLite database (`edulytix.db`)
- New table: `chat_history` (users table already exists)
- Existing Google OAuth 2.0 authentication (v5.2)
- Streamlit Cloud or local deployment
- API key management system (Streamlit secrets)

---

## Implementation Phases

### Phase 1: MVP with Gemini (Week 1-2)
- Basic chat interface (floating button, positioned near back-to-top)
- **Authentication gate** (check `auth.is_authenticated()`)
- Google Gemini integration (free API)
- Simple query understanding (single table queries)
- Direct SQL generation with validation
- Basic response formatting
- ChromaDB for schema embeddings
- User greeting with OAuth profile name

### Phase 2: Chat History & Persistence (Week 3)
- Create `chat_history` table (link to existing `users` table)
- Store conversations per user (user_id from OAuth)
- Display chat history in UI
- Search and export functionality
- Conversation threading
- Clear/delete history options

### Phase 3: Navigation Intelligence (Week 4)
- Platform pages knowledge base
- Navigation recommendations
- Filter suggestions
- Step-by-step guidance
- Deep linking to pages

### Phase 4: Enhanced RAG Pipeline (Week 5-6)
- Full RAG pipeline implementation
- Schema embedding and semantic search
- Conversation memory (5 exchanges)
- Complex query support (joins, aggregations)
- Context-aware responses

### Phase 5: Optimization (Week 7)
- Token optimization
- Response caching
- Query pattern recognition
- Performance tuning
- Rate limiting

### Phase 6: Polish & Testing (Week 8)
- UI/UX refinements
- Error handling improvements
- User feedback integration
- Documentation and examples
- Load testing

---

## Risk Assessment

### High Risk
- **LLM Hallucinations**: Model may generate incorrect SQL or data
  - *Mitigation*: Query validation, result verification, confidence scoring

### Medium Risk
- **Token Costs**: High usage could increase API costs
  - *Mitigation*: Token optimization, caching, rate limiting
- **Response Time**: Complex queries may be slow
  - *Mitigation*: Query optimization, timeout handling, async processing

### Low Risk
- **User Adoption**: Users may prefer traditional dashboards
  - *Mitigation*: User training, prominent placement, helpful examples

---

## Open Questions

1. **LLM Provider**: Start with Google Gemini (free) for testing, then evaluate OpenAI/Claude for production?
2. **Vector Database**: ChromaDB (embedded, simple) or Supabase Vector (production-ready)?
3. **Chat Placement**: Floating button next to back-to-top button (bottom-right)?
4. **Memory Storage**: Session-based initially, then persistent with user_id from OAuth?
5. **Query Logging**: Store anonymized queries for improvement, with user consent?
6. **Chat History Retention**: How long to keep chat history? 30 days? 90 days? Forever?
7. **Navigation Links**: Should chat provide clickable links to pages, or just text instructions?
8. **Free Tier Limits**: What's acceptable for Gemini API usage? (Gemini has generous free tier)
9. **Chat Window Size**: Fixed size or resizable? Mobile responsive behavior?
10. **Conversation Organization**: Group by date, topic, or simple chronological list?

---

## Recommended Starting Configuration

Based on your requirements for free testing and quick implementation:

### **Recommended Stack for MVP**:
- **LLM**: Google Gemini 1.5 Flash (free tier: 15 requests/minute, 1M tokens/day)
- **Vector DB**: ChromaDB (embedded, no external service)
- **Auth**: **Existing Google OAuth 2.0** (v5.2 - already implemented!)
- **Chat UI**: Floating button (bottom-right, near back-to-top button)
- **Storage**: SQLite for chat history (same DB as existing `users` table)

### **Why This Stack**:
1. **Zero Cost**: Gemini free tier is very generous
2. **Fast Setup**: ChromaDB is embedded, no external services
3. **Auth Already Done**: Leverage existing OAuth implementation (v5.2)
4. **Familiar**: SQLite for everything keeps it simple
5. **Upgradeable**: Easy to swap Gemini→OpenAI, ChromaDB→Pinecone later

### **Estimated Costs (After Free Tier)**:
- Gemini: $0 (free tier sufficient for testing)
- ChromaDB: $0 (embedded)
- Hosting: $0 (Streamlit Cloud free tier)
- Auth: $0 (already implemented)
- **Total MVP Cost**: $0

### **Production Costs (Estimated)**:
- Gemini Pro: ~$0.50-2/day for 100 users
- OR OpenAI GPT-3.5: ~$1-3/day for 100 users
- Supabase (if upgraded): $0-25/month
- **Total Production**: ~$15-90/month

---

**Document Version**: 2.0  
**Created**: January 24, 2026  
**Updated**: January 25, 2026  
**Status**: Updated - Ready for Design Phase
