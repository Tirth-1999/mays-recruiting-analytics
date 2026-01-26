"""
Chat history management for AI chatbot assistant
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


class ChatHistory:
    """Manages chat history storage and retrieval."""
    
    def __init__(self, db_path: str = 'edulytix.db'):
        """
        Initialize chat history manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    def save_message(
        self,
        user_id: int,
        conversation_id: str,
        message: str,
        role: str,
        tokens_used: int = 0,
        query_type: Optional[str] = None,
        sql_query: Optional[str] = None
    ) -> int:
        """
        Save a message to chat history.
        
        Args:
            user_id: User ID from OAuth
            conversation_id: UUID for conversation grouping
            message: Message text
            role: 'user' or 'assistant'
            tokens_used: Number of tokens used
            query_type: Type of query (data, navigation, help, conversational)
            sql_query: Generated SQL query (if applicable)
            
        Returns:
            chat_id of inserted message
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO chat_history 
                (user_id, conversation_id, message, role, tokens_used, query_type, sql_query)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, conversation_id, message, role, tokens_used, query_type, sql_query))
            
            chat_id = cursor.lastrowid
            conn.commit()
            return chat_id
            
        finally:
            conn.close()
    
    def get_conversation(
        self,
        user_id: int,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Retrieve conversation history.
        
        Args:
            user_id: User ID (for security check)
            conversation_id: Conversation UUID
            limit: Maximum messages to retrieve
            
        Returns:
            List of message dicts in chronological order
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT chat_id, message, role, timestamp, tokens_used, query_type, sql_query
                FROM chat_history
                WHERE user_id = ? AND conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, conversation_id, limit))
            
            messages = []
            for row in reversed(cursor.fetchall()):  # Reverse for chronological order
                messages.append({
                    'chat_id': row[0],
                    'message': row[1],
                    'role': row[2],
                    'timestamp': row[3],
                    'tokens_used': row[4],
                    'query_type': row[5],
                    'sql_query': row[6]
                })
            
            return messages
            
        finally:
            conn.close()
    
    def get_conversation_context(
        self,
        user_id: int,
        conversation_id: str,
        limit: int = 5
    ) -> str:
        """
        Get recent conversation for context in prompts.
        
        Args:
            user_id: User ID
            conversation_id: Conversation UUID
            limit: Number of recent exchanges to include
            
        Returns:
            Formatted conversation context string
        """
        messages = self.get_conversation(user_id, conversation_id, limit * 2)  # *2 for user+assistant pairs
        
        if not messages:
            return "No previous context."
        
        context = "Recent conversation:\n"
        for msg in messages[-limit*2:]:  # Last N exchanges
            role = "User" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['message']}\n"
        
        return context
    
    def get_user_conversations(self, user_id: int) -> List[Dict]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of conversation summaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    conversation_id,
                    user_id,
                    MIN(timestamp) as started_at,
                    MAX(timestamp) as last_message_at,
                    COUNT(*) as message_count,
                    SUM(tokens_used) as total_tokens
                FROM chat_history
                WHERE user_id = ?
                GROUP BY conversation_id, user_id
                ORDER BY last_message_at DESC
            ''', (user_id,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'conversation_id': row[0],
                    'user_id': row[1],
                    'started_at': row[2],
                    'last_message_at': row[3],
                    'message_count': row[4],
                    'total_tokens': row[5]
                })
            
            return conversations
            
        finally:
            conn.close()
    
    def get_all_conversations(self) -> List[Dict]:
        """
        Get all conversations across all users (admin only).
        
        Returns:
            List of conversation summaries with user_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    conversation_id,
                    user_id,
                    MIN(timestamp) as started_at,
                    MAX(timestamp) as last_message_at,
                    COUNT(*) as message_count,
                    SUM(tokens_used) as total_tokens
                FROM chat_history
                GROUP BY conversation_id, user_id
                ORDER BY last_message_at DESC
            ''')
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'conversation_id': row[0],
                    'user_id': row[1],
                    'started_at': row[2],
                    'last_message_at': row[3],
                    'message_count': row[4],
                    'total_tokens': row[5]
                })
            
            return conversations
            
        finally:
            conn.close()
    
    def get_conversation_preview(self, user_id: int, conversation_id: str) -> Optional[str]:
        """
        Get first user message as conversation preview.
        
        Args:
            user_id: User ID
            conversation_id: Conversation UUID
            
        Returns:
            First user message or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT message
                FROM chat_history
                WHERE user_id = ? AND conversation_id = ? AND role = 'user'
                ORDER BY timestamp ASC
                LIMIT 1
            ''', (user_id, conversation_id))
            
            row = cursor.fetchone()
            return row[0] if row else None
            
        finally:
            conn.close()
    
    def delete_conversation(self, user_id: int, conversation_id: str) -> int:
        """
        Delete a conversation (hard delete).
        
        Args:
            user_id: User ID (for security check)
            conversation_id: Conversation UUID
            
        Returns:
            Number of messages deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM chat_history
                WHERE user_id = ? AND conversation_id = ?
            ''', (user_id, conversation_id))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
            
        finally:
            conn.close()
    
    def delete_all_user_history(self, user_id: int) -> int:
        """
        Delete all chat history for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of messages deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM chat_history
                WHERE user_id = ?
            ''', (user_id,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
            
        finally:
            conn.close()
    
    def cleanup_old_conversations(self, days: int = 90) -> int:
        """
        Delete conversations older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of messages deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM chat_history
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
            
        finally:
            conn.close()
    
    def cleanup_old_conversations(self, days: int = 90) -> int:
        """
        Delete conversations older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of messages deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM chat_history
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
            
        finally:
            conn.close()
    
    def delete_user_data(self, user_id: int) -> Dict[str, int]:
        """
        Delete all data for a user (GDPR compliance).
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with deletion counts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Count before deletion
            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE user_id = ?', (user_id,))
            message_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT conversation_id) FROM chat_history WHERE user_id = ?', (user_id,))
            conversation_count = cursor.fetchone()[0]
            
            # Delete all chat history
            cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
            
            conn.commit()
            
            return {
                'messages_deleted': message_count,
                'conversations_deleted': conversation_count
            }
            
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """
        Get usage statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT conversation_id) as conversation_count,
                    COUNT(*) as total_messages,
                    SUM(tokens_used) as total_tokens,
                    MIN(timestamp) as first_message,
                    MAX(timestamp) as last_message
                FROM chat_history
                WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            
            return {
                'conversation_count': row[0] or 0,
                'total_messages': row[1] or 0,
                'total_tokens': row[2] or 0,
                'first_message': row[3],
                'last_message': row[4]
            }
            
        finally:
            conn.close()
    
    def search_messages(
        self,
        user_id: int,
        search_query: str,
        conversation_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Search messages by keyword.
        
        Args:
            user_id: User ID
            search_query: Search keyword
            conversation_id: Optional conversation ID to limit search
            
        Returns:
            List of matching messages
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if conversation_id:
                cursor.execute('''
                    SELECT chat_id, conversation_id, message, role, timestamp
                    FROM chat_history
                    WHERE user_id = ? AND conversation_id = ? 
                    AND message LIKE ?
                    ORDER BY timestamp DESC
                ''', (user_id, conversation_id, f'%{search_query}%'))
            else:
                cursor.execute('''
                    SELECT chat_id, conversation_id, message, role, timestamp
                    FROM chat_history
                    WHERE user_id = ? AND message LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                ''', (user_id, f'%{search_query}%'))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'chat_id': row[0],
                    'conversation_id': row[1],
                    'message': row[2],
                    'role': row[3],
                    'timestamp': row[4]
                })
            
            return results
            
        finally:
            conn.close()
    
    def export_conversation_json(
        self,
        user_id: int,
        conversation_id: str
    ) -> str:
        """
        Export conversation to JSON format.
        
        Args:
            user_id: User ID
            conversation_id: Conversation UUID
            
        Returns:
            JSON string of conversation
        """
        import json
        
        messages = self.get_conversation(user_id, conversation_id, limit=1000)
        
        export_data = {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'message_count': len(messages),
            'messages': messages
        }
        
        return json.dumps(export_data, indent=2)
    
    def export_all_conversations_json(self, user_id: int) -> str:
        """
        Export all user conversations to JSON.
        
        Args:
            user_id: User ID
            
        Returns:
            JSON string of all conversations
        """
        import json
        
        conversations = self.get_user_conversations(user_id)
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'conversation_count': len(conversations),
            'conversations': []
        }
        
        for conv in conversations:
            messages = self.get_conversation(user_id, conv['conversation_id'], limit=1000)
            export_data['conversations'].append({
                'conversation_id': conv['conversation_id'],
                'started_at': conv['started_at'],
                'last_message_at': conv['last_message_at'],
                'message_count': conv['message_count'],
                'messages': messages
            })
        
        return json.dumps(export_data, indent=2)
    
    @staticmethod
    def generate_conversation_id() -> str:
        """Generate a new conversation UUID."""
        return str(uuid.uuid4())
    
    def save_feedback(
        self,
        user_id: int,
        chat_id: int,
        conversation_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> int:
        """
        Save user feedback for a chat response.
        
        Args:
            user_id: User ID
            chat_id: Chat message ID
            conversation_id: Conversation UUID
            rating: 1 for positive, -1 for negative
            comment: Optional feedback comment
            
        Returns:
            feedback_id of inserted feedback
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO chat_feedback 
                (user_id, chat_id, conversation_id, rating, comment)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, chat_id, conversation_id, rating, comment))
            
            feedback_id = cursor.lastrowid
            conn.commit()
            return feedback_id
            
        finally:
            conn.close()
    
    def get_feedback_stats(self, days: int = 7) -> Dict:
        """
        Get feedback statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with feedback stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_feedback,
                    SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as positive,
                    SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as negative
                FROM chat_feedback
                WHERE created_at >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            row = cursor.fetchone()
            
            total = row[0] or 0
            positive = row[1] or 0
            negative = row[2] or 0
            satisfaction_rate = (positive / total * 100) if total > 0 else 0
            
            return {
                'total_feedback': total,
                'positive': positive,
                'negative': negative,
                'satisfaction_rate': satisfaction_rate
            }
            
        finally:
            conn.close()
    
    def get_feedback_by_query_type(self, days: int = 30) -> List[Dict]:
        """
        Get feedback statistics grouped by query type.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of dicts with query_type and feedback stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    ch.query_type,
                    COUNT(cf.feedback_id) as total_feedback,
                    SUM(CASE WHEN cf.rating = 1 THEN 1 ELSE 0 END) as positive,
                    SUM(CASE WHEN cf.rating = -1 THEN 1 ELSE 0 END) as negative,
                    ROUND(
                        CAST(SUM(CASE WHEN cf.rating = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
                        COUNT(cf.feedback_id) * 100, 
                        1
                    ) as satisfaction_rate
                FROM chat_feedback cf
                JOIN chat_history ch ON cf.chat_id = ch.chat_id
                WHERE cf.created_at >= datetime('now', '-' || ? || ' days')
                    AND ch.query_type IS NOT NULL
                GROUP BY ch.query_type
                ORDER BY satisfaction_rate ASC
            ''', (days,))
            
            rows = cursor.fetchall()
            
            return [
                {
                    'query_type': row[0],
                    'total_feedback': row[1],
                    'positive': row[2],
                    'negative': row[3],
                    'satisfaction_rate': row[4] or 0
                }
                for row in rows
            ]
            
        finally:
            conn.close()
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """
        Get most popular user queries based on frequency.
        
        Args:
            limit: Number of queries to return
            
        Returns:
            List of dicts with query and count
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    message,
                    COUNT(*) as query_count
                FROM chat_history
                WHERE role = 'user'
                    AND timestamp >= datetime('now', '-30 days')
                GROUP BY LOWER(message)
                ORDER BY query_count DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            return [
                {
                    'query': row[0],
                    'count': row[1]
                }
                for row in rows
            ]
            
        finally:
            conn.close()


if __name__ == "__main__":
    # Test chat history operations
    print("Testing ChatHistory...")
    
    history = ChatHistory()
    
    # Generate test conversation
    conv_id = ChatHistory.generate_conversation_id()
    user_id = 1
    
    # Save test messages
    history.save_message(user_id, conv_id, "How many MBA applications?", "user")
    history.save_message(user_id, conv_id, "There are 234 MBA applications in 2025.", "assistant", tokens_used=50)
    
    # Retrieve conversation
    messages = history.get_conversation(user_id, conv_id)
    print(f"\n✅ Saved and retrieved {len(messages)} messages")
    
    # Get context
    context = history.get_conversation_context(user_id, conv_id)
    print(f"\n✅ Context:\n{context}")
    
    # Get stats
    stats = history.get_user_stats(user_id)
    print(f"\n✅ User stats: {stats}")
    
    # Cleanup test data
    deleted = history.delete_conversation(user_id, conv_id)
    print(f"\n✅ Cleaned up {deleted} test messages")
