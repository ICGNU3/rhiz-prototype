import sqlite3
import uuid
from datetime import datetime
import json
import logging

class Database:
    def __init__(self, db_path='db.sqlite3'):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

class User:
    def __init__(self, db):
        self.db = db
    
    def create(self, email):
        user_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO users (id, email) VALUES (?, ?)",
                (user_id, email)
            )
            conn.commit()
            logging.info(f"Created user: {user_id}")
            return user_id
        except Exception as e:
            logging.error(f"Failed to create user: {e}")
            return None
        finally:
            conn.close()
    
    def get_or_create_default(self):
        """Get or create a default user for demo purposes"""
        conn = self.db.get_connection()
        try:
            user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            if user:
                return user['id']
            else:
                return self.create("demo@founder-network.ai")
        finally:
            conn.close()

class Contact:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, name, email=None, phone=None, twitter=None, linkedin=None, notes=None, tags=None):
        contact_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO contacts 
                   (id, user_id, name, email, phone, twitter, linkedin, notes, tags) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (contact_id, user_id, name, email, phone, twitter, linkedin, notes, tags)
            )
            conn.commit()
            logging.info(f"Created contact: {contact_id}")
            return contact_id
        except Exception as e:
            logging.error(f"Failed to create contact: {e}")
            return None
        finally:
            conn.close()
    
    def get_all(self, user_id):
        conn = self.db.get_connection()
        try:
            contacts = conn.execute(
                "SELECT * FROM contacts WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(contact) for contact in contacts]
        finally:
            conn.close()
    
    def get_by_id(self, contact_id):
        conn = self.db.get_connection()
        try:
            contact = conn.execute(
                "SELECT * FROM contacts WHERE id = ?",
                (contact_id,)
            ).fetchone()
            return dict(contact) if contact else None
        finally:
            conn.close()
    
    def update_last_interaction(self, contact_id):
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE contacts SET last_interaction = datetime('now') WHERE id = ?",
                (contact_id,)
            )
            conn.commit()
        finally:
            conn.close()

class Goal:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, title, description, embedding=None):
        goal_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO goals (id, user_id, title, description, embedding) VALUES (?, ?, ?, ?, ?)",
                (goal_id, user_id, title, description, embedding)
            )
            conn.commit()
            logging.info(f"Created goal: {goal_id}")
            return goal_id
        except Exception as e:
            logging.error(f"Failed to create goal: {e}")
            return None
        finally:
            conn.close()
    
    def get_all(self, user_id):
        conn = self.db.get_connection()
        try:
            goals = conn.execute(
                "SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(goal) for goal in goals]
        finally:
            conn.close()
    
    def get_by_id(self, goal_id):
        conn = self.db.get_connection()
        try:
            goal = conn.execute(
                "SELECT * FROM goals WHERE id = ?",
                (goal_id,)
            ).fetchone()
            return dict(goal) if goal else None
        finally:
            conn.close()
    
    def update_embedding(self, goal_id, embedding):
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE goals SET embedding = ? WHERE id = ?",
                (embedding, goal_id)
            )
            conn.commit()
        finally:
            conn.close()

class AISuggestion:
    def __init__(self, db):
        self.db = db
    
    def create(self, contact_id, goal_id, suggestion, confidence):
        suggestion_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO ai_suggestions (id, contact_id, goal_id, suggestion, confidence) VALUES (?, ?, ?, ?, ?)",
                (suggestion_id, contact_id, goal_id, suggestion, confidence)
            )
            conn.commit()
            return suggestion_id
        finally:
            conn.close()

class ContactInteraction:
    def __init__(self, db):
        self.db = db
    
    def create(self, contact_id, user_id, status, notes=None):
        interaction_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO contact_interactions (id, contact_id, user_id, status, notes) VALUES (?, ?, ?, ?, ?)",
                (interaction_id, contact_id, user_id, status, notes)
            )
            conn.commit()
            return interaction_id
        finally:
            conn.close()
    
    def get_by_contact(self, contact_id):
        conn = self.db.get_connection()
        try:
            interactions = conn.execute(
                "SELECT * FROM contact_interactions WHERE contact_id = ? ORDER BY timestamp DESC",
                (contact_id,)
            ).fetchall()
            return [dict(interaction) for interaction in interactions]
        finally:
            conn.close()
