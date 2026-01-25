# AI Chat Assistant - Deployment Checklist

## Pre-Deployment

### 1. Environment Setup

- [ ] **Gemini API Key**: Obtain API key from Google AI Studio
- [ ] **Streamlit Secrets**: Add API key to `.streamlit/secrets.toml`
- [ ] **Dependencies**: Verify all packages in `requirements.txt` are installed
- [ ] **Database**: Ensure `edulytix.db` exists and is accessible

### 2. Database Migrations

Run all required migrations in order:

```bash
# 1. Chat history table
python migrations/add_chat_history_table.py

# 2. Chat metrics table (created automatically by MetricsTracker)
# 3. Performance indexes
python migrations/add_chat_indexes.py

# 4. Feedback table
python migrations/add_feedback_table.py
```

Verify tables exist:
```bash
sqlite3 edulytix.db ".tables"
# Should show: chat_history, chat_metrics, chat_feedback
```

### 3. ChromaDB Setup

- [ ] **Directory**: Ensure `.chromadb` directory exists
- [ ] **Permissions**: Verify write permissions for ChromaDB
- [ ] **Initialization**: Run vector store initialization

```python
from utils.ai_chat import VectorStore
store = VectorStore()
store.initialize_schema_embeddings()
store.initialize_platform_embeddings()
```

### 4. Configuration Files

**`.streamlit/secrets.toml`**:
```toml
[gemini]
api_key = "YOUR_GEMINI_API_KEY_HERE"

[google_oauth]
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "YOUR_REDIRECT_URI"
```

**`requirements.txt`** (verify these are included):
```
google-generativeai>=0.3.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
```

## Deployment Steps

### Step 1: Code Preparation

1. **Commit Changes**:
```bash
git add .
git commit -m "feat: Add AI Chat Assistant v5.3"
git push origin main
```

2. **Create Tag**:
```bash
git tag -a v5.3 -m "Release v5.3: AI Chat Assistant"
git push origin v5.3
```

### Step 2: Streamlit Cloud Deployment

1. **Navigate to Streamlit Cloud**: https://share.streamlit.io
2. **Select Repository**: Choose your GitHub repository
3. **Configure App**:
   - Main file: `main_app.py`
   - Python version: 3.12
   - Branch: `main`

