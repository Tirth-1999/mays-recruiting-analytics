# Technical Guide

[← Back to Documentation](README.md)

---

## Database Schema

### Admissions Tables

#### programs
- program_code (TEXT, PRIMARY KEY)
- program_name (TEXT)
- is_active (INTEGER)

#### admissions_metrics
- id (INTEGER, PRIMARY KEY)
- report_date (TEXT)
- program (TEXT)
- cohort_year (INTEGER)
- metric_name (TEXT)
- metric_value (REAL)
- created_at (TIMESTAMP)
- UNIQUE constraint on (report_date, program, cohort_year, metric_name)

### Marketing Tables

#### marketing_spend
- spend_id (INTEGER, PRIMARY KEY)
- spend_date (TEXT)
- program (TEXT)
- channel (TEXT) - Search, Display, LinkedIn, Meta, etc.
- amount (REAL)
- fiscal_year (TEXT)
- currency (TEXT)

#### marketing_metrics
- metric_id (INTEGER, PRIMARY KEY)
- report_date (TEXT)
- program (TEXT)
- channel (TEXT)
- spend (REAL)
- is_active (INTEGER) - 1 = active, 0 = inactive
- impressions, clicks, inquiries, applications (for future use)

#### marketing_campaigns
Ready for future data:
- campaign_id, campaign_name, campaign_type, start_date, end_date, etc.

#### inquiry_sources
Ready for future data:
- inquiry_id, inquiry_date, source, campaign_id, converted_to_application, etc.

### System Tables

#### metadata
- key (TEXT, PRIMARY KEY)
- value (TEXT)
- updated_at (TIMESTAMP)

Tracks:
- `last_data_update` - When admissions data was last loaded
- `last_marketing_update` - When marketing data was last loaded

#### model_predictions
- prediction_id (INTEGER, PRIMARY KEY)
- model_name (TEXT)
- program (TEXT)
- cohort_year (INTEGER)
- metric_name (TEXT)
- prediction_date (TEXT)
- predicted_value (REAL)
- lower_bound (REAL)
- upper_bound (REAL)
- actual_value (REAL)
- mape (REAL)
- created_at (TIMESTAMP)

---

## Configuration

### Database Setup

```bash
# Initialize database
python3 etl_pipeline.py          # Admissions data
python3 marketing_etl.py         # Marketing data

# Database location
edulytix.db                      # SQLite database file

# Schema files
marketing_schema.sql             # Marketing tables schema
```

### Environment Variables

```bash
# Optional configuration
STREAMLIT_SERVER_PORT=8501       # Default port
STREAMLIT_SERVER_ADDRESS=localhost
```

### Data Sources

```
Dataset/
├── MBS-Flex-Online-Admissions-2024-04-30.xlsx
├── MBS-Flex-Online-Admissions-2024-05-31.xlsx
├── MBS-Flex-Online-Admissions-2024-07-31.xlsx
├── MBS-Flex-Online-Admissions-2025-07-31.xlsx
├── MBS-Flex-Online-Admissions-2025-10-31.xlsx
├── MBS-Flex-Online-Admissions-2025-11-30.xlsx
├── MBS-Flex-Online-Admissions-2025-12-31.xlsx
└── Mays Flex Online Ad Spend Year 1.xlsx
```

### Version Management

```python
# Update version in ONE file
version.py

# Version format
VERSION_MAJOR = 4
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_FULL = f"v{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

# Automatically propagates to:
- Sidebar footer
- Help page footer
- Troubleshooting section
```

### Customization

#### Colors
```python
# Mays Business School brand colors
maroon = '#500000'
gold = '#C5A572'
dark_maroon = '#700000'
light_maroon = '#B00000'
```

#### Filters
```python
# Cohort options
cohort_options = [2028, 2027, 2026]

# Program options
program_options = ['All Programs', 'MBA', 'MS ACCT', 
                   'MS ENLD', 'MS HRM', 'MS MISY', 
                   'MS MKTG', 'MS SPBA']
```

---

## Troubleshooting

### Common Issues

#### Database Errors

**"No data available"**
```bash
# Solution: Run ETL pipeline
python3 etl_pipeline.py
python3 marketing_etl.py
```

**"Database connection failed"**
```bash
# Check database file exists
ls -la edulytix.db

# Check permissions
chmod 644 edulytix.db
```

#### Display Issues

**"Charts not rendering"**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart application
streamlit run main_app.py
```

**"Filters not working"**
```bash
# Reset session state
# Refresh browser (Ctrl+R or Cmd+R)
```

#### Performance Issues

**"Slow loading"**
```bash
# Check database size
du -h edulytix.db

