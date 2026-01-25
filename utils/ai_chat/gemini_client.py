"""
Google Gemini API client for AI chatbot assistant
"""

import streamlit as st
import time
from collections import deque
from typing import Optional, Dict, Any

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ google-genai not installed. Run: pip install google-genai")


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 10, window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window: Time window in seconds
        """
        self.max_requests = max_requests
        self.window = window
        self.requests = deque()
    
    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()
        
        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()
        
        # Check limit
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
    
    def time_until_next_request(self) -> float:
        """Get seconds until next request is allowed."""
        if len(self.requests) < self.max_requests:
            return 0.0
        
        oldest_request = self.requests[0]
        time_passed = time.time() - oldest_request
        return max(0.0, self.window - time_passed)


class GeminiClient:
    """Client for Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini client with API key from secrets."""
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai package not installed")
        
        # Load API key from Streamlit secrets
        try:
            # Check if secrets exist
            if not hasattr(st, 'secrets'):
                raise ValueError("Streamlit secrets not available")
            
            # Try to access gemini section
            if "gemini" not in st.secrets:
                raise ValueError("Gemini configuration not found in secrets. Please add [gemini] section with api_key.")
            
            gemini_config = st.secrets["gemini"]
            
            # Handle both dict and AttrDict from Streamlit
            if hasattr(gemini_config, 'get'):
                api_key = gemini_config.get("api_key", "")
            elif hasattr(gemini_config, 'api_key'):
                api_key = gemini_config.api_key
            else:
                raise ValueError("Cannot access api_key from gemini configuration")
            
            if not api_key or api_key == "YOUR_GEMINI_API_KEY":
                raise ValueError("Gemini API key not configured. Please set a valid API key in Streamlit secrets.")
                
        except KeyError as e:
            raise ValueError(f"Missing configuration in secrets: {e}")
        except AttributeError as e:
            raise ValueError(f"Invalid secrets structure: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load Gemini API key: {e}")
        
        # Configure Gemini client
        self.client = genai.Client(api_key=api_key)
        
        # Model name (use latest flash model)
        self.model_name = 'gemini-2.5-flash'
        
        # Generation config for accuracy and token limits
        self.config = types.GenerateContentConfig(
            temperature=0.1,  # Low for accuracy
            top_p=0.95,
            top_k=40,
            max_output_tokens=512,  # Limit to 512 tokens to control costs
        )
        
        # Rate limiter (10 requests per minute for free tier safety)
        try:
            if "chat" in st.secrets:
                chat_config = st.secrets["chat"]
                if hasattr(chat_config, 'get'):
                    rate_limit = chat_config.get("rate_limit_requests", 10)
                    rate_window = chat_config.get("rate_limit_window", 60)
                else:
                    rate_limit = getattr(chat_config, 'rate_limit_requests', 10)
                    rate_window = getattr(chat_config, 'rate_limit_window', 60)
            else:
                # Use defaults if chat config not present
                rate_limit = 10
                rate_window = 60
        except Exception:
            # Fallback to safe defaults
            rate_limit = 10
            rate_window = 60
            
        self.rate_limiter = RateLimiter(rate_limit, rate_window)
        
        # Token tracking
        self.total_tokens_used = 0
    
    def generate(self, prompt: str, stream: bool = False) -> Optional[str]:
        """
        Generate response from Gemini.
        
        Args:
            prompt: Input prompt
            stream: Whether to stream response (not implemented yet)
            
        Returns:
            Generated text or None if error
        """
        # Check rate limit
        if not self.rate_limiter.allow_request():
            wait_time = self.rate_limiter.time_until_next_request()
            raise Exception(f"Rate limit exceeded. Please wait {wait_time:.0f} seconds.")
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )
            
            # Extract text from response
            response_text = response.text
            
            # Track tokens (approximate)
            self.total_tokens_used += self._estimate_tokens(prompt) + self._estimate_tokens(response_text)
            
            return response_text
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific errors
            if "quota" in error_msg.lower():
                raise Exception("API quota exceeded. Please try again later.")
            elif "api key" in error_msg.lower():
                raise Exception("Invalid API key. Please check your configuration.")
            elif "rate limit" in error_msg.lower():
                raise Exception("Rate limit exceeded. Please wait a moment.")
            else:
                raise Exception(f"Gemini API error: {error_msg}")
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Rough approximation: 1 token ≈ 4 characters
        """
        return len(text) // 4
    
    def get_token_usage(self) -> int:
        """Get total tokens used in this session."""
        return self.total_tokens_used
    
    def reset_token_usage(self):
        """Reset token usage counter."""
        self.total_tokens_used = 0


def test_gemini_connection() -> Dict[str, Any]:
    """
    Test Gemini API connection.
    
    Returns:
        Dict with status and message
    """
    try:
        client = GeminiClient()
        response = client.generate("Say 'Hello' in one word.")
        
        return {
            "status": "success",
            "message": "Gemini API connected successfully",
            "response": response,
            "tokens_used": client.get_token_usage()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "response": None,
            "tokens_used": 0
        }


if __name__ == "__main__":
    # Test the client
    print("Testing Gemini API connection...")
    result = test_gemini_connection()
    
    if result["status"] == "success":
        print(f"✅ {result['message']}")
        print(f"   Response: {result['response']}")
        print(f"   Tokens used: {result['tokens_used']}")
    else:
        print(f"❌ {result['message']}")
