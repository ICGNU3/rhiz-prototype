"""
Database helper functions for PostgreSQL access
Provides consistent database connection and query patterns
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """Get PostgreSQL database connection with proper error handling"""
    conn = None
    try:
        conn = psycopg2.connect(
            os.environ.get("DATABASE_URL"),
            cursor_factory=RealDictCursor
        )
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor():
    """Get PostgreSQL cursor with automatic commit/rollback"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database query error: {e}")
            raise
        finally:
            cursor.close()

def execute_query(query, params=None):
    """Execute a single query and return results"""
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        return cursor.rowcount

def execute_query_one(query, params=None):
    """Execute query and return single result"""
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchone()