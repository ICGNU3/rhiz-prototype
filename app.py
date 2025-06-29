"""
Flask Application Entry Point
This file creates the Flask app using the application factory pattern.
Use this for 'flask run' command.
"""
import os
from backend import create_app

# Create the application instance using the factory pattern
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)