"""
Database helper functions for PostgreSQL
Provides unified database access patterns for the Rhiz platform
"""
import os
import psycopg2
import psycopg2.extras
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseHelper:
    """Helper class for PostgreSQL database operations"""
    
    @staticmethod
    def get_connection():
        """Get PostgreSQL connection with proper configuration"""
        try:
            conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False) -> Optional[Any]:
        """Execute a query and return results"""
        try:
            conn = DatabaseHelper.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise
    
    @staticmethod
    def execute_insert(query: str, params: tuple = None, return_id: bool = False) -> Optional[Any]:
        """Execute an insert query and optionally return the inserted ID"""
        try:
            conn = DatabaseHelper.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            if return_id:
                cursor.execute(query + " RETURNING id", params or ())
                result = cursor.fetchone()
                inserted_id = result['id'] if result else None
            else:
                cursor.execute(query, params or ())
                inserted_id = None
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return inserted_id
            
        except Exception as e:
            logger.error(f"Database insert error: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        query = "SELECT * FROM users WHERE email = %s"
        return DatabaseHelper.execute_query(query, (email,), fetch_one=True)
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        return DatabaseHelper.execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Check database health"""
        try:
            result = DatabaseHelper.execute_query("SELECT 1 as test", fetch_one=True)
            return {
                "database": "healthy" if result else "unhealthy",
                "test_result": result
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "database": "unhealthy",
                "error": str(e)
            }