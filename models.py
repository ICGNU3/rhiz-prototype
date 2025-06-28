"""
Models Module
Legacy models for compatibility with the existing routes system
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict, Any
import hashlib

class Database:
    """Database connection and management"""
    
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
    
    def get_connection(self):
        """Get database connection"""
        if self.db_url and self.db_url.startswith('postgresql'):
            return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
        else:
            # Fallback to SQLite for development
            return sqlite3.connect('db.sqlite3')

class User:
    """User model for compatibility"""
    
    @staticmethod
    def get_by_id(user_id: str):
        """Get user by ID"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()

class Contact:
    """Contact model for compatibility"""
    
    @staticmethod
    def get_by_user_id(user_id: str):
        """Get contacts by user ID"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE user_id = %s", (user_id,))
            return cursor.fetchall()

class Goal:
    """Goal model for compatibility"""
    
    @staticmethod
    def get_by_user_id(user_id: str):
        """Get goals by user ID"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM goals WHERE user_id = %s", (user_id,))
            return cursor.fetchall()

class AISuggestion:
    """AI Suggestion model for compatibility"""
    
    @staticmethod
    def get_recent(user_id: str, limit: int = 10):
        """Get recent AI suggestions"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM ai_suggestions WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                (user_id, limit)
            )
            return cursor.fetchall()

class ContactInteraction:
    """Contact interaction model for compatibility"""
    
    @staticmethod
    def get_recent(user_id: str, limit: int = 10):
        """Get recent contact interactions"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM contact_interactions WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                (user_id, limit)
            )
            return cursor.fetchall()