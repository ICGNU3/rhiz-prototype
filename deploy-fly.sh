#!/bin/bash

# One-click Fly.io deployment script for Rhiz Platform
# Prerequisites: 
# 1. Install Fly CLI: curl -L https://fly.io/install.sh | sh
# 2. Sign up and login: fly auth signup && fly auth login
# 3. Set environment variables in .env file

set -e

echo "🚀 Starting Rhiz Platform deployment to Fly.io..."

# Check if Fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI is not installed. Please install it first:"
    echo "curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if logged in to Fly.io
if ! fly auth whoami &> /dev/null; then
    echo "❌ Please login to Fly.io first:"
    echo "fly auth signup && fly auth login"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it"
    exit 1
fi

# Generate app name
APP_NAME="rhiz-$(date +%s)"

# Create fly.toml configuration
echo "⚙️ Creating Fly.io configuration..."
cat > fly.toml << EOF
app = "$APP_NAME"
primary_region = "iad"

[build]

[env]
FLASK_ENV = "production"
FLASK_DEBUG = "0"
PORT = "8080"

[http_service]
internal_port = 8080
force_https = true
auto_stop_machines = true
auto_start_machines = true
min_machines_running = 1
processes = ["app"]

[[http_service.checks]]
grace_period = "10s"
interval = "30s"
method = "GET"
timeout = "5s"
path = "/health"

[machine]
memory = "1gb"
cpu_kind = "shared"
cpus = 1

[processes]
app = "gunicorn --bind 0.0.0.0:8080 --workers 2 main:app"

[[services]]
protocol = "tcp"
internal_port = 8080

[services.concurrency]
type = "connections"
hard_limit = 25
soft_limit = 20

[[services.http_checks]]
interval = "10s"
grace_period = "5s"
method = "get"
path = "/health"
protocol = "http"
timeout = "2s"
tls_skip_verify = false

[[services.ports]]
force_https = true
handlers = ["http"]
port = 80

[[services.ports]]
handlers = ["tls", "http"]
port = 443

[[services.tcp_checks]]
grace_period = "1s"
interval = "15s"
restart_limit = 0
timeout = "2s"
EOF

# Initialize Fly app
echo "📦 Initializing Fly.io app..."
fly apps create $APP_NAME --generate-name

# Create PostgreSQL database
echo "🗄️ Creating PostgreSQL database..."
fly postgres create --name "$APP_NAME-db" --region iad --initial-cluster-size 1

# Attach database to app
fly postgres attach --app $APP_NAME "$APP_NAME-db"

# Set environment variables from .env file
echo "⚙️ Setting environment variables..."
source .env

# Required variables
fly secrets set SESSION_SECRET="$SESSION_SECRET"
fly secrets set JWT_SECRET_KEY="$JWT_SECRET_KEY"

# Optional API keys (only set if present in .env)
[ -n "$OPENAI_API_KEY" ] && fly secrets set OPENAI_API_KEY="$OPENAI_API_KEY"
[ -n "$RESEND_API_KEY" ] && fly secrets set RESEND_API_KEY="$RESEND_API_KEY"
[ -n "$STRIPE_SECRET_KEY" ] && fly secrets set STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY"
[ -n "$STRIPE_PUBLISHABLE_KEY" ] && fly secrets set STRIPE_PUBLISHABLE_KEY="$STRIPE_PUBLISHABLE_KEY"
[ -n "$GOOGLE_OAUTH_CLIENT_ID" ] && fly secrets set GOOGLE_OAUTH_CLIENT_ID="$GOOGLE_OAUTH_CLIENT_ID"
[ -n "$GOOGLE_OAUTH_CLIENT_SECRET" ] && fly secrets set GOOGLE_OAUTH_CLIENT_SECRET="$GOOGLE_OAUTH_CLIENT_SECRET"

# Create .dockerignore for efficient builds
cat > .dockerignore << EOF
.git
.gitignore
README.md
Dockerfile
.dockerignore
frontend/node_modules
frontend/dist
.env
*.log
__pycache__
*.pyc
.pytest_cache
.coverage
.vscode
.idea
EOF

# Deploy the application
echo "🚀 Deploying to Fly.io..."
fly deploy --remote-only

# Run database migrations
echo "📊 Running database migrations..."
fly ssh console --command "python -c '
from app import app, db
with app.app_context():
    db.create_all()
    print(\"Database tables created successfully\")
'"

# Get the deployment URL
DEPLOYMENT_URL="https://$APP_NAME.fly.dev"

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Your Rhiz Platform is available at: $DEPLOYMENT_URL"
echo ""
echo "📋 Next steps:"
echo "1. Visit the deployment URL to verify everything is working"
echo "2. Configure custom domain: fly certs create yourdomain.com"
echo "3. Set up monitoring: fly logs"
echo "4. Scale if needed: fly scale count 2"
echo ""
echo "📊 Monitor your deployment:"
echo "fly logs --app $APP_NAME"
echo ""
echo "🔧 Manage secrets:"
echo "fly secrets list --app $APP_NAME"
echo ""
echo "💾 Database management:"
echo "fly postgres connect --app $APP_NAME-db"
echo ""

echo "🎉 Happy relationship building with Rhiz!"