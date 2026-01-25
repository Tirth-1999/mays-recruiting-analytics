# AI Chatbot Assistant - Design Document

## Overview
This document outlines the technical design for implementing an AI-powered chatbot assistant that enables authenticated users to query the Mays Analytics Platform using natural language. The chatbot will leverage Google Gemini, ChromaDB for vector storage, and the existing Google OAuth authentication system.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Floating     │  │ Chat Window  │  │ Auth Gate    │         │
│  │ Chat Button  │  │ (Overlay)    │  │ Check        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Chat Module (Python)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Message      │  │ Query        │  │ Response     │         │
│  │ Handler      │  │ Processor    │  │ Formatter    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│   Google Gemini  │ │   ChromaDB   │ │   SQLite DB  │
│   (LLM API)      │ │   (Vectors)  │ │   (Data)     │
└──────────────────┘ └──────────────┘ └──────────────┘
```

---

## Component Design

### 1. UI Components

#### 1.1 Floating Chat Button
**Location**: Bottom-right corner, 20px above back-to-top button

**Design**:
```css
- Size: 60px × 60px (circular)
- Background: Maroon gradient (#500000 → #700000)
- Icon: Chat bubble or message icon (white)
- Shadow: 0 4px 12px rgba(80, 0, 0, 0.3)
- Hover: Lift 3px, scale 1.05
- Z-index: 999998 (below back-to-top: 999999)
```

**States**:
- **Authenticated**: Visible, clickable, shows unread count badge
- **Unauthenticated**: Hidden or shows "Sign in to chat" tooltip
- **Active**: Highlighted when chat window is open

**Implementation**:
```python
# In main_app.py
if auth.is_authenticated():
    # Show chat button with st.markdown (HTML/CSS)
    # Click opens chat window
else:
    # Hide button or show disabled state
```

#### 1.2 Chat Window
**Layout**: Overlay panel, doesn't shift page content

**Dimensions**:
- Desktop: 400px wide × 600px tall
- Mobile: Full screen (100vw × 100vh)
- Position: Bottom-right, 20px from edges

**Structure**:
```
┌─────────────────────────────────┐
│ Header                          │
│ ┌─────────────────────────────┐ │
│ │ User Profile | Clear | Close│ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ Message History (Scrollable)    │
│ ┌─────────────────────────────┐ │
│ │ User: How many MBA apps?    │ │
│ │ Bot: There are 234 MBA...   │ │
│ │ User: What about ACCT?      │ │
│ │ Bot: ACCT has 156...        │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ Input Area                      │
│ ┌─────────────────────────────┐ │
│ │ Type your question...       │ │
│ │                      [Send] │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

**Features**:
- Auto-scroll to latest message
- Typing indicator while processing
- Copy button on each bot response
- Timestamp on each message
- User profile picture in header (from OAuth)

#### 1.3 Authentication Gate
**Unauthenticated State**:
```python
if not auth.is_authenticated():
    st.info("🔒 Sign in to use the AI Chat Assistant")
    # Show OAuth button
    auth_url = auth.get_authorization_url()
    st.link_button("Sign in with Google", auth_url)
```

**Authenticated State**:
```python
user = auth.get_current_user()
st.write(f"Welcome, {user['name']}!")
# Show chat interface
```

---

### 2. Backend Components

#### 2.1 Chat Module Structure
```
modules/
└── ai_chat.py          # Main chat module
    ├── render()        # Main render function
    ├── ChatManager     # Manages chat state
    ├── QueryProcessor  # Processes user queries
    └── ResponseFormatter # Formats responses

utils/
└── ai_chat/
    ├── __init__.py
    ├── gemini_client.py    # Gemini API wrapper
    ├── vector_store.py     # ChromaDB operations
    ├── sql_generator.py    # SQL query generation
    ├── chat_history.py     # Database operations
    └── prompts.py          # Prompt templates
```

#### 2.2 Database Schema

**New Table: `chat_history`**
```sql
CREATE TABLE chat_history (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_id TEXT NOT NULL,  -- UUID for grouping messages
    message TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER DEFAULT 0,
    query_type TEXT,  -- 'data', 'navigation', 'help', etc.
    sql_query TEXT,  -- Generated SQL (if applicable)
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_chat_user ON chat_history(user_id);
CREATE INDEX idx_chat_conversation ON chat_history(conversation_id);
CREATE INDEX idx_chat_timestamp ON chat_history(timestamp);
```

**Migration Script**: `migrations/add_chat_history_table.py`

#### 2.3 ChromaDB Vector Store

**Purpose**: Store schema embeddings for semantic search

**Collections**:
1. **schema_collection**: Table and column descriptions
2. **query_patterns_collection**: Common query patterns
3. **platform_knowledge_collection**: Page descriptions and navigation

**Schema Embedding Example**:
```python
{
    "id": "admissions_metrics_table",
    "metadata": {
        "type": "table",
        "name": "admissions_metrics",
        "description": "Core admissions funnel metrics",
        "columns": ["program_code", "cohort_year", "metric_name", "metric_value", "date"]
    },
    "document": "Table: admissions_metrics. Contains inquiries, applications, admits, enrolled, deposits, confirmed for each program and cohort."
}
```

**Initialization**:
```python
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB (persistent)
client = chromadb.PersistentClient(path=".chromadb")
collection = client.get_or_create_collection("schema_collection")

# Embed schema on first run
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight
```

---

### 3. Query Processing Pipeline

#### 3.1 Query Flow
```
User Input
    ↓
1. Authentication Check
    ↓
2. Query Classification
    ├─→ Data Query (SQL generation)
    ├─→ Navigation Query (page recommendation)
    ├─→ Help Query (platform knowledge)
    └─→ Conversational (context-aware response)
    ↓
3. Context Retrieval (ChromaDB)
    ↓
4. Prompt Construction
    ↓
5. Gemini API Call
    ↓
6. Response Processing
    ├─→ SQL Validation (if data query)
    ├─→ SQL Execution
    └─→ Result Formatting
    ↓
7. Response Delivery
    ↓
8. History Storage
```

#### 3.2 Query Classification

**Classifier Logic**:
```python
def classify_query(user_message: str) -> str:
    """Classify query type using keywords and patterns."""
    
    # Data queries
    if any(word in user_message.lower() for word in 
           ['how many', 'show me', 'what is', 'count', 'total']):
        return 'data'
    
    # Navigation queries
    if any(word in user_message.lower() for word in 
           ['where', 'which page', 'how do i', 'navigate']):
        return 'navigation'
    
    # Help queries
    if any(word in user_message.lower() for word in 
           ['what does', 'explain', 'help', 'how to use']):
        return 'help'
    
    # Default: conversational
    return 'conversational'
```

#### 3.3 Prompt Templates

**Data Query Prompt**:
```python
DATA_QUERY_PROMPT = """
You are a SQL expert for the Mays Analytics Platform database.

Database Schema:
{schema_context}

User Question: {user_question}

Previous Context: {conversation_history}

Generate a valid SQLite query to answer the question.
Return ONLY the SQL query, no explanations.

Rules:
- Use proper table and column names from schema
- Include appropriate WHERE clauses
- Format dates as 'YYYY-MM-DD'
- Limit results to 100 rows
- Use aggregations when appropriate

SQL Query:
"""
```

**Navigation Query Prompt**:
```python
NAVIGATION_PROMPT = """
You are a helpful guide for the Mays Analytics Platform.

Platform Pages:
{platform_knowledge}

User Question: {user_question}

Recommend the best page and provide step-by-step navigation instructions.
Include which filters to apply.

Response format:
**Recommended Page**: [Page Name]
**Why**: [Brief explanation]
**Steps**:
1. [Step 1]
2. [Step 2]
...
"""
```

---

### 4. Gemini Integration

#### 4.1 API Configuration
```python
# utils/ai_chat/gemini_client.py
import google.generativeai as genai
import streamlit as st

class GeminiClient:
    def __init__(self):
        # Load API key from Streamlit secrets
        api_key = st.secrets.get("gemini_api_key", "")
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash (free tier)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generation config
        self.config = {
            'temperature': 0.1,  # Low for accuracy
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 1024,
        }
    
    def generate(self, prompt: str) -> str:
        """Generate response from Gemini."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.config
            )
            return response.text
        except Exception as e:
            st.error(f"Gemini API error: {str(e)}")
            return None
```

#### 4.2 Token Optimization
- Use concise prompts (< 500 tokens context)
- Retrieve only relevant schema elements (semantic search)
- Limit conversation history to last 5 exchanges
- Cache common query patterns

#### 4.3 Rate Limiting
```python
# Free tier limits: 15 requests/minute
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = deque()
    
    def allow_request(self, user_id: int) -> bool:
        """Check if user can make request."""
        now = time.time()
        
        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()
        
        # Check limit
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
```

---

### 5. Response Formatting

#### 5.1 Data Response Format
```python
def format_data_response(query_result, user_question):
    """Format SQL query results into readable response."""
    
    if not query_result:
        return "No data found for your query."
    
    # For single value
    if len(query_result) == 1 and len(query_result[0]) == 1:
        value = query_result[0][0]
        return f"**Answer**: {format_number(value)}"
    
    # For multiple rows
    response = f"**Results for**: {user_question}\n\n"
    
    # Format as table or bullet points
    if len(query_result) <= 10:
        # Show all rows
        for row in query_result:
            response += f"- {format_row(row)}\n"
    else:
        # Show summary
        response += f"Found {len(query_result)} results. Here are the top 10:\n\n"
        for row in query_result[:10]:
            response += f"- {format_row(row)}\n"
    
    return response
```

#### 5.2 Number Formatting
```python
def format_number(value):
    """Format numbers with proper separators."""
    if isinstance(value, (int, float)):
        if value >= 1000:
            return f"{value:,}"
        elif isinstance(value, float):
            return f"{value:.2f}"
    return str(value)
```

---

### 6. Chat History Management

#### 6.1 Storage Operations
```python
# utils/ai_chat/chat_history.py
import sqlite3
import uuid
from datetime import datetime

class ChatHistory:
    def __init__(self, db_path='edulytix.db'):
        self.db_path = db_path
    
    def save_message(self, user_id, conversation_id, message, role, 
                     tokens_used=0, query_type=None, sql_query=None):
        """Save a message to chat history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history 
            (user_id, conversation_id, message, role, tokens_used, query_type, sql_query)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, conversation_id, message, role, tokens_used, query_type, sql_query))
        
        conn.commit()
        conn.close()
    
    def get_conversation(self, user_id, conversation_id, limit=10):
        """Retrieve conversation history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message, role, timestamp 
            FROM chat_history
            WHERE user_id = ? AND conversation_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, conversation_id, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        return list(reversed(messages))  # Chronological order
    
    def get_user_conversations(self, user_id):
        """Get all conversations for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT conversation_id, 
                   MIN(timestamp) as started_at,
                   MAX(timestamp) as last_message_at,
                   COUNT(*) as message_count
            FROM chat_history
            WHERE user_id = ?
            GROUP BY conversation_id
            ORDER BY last_message_at DESC
        ''', (user_id,))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return conversations
    
    def delete_conversation(self, user_id, conversation_id):
        """Delete a conversation (soft delete)."""
        # Implement soft delete or hard delete based on requirements
        pass
```

#### 6.2 Conversation Context
```python
def get_conversation_context(user_id, conversation_id, limit=5):
    """Get recent conversation for context."""
    history = ChatHistory()
    messages = history.get_conversation(user_id, conversation_id, limit)
    
    context = ""
    for msg, role, timestamp in messages:
        context += f"{role.capitalize()}: {msg}\n"
    
    return context
```

---

### 7. Security & Privacy

#### 7.1 Input Sanitization
```python
def sanitize_input(user_input: str) -> str:
    """Sanitize user input to prevent injection."""
    # Remove SQL keywords that could be malicious
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    
    for keyword in dangerous_keywords:
        if keyword in user_input.upper():
            raise ValueError(f"Input contains forbidden keyword: {keyword}")
    
    return user_input.strip()
```

#### 7.2 SQL Validation
```python
def validate_sql(sql_query: str) -> bool:
    """Validate generated SQL is safe."""
    # Only allow SELECT statements
    if not sql_query.strip().upper().startswith('SELECT'):
        return False
    
    # Check for dangerous operations
    dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'EXEC']
    if any(keyword in sql_query.upper() for keyword in dangerous):
        return False
    
    return True
```

#### 7.3 User Data Isolation
```python
def get_user_chat_history(user_id: int):
    """Ensure users only access their own chat history."""
    # Always filter by user_id from authenticated session
    current_user = auth.get_current_user()
    
    if current_user['user_id'] != user_id:
        raise PermissionError("Cannot access other user's chat history")
    
    # Proceed with query
    ...
```

---

### 8. Error Handling

#### 8.1 Error Types & Responses
```python
ERROR_MESSAGES = {
    'no_data': "I couldn't find any data matching your query. Try rephrasing or check the date range.",
    'sql_error': "I had trouble generating a valid query. Could you rephrase your question?",
    'api_error': "I'm having trouble connecting to the AI service. Please try again in a moment.",
    'rate_limit': "You've reached the query limit (10/minute). Please wait a moment.",
    'auth_required': "Please sign in to use the chat assistant.",
    'ambiguous': "Your question is a bit ambiguous. Could you be more specific? For example: 'How many MBA applications in 2025?'"
}
```

#### 8.2 Graceful Degradation
```python
def handle_query_error(error_type: str, user_question: str):
    """Provide helpful error messages."""
    base_message = ERROR_MESSAGES.get(error_type, "Something went wrong.")
    
    # Add suggestions
    if error_type == 'ambiguous':
        suggestions = get_similar_queries(user_question)
        base_message += f"\n\n**Did you mean**:\n"
        for suggestion in suggestions:
            base_message += f"- {suggestion}\n"
    
    return base_message
```

---

### 9. Performance Optimization

#### 9.1 Caching Strategy
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_schema_context(query_type: str):
    """Cache schema context for common query types."""
    # Retrieve from ChromaDB
    ...

@lru_cache(maxsize=50)
def get_common_query_result(query_hash: str):
    """Cache results for common queries."""
    # Check if query has been run recently
    ...
```

#### 9.2 Async Processing
```python
import asyncio

async def process_query_async(user_message: str):
    """Process query asynchronously for better UX."""
    # Show typing indicator
    with st.spinner("Thinking..."):
        # Parallel operations
        schema_task = asyncio.create_task(retrieve_schema())
        context_task = asyncio.create_task(get_conversation_context())
        
        schema, context = await asyncio.gather(schema_task, context_task)
        
        # Generate response
        response = await generate_response(user_message, schema, context)
    
    return response
```

---

### 10. Testing Strategy

#### 10.1 Unit Tests
```python
# tests/test_ai_chat.py
def test_query_classification():
    assert classify_query("How many MBA applications?") == 'data'
    assert classify_query("Where can I see trends?") == 'navigation'
    assert classify_query("What does Executive Dive show?") == 'help'

def test_sql_validation():
    assert validate_sql("SELECT * FROM admissions_metrics") == True
    assert validate_sql("DROP TABLE users") == False

def test_number_formatting():
    assert format_number(1234) == "1,234"
    assert format_number(12.345) == "12.35"
```

#### 10.2 Integration Tests
```python
def test_end_to_end_query():
    """Test complete query flow."""
    user_message = "How many MBA applications in 2025?"
    
    # Process query
    response = process_query(user_message, user_id=1)
    
    # Verify response
    assert response is not None
    assert "MBA" in response
    assert "2025" in response
```

---

## Implementation Checklist

### Phase 1: MVP (Week 1-2)
- [ ] Create `modules/ai_chat.py` with basic UI
- [ ] Implement floating chat button (auth-gated)
- [ ] Set up Gemini API client
- [ ] Create ChromaDB vector store
- [ ] Implement basic query classification
- [ ] Build SQL generation for simple queries
- [ ] Add response formatting
- [ ] Test with sample queries

### Phase 2: Chat History (Week 3)
- [ ] Create migration for `chat_history` table
- [ ] Implement `ChatHistory` class
- [ ] Add conversation storage
- [ ] Build conversation retrieval UI
- [ ] Add search functionality
- [ ] Implement export feature
- [ ] Add clear/delete options

### Phase 3: Navigation Intelligence (Week 4)
- [ ] Embed platform knowledge in ChromaDB
- [ ] Build navigation query handler
- [ ] Create page recommendation logic
- [ ] Add step-by-step guidance
- [ ] Implement deep linking (optional)

### Phase 4: Enhanced RAG (Week 5-6)
- [ ] Improve schema embeddings
- [ ] Add conversation memory (5 exchanges)
- [ ] Support complex queries (joins, aggregations)
- [ ] Enhance context retrieval
- [ ] Add query pattern recognition

### Phase 5: Optimization (Week 7)
- [ ] Implement caching
- [ ] Add rate limiting
- [ ] Optimize token usage
- [ ] Performance tuning
- [ ] Load testing

### Phase 6: Polish (Week 8)
- [ ] UI/UX refinements
- [ ] Error handling improvements
- [ ] Documentation
- [ ] User testing
- [ ] Production deployment

---

## Configuration

### Streamlit Secrets
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

### Environment Variables
```bash
# For local development
export GEMINI_API_KEY="your_api_key_here"
export CHROMADB_PATH=".chromadb"
```

---

## Deployment Considerations

### Streamlit Cloud
- Store Gemini API key in Streamlit secrets
- ChromaDB data persists in `.chromadb` folder
- SQLite database already deployed
- No additional infrastructure needed

### Monitoring
- Log query types and response times
- Track token usage per user
- Monitor error rates
- Alert on API failures

### Scaling
- Current design supports 10-50 concurrent users
- For 100+ users, consider:
  - Moving to Pinecone for vector storage
  - Adding Redis for caching
  - Using async processing
  - Load balancing

---

**Document Version**: 1.0  
**Created**: January 25, 2026  
**Status**: Ready for Implementation

