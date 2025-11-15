"""Supabase client and database operations."""

from typing import Optional, List, Dict
from functools import lru_cache
from uuid import UUID
from loguru import logger

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Supabase library not installed")
    SUPABASE_AVAILABLE = False

from ..utils.config import get_settings


class SupabaseClient:
    """Supabase database client wrapper."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL
            key: Supabase anon/service key

        Example:
            >>> client = SupabaseClient()
            >>> users = client.get_table("users")
        """
        settings = get_settings()
        self.url = url or settings.supabase_url
        self.key = key or settings.supabase_key

        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase not available - using mock mode")
            self.client = None
            return

        if not self.url or not self.key:
            logger.warning("Supabase credentials not configured")
            self.client = None
            return

        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Supabase initialization error: {e}")
            self.client = None

    def get_table(self, table_name: str):
        """
        Get table reference.

        Args:
            table_name: Name of the table

        Returns:
            Table reference or None

        Example:
            >>> users_table = client.get_table("users")
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return None

        try:
            return self.client.table(table_name)
        except Exception as e:
            logger.error(f"Error getting table {table_name}: {e}")
            return None

    def insert(self, table_name: str, data: Dict) -> Optional[Dict]:
        """
        Insert data into table.

        Args:
            table_name: Table name
            data: Data to insert

        Returns:
            Inserted row or None

        Example:
            >>> client.insert("users", {"email": "test@example.com"})
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return None

        try:
            table = self.get_table(table_name)
            result = table.insert(data).execute()

            logger.info(f"Inserted into {table_name}", extra={"table": table_name})
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Insert error in {table_name}: {e}")
            return None

    def select(
        self,
        table_name: str,
        columns: str = "*",
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Select data from table.

        Args:
            table_name: Table name
            columns: Columns to select
            filters: Filter conditions
            limit: Maximum rows to return

        Returns:
            List of rows

        Example:
            >>> users = client.select("users", filters={"plan": "pro"})
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return []

        try:
            table = self.get_table(table_name)
            query = table.select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            if limit:
                query = query.limit(limit)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Select error from {table_name}: {e}")
            return []

    def update(
        self,
        table_name: str,
        data: Dict,
        filters: Dict,
    ) -> Optional[Dict]:
        """
        Update data in table.

        Args:
            table_name: Table name
            data: Data to update
            filters: Filter conditions

        Returns:
            Updated row or None

        Example:
            >>> client.update("users", {"plan": "premium"}, {"id": user_id})
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return None

        try:
            table = self.get_table(table_name)
            query = table.update(data)

            for key, value in filters.items():
                query = query.eq(key, value)

            result = query.execute()

            logger.info(f"Updated {table_name}", extra={"table": table_name})
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Update error in {table_name}: {e}")
            return None

    def delete(self, table_name: str, filters: Dict) -> bool:
        """
        Delete data from table.

        Args:
            table_name: Table name
            filters: Filter conditions

        Returns:
            True if successful

        Example:
            >>> client.delete("signals", {"id": signal_id})
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return False

        try:
            table = self.get_table(table_name)
            query = table.delete()

            for key, value in filters.items():
                query = query.eq(key, value)

            query.execute()

            logger.info(f"Deleted from {table_name}", extra={"table": table_name})
            return True

        except Exception as e:
            logger.error(f"Delete error from {table_name}: {e}")
            return False

    def execute_rpc(self, function_name: str, params: Dict) -> Optional[Dict]:
        """
        Execute stored procedure.

        Args:
            function_name: RPC function name
            params: Function parameters

        Returns:
            Function result or None

        Example:
            >>> client.execute_rpc("calculate_metrics", {"period": "month"})
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return None

        try:
            result = self.client.rpc(function_name, params).execute()
            return result.data if result.data else None

        except Exception as e:
            logger.error(f"RPC error for {function_name}: {e}")
            return None


@lru_cache()
def get_supabase_client() -> SupabaseClient:
    """
    Get cached Supabase client instance.

    Returns:
        SupabaseClient instance

    Example:
        >>> db = get_supabase_client()
        >>> users = db.select("users")
    """
    return SupabaseClient()
