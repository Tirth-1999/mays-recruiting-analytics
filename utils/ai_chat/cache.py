"""
Caching utilities for AI chatbot responses
"""

import hashlib
import time
from typing import Optional, Dict, Any, Tuple
from collections import OrderedDict
from datetime import datetime, timedelta


class LRUCache:
    """Least Recently Used cache with time-based expiration."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries
            ttl_seconds: Time to live in seconds (default 5 minutes)
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if cache entry is expired."""
        age = time.time() - entry['timestamp']
        return age > self.ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if self._is_expired(entry):
            del self.cache[key]
            self.misses += 1
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        
        return entry['value']
    
    def set(self, key: str, value: Any):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
        
        # Add/update entry
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        
        # Move to end
        self.cache.move_to_end(key)
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }


class QueryCache:
    """Cache for SQL query results and bot responses."""
    
    def __init__(
        self,
        sql_cache_size: int = 100,
        sql_ttl: int = 300,
        response_cache_size: int = 100,
        response_ttl: int = 300
    ):
        """
        Initialize query cache.
        
        Args:
            sql_cache_size: Max SQL result cache entries
            sql_ttl: SQL cache TTL in seconds
            response_cache_size: Max response cache entries
            response_ttl: Response cache TTL in seconds
        """
        self.sql_cache = LRUCache(max_size=sql_cache_size, ttl_seconds=sql_ttl)
        self.response_cache = LRUCache(max_size=response_cache_size, ttl_seconds=response_ttl)
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query string."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get_sql_result(self, sql_query: str) -> Optional[Any]:
        """
        Get cached SQL query result.
        
        Args:
            sql_query: SQL query string
            
        Returns:
            Cached result or None
        """
        key = self._hash_query(sql_query)
        return self.sql_cache.get(key)
    
    def set_sql_result(self, sql_query: str, result: Any):
        """
        Cache SQL query result.
        
        Args:
            sql_query: SQL query string
            result: Query result to cache
        """
        key = self._hash_query(sql_query)
        self.sql_cache.set(key, result)
    
    def get_response(self, user_query: str, context: str = "") -> Optional[Dict]:
        """
        Get cached bot response.
        
        Args:
            user_query: User's question
            context: Conversation context
            
        Returns:
            Cached response dict or None
        """
        # Include context in cache key for context-aware caching
        cache_key = f"{user_query}|{context}"
        key = self._hash_query(cache_key)
        return self.response_cache.get(key)
    
    def set_response(self, user_query: str, context: str, response: Dict):
        """
        Cache bot response.
        
        Args:
            user_query: User's question
            context: Conversation context
            response: Response dict to cache
        """
        # Add timestamp to cached response
        response_with_meta = response.copy()
        response_with_meta['cached_at'] = datetime.now().isoformat()
        
        cache_key = f"{user_query}|{context}"
        key = self._hash_query(cache_key)
        self.response_cache.set(key, response_with_meta)
    
    def clear_all(self):
        """Clear all caches."""
        self.sql_cache.clear()
        self.response_cache.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'sql_cache': self.sql_cache.get_stats(),
            'response_cache': self.response_cache.get_stats()
        }


if __name__ == "__main__":
    # Test caching
    print("Testing QueryCache...")
    
    cache = QueryCache()
    
    # Test SQL caching
    sql = "SELECT * FROM admissions_metrics WHERE program = 'MBA'"
    result = [(1, 'MBA', 2025, 'total_applications', 100)]
    
    print("\n📝 Testing SQL Cache:")
    print(f"   Set: {sql[:50]}...")
    cache.set_sql_result(sql, result)
    
    cached = cache.get_sql_result(sql)
    print(f"   Get: {'✅ Hit' if cached else '❌ Miss'}")
    print(f"   Result: {cached}")
    
    # Test response caching
    print("\n📝 Testing Response Cache:")
    query = "How many MBA applications?"
    context = "No previous context."
    response = {
        'response': 'There are 3,557 MBA applications.',
        'query_type': 'data',
        'sql_query': sql,
        'tokens_used': 500
    }
    
    print(f"   Set: {query}")
    cache.set_response(query, context, response)
    
    cached_response = cache.get_response(query, context)
    print(f"   Get: {'✅ Hit' if cached_response else '❌ Miss'}")
    if cached_response:
        print(f"   Cached at: {cached_response.get('cached_at')}")
    
    # Test cache stats
    print("\n📊 Cache Stats:")
    stats = cache.get_stats()
    print(f"   SQL Cache: {stats['sql_cache']}")
    print(f"   Response Cache: {stats['response_cache']}")
    
    print("\n✅ QueryCache tests complete")
