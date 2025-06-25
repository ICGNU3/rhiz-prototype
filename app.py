import os
import logging
import sqlite3
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database
def init_db():
    """Initialize the database with schema"""
    conn = sqlite3.connect('db.sqlite3')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully")

# Initialize database on startup
try:
    init_db()
except Exception as e:
    logging.error(f"Failed to initialize database: {e}")

# Import routes after app creation
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
