#!/bin/bash

# Deployment verification script for Rhiz Platform
# This script verifies all deployment files are properly configured

set -e

echo "🔍 Rhiz Platform Deployment Verification"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
        return 0
    else
        echo -e "${RED}✗${NC} $description: $file (missing)"
        return 1
    fi
}

check_executable() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ] && [ -x "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file (executable)"
        return 0
    elif [ -f "$file" ]; then
        echo -e "${YELLOW}⚠${NC} $description: $file (not executable)"
        return 1
    else
        echo -e "${RED}✗${NC} $description: $file (missing)"
        return 1
    fi
}

# Track verification status
ERRORS=0

echo ""
echo "📋 Configuration Files"
echo "----------------------"
check_file ".env.example" "Environment template" || ((ERRORS++))
check_file ".dockerignore" "Docker build optimization" || ((ERRORS++))

echo ""
echo "🐳 Docker Configuration"
echo "-----------------------"
check_file "Dockerfile" "Backend container" || ((ERRORS++))
check_file "frontend/Dockerfile" "Frontend container" || ((ERRORS++))
check_file "frontend/nginx.conf" "Nginx configuration" || ((ERRORS++))
check_file "docker-compose.yml" "Development orchestration" || ((ERRORS++))
check_file "docker-compose.prod.yml" "Production orchestration" || ((ERRORS++))

echo ""
echo "🚀 Deployment Scripts"
echo "--------------------"
check_executable "deploy-railway.sh" "Railway deployment" || ((ERRORS++))
check_executable "deploy-fly.sh" "Fly.io deployment" || ((ERRORS++))

echo ""
echo "📚 Documentation"
echo "----------------"
check_file "RELEASE_NOTES.md" "Release documentation" || ((ERRORS++))
check_file "DEPLOYMENT_CHECKLIST.md" "Deployment guide" || ((ERRORS++))

echo ""
echo "🔧 Environment Verification"
echo "----------------------------"

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check for required variables
    if grep -q "SESSION_SECRET=" .env; then
        echo -e "${GREEN}✓${NC} SESSION_SECRET configured"
    else
        echo -e "${RED}✗${NC} SESSION_SECRET not found in .env"
        ((ERRORS++))
    fi
    
    if grep -q "JWT_SECRET_KEY=" .env; then
        echo -e "${GREEN}✓${NC} JWT_SECRET_KEY configured"
    else
        echo -e "${RED}✗${NC} JWT_SECRET_KEY not found in .env"
        ((ERRORS++))
    fi
    
    if grep -q "OPENAI_API_KEY=" .env; then
        echo -e "${GREEN}✓${NC} OPENAI_API_KEY configured"
    else
        echo -e "${YELLOW}⚠${NC} OPENAI_API_KEY not found (AI features will be limited)"
    fi
    
else
    echo -e "${YELLOW}⚠${NC} .env file not found (copy from .env.example)"
fi

echo ""
echo "📦 Dependencies Check"
echo "--------------------"

# Check Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker installed"
else
    echo -e "${RED}✗${NC} Docker not installed"
    ((ERRORS++))
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose installed"
else
    echo -e "${RED}✗${NC} Docker Compose not installed"
    ((ERRORS++))
fi

# Check Node.js (for frontend)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js installed ($NODE_VERSION)"
else
    echo -e "${YELLOW}⚠${NC} Node.js not found (needed for frontend development)"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python installed ($PYTHON_VERSION)"
else
    echo -e "${RED}✗${NC} Python 3 not installed"
    ((ERRORS++))
fi

echo ""
echo "========================================"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 All deployment files verified successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure .env file with your secrets"
    echo "2. Choose your deployment platform:"
    echo "   • Railway: ./deploy-railway.sh"
    echo "   • Fly.io: ./deploy-fly.sh"
    echo "   • Docker: docker-compose up -d"
    echo ""
    echo "3. Follow DEPLOYMENT_CHECKLIST.md for detailed instructions"
else
    echo -e "${RED}❌ Found $ERRORS issue(s) that need to be resolved${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
fi

echo ""
echo "For detailed deployment instructions, see:"
echo "• DEPLOYMENT_CHECKLIST.md"
echo "• RELEASE_NOTES.md"