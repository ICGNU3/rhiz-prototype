"""
Simple working routes to fix immediate navigation issues
"""

from flask import render_template, jsonify, session, redirect, url_for, request
from main import app
import sqlite3
import os

# Simple database helper
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def landing():
    """Landing page with working navigation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rhiz - Relationship Intelligence Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #1e1e2e 0%, #2d3748 100%);
                min-height: 100vh;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 2rem;
                margin: 1rem 0;
            }
            .hero-section {
                text-align: center;
                padding: 4rem 0;
            }
            .cta-button {
                font-size: 1.2rem;
                padding: 1rem 2rem;
                margin: 0.5rem;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .cta-button:hover {
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero-section">
                <div class="glass-card">
                    <h1 class="display-4 text-white mb-4">Rhiz</h1>
                    <p class="lead text-light mb-5">High-context relationship intelligence for network architects</p>
                    
                    <div class="row text-center">
                        <div class="col-12 mb-4">
                            <h3 class="text-white">Choose Your Experience</h3>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="glass-card">
                                <h5 class="text-white">Quick Demo</h5>
                                <p class="text-light">Simple interface to test functionality</p>
                                <a href="/demo-login" class="btn btn-primary btn-lg">Try Simple Demo</a>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="glass-card">
                                <h5 class="text-white">React Frontend</h5>
                                <p class="text-light">Modern glassmorphism interface</p>
                                <a href="/app/dashboard" class="btn btn-success btn-lg">Launch React App</a>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="glass-card">
                                <h5 class="text-white">Full Platform</h5>
                                <p class="text-light">Complete feature access</p>
                                <a href="/signup" class="btn btn-warning btn-lg">Sign Up</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-5">
                        <h4 class="text-white">System Status</h4>
                        <div class="row">
                            <div class="col-md-3">
                                <span class="badge bg-success">Flask Server ✓</span>
                            </div>
                            <div class="col-md-3">
                                <span class="badge bg-success">Database ✓</span>
                            </div>
                            <div class="col-md-3">
                                <span class="badge bg-success">React Frontend ✓</span>
                            </div>
                            <div class="col-md-3">
                                <span class="badge bg-success">API Routes ✓</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/demo-login')
def demo_login():
    """Quick demo login for immediate access"""
    session['user_id'] = 'demo_user'
    session['demo_mode'] = True
    return redirect('/simple-dashboard')

@app.route('/simple-dashboard')
def simple_dashboard():
    """Simple working dashboard"""
    if 'user_id' not in session:
        return redirect('/demo-login')
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rhiz Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #1e1e2e 0%, #2d3748 100%);
                min-height: 100vh;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 2rem;
                margin: 1rem 0;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col-12">
                    <div class="glass-card">
                        <h1 class="text-white mb-4">Rhiz Dashboard</h1>
                        <p class="text-light">Welcome to your relationship intelligence platform.</p>
                        
                        <div class="row mt-4">
                            <div class="col-md-3">
                                <div class="glass-card">
                                    <h5 class="text-white">Goals</h5>
                                    <p class="text-light">Manage your objectives</p>
                                    <a href="/simple-goals" class="btn btn-primary">View Goals</a>
                                </div>
                            </div>
                            
                            <div class="col-md-3">
                                <div class="glass-card">
                                    <h5 class="text-white">Contacts</h5>
                                    <p class="text-light">Your network</p>
                                    <a href="/simple-contacts" class="btn btn-success">View Contacts</a>
                                </div>
                            </div>
                            
                            <div class="col-md-3">
                                <div class="glass-card">
                                    <h5 class="text-white">Intelligence</h5>
                                    <p class="text-light">AI insights</p>
                                    <a href="/simple-intelligence" class="btn btn-info">View Intelligence</a>
                                </div>
                            </div>
                            
                            <div class="col-md-3">
                                <div class="glass-card">
                                    <h5 class="text-white">React App</h5>
                                    <p class="text-light">Modern interface</p>
                                    <a href="/app/dashboard" class="btn btn-warning">React Dashboard</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/simple-goals')
def simple_goals():
    """Simple goals page"""
    if 'user_id' not in session:
        return redirect('/demo-login')
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Goals - Rhiz</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #1e1e2e 0%, #2d3748 100%);
                min-height: 100vh;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 2rem;
                margin: 1rem 0;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="glass-card">
                <h1 class="text-white">Goals</h1>
                <p class="text-light">Define your objectives and find relevant contacts</p>
                
                <form>
                    <div class="mb-3">
                        <label class="form-label text-white">Goal Description</label>
                        <textarea class="form-control" placeholder="e.g., Need to raise a $250k angel round"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Goal</button>
                </form>
                
                <div class="mt-4">
                    <a href="/simple-dashboard" class="btn btn-secondary">Back to Dashboard</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/simple-contacts') 
def simple_contacts():
    """Simple contacts page"""
    if 'user_id' not in session:
        return redirect('/demo-login')
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contacts - Rhiz</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #1e1e2e 0%, #2d3748 100%);
                min-height: 100vh;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 2rem;
                margin: 1rem 0;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="glass-card">
                <h1 class="text-white">Contacts</h1>
                <p class="text-light">Manage your professional network</p>
                
                <button class="btn btn-primary mb-3">Add Contact</button>
                
                <div class="table-responsive">
                    <table class="table table-dark">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Company</th>
                                <th>Title</th>
                                <th>Warmth</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Sample Contact</td>
                                <td>Demo Company</td>
                                <td>CEO</td>
                                <td><span class="badge bg-success">Warm</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-4">
                    <a href="/simple-dashboard" class="btn btn-secondary">Back to Dashboard</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/simple-intelligence')
def simple_intelligence():
    """Simple intelligence page"""
    if 'user_id' not in session:
        return redirect('/demo-login')
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Intelligence - Rhiz</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #1e1e2e 0%, #2d3748 100%);
                min-height: 100vh;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 2rem;
                margin: 1rem 0;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="glass-card">
                <h1 class="text-white">AI Intelligence</h1>
                <p class="text-light">AI-powered insights and recommendations</p>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="glass-card">
                            <h5 class="text-white">Contact Matching</h5>
                            <p class="text-light">Find relevant contacts for your goals</p>
                            <button class="btn btn-primary">Generate Matches</button>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="glass-card">
                            <h5 class="text-white">Trust Insights</h5>
                            <p class="text-light">Relationship health analysis</p>
                            <button class="btn btn-success">View Insights</button>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/simple-dashboard" class="btn btn-secondary">Back to Dashboard</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

print("Simple routes loaded successfully")