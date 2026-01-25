# AI Chat Assistant - User Guide

## Overview

The AI Chat Assistant is your intelligent companion for exploring the Mays Analytics Platform. Ask questions in natural language and get instant answers about admissions data, marketing metrics, and platform navigation.

## Getting Started

### Accessing the Chat

1. **Sign In**: You must be signed in with your Google account to use the chat
2. **Find the Chat**: Look for the chat icon in the navigation or go to the AI Chat page
3. **Start Chatting**: Type your question and press Enter or click Send

### Your First Query

Try these example queries to get started:

```
How many MBA applications in 2026?
Show me inquiries for MS ACCT
Where can I see year-over-year comparisons?
What does the Executive Deep Dive show?
```

## What You Can Ask

### 1. Data Queries

Ask about specific metrics and numbers:

**Applications & Enrollments:**
- "How many MBA applications in 2026?"
- "Show me total applications for MS ACCT"
- "How many students enrolled in MS MKTG?"

**Inquiries & Leads:**
- "How many inquiries for MBA?"
- "Show me inquiries received for all programs"

**Comparisons:**
- "Compare MBA applications between 2024 and 2025"
- "Compare enrollments for MBA and MS ACCT"

**Trends:**
- "What's the growth rate for MBA applications?"
- "Show me application trends over time"

### 2. Navigation Queries

Get help finding the right page:

**Finding Pages:**
- "Where can I see year-over-year comparisons?"
- "Which page shows marketing ROI?"
- "How do I access the Data Explorer?"

**Workflows:**
- "How do I create a program performance report?"
- "Walk me through analyzing marketing effectiveness"
- "How do I forecast future enrollments?"

### 3. Help Queries

Learn about platform features:

**Understanding Features:**
- "What does the Executive Deep Dive show?"
- "Explain the Comparison Tool"
- "What metrics are available?"

**Getting Help:**
- "What can you help me with?"
- "Show me example queries"
- "How do I use this chat?"

## Tips for Best Results

### ✅ DO:

1. **Be Specific**: Include program names, years, and metrics
   - Good: "How many MBA applications in 2026?"
   - Bad: "Show me applications"

2. **Use Program Codes**: MBA, MS ACCT, MS HRM, MS MISY, MS MKTG, MS ENLD, MS SPBA
   - Good: "How many inquiries for MS ACCT?"
   - Bad: "How many inquiries for accounting?"

3. **Ask Follow-up Questions**: The chat remembers context
   - First: "How many MBA applications?"
   - Then: "What about ACCT?" (it knows you mean applications)

4. **Use Natural Language**: Ask like you're talking to a colleague
   - "Show me MBA applications for 2026"
   - "Compare MBA and ACCT enrollments"

### ❌ DON'T:

1. **Don't Ask Off-Topic Questions**: Stick to platform-related queries
   - ❌ "What's the weather today?"
   - ✅ "What's the enrollment trend for MBA?"

2. **Don't Use Vague Terms**: Be specific about what you want
   - ❌ "Show me data"
   - ✅ "Show me MBA applications in 2026"

3. **Don't Expect Real-Time Data**: Data is updated periodically
   - ❌ "How many applications today?"
   - ✅ "How many applications in 2026?"

## Features

### 💬 Conversation History

- **View Past Conversations**: Access all your previous chats in the "Chat History" tab
- **Search Messages**: Find specific conversations using the search bar
- **Export Data**: Download your chat history as JSON
- **Delete Conversations**: Remove conversations you no longer need

### ⚡ Rate Limiting

To ensure fair usage and system stability:

- **Limit**: 10 queries per minute per user
- **Indicator**: See remaining queries in the chat header
- **Reset**: Counter resets every minute
- **Message**: You'll see a friendly message if you hit the limit

### 🎯 Smart Features

1. **Pattern Matching**: Common queries get instant responses (< 10ms)
2. **Caching**: Repeated queries are served from cache (instant)
3. **Context Awareness**: Remembers your last 3-5 exchanges
4. **Reference Resolution**: Understands "it", "that", "same" in follow-ups

### 🔒 Privacy & Data

- **Your Data**: Only you can see your chat history
- **Retention**: Conversations older than 90 days are automatically deleted
- **Export**: Download your data anytime
- **GDPR**: Request complete data deletion in Settings & Privacy

## Troubleshooting

### "I'm getting an error message"

**Common Causes:**
1. **API Issue**: Wait a moment and try again
2. **Invalid Query**: Rephrase your question more specifically
3. **Rate Limit**: Wait for the counter to reset
4. **Database Error**: Try a simpler query or use Data Explorer

**What to Do:**
- Read the error message carefully - it often suggests solutions
- Try rephrasing your question
- Use one of the example queries
- Check the Data Explorer for raw data access

### "The chat isn't understanding my question"

**Tips:**
1. **Be More Specific**: Include program name, year, and metric
2. **Use Program Codes**: MBA, MS ACCT, etc.
3. **Check Spelling**: Ensure program names are correct
4. **Try Examples**: Start with a working example and modify it

### "I can't find my old conversations"

**Solutions:**
1. **Check Chat History Tab**: All conversations are listed there
2. **Use Search**: Search for keywords from your conversation
3. **Check Retention**: Conversations older than 90 days are deleted
4. **Export Regularly**: Download important conversations

### "The response is slow"

**Reasons:**
1. **Complex Query**: Joins and aggregations take longer
2. **First Query**: Initial queries may be slower (no cache)
3. **High Load**: Many users querying simultaneously

**Solutions:**
- Simplify your query
- Try again (cached responses are instant)
- Use pattern-matched queries (see examples above)

## Example Workflows

### Workflow 1: Analyze Program Performance

```
1. "How many MBA applications in 2026?"
2. "How many enrolled?"
3. "What's the conversion rate?"
4. "Compare with 2025"
```

### Workflow 2: Marketing ROI Analysis

```
1. "Where can I see marketing ROI?"
   → Bot recommends Marketing Analysis page
2. Navigate to Marketing Analysis
3. "How much did we spend on MBA marketing?"
4. "What's the cost per application?"
```

### Workflow 3: Year-over-Year Comparison

```
1. "Compare MBA applications between 2024 and 2025"
2. "What about enrollments?"
3. "Show me the growth rate"
```

## Advanced Features

### Context-Aware Queries

The chat remembers your recent questions:

```
You: "How many MBA applications in 2026?"
Bot: "There are 3,557 MBA applications in 2026."

You: "What about ACCT?"
Bot: "There are 1,234 applications for MS ACCT in 2026."
     (Understands you mean applications)

You: "Show me the same for 2025"
Bot: "There are 1,100 applications for MS ACCT in 2025."
     (Remembers both program and metric)
```

### Pattern-Matched Queries

These queries get instant responses (< 10ms):

- "How many [metric] for [program]?"
- "How many [program] [metric] in [year]?"
- "Compare [metric] between [program1] and [program2]"
- "Compare [metric] between [year1] and [year2]"

### Suggested Queries

After each response, the chat may suggest related queries:

- "Would you like to see this for other programs?"
- "Want to compare with last year?"
- "Interested in the conversion rate?"

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message
- **Esc**: Close chat window (if floating)

## Support

### Need Help?

1. **In-App Help**: Click the help button in the chat header
2. **Documentation**: Visit the Help page
3. **Examples**: Type "show me examples" in the chat
4. **Contact**: Reach out to your platform administrator

### Feedback

Help us improve! Use the thumbs up/down buttons on bot responses to rate your experience.

---

**Version**: 5.3  
**Last Updated**: January 25, 2026  
**Platform**: Mays Analytics Platform