# Filter data before exporting
# Close unused browser tabs
```

**"Memory errors"**
```bash
# Reduce row limits in Data Explorer
# Filter data before exporting
# Close unused browser tabs
```

#### Predictive Analytics Issues

**"Insufficient data for forecasting"**
- Need at least 6 months of historical data
- Wait for more data or use simpler methods

**"Model training failed"**
- Check data quality (missing values, outliers)
- Review logs for specific errors
- Ensure ETL pipeline completed successfully

**"High MAPE (> 15%)"**
- Model may need retraining
- Patterns may have changed
- Consider collecting more data

### Debug Mode

```bash
# Run with debug logging
streamlit run main_app.py --logger.level=debug

# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
pip list | grep streamlit
pip list | grep pandas
pip list | grep plotly
```

---

## Data Clarifications

### Admissions Data
- Campaign matrix values labeled `- NA -` indicate the campaign was not active for that program/month and are excluded from totals
- Blank/`NaN` values are preserved as missing data rather than treated as zeros
- Dates represent the last day of the reporting month
- All metrics are cumulative within a cohort year

### Marketing Data
- "No Ad Spend" entries are handled as NULL (not zero)
- Spend is tracked monthly by program and channel
- FY25 Year 1 covers September 2024 - June 2025
- Search advertising represents 98% of total spend ($202K of $206K)
- General Awareness campaigns are tracked separately from program-specific campaigns

---

[← Back to Documentation](README.md)


---

## AI Chat Assistant

### Overview
The AI Chat Assistant provides a natural language interface to query the Mays Analytics Platform. Users can ask questions about admissions data, marketing metrics, and platform navigation in plain English.

### Architecture

#### Components
1. **Frontend (modules/ai_chat.py)**
   - Floating chat button (bottom-right, above back-to-top)
   - Chat window overlay (400px × 600px on desktop, full-screen on mobile)
   - Message display with user/assistant differentiation
   - Authentication gate (requires Google OAuth)

2. **Backend Utilities (utils/ai_chat/)**
   - `gemini_client.py`: Google Gemini API integration
   - `vector_store.py`: ChromaDB for schema embeddings
   - `sql_generator.py`: Query processing and SQL generation
   - `chat_history.py`: Database operations for chat persistence
   - `prompts.py`: Prompt templates for different query types

3. **Database**
   - `chat_history` table: Stores user conversations
   - Linked to `users` table via `user_id` foreign key

### Database Schema

#### chat_history Table
```sql
CREATE TABLE chat_history (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_id TEXT NOT NULL,
    message TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER DEFAULT 0,
    query_type TEXT,
    sql_query TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_chat_user ON chat_history(user_id);
CREATE INDEX idx_chat_conversation ON chat_history(conversation_id);
CREATE INDEX idx_chat_timestamp ON chat_history(timestamp);
CREATE INDEX idx_chat_user_conversation ON chat_history(user_id, conversation_id);
```

### Query Processing Pipeline

1. **Authentication Check**: Verify user is signed in via OAuth
2. **Query Classification**: Determine query type (data, navigation, help, conversational)
3. **Context Retrieval**: Get relevant schema/platform knowledge from ChromaDB
4. **Prompt Construction**: Build prompt with context and conversation history
5. **LLM Generation**: Call Gemini API to generate SQL or response
6. **SQL Validation**: Ensure generated SQL is safe (SELECT only, no dangerous operations)
7. **Execution**: Run SQL query against database
8. **Response Formatting**: Format results into readable response
9. **History Storage**: Save conversation to database

### Query Types

#### Data Queries
- Keywords: "how many", "show me", "what is", "count", "total"
- Process: Generate SQL → Validate → Execute → Format results
- Example: "How many MBA applications in 2025?"

#### Navigation Queries
- Keywords: "where", "which page", "how do i", "navigate"
- Process: Search platform knowledge → Recommend page → Provide steps
- Example: "Where can I see year-over-year comparisons?"

#### Help Queries
- Keywords: "what does", "explain", "help", "how to use"
- Process: Search platform knowledge → Explain feature
- Example: "What does the Executive Deep Dive show?"

#### Conversational Queries
- Default for greetings and general chat
- Process: Generate friendly response
- Example: "Hello!"

### Vector Store (ChromaDB)

#### Collections

**schema_collection**: Database schema embeddings
- Tables: admissions_metrics, marketing_spend, programs, model_predictions
- Metrics: Inquiries, Applications, Admits, Enrolled, etc.
- Used for semantic search to find relevant schema for SQL generation

**platform_collection**: Platform knowledge embeddings
- Pages: Home, Executive Deep Dive, Comparison, Marketing, Data Explorer, Predictive
- Features, filters, and use cases for each page
- Used for navigation recommendations

#### Embedding Model
- Model: `all-MiniLM-L6-v2` (SentenceTransformers)
- Fast, lightweight, good accuracy for semantic search
- Embeddings stored persistently in `.chromadb/` directory

### API Configuration

#### Gemini API
- Model: `gemini-1.5-flash` (free tier, fast)
- Temperature: 0.1 (low for accuracy)
- Max tokens: 1024 per response
- Rate limit: 10 requests/minute (configurable)

#### Secrets Configuration
```toml
# .streamlit/secrets.toml
[gemini]
api_key = "YOUR_GEMINI_API_KEY"

[chat]
rate_limit_requests = 10
rate_limit_window = 60
max_conversation_history = 5
token_limit_per_query = 1000
```

### Security

#### SQL Injection Prevention
- Only SELECT statements allowed
- Dangerous keywords blocked (DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, EXEC)
- Input sanitization for user queries
- SQL validation before execution

#### User Data Isolation
- Chat history filtered by `user_id` from OAuth
- Users can only access their own conversations
- Foreign key constraint ensures data integrity

#### Rate Limiting
- Per-user rate limiting (10 queries/minute default)
- Prevents API quota exhaustion
- Graceful error messages when limit exceeded

### Performance

#### Token Optimization
- Concise prompts (< 500 tokens context)
- Semantic search retrieves only relevant schema
- Conversation history limited to last 5 exchanges
- Approximate token counting for monitoring

#### Response Time
- Target: < 3 seconds for 80% of queries
- ChromaDB semantic search: ~100ms
- Gemini API call: ~1-2 seconds
- SQL execution: ~50-200ms

#### Caching (Future)
- Query result caching for common queries
- Response caching for identical questions
- LRU cache with configurable size

### Error Handling

#### Error Types
- `no_data`: No results found for query
- `sql_error`: Invalid SQL generated
- `api_error`: Gemini API failure
- `rate_limit`: Rate limit exceeded
- `auth_required`: User not authenticated
- `ambiguous`: Query too vague

#### Error Messages
- User-friendly explanations
- Suggestions for rephrasing
- Examples of supported queries
- No technical details exposed to users

### Monitoring

#### Metrics to Track
- Query volume per user
- Response times by query type
- Token usage per query
- Error rates by type
- User adoption rate

#### Logging
- All queries logged with user_id, query_type, tokens_used
- SQL queries stored for debugging
- Errors logged with context
- Anonymized for privacy

### Maintenance

#### Database Cleanup
```python
# Delete conversations older than 90 days
from utils.ai_chat import ChatHistory
history = ChatHistory()
deleted = history.cleanup_old_conversations(days=90)
```

#### Vector Store Reinitialization
```python
# Reinitialize embeddings (if schema changes)
from utils.ai_chat import VectorStore
store = VectorStore()
store.initialize_schema_embeddings()
store.initialize_platform_embeddings()
```

### Testing

#### Unit Tests
- Query classification accuracy
- SQL validation logic
- Number formatting
- Error handling

#### Integration Tests
- End-to-end query processing
- Database operations
- API integration
- Authentication flow

#### Test Commands
```bash
# Test chat history
python utils/ai_chat/chat_history.py

# Test vector store
python utils/ai_chat/vector_store.py

# Test query classification
python -c "from utils.ai_chat.sql_generator import QueryProcessor; ..."
```

### Deployment

#### Requirements
- Python packages: `google-genai`, `chromadb`, `sentence-transformers`, `streamlit-chat`
- Gemini API key configured in Streamlit secrets
- ChromaDB data directory (`.chromadb/`) persisted
- Database migration run: `python migrations/add_chat_history_table.py up`

#### Streamlit Cloud
- Add Gemini API key to secrets
- ChromaDB data persists in app storage
- No additional infrastructure needed
- OAuth already configured

### Future Enhancements (Phase 2-6)

#### Phase 2: Chat History UI
- Conversation list sidebar
- Search across history
- Export conversations (JSON/CSV)
- Delete conversations

#### Phase 3: Navigation Intelligence
- Deep linking to pages with filters
- Clickable navigation links
- Step-by-step workflow guides

#### Phase 4: Enhanced RAG
- Conversation memory (reference resolution)
- Complex queries (joins, aggregations)
- Multi-turn conversations

#### Phase 5: Optimization
- Response caching
- Query pattern recognition
- Async processing
- Performance tuning

#### Phase 6: Polish
- User feedback buttons
- Suggested queries
- In-app help
- Video tutorials

---
