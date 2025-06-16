"""
NEO Database Service

Replaces Supabase with direct PostgreSQL connections.
Provides database operations, connection management, and query utilities.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
import asyncpg
from asyncpg import Pool, Connection
import json
from contextlib import asynccontextmanager

from utils.config import config

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    NEO Database Service - Direct PostgreSQL connection manager.
    Replaces Supabase client functionality.
    """
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self.database_url = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connection pool."""
        if self._initialized:
            return
        
        try:
            # Build database URL
            self.database_url = (
                f"postgresql://{config.get('DATABASE_USER', 'neo_user')}:"
                f"{config.get('DATABASE_PASSWORD', 'neo_password')}@"
                f"{config.get('DATABASE_HOST', 'localhost')}:"
                f"{config.get('DATABASE_PORT', 5432)}/"
                f"{config.get('DATABASE_NAME', 'neo_db')}"
            )
            
            # Override with full URL if provided
            if hasattr(config, 'DATABASE_URL') and config.DATABASE_URL:
                self.database_url = config.DATABASE_URL
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'jit': 'off'  # Disable JIT for better performance on small queries
                }
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            
            self._initialized = True
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self._initialized = False
            logger.info("Database service closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool."""
        if not self._initialized:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute_query(
        self,
        query: str,
        *args,
        fetch: str = "all"
    ) -> Union[List[Dict], Dict, Any, None]:
        """
        Execute a database query.
        
        Args:
            query: SQL query string
            *args: Query parameters
            fetch: "all", "one", "val", or "none"
        """
        async with self.get_connection() as conn:
            try:
                if fetch == "all":
                    rows = await conn.fetch(query, *args)
                    return [dict(row) for row in rows]
                elif fetch == "one":
                    row = await conn.fetchrow(query, *args)
                    return dict(row) if row else None
                elif fetch == "val":
                    return await conn.fetchval(query, *args)
                elif fetch == "none":
                    await conn.execute(query, *args)
                    return None
                else:
                    raise ValueError(f"Invalid fetch type: {fetch}")
            except Exception as e:
                logger.error(f"Database query failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Args: {args}")
                raise
    
    async def insert(
        self,
        table: str,
        data: Dict[str, Any],
        returning: str = "id"
    ) -> Any:
        """Insert data into table."""
        import json
        
        # Convert dict values to JSON strings for JSONB columns
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                processed_data[key] = json.dumps(value)
            else:
                processed_data[key] = value
        
        columns = list(processed_data.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        values = [processed_data[col] for col in columns]
        
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING {returning}
        """
        
        return await self.execute_query(query, *values, fetch="val")
    
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any],
        returning: str = None
    ) -> Union[Dict, None]:
        """Update data in table."""
        import json
        
        # Convert dict values to JSON strings for JSONB columns
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                processed_data[key] = json.dumps(value)
            else:
                processed_data[key] = value
        
        set_clauses = [f"{col} = ${i+1}" for i, col in enumerate(processed_data.keys())]
        where_clauses = [f"{col} = ${i+len(processed_data)+1}" for i, col in enumerate(where.keys())]
        
        values = list(processed_data.values()) + list(where.values())
        
        query = f"""
            UPDATE {table}
            SET {', '.join(set_clauses)}
            WHERE {' AND '.join(where_clauses)}
        """
        
        if returning:
            query += f" RETURNING {returning}"
            return await self.execute_query(query, *values, fetch="one")
        else:
            await self.execute_query(query, *values, fetch="none")
            return None
    
    async def delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> None:
        """Delete data from table."""
        where_clauses = [f"{col} = ${i+1}" for i, col in enumerate(where.keys())]
        values = list(where.values())
        
        query = f"""
            DELETE FROM {table}
            WHERE {' AND '.join(where_clauses)}
        """
        
        await self.execute_query(query, *values, fetch="none")
    
    async def select(
        self,
        table: str,
        columns: str = "*",
        where: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None
    ) -> List[Dict]:
        """Select data from table."""
        query = f"SELECT {columns} FROM {table}"
        values = []
        
        if where:
            where_clauses = [f"{col} = ${i+1}" for i, col in enumerate(where.keys())]
            query += f" WHERE {' AND '.join(where_clauses)}"
            values = list(where.values())
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        if offset:
            query += f" OFFSET {offset}"
        
        return await self.execute_query(query, *values, fetch="all")
    
    async def count(
        self,
        table: str,
        where: Dict[str, Any] = None
    ) -> int:
        """Count rows in table."""
        query = f"SELECT COUNT(*) FROM {table}"
        values = []
        
        if where:
            where_clauses = [f"{col} = ${i+1}" for i, col in enumerate(where.keys())]
            query += f" WHERE {' AND '.join(where_clauses)}"
            values = list(where.values())
        
        return await self.execute_query(query, *values, fetch="val")
    
    # User management methods
    async def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: str = None,
        metadata: Dict = None
    ) -> str:
        """Create a new user."""
        data = {
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "metadata": json.dumps(metadata or {})
        }
        
        return await self.insert("users", data)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        return await self.execute_query(
            "SELECT * FROM users WHERE email = $1",
            email,
            fetch="one"
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        return await self.execute_query(
            "SELECT * FROM users WHERE id = $1",
            user_id,
            fetch="one"
        )
    
    async def update_user_login(self, user_id: str):
        """Update user last login timestamp."""
        await self.update(
            "users",
            {"last_login": datetime.now(timezone.utc)},
            {"id": user_id}
        )
    
    # Account management methods
    async def create_account(
        self,
        name: str,
        slug: str,
        personal_account: bool = False,
        billing_email: str = None
    ) -> str:
        """Create a new account."""
        data = {
            "name": name,
            "slug": slug,
            "personal_account": personal_account,
            "billing_email": billing_email
        }
        
        return await self.insert("accounts", data)
    
    async def add_user_to_account(
        self,
        account_id: str,
        user_id: str,
        role: str = "member"
    ):
        """Add user to account."""
        data = {
            "account_id": account_id,
            "user_id": user_id,
            "role": role
        }
        
        await self.insert("account_users", data)
    
    async def get_user_accounts(self, user_id: str) -> List[Dict]:
        """Get accounts for user."""
        return await self.execute_query("""
            SELECT a.*, au.role
            FROM accounts a
            JOIN account_users au ON a.id = au.account_id
            WHERE au.user_id = $1
            ORDER BY a.created_at
        """, user_id, fetch="all")
    
    # Thread and message methods
    async def create_thread(
        self,
        account_id: str,
        project_id: str = None,
        title: str = None,
        is_public: bool = False,
        metadata: Dict = None
    ) -> str:
        """Create a new thread."""
        data = {
            "account_id": account_id,
            "project_id": project_id,
            "title": title,
            "is_public": is_public,
            "metadata": json.dumps(metadata or {})
        }
        
        return await self.insert("threads", data)
    
    async def create_message(
        self,
        thread_id: str,
        message_type: str,
        content: Dict,
        is_llm_message: bool = True,
        metadata: Dict = None
    ) -> str:
        """Create a new message."""
        data = {
            "thread_id": thread_id,
            "type": message_type,
            "content": json.dumps(content),
            "is_llm_message": is_llm_message,
            "metadata": json.dumps(metadata or {})
        }
        
        return await self.insert("messages", data)
    
    async def get_thread_messages(self, thread_id: str) -> List[Dict]:
        """Get messages for thread."""
        return await self.execute_query("""
            SELECT * FROM messages
            WHERE thread_id = $1
            ORDER BY created_at
        """, thread_id, fetch="all")
    
    async def get_llm_formatted_messages(self, thread_id: str) -> List[Dict]:
        """Get LLM formatted messages for thread."""
        result = await self.execute_query(
            "SELECT get_llm_formatted_messages($1) as messages",
            thread_id,
            fetch="val"
        )
        
        return result if result else []
    
    # Session management
    async def create_session(
        self,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
        user_agent: str = None,
        ip_address: str = None
    ) -> str:
        """Create a new session."""
        data = {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "user_agent": user_agent,
            "ip_address": ip_address
        }
        
        return await self.insert("sessions", data)
    
    async def get_session(self, token_hash: str) -> Optional[Dict]:
        """Get session by token hash."""
        return await self.execute_query("""
            SELECT s.*, u.email, u.full_name, u.is_active
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token_hash = $1 AND s.expires_at > NOW()
        """, token_hash, fetch="one")
    
    async def delete_session(self, token_hash: str):
        """Delete session."""
        await self.delete("sessions", {"token_hash": token_hash})
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        await self.execute_query(
            "DELETE FROM sessions WHERE expires_at < NOW()",
            fetch="none"
        )

# Global database service instance
db_service = DatabaseService()

# Legacy compatibility - alias for old Supabase-based code
class DBConnection:
    """Legacy compatibility wrapper for DatabaseService."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.db = db_service
    
    async def initialize(self):
        """Initialize database connection."""
        await self.db.initialize()
    
    @property
    def client(self):
        """Mock Supabase client interface."""
        return MockSupabaseClient()
    
    async def disconnect(self):
        """Disconnect from database."""
        await self.db.close()

class MockSupabaseClient:
    """Mock Supabase client for compatibility."""
    
    def __init__(self):
        self.auth = MockAuth()
    
    def table(self, table_name: str):
        return MockTable(table_name)
    
    def from_(self, table_name: str):
        return MockTable(table_name)

class MockAuth:
    """Mock Supabase auth."""
    
    async def get_user(self, jwt_token: str = None):
        return {"user": None, "error": None}

class MockTable:
    """Mock Supabase table."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def select(self, columns: str = "*"):
        return MockQuery(self.table_name, "select", columns)
    
    def insert(self, data: dict):
        return MockQuery(self.table_name, "insert", data)
    
    def update(self, data: dict):
        return MockQuery(self.table_name, "update", data)
    
    def delete(self):
        return MockQuery(self.table_name, "delete")

class MockQuery:
    """Mock Supabase query."""
    
    def __init__(self, table_name: str, operation: str, data=None):
        self.table_name = table_name
        self.operation = operation
        self.data = data
        self._filters = {}
    
    def eq(self, column: str, value):
        self._filters[column] = value
        return self
    
    def filter(self, column: str, operator: str, value):
        self._filters[f"{column}__{operator}"] = value
        return self
    
    def order(self, column: str, desc: bool = False):
        return self
    
    def limit(self, count: int):
        return self
    
    async def execute(self):
        """Execute the query using DatabaseService."""
        try:
            # Special handling for non-existent tables
            if self.table_name == "agents":
                # Return empty result for agents table (doesn't exist in our schema)
                if self.operation == "select":
                    return MockResult([], None)
                elif self.operation == "insert":
                    return MockResult([{"id": "mock-agent-id"}], None)
                elif self.operation == "update":
                    return MockResult([{"updated": True}], None)
                elif self.operation == "delete":
                    return MockResult(None, None)
            
            if self.operation == "select":
                result = await db_service.select(
                    self.table_name,
                    columns=self.data if isinstance(self.data, str) else "*",
                    where=self._filters if self._filters else None
                )
                return MockResult(result, None)
            
            elif self.operation == "insert":
                result = await db_service.insert(self.table_name, self.data)
                return MockResult([{"id": result}], None)
            
            elif self.operation == "update":
                await db_service.update(self.table_name, self.data, self._filters)
                # Return mock data that simulates Supabase update response
                # Supabase returns the updated record(s), so we simulate that
                mock_updated_record = {"id": "mock-id", **self.data}
                return MockResult([mock_updated_record], None)
            
            elif self.operation == "delete":
                await db_service.delete(self.table_name, self._filters)
                return MockResult(None, None)
            
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            return MockResult(None, str(e))

class MockResult:
    """Mock Supabase result object."""
    
    def __init__(self, data, error):
        self.data = data
        self.error = error
        # Debug logging
        logger.info(f"MockResult created: data={data}, error={error}")