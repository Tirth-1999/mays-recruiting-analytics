"""
Query processing and SQL generation for AI chatbot
"""

import re
import sqlite3
import time
from typing import Optional, Dict, Any, List, Tuple

from .gemini_client import GeminiClient
from .vector_store import VectorStore
from .cache import QueryCache
from .metrics import MetricsTracker
from .prompts import (
    DATA_QUERY_PROMPT,
    NAVIGATION_PROMPT,
    HELP_PROMPT,
    CONVERSATIONAL_PROMPT,
    SCHEMA_CONTEXT_TEMPLATE,
    PLATFORM_KNOWLEDGE
)


class QueryProcessor:
    """Processes user queries and generates responses."""
    
    # Query pattern templates for common queries
    QUERY_PATTERNS = {
        'count_metric_program': {
            'pattern': r'how many (\w+) (?:for|in) (\w+\s?\w*)',
            'template': "SELECT metric_value FROM admissions_metrics WHERE program = '{program}' AND metric_name = '{metric}' ORDER BY report_date DESC LIMIT 1",
            'params': ['metric', 'program']
        },
        'count_metric_program_year': {
            'pattern': r'how many (\w+) (?:for|in) (\w+\s?\w*) in (\d{4})',
            'template': "SELECT SUM(metric_value) FROM admissions_metrics WHERE program = '{program}' AND metric_name = '{metric}' AND cohort_year = {year}",
            'params': ['metric', 'program', 'year']
        },
        'count_program_metric_year': {
            'pattern': r'how many (\w+\s?\w*) (\w+) in (\d{4})',
            'template': "SELECT SUM(metric_value) FROM admissions_metrics WHERE program = '{program}' AND metric_name = '{metric}' AND cohort_year = {year}",
            'params': ['program', 'metric', 'year']
        },
        'compare_programs': {
            'pattern': r'compare (\w+) between (\w+\s?\w*) and (\w+\s?\w*)',
            'template': "SELECT program, SUM(metric_value) as total FROM admissions_metrics WHERE metric_name = '{metric}' AND program IN ('{program1}', '{program2}') GROUP BY program",
            'params': ['metric', 'program1', 'program2']
        },
        'compare_years': {
            'pattern': r'compare (\w+) between (\d{4}) and (\d{4})',
            'template': "SELECT cohort_year, SUM(metric_value) as total FROM admissions_metrics WHERE metric_name = '{metric}' AND cohort_year IN ({year1}, {year2}) GROUP BY cohort_year",
            'params': ['metric', 'year1', 'year2']
        }
    }
    
    # Metric name mappings
    METRIC_MAPPINGS = {
        'applications': 'total_applications',
        'apps': 'total_applications',
        'applicants': 'total_applications',
        'inquiries': 'inquiries_received',
        'leads': 'inquiries_received',
        'enrolled': 'enrolled',
        'enrollments': 'enrolled',
        'admits': 'admits',
        'admitted': 'admits'
    }
    
    # Program name mappings (short code to full name)
    PROGRAM_MAPPINGS = {
        'mba': 'Flex Online MBA',
        'ms acct': 'Flex Online MS Accounting',
        'acct': 'Flex Online MS Accounting',
        'ms hrm': 'Flex Online MS Human Resource Management',
        'hrm': 'Flex Online MS Human Resource Management',
        'ms misy': 'Flex Online MS Management Information Systems',
        'misy': 'Flex Online MS Management Information Systems',
        'ms mktg': 'Flex Online MS Marketing',
        'mktg': 'Flex Online MS Marketing',
        'ms enld': 'Flex Online MS Entrepreneurial Leadership',
        'enld': 'Flex Online MS Entrepreneurial Leadership',
        'ms spba': 'Flex Online AI in Business Program',
        'spba': 'Flex Online AI in Business Program',
        'ai': 'Flex Online AI in Business Program'
    }
    
    def __init__(self, db_path: str = 'edulytix.db', enable_cache: bool = True, enable_metrics: bool = True):
        """
        Initialize query processor.
        
        Args:
            db_path: Path to SQLite database
            enable_cache: Enable response caching
            enable_metrics: Enable metrics tracking
        """
        self.db_path = db_path
        self.gemini_client = GeminiClient()
        self.vector_store = VectorStore()  # Auto-initializes embeddings
        
        # Initialize cache and metrics
        self.enable_cache = enable_cache
        self.enable_metrics = enable_metrics
        
        if enable_cache:
            self.cache = QueryCache(
                sql_cache_size=100,
                sql_ttl=300,  # 5 minutes
                response_cache_size=100,
                response_ttl=300  # 5 minutes
            )
        else:
            self.cache = None
        
        if enable_metrics:
            self.metrics = MetricsTracker(db_path)
        else:
            self.metrics = None
    
    def classify_query(self, user_message: str) -> str:
        """
        Classify query type using keywords and patterns.
        
        Args:
            user_message: User's question
            
        Returns:
            Query type: 'data', 'navigation', 'help', 'conversational', or 'out_of_scope'
        """
        message_lower = user_message.lower()
        
        # Check for out-of-scope queries first
        out_of_scope_indicators = [
            'apple', 'banana', 'weather', 'news', 'stock', 'price',
            'recipe', 'movie', 'song', 'game', 'joke', 'story',
            'calculate', 'math', 'solve', 'equation', '+ ', '- ', '* ', '/ ',
            'what is 2+2', 'who is', 'when was', 'where is the',
            'capital of', 'president', 'celebrity', 'sports', 'football'
        ]
        
        # Check if query is about platform-related topics
        platform_keywords = [
            'mba', 'acct', 'hrm', 'misy', 'mktg', 'enld', 'spba',
            'application', 'inquiry', 'inquiries', 'admit', 'enroll',
            'cohort', 'program', 'marketing', 'spend', 'roi',
            'dashboard', 'page', 'tool', 'analytics', 'data',
            'metric', 'report', 'chart', 'graph', 'filter'
        ]
        
        # If contains out-of-scope indicators and no platform keywords, mark as out of scope
        has_out_of_scope = any(indicator in message_lower for indicator in out_of_scope_indicators)
        has_platform_keyword = any(keyword in message_lower for keyword in platform_keywords)
        
        if has_out_of_scope and not has_platform_keyword:
            return 'out_of_scope'
        
        # Navigation queries - asking where to go or how to do something
        navigation_keywords = [
            'where', 'which page', 'how do i', 'navigate', 'go to',
            'find the page', 'show me where', 'take me to', 'where can i',
            'how to create', 'how to analyze', 'walk me through', 'guide me',
            'workflow', 'process', 'steps to'
        ]
        if any(keyword in message_lower for keyword in navigation_keywords):
            return 'navigation'
        
        # Data queries - asking for specific metrics or numbers
        data_keywords = [
            'how many', 'show me', 'what is', 'what are', 'count', 'total',
            'list', 'get', 'find', 'display', 'give me', 'tell me the number',
            'applications', 'enrollments', 'inquiries', 'admits', 'spend'
        ]
        if any(keyword in message_lower for keyword in data_keywords):
            return 'data'
        
        # Help queries - asking about platform features
        help_keywords = [
            'what does', 'explain', 'help', 'how to use', 'what is the',
            'tell me about', 'describe', 'what can'
        ]
        if any(keyword in message_lower for keyword in help_keywords):
            return 'help'
        
        # Default: conversational
        return 'conversational'
    
    def process_query(
        self,
        user_message: str,
        conversation_context: str = "",
        user_id: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user query and generate response.
        
        Args:
            user_message: User's question
            conversation_context: Previous conversation context
            user_id: User ID for metrics tracking
            conversation_id: Conversation ID for metrics tracking
            
        Returns:
            Dict with response, query_type, sql_query, tokens_used, cache_hit
        """
        start_time = time.time()
        cache_hit = False
        pattern_matched = False
        
        # Check cache first
        if self.enable_cache and self.cache:
            cached_response = self.cache.get_response(user_message, conversation_context)
            if cached_response:
                cache_hit = True
                response_time_ms = int((time.time() - start_time) * 1000)
                
                # Log metrics
                if self.enable_metrics and self.metrics and user_id:
                    self.metrics.log_query(
                        user_id=user_id,
                        conversation_id=conversation_id or "unknown",
                        query_type=cached_response.get('query_type', 'unknown'),
                        tokens_used=0,  # No tokens used for cached response
                        response_time_ms=response_time_ms,
                        cache_hit=True,
                        pattern_matched=False
                    )
                
                # Add cache indicator
                cached_response['cache_hit'] = True
                cached_response['response_time_ms'] = response_time_ms
                return cached_response
        
        # Classify query
        query_type = self.classify_query(user_message)
        
        # Handle out-of-scope queries
        if query_type == 'out_of_scope':
            result = {
                'response': "I'm sorry, but I can only answer questions about the Mays Analytics Platform, including:\n\n"
                           "• Admissions data (applications, inquiries, enrollments)\n"
                           "• Marketing metrics and ROI\n"
                           "• Platform navigation and features\n"
                           "• Program information and statistics\n\n"
                           "Please ask a question related to these topics.",
                'query_type': 'out_of_scope',
                'sql_query': None,
                'tokens_used': 0,
                'cache_hit': False,
                'pattern_matched': False
            }
            
            response_time_ms = int((time.time() - start_time) * 1000)
            result['response_time_ms'] = response_time_ms
            
            # Log metrics
            if self.enable_metrics and self.metrics and user_id:
                self.metrics.log_query(
                    user_id=user_id,
                    conversation_id=conversation_id or "unknown",
                    query_type='out_of_scope',
                    tokens_used=0,
                    response_time_ms=response_time_ms,
                    cache_hit=False,
                    pattern_matched=False
                )
            
            return result
        
        try:
            if query_type == 'data':
                result = self._process_data_query(user_message, conversation_context)
                pattern_matched = result.get('pattern_matched', False)
            elif query_type == 'navigation':
                result = self._process_navigation_query(user_message)
            elif query_type == 'help':
                result = self._process_help_query(user_message)
            else:
                result = self._process_conversational_query(user_message, conversation_context)
            
            # Add metadata
            response_time_ms = int((time.time() - start_time) * 1000)
            result['cache_hit'] = cache_hit
            result['response_time_ms'] = response_time_ms
            
            # Cache response
            if self.enable_cache and self.cache and not cache_hit:
                self.cache.set_response(user_message, conversation_context, result)
            
            # Log metrics
            if self.enable_metrics and self.metrics and user_id:
                self.metrics.log_query(
                    user_id=user_id,
                    conversation_id=conversation_id or "unknown",
                    query_type=result.get('query_type', 'unknown'),
                    tokens_used=result.get('tokens_used', 0),
                    response_time_ms=response_time_ms,
                    cache_hit=cache_hit,
                    pattern_matched=pattern_matched
                )
            
            return result
        
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            result = {
                'response': f"I encountered an error: {str(e)}\n\nCould you rephrase your question?",
                'query_type': query_type,
                'sql_query': None,
                'tokens_used': 0,
                'error': str(e),
                'cache_hit': False,
                'pattern_matched': False,
                'response_time_ms': response_time_ms
            }
            
            # Log metrics
            if self.enable_metrics and self.metrics and user_id:
                self.metrics.log_query(
                    user_id=user_id,
                    conversation_id=conversation_id or "unknown",
                    query_type='error',
                    tokens_used=0,
                    response_time_ms=response_time_ms,
                    cache_hit=False,
                    pattern_matched=False
                )
            
            return result
    
    def _process_data_query(
        self,
        user_message: str,
        conversation_context: str
    ) -> Dict[str, Any]:
        """Process data query - generate SQL and execute."""
        pattern_matched = False
        
        # Resolve references in the query
        resolved_message = self._resolve_references(user_message, conversation_context)
        
        # Try pattern matching first for faster response
        pattern_result = self._try_pattern_match(resolved_message)
        if pattern_result:
            sql_query = pattern_result
            pattern_matched = True
        else:
            # Fall back to LLM generation
            # Get relevant schema context
            schema_results = self.vector_store.search_schema(resolved_message, n_results=3)
            schema_context = SCHEMA_CONTEXT_TEMPLATE
            
            # Build prompt
            prompt = DATA_QUERY_PROMPT.format(
                schema_context=schema_context,
                user_question=resolved_message,
                conversation_history=conversation_context or "No previous context."
            )
            
            # Generate SQL
            sql_query = self.gemini_client.generate(prompt)
            
            if not sql_query:
                return {
                    'response': "I couldn't generate a query for that. Could you rephrase?",
                    'query_type': 'data',
                    'sql_query': None,
                    'tokens_used': 0,
                    'pattern_matched': False
                }
            
            # Clean SQL (remove markdown formatting if present)
            sql_query = self._clean_sql(sql_query)
        
        # Validate SQL
        if not self.validate_sql(sql_query):
            return {
                'response': "I generated an invalid query. Could you rephrase your question more specifically?",
                'query_type': 'data',
                'sql_query': sql_query,
                'tokens_used': self.gemini_client.get_token_usage(),
                'pattern_matched': pattern_matched
            }
        
        # Check SQL result cache
        cached_result = None
        if self.enable_cache and self.cache:
            cached_result = self.cache.get_sql_result(sql_query)
        
        # Execute SQL if not cached
        if cached_result is not None:
            results = cached_result
        else:
            results = self.execute_sql(sql_query)
            
            # Cache SQL result
            if self.enable_cache and self.cache and results is not None:
                self.cache.set_sql_result(sql_query, results)
        
        if results is None:
            return {
                'response': "I had trouble executing the query. The data might not be available.",
                'query_type': 'data',
                'sql_query': sql_query,
                'tokens_used': self.gemini_client.get_token_usage(),
                'pattern_matched': pattern_matched
            }
        
        # Format response with context indicator
        response = self.format_results(results, resolved_message)
        
        # Add context indicator if references were resolved
        if resolved_message != user_message:
            response = f"_Based on our previous conversation..._\n\n{response}"
        
        return {
            'response': response,
            'query_type': 'data',
            'sql_query': sql_query,
            'tokens_used': self.gemini_client.get_token_usage() if not pattern_matched else 0,
            'pattern_matched': pattern_matched
        }
    
    def _try_pattern_match(self, user_message: str) -> Optional[str]:
        """
        Try to match user query to a known pattern and generate SQL from template.
        
        Args:
            user_message: User's question
            
        Returns:
            SQL query if pattern matched, None otherwise
        """
        import re
        
        message_lower = user_message.lower()
        
        for pattern_name, pattern_info in self.QUERY_PATTERNS.items():
            match = re.search(pattern_info['pattern'], message_lower)
            if match:
                # Extract parameters
                params = {}
                for i, param_name in enumerate(pattern_info['params']):
                    value = match.group(i + 1)
                    
                    # Map metric names
                    if param_name == 'metric':
                        value = self.METRIC_MAPPINGS.get(value, value)
                    
                    # Map program names (short code to full name)
                    if param_name in ['program', 'program1', 'program2']:
                        value_lower = value.lower()
                        # Try to map short code to full name
                        value = self.PROGRAM_MAPPINGS.get(value_lower, value)
                    
                    params[param_name] = value
                
                # Generate SQL from template
                try:
                    sql = pattern_info['template'].format(**params)
                    return sql
                except KeyError:
                    # Missing parameter, fall back to LLM
                    return None
        
        return None
    
    def _resolve_references(self, user_message: str, conversation_context: str) -> str:
        """
        Resolve pronouns and references in user message using conversation context.
        
        Args:
            user_message: Current user message
            conversation_context: Previous conversation context
            
        Returns:
            Message with resolved references
        """
        if not conversation_context or conversation_context == "No previous context.":
            return user_message
        
        message_lower = user_message.lower()
        
        # Extract entities from context - use full program names
        programs = [
            'flex online mba', 'flex online ms accounting', 'flex online ms human resource management',
            'flex online ms management information systems', 'flex online ms marketing',
            'flex online ms entrepreneurial leadership', 'flex online ai in business program',
            # Also check for short codes
            'mba', 'ms acct', 'acct', 'ms hrm', 'hrm', 'ms misy', 'misy', 
            'ms mktg', 'mktg', 'ms enld', 'enld', 'ms spba', 'spba'
        ]
        metrics = ['applications', 'inquiries', 'admits', 'enrolled', 'deposits', 'confirmed']
        years = ['2024', '2025', '2026']
        
        # Find last mentioned program
        last_program = None
        for program in programs:
            if program in conversation_context.lower():
                last_program = program
                # Convert short code to full name if needed
                if last_program in self.PROGRAM_MAPPINGS:
                    last_program = self.PROGRAM_MAPPINGS[last_program]
                break
        
        # Find last mentioned metric
        last_metric = None
        for metric in metrics:
            if metric in conversation_context.lower():
                last_metric = metric
        
        # Find last mentioned year
        last_year = None
        for year in years:
            if year in conversation_context:
                last_year = year
        
        resolved = user_message
        
        # Resolve "it", "that", "this"
        if any(word in message_lower for word in ['it', 'that', 'this']):
            if last_program:
                resolved = resolved.replace('it', last_program)
                resolved = resolved.replace('that', last_program)
                resolved = resolved.replace('this', last_program)
        
        # Resolve "same"
        if 'same' in message_lower:
            if last_metric:
                resolved = resolved.replace('same', last_metric)
        
        # Resolve program references like "what about ACCT?"
        if 'what about' in message_lower or 'how about' in message_lower:
            # Extract the program mentioned after "what about"
            for program in programs:
                if program in message_lower:
                    # Convert to full name if it's a short code
                    full_program = self.PROGRAM_MAPPINGS.get(program, program)
                    # Add the last metric if available
                    if last_metric:
                        resolved = f"How many {last_metric} for {full_program}?"
                    break
        
        # Resolve year references like "for 2024"
        if 'for' in message_lower and any(year in message_lower for year in years):
            # Already has year, no need to resolve
            pass
        elif last_year and not any(year in message_lower for year in years):
            # Add last year if no year mentioned
            if last_metric and last_program:
                resolved = f"{resolved} in {last_year}"
        
        return resolved
    
    def _process_navigation_query(self, user_message: str) -> Dict[str, Any]:
        """Process navigation query - recommend page."""
        # Get relevant platform knowledge
        platform_results = self.vector_store.search_platform(user_message, n_results=2)
        
        # Build prompt
        prompt = NAVIGATION_PROMPT.format(
            platform_knowledge=PLATFORM_KNOWLEDGE,
            user_question=user_message
        )
        
        # Generate response
        response = self.gemini_client.generate(prompt)
        
        return {
            'response': response or "I couldn't find a good page recommendation. Could you be more specific?",
            'query_type': 'navigation',
            'sql_query': None,
            'tokens_used': self.gemini_client.get_token_usage()
        }
    
    def _process_help_query(self, user_message: str) -> Dict[str, Any]:
        """Process help query - explain platform features."""
        # Build prompt
        prompt = HELP_PROMPT.format(
            platform_knowledge=PLATFORM_KNOWLEDGE,
            user_question=user_message
        )
        
        # Generate response
        response = self.gemini_client.generate(prompt)
        
        return {
            'response': response or "I couldn't find information about that. Could you rephrase?",
            'query_type': 'help',
            'sql_query': None,
            'tokens_used': self.gemini_client.get_token_usage()
        }
    
    def _process_conversational_query(
        self,
        user_message: str,
        conversation_context: str
    ) -> Dict[str, Any]:
        """Process conversational query - general chat."""
        # Build prompt
        prompt = CONVERSATIONAL_PROMPT.format(
            conversation_history=conversation_context or "No previous context.",
            user_question=user_message
        )
        
        # Generate response
        response = self.gemini_client.generate(prompt)
        
        return {
            'response': response or "I'm here to help with the Mays Analytics Platform. What would you like to know?",
            'query_type': 'conversational',
            'sql_query': None,
            'tokens_used': self.gemini_client.get_token_usage()
        }
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL query by removing markdown formatting."""
        # Remove markdown code blocks
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```\s*', '', sql)
        
        # Remove extra whitespace
        sql = sql.strip()
        
        return sql
    
    def validate_sql(self, sql_query: str) -> bool:
        """
        Validate generated SQL is safe.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not sql_query:
            return False
        
        sql_upper = sql_query.upper().strip()
        
        # Only allow SELECT statements
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Check for dangerous operations
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE']
        if any(keyword in sql_upper for keyword in dangerous):
            return False
        
        return True
    
    def execute_sql(self, sql_query: str) -> Optional[List[Tuple]]:
        """
        Execute SQL query safely.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            Query results or None if error
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            return results
        
        except sqlite3.Error as e:
            print(f"SQL execution error: {e}")
            return None
        
        finally:
            conn.close()
    
    def format_results(self, results: List[Tuple], user_question: str) -> str:
        """
        Format SQL results into readable response.
        
        Args:
            results: Query results
            user_question: Original question
            
        Returns:
            Formatted response string
        """
        if not results:
            return "No data found for your query. Try adjusting the date range or program."
        
        # Single value result
        if len(results) == 1 and len(results[0]) == 1:
            value = results[0][0]
            formatted_value = self._format_number(value)
            return f"**Answer**: {formatted_value}"
        
        # Multiple rows
        response = f"**Results**:\n\n"
        
        # Show up to 10 rows
        display_count = min(len(results), 10)
        
        for i, row in enumerate(results[:display_count]):
            formatted_row = " | ".join([self._format_number(val) for val in row])
            response += f"{i+1}. {formatted_row}\n"
        
        if len(results) > 10:
            response += f"\n_Showing 10 of {len(results)} results_"
        
        return response
    
    def _format_number(self, value: Any) -> str:
        """Format numbers with proper separators."""
        if value is None:
            return "N/A"
        
        if isinstance(value, (int, float)):
            if isinstance(value, float) and value != int(value):
                return f"{value:,.2f}"
            else:
                return f"{int(value):,}"
        
        return str(value)


if __name__ == "__main__":
    # Test query processor
    print("Testing QueryProcessor...")
    
    processor = QueryProcessor()
    
    # Test queries
    test_queries = [
        "How many MBA applications in 2025?",
        "Where can I see year-over-year comparisons?",
        "What does the Director's Deep Dive show?",
        "Hello!"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        query_type = processor.classify_query(query)
        print(f"   Type: {query_type}")
    
    print("\n✅ QueryProcessor tests complete")
