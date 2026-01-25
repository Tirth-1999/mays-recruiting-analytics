"""
Metrics tracking for AI chatbot performance monitoring
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import statistics


class MetricsTracker:
    """Tracks and analyzes chatbot performance metrics."""
    
    def __init__(self, db_path: str = 'edulytix.db'):
        """
        Initialize metrics tracker.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ensure_metrics_table()
    
    def _ensure_metrics_table(self):
        """Create metrics table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                conversation_id TEXT,
                query_type TEXT,
                tokens_used INTEGER,
                response_time_ms INTEGER,
                cache_hit BOOLEAN DEFAULT 0,
                pattern_matched BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Add index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_metrics_timestamp 
            ON chat_metrics(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_metrics_user 
            ON chat_metrics(user_id, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def log_query(
        self,
        user_id: int,
        conversation_id: str,
        query_type: str,
        tokens_used: int,
        response_time_ms: int,
        cache_hit: bool = False,
        pattern_matched: bool = False
    ):
        """
        Log a query metric.
        
        Args:
            user_id: User ID
            conversation_id: Conversation UUID
            query_type: Type of query
            tokens_used: Tokens consumed
            response_time_ms: Response time in milliseconds
            cache_hit: Whether response was cached
            pattern_matched: Whether query matched a pattern
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_metrics 
            (user_id, conversation_id, query_type, tokens_used, response_time_ms, cache_hit, pattern_matched)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, conversation_id, query_type, tokens_used, response_time_ms, cache_hit, pattern_matched))
        
        conn.commit()
        conn.close()
    
    def get_token_stats(self, days: int = 7) -> Dict:
        """
        Get token usage statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with token statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tokens_used
            FROM chat_metrics
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            AND tokens_used > 0
        """, (days,))
        
        tokens = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not tokens:
            return {
                'total': 0,
                'average': 0,
                'median': 0,
                'p95': 0,
                'p99': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }
        
        sorted_tokens = sorted(tokens)
        
        return {
            'total': sum(tokens),
            'average': statistics.mean(tokens),
            'median': statistics.median(tokens),
            'p95': sorted_tokens[int(len(sorted_tokens) * 0.95)] if len(sorted_tokens) > 0 else 0,
            'p99': sorted_tokens[int(len(sorted_tokens) * 0.99)] if len(sorted_tokens) > 0 else 0,
            'min': min(tokens),
            'max': max(tokens),
            'count': len(tokens)
        }
    
    def get_response_time_stats(self, days: int = 7) -> Dict:
        """
        Get response time statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with response time statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT response_time_ms
            FROM chat_metrics
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            AND response_time_ms > 0
        """, (days,))
        
        times = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not times:
            return {
                'average': 0,
                'median': 0,
                'p95': 0,
                'p99': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }
        
        sorted_times = sorted(times)
        
        return {
            'average': statistics.mean(times),
            'median': statistics.median(times),
            'p95': sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0,
            'p99': sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0,
            'min': min(times),
            'max': max(times),
            'count': len(times)
        }
    
    def get_cache_hit_rate(self, days: int = 7) -> float:
        """
        Get cache hit rate.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Cache hit rate as percentage
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as hits,
                COUNT(*) as total
            FROM chat_metrics
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or row[1] == 0:
            return 0.0
        
        return (row[0] / row[1]) * 100
    
    def get_pattern_match_rate(self, days: int = 7) -> float:
        """
        Get pattern match rate.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Pattern match rate as percentage
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN pattern_matched = 1 THEN 1 ELSE 0 END) as matches,
                COUNT(*) as total
            FROM chat_metrics
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            AND query_type = 'data'
        """, (days,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or row[1] == 0:
            return 0.0
        
        return (row[0] / row[1]) * 100
    
    def get_query_type_distribution(self, days: int = 7) -> Dict[str, int]:
        """
        Get distribution of query types.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict mapping query type to count
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT query_type, COUNT(*) as count
            FROM chat_metrics
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY query_type
            ORDER BY count DESC
        """, (days,))
        
        distribution = {}
        for row in cursor.fetchall():
            distribution[row[0]] = row[1]
        
        conn.close()
        return distribution


if __name__ == "__main__":
    # Test metrics tracker
    print("Testing MetricsTracker...")
    
    tracker = MetricsTracker()
    
    # Log some test metrics
    tracker.log_query(
        user_id=1,
        conversation_id="test-123",
        query_type="data",
        tokens_used=500,
        response_time_ms=1200,
        cache_hit=False,
        pattern_matched=True
    )
    
    # Get stats
    token_stats = tracker.get_token_stats(days=7)
    print(f"\n📊 Token Stats: {token_stats}")
    
    response_stats = tracker.get_response_time_stats(days=7)
    print(f"⏱️  Response Time Stats: {response_stats}")
    
    cache_rate = tracker.get_cache_hit_rate(days=7)
    print(f"💾 Cache Hit Rate: {cache_rate:.1f}%")
    
    pattern_rate = tracker.get_pattern_match_rate(days=7)
    print(f"🎯 Pattern Match Rate: {pattern_rate:.1f}%")
    
    distribution = tracker.get_query_type_distribution(days=7)
    print(f"📈 Query Type Distribution: {distribution}")
    
    print("\n✅ MetricsTracker tests complete")
