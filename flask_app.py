#!/usr/bin/env python3
"""
Flask application entry point for Flask-Migrate commands.
This file provides the Flask app instance for migration commands.
"""
import os
from backend import create_app

# Create Flask app instance
app = create_app()

# Make sure this runs only when this file is executed directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)