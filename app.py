import os
import logging
import sqlite3
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Environment variables loaded from .env file")
except ImportError:
    # python-dotenv not installed, use os.environ directly
    logging.info("Loading environment variables from system")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database with migration support
def init_db():
    """Initialize the database with schema and handle migrations"""
    import os
    
    # If database doesn't exist, create it fresh
    if not os.path.exists('db.sqlite3'):
        conn = sqlite3.connect('db.sqlite3')
        try:
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            logging.info("Database created successfully from schema.sql")
        except FileNotFoundError:
            logging.error("schema.sql not found! Creating basic schema...")
            # Create basic schema if schema.sql is missing
            basic_schema = """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
            conn.executescript(basic_schema)
            conn.commit()
            logging.info("Basic database schema created")
        finally:
            conn.close()
        return
    
    # Check if we need to migrate existing database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'warmth_status' not in columns:
            logging.info("Migrating database to new CRM schema...")
            # Drop and recreate with new schema for simplicity in this case
            conn.close()
            os.remove('db.sqlite3')
            # Recreate fresh
            conn = sqlite3.connect('db.sqlite3')
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            logging.info("Database migrated successfully")
        else:
            logging.info("Database schema is up to date")
            
    except Exception as e:
        logging.error(f"Migration error: {e}")
        # If anything goes wrong, recreate fresh
        conn.close()
        if os.path.exists('db.sqlite3'):
            os.remove('db.sqlite3')
        conn = sqlite3.connect('db.sqlite3')
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        logging.info("Database recreated due to migration error")
    
    finally:
        conn.close()

# Initialize database on startup
try:
    init_db()
    
    # Initialize sync tables for multi-source contact management
    try:
        from services.contact_sync_engine import ContactSyncEngine
        sync_engine = ContactSyncEngine()
        sync_engine.init_sync_tables()
        logging.info("Multi-source contact sync tables initialized")
    except Exception as sync_error:
        logging.warning(f"Sync tables initialization warning: {sync_error}")
        # Continue without sync tables - they'll be created on first use
        
except Exception as e:
    logging.error(f"Failed to initialize database: {e}")

# Import routes after app creation
from backend.routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