4. **Add Secrets** (CRITICAL STEP):
   - Go to App Settings → Secrets (or click ⚙️ → Secrets)
   - Add the following configuration:
   
   ```toml
   [gemini]
   api_key = "YOUR_ACTUAL_GEMINI_API_KEY"
   
   [chat]
   rate_limit_requests = 10
   rate_limit_window = 60
   max_conversation_history = 5
   token_limit_per_query = 1000
   
   [google_oauth]
   client_id = "YOUR_GOOGLE_CLIENT_ID"
   client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
   redirect_uri = "https://your-app.streamlit.app"
   
   [resend]
   api_key = "YOUR_RESEND_API_KEY"
   
   [email]
   contact_email = "your-email@example.com"
   from_email = "onboarding@resend.dev"
   ```
   
   - **Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Click "Create API Key" (it's free!)
   - Copy the key and paste it in the secrets
   - **IMPORTANT**: Replace ALL placeholder values with actual keys
   - Save the secrets

5. **Deploy**: Click "Deploy" or "Reboot" if already deployed

6. **Verify Deployment**:
   - Wait for app to rebuild (2-3 minutes)
   - Check logs for any errors
   - Test the AI Chat page
   - Verify authentication works

### Step 3: Post-Deployment Verification

#### 3.1 Basic Functionality

- [ ] App loads without errors
- [ ] OAuth authentication works
- [ ] Chat page is accessible
- [ ] Can send and receive messages

#### 3.2 Chat Features

- [ ] Simple queries work: "How many MBA applications in 2026?"
- [ ] Pattern matching works (< 10ms response)
- [ ] Caching works (instant on repeat queries)
- [ ] Rate limiting works (10 queries/min)
- [ ] Chat history saves correctly
- [ ] Search and export work

#### 3.3 Error Handling

- [ ] Invalid queries show helpful errors
- [ ] API failures are handled gracefully
- [ ] Rate limit messages are clear
- [ ] Database errors don't crash app

#### 3.4 Performance

- [ ] Response time < 3s for 80% of queries
- [ ] Response time < 5s for 95% of queries
- [ ] Chat history loads < 1s
- [ ] No memory leaks after extended use

### Step 4: Monitoring Setup

#### 4.1 Metrics to Monitor

1. **Usage Metrics**:
   - Query volume per day
   - Active users per day
   - Queries per user
   - Peak usage times

2. **Performance Metrics**:
   - Average response time
   - P95/P99 response times
   - Cache hit rate
   - Pattern match rate

3. **Quality Metrics**:
   - Error rate
   - User satisfaction (feedback)
   - Token usage
   - API quota usage

#### 4.2 Monitoring Queries

```python
# Get usage stats
from utils.ai_chat import MetricsTracker
tracker = MetricsTracker()

# Token usage
token_stats = tracker.get_token_stats(days=7)
print(f"Avg tokens: {token_stats['average']}")

# Response times
response_stats = tracker.get_response_time_stats(days=7)
print(f"Avg response time: {response_stats['average']}ms")

# Cache performance
cache_rate = tracker.get_cache_hit_rate(days=7)
print(f"Cache hit rate: {cache_rate:.1f}%")

# Pattern matching
pattern_rate = tracker.get_pattern_match_rate(days=7)
print(f"Pattern match rate: {pattern_rate:.1f}%")
```

#### 4.3 Feedback Analysis

```python
from utils.ai_chat import ChatHistory
history = ChatHistory()

# Get feedback stats
feedback_stats = history.get_feedback_stats(days=7)
print(f"Satisfaction rate: {feedback_stats['satisfaction_rate']:.1f}%")
print(f"Total feedback: {feedback_stats['total_feedback']}")
```

## Rollback Plan

### If Issues Occur

1. **Immediate Actions**:
   - Check Streamlit Cloud logs
   - Verify secrets are configured
   - Check database connectivity
   - Verify ChromaDB persistence

2. **Rollback Procedure**:

```bash
# Revert to previous version
git revert HEAD
git push origin main

# Or rollback to specific tag
git checkout v5.2
git push origin main --force
```

3. **Database Rollback** (if needed):

```bash
# Remove chat indexes
python migrations/add_chat_indexes.py rollback

# Remove feedback table
python migrations/add_feedback_table.py rollback

# Remove chat history (CAUTION: deletes all chat data)
# python migrations/add_chat_history_table.py rollback
```

4. **Communication**:
   - Notify users of temporary issues
   - Provide ETA for resolution
   - Offer alternative (Data Explorer)

## Maintenance

### Daily

- [ ] Check error logs
- [ ] Monitor query volume
- [ ] Check API quota usage

### Weekly

- [ ] Review performance metrics
- [ ] Analyze user feedback
- [ ] Check token usage trends
- [ ] Review cache hit rates

### Monthly

- [ ] Clean up old conversations (90+ days)
- [ ] Analyze query patterns
- [ ] Update pattern library if needed
- [ ] Review and optimize prompts

### Quarterly

- [ ] Review user satisfaction
- [ ] Identify improvement opportunities
- [ ] Update documentation
- [ ] Plan feature enhancements

## Troubleshooting

### Common Issues

#### Issue: "API key not found"

**Solution**:
1. Check Streamlit secrets are configured
2. Verify secret key name matches code
3. Restart app after adding secrets

#### Issue: "ChromaDB collection not found"

**Solution**:
1. Check `.chromadb` directory exists
2. Run initialization script
3. Verify write permissions

#### Issue: "High response times"

**Solution**:
1. Check cache hit rate
2. Verify indexes are created
3. Review query patterns
4. Consider increasing cache size

#### Issue: "Rate limit errors"

**Solution**:
1. Check if legitimate high usage
2. Adjust rate limits if needed
3. Verify rate limiter is working
4. Check for abuse patterns

## Security Checklist

- [ ] API keys are in secrets (not code)
- [ ] SQL injection protection enabled
- [ ] User data isolation verified
- [ ] Authentication required for all operations
- [ ] Rate limiting prevents abuse
- [ ] Error messages don't expose sensitive info
- [ ] GDPR compliance (data deletion)

## Performance Benchmarks

### Target Metrics

- **Response Time**: 
  - P50: < 1s
  - P80: < 3s
  - P95: < 5s

- **Cache Hit Rate**: > 30%
- **Pattern Match Rate**: > 80%
- **Token Usage**: < 1000 tokens/query avg
- **User Satisfaction**: > 80%
- **Error Rate**: < 10%

### Load Capacity

- **Concurrent Users**: 10+
- **Queries per Minute**: 100 (global)
- **Queries per User**: 10/min
- **Database Size**: Monitor growth

## Support Contacts

- **Platform Admin**: [Your contact]
- **Technical Support**: [Your contact]
- **Emergency**: [Your contact]

---

**Version**: 5.3  
**Last Updated**: January 25, 2026  
**Status**: Production Ready
