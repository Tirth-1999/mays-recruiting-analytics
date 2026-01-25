"""
Rate limiting for AI chatbot to prevent abuse
"""

import time
from typing import Dict, Optional, Tuple
from collections import deque
from datetime import datetime, timedelta


class RateLimiter:
    """Token bucket rate limiter with per-user and global limits."""
    
    def __init__(
        self,
        per_user_limit: int = 10,
        per_user_window: int = 60,
        global_limit: int = 100,
        global_window: int = 60
    ):
        """
        Initialize rate limiter.
        
        Args:
            per_user_limit: Max requests per user per window
            per_user_window: Time window in seconds for per-user limit
            global_limit: Max requests globally per window
            global_window: Time window in seconds for global limit
        """
        self.per_user_limit = per_user_limit
        self.per_user_window = per_user_window
        self.global_limit = global_limit
        self.global_window = global_window
        
        # Store request timestamps
        self.user_requests: Dict[int, deque] = {}
        self.global_requests = deque()
    
    def _clean_old_requests(self, requests: deque, window: int) -> deque:
        """Remove requests older than window."""
        cutoff = time.time() - window
        
        # Remove old requests from front
        while requests and requests[0] < cutoff:
            requests.popleft()
        
        return requests
    
    def check_user_limit(self, user_id: int) -> Tuple[bool, int, int]:
        """
        Check if user is within rate limit.
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (allowed, remaining, reset_seconds)
        """
        # Initialize user if not exists
        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()
        
        # Clean old requests
        self.user_requests[user_id] = self._clean_old_requests(
            self.user_requests[user_id],
            self.per_user_window
        )
        
        # Check limit
        current_count = len(self.user_requests[user_id])
        allowed = current_count < self.per_user_limit
        remaining = max(0, self.per_user_limit - current_count)
        
        # Calculate reset time
        if self.user_requests[user_id]:
            oldest_request = self.user_requests[user_id][0]
            reset_seconds = int(self.per_user_window - (time.time() - oldest_request))
        else:
            reset_seconds = 0
        
        return allowed, remaining, reset_seconds
    
    def check_global_limit(self) -> Tuple[bool, int, int]:
        """
        Check if global rate limit is within bounds.
        
        Returns:
            Tuple of (allowed, remaining, reset_seconds)
        """
        # Clean old requests
        self.global_requests = self._clean_old_requests(
            self.global_requests,
            self.global_window
        )
        
        # Check limit
        current_count = len(self.global_requests)
        allowed = current_count < self.global_limit
        remaining = max(0, self.global_limit - current_count)
        
        # Calculate reset time
        if self.global_requests:
            oldest_request = self.global_requests[0]
            reset_seconds = int(self.global_window - (time.time() - oldest_request))
        else:
            reset_seconds = 0
        
        return allowed, remaining, reset_seconds
    
    def check_rate_limit(self, user_id: int) -> Dict:
        """
        Check both user and global rate limits.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with rate limit status
        """
        user_allowed, user_remaining, user_reset = self.check_user_limit(user_id)
        global_allowed, global_remaining, global_reset = self.check_global_limit()
        
        allowed = user_allowed and global_allowed
        
        # Determine which limit is more restrictive
        if not user_allowed:
            limit_type = 'user'
            remaining = user_remaining
            reset_seconds = user_reset
        elif not global_allowed:
            limit_type = 'global'
            remaining = global_remaining
            reset_seconds = global_reset
        else:
            limit_type = None
            remaining = min(user_remaining, global_remaining)
            reset_seconds = 0
        
        return {
            'allowed': allowed,
            'limit_type': limit_type,
            'remaining': remaining,
            'reset_seconds': reset_seconds,
            'user_limit': self.per_user_limit,
            'global_limit': self.global_limit
        }
    
    def record_request(self, user_id: int):
        """
        Record a request for rate limiting.
        
        Args:
            user_id: User ID
        """
        current_time = time.time()
        
        # Record user request
        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()
        self.user_requests[user_id].append(current_time)
        
        # Record global request
        self.global_requests.append(current_time)
    
    def get_wait_message(self, reset_seconds: int, limit_type: str) -> str:
        """
        Generate user-friendly wait message.
        
        Args:
            reset_seconds: Seconds until reset
            limit_type: 'user' or 'global'
            
        Returns:
            Formatted message
        """
        if reset_seconds <= 0:
            return "Please try again in a moment."
        
        if reset_seconds < 60:
            time_str = f"{reset_seconds} seconds"
        else:
            minutes = reset_seconds // 60
            time_str = f"{minutes} minute{'s' if minutes > 1 else ''}"
        
        if limit_type == 'user':
            return f"You've reached your rate limit of {self.per_user_limit} queries per minute. Please wait {time_str} before trying again."
        else:
            return f"The system is experiencing high load. Please wait {time_str} before trying again."
    
    def reset_user(self, user_id: int):
        """Reset rate limit for a specific user."""
        if user_id in self.user_requests:
            self.user_requests[user_id].clear()
    
    def reset_all(self):
        """Reset all rate limits."""
        self.user_requests.clear()
        self.global_requests.clear()
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics."""
        return {
            'active_users': len(self.user_requests),
            'total_requests_tracked': sum(len(reqs) for reqs in self.user_requests.values()),
            'global_requests_tracked': len(self.global_requests),
            'per_user_limit': self.per_user_limit,
            'per_user_window': self.per_user_window,
            'global_limit': self.global_limit,
            'global_window': self.global_window
        }


if __name__ == "__main__":
    # Test rate limiter
    print("Testing RateLimiter...")
    
    limiter = RateLimiter(per_user_limit=3, per_user_window=60)
    
    user_id = 1
    
    print(f"\n📝 Testing Rate Limiting (limit: {limiter.per_user_limit} per minute):")
    
    for i in range(5):
        status = limiter.check_rate_limit(user_id)
        
        if status['allowed']:
            limiter.record_request(user_id)
            print(f"   Request {i+1}: ✅ Allowed (remaining: {status['remaining']})")
        else:
            print(f"   Request {i+1}: ❌ Blocked")
            print(f"   Message: {limiter.get_wait_message(status['reset_seconds'], status['limit_type'])}")
    
    # Test stats
    print("\n📊 Rate Limiter Stats:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ RateLimiter tests complete")
