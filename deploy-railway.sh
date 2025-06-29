#!/bin/bash

# One-click Railway deployment script for Rhiz Platform
# Prerequisites: 
# 1. Install Railway CLI: npm install -g @railway/cli
# 2. Login: railway login
# 3. Set environment variables in .env file

set -e

echo "🚀 Starting Rhiz Platform deployment to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Please login to Railway first:"
    echo "railway login"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it"
    exit 1
fi

# Create new Railway project
echo "📦 Creating new Railway project..."
railway init

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add postgresql

# Deploy backend service
echo "🔧 Deploying backend service..."
railway up --detach

# Set environment variables from .env file
echo "⚙️ Setting environment variables..."
source .env

# Required variables
railway variables set FLASK_ENV=production
railway variables set FLASK_DEBUG=0
railway variables set SESSION_SECRET="$SESSION_SECRET"
railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"

# Optional API keys (only set if present in .env)
[ -n "$OPENAI_API_KEY" ] && railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
[ -n "$RESEND_API_KEY" ] && railway variables set RESEND_API_KEY="$RESEND_API_KEY"
[ -n "$STRIPE_SECRET_KEY" ] && railway variables set STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY"
[ -n "$STRIPE_PUBLISHABLE_KEY" ] && railway variables set STRIPE_PUBLISHABLE_KEY="$STRIPE_PUBLISHABLE_KEY"
[ -n "$GOOGLE_OAUTH_CLIENT_ID" ] && railway variables set GOOGLE_OAUTH_CLIENT_ID="$GOOGLE_OAUTH_CLIENT_ID"
[ -n "$GOOGLE_OAUTH_CLIENT_SECRET" ] && railway variables set GOOGLE_OAUTH_CLIENT_SECRET="$GOOGLE_OAUTH_CLIENT_SECRET"

# Railway will automatically set DATABASE_URL for PostgreSQL

# Create railway.json for build configuration
cat > railway.json << EOF
{
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:\$PORT --workers 4 main:app",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
EOF

# Deploy with database migrations
echo "📊 Running database migrations..."
railway run python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Final deployment
echo "🚀 Final deployment..."
railway up

# Get the deployment URL
DEPLOYMENT_URL=$(railway status --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
deployments = data.get('deployments', [])
if deployments:
    print(deployments[0].get('url', 'Not available'))
else:
    print('Not available')
")

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Your Rhiz Platform is available at: $DEPLOYMENT_URL"
echo ""
echo "📋 Next steps:"
echo "1. Visit the deployment URL to verify everything is working"
echo "2. Configure your custom domain in Railway dashboard (optional)"
echo "3. Set up monitoring and alerts"
echo "4. Configure SSL certificate (automatic with Railway)"
echo ""
echo "📊 Monitor your deployment:"
echo "railway logs --follow"
echo ""
echo "🔧 Manage environment variables:"
echo "railway variables"
echo ""

# Clean up temporary files
rm -f railway.json

echo "🎉 Happy relationship building with Rhiz!"