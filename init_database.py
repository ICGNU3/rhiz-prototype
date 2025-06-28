#!/usr/bin/env python3

import sqlite3
import os

def init_database():
    """Initialize the database with the schema"""
    db_path = 'db.sqlite3'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Read schema file
    with open('schema.sql', 'r') as f:
        schema = f.read()
    
    # Create new database with schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute schema
    cursor.executescript(schema)
    conn.commit()
    
    print(f"Database created successfully: {db_path}")
    
    # Check tables created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables created: {[table[0] for table in tables]}")
    
    conn.close()

if __name__ == "__main__":
    init_database()