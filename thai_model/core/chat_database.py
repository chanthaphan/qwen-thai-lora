#!/usr/bin/env python3
"""
PostgreSQL Database Manager for Chat History
Provides persistent storage for conversation data across all chat interfaces
"""
import psycopg2
import psycopg2.extras
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

class ChatDatabaseManager:
    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        # Try to load from .env file if DATABASE_URL not in environment
        if not database_url and not os.getenv('DATABASE_URL'):
            env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('DATABASE_URL='):
                            database_url = line.split('=', 1)[1].strip()
                            break
        
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'postgresql://thai_user:thai_pass@localhost:5432/thai_chat'
        )
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        create_tables_sql = """
        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        
        -- Chat Sessions table
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            session_name VARCHAR(255),
            backend VARCHAR(50) NOT NULL,
            model VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}'::jsonb
        );
        
        -- Chat Messages table
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            session_id UUID REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            message_order INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}'::jsonb
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_order ON chat_messages(session_id, message_order);
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at DESC);
        
        -- Update trigger for sessions
        CREATE OR REPLACE FUNCTION update_session_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS trigger_update_session_timestamp ON chat_sessions;
        CREATE TRIGGER trigger_update_session_timestamp
            BEFORE UPDATE ON chat_sessions
            FOR EACH ROW
            EXECUTE FUNCTION update_session_timestamp();
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_tables_sql)
            print("✅ Database tables initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            raise
    
    def create_session(self, backend: str, model: str, session_name: str = None) -> str:
        """Create a new chat session and return session_id"""
        if not session_name:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            session_name = f"{backend}-{model}-{timestamp}"
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_sessions (session_name, backend, model, metadata)
                    VALUES (%s, %s, %s, %s)
                    RETURNING session_id
                """, (session_name, backend, model, json.dumps({})))
                
                session_id = cur.fetchone()[0]
                return str(session_id)
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> str:
        """Add a message to the session"""
        if metadata is None:
            metadata = {}
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Get the next message order
                cur.execute("""
                    SELECT COALESCE(MAX(message_order), 0) + 1 
                    FROM chat_messages 
                    WHERE session_id = %s
                """, (session_id,))
                message_order = cur.fetchone()[0]
                
                # Insert the message
                cur.execute("""
                    INSERT INTO chat_messages (session_id, role, content, message_order, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING message_id
                """, (session_id, role, content, message_order, json.dumps(metadata)))
                
                message_id = cur.fetchone()[0]
                return str(message_id)
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get all messages for a session in chronological order"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT role, content, created_at, metadata
                    FROM chat_messages 
                    WHERE session_id = %s 
                    ORDER BY message_order ASC
                """, (session_id,))
                
                messages = []
                for row in cur.fetchall():
                    messages.append({
                        "role": row['role'],
                        "content": row['content'],
                        "timestamp": row['created_at'].isoformat(),
                        "metadata": row['metadata'] or {}
                    })
                
                return messages
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT session_id, session_name, backend, model, created_at, updated_at, metadata
                    FROM chat_sessions 
                    WHERE session_id = %s
                """, (session_id,))
                
                row = cur.fetchone()
                if row:
                    return {
                        "session_id": str(row['session_id']),
                        "session_name": row['session_name'],
                        "backend": row['backend'],
                        "model": row['model'],
                        "created_at": row['created_at'].isoformat(),
                        "updated_at": row['updated_at'].isoformat(),
                        "metadata": row['metadata'] or {}
                    }
                return None
    
    def list_sessions(self, limit: int = 50) -> List[Dict]:
        """List recent chat sessions"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT s.session_id, s.session_name, s.backend, s.model, 
                           s.created_at, s.updated_at,
                           COUNT(m.message_id) as message_count
                    FROM chat_sessions s
                    LEFT JOIN chat_messages m ON s.session_id = m.session_id
                    GROUP BY s.session_id, s.session_name, s.backend, s.model, s.created_at, s.updated_at
                    ORDER BY s.updated_at DESC
                    LIMIT %s
                """, (limit,))
                
                sessions = []
                for row in cur.fetchall():
                    sessions.append({
                        "session_id": str(row['session_id']),
                        "session_name": row['session_name'],
                        "backend": row['backend'],
                        "model": row['model'],
                        "created_at": row['created_at'].isoformat(),
                        "updated_at": row['updated_at'].isoformat(),
                        "message_count": row['message_count']
                    })
                
                return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM chat_sessions WHERE session_id = %s", (session_id,))
                return cur.rowcount > 0
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for conversations containing specific text"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT s.session_id, s.session_name, s.backend, s.model, 
                           s.updated_at, m.content, m.created_at as message_time
                    FROM chat_sessions s
                    JOIN chat_messages m ON s.session_id = m.session_id
                    WHERE m.content ILIKE %s
                    ORDER BY m.created_at DESC
                    LIMIT %s
                """, (f'%{query}%', limit))
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        "session_id": str(row['session_id']),
                        "session_name": row['session_name'],
                        "backend": row['backend'],
                        "model": row['model'],
                        "updated_at": row['updated_at'].isoformat(),
                        "matching_content": row['content'][:200] + "..." if len(row['content']) > 200 else row['content'],
                        "message_time": row['message_time'].isoformat()
                    })
                
                return results
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT s.session_id) as total_sessions,
                        COUNT(m.message_id) as total_messages,
                        COUNT(DISTINCT s.backend) as unique_backends,
                        COUNT(DISTINCT s.model) as unique_models
                    FROM chat_sessions s
                    LEFT JOIN chat_messages m ON m.session_id = s.session_id
                """)
                
                stats = cur.fetchone()
                
                # Get backend distribution
                cur.execute("""
                    SELECT backend, COUNT(*) as count
                    FROM chat_sessions
                    GROUP BY backend
                    ORDER BY count DESC
                """)
                
                backend_stats = {row['backend']: row['count'] for row in cur.fetchall()}
                
                return {
                    "total_sessions": stats['total_sessions'],
                    "total_messages": stats['total_messages'],
                    "unique_backends": stats['unique_backends'],
                    "unique_models": stats['unique_models'],
                    "backend_distribution": backend_stats
                }
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return cur.fetchone()[0] == 1
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False