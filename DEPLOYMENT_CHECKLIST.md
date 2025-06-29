# Rhiz Platform Deployment Checklist

## 🚀 Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `SESSION_SECRET` (32+ character random string)
- [ ] Set `JWT_SECRET_KEY` (32+ character random string)
- [ ] Configure `OPENAI_API_KEY` (required for AI features)
- [ ] Configure `DATABASE_URL` (PostgreSQL connection string)
- [ ] Optional: Set `RESEND_API_KEY` for email functionality
- [ ] Optional: Set Stripe keys for payment processing
- [ ] Optional: Set Google OAuth credentials for social login

### 2. Security Verification
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Verify no secrets are committed to git
- [ ] Generate cryptographically secure session secrets
- [ ] Use environment-specific API keys (not test keys in production)
- [ ] Configure proper CORS settings for your domain

### 3. Testing & Quality Assurance
- [ ] Run frontend tests: `cd frontend && npm test`
- [ ] Run backend tests: `pytest`
- [ ] Run E2E tests: `npx playwright test`
- [ ] Verify TypeScript compilation: `cd frontend && npm run type-check`
- [ ] Check linting: `npm run lint` (frontend) and `flake8` (backend)

### 4. Database Preparation
- [ ] Ensure PostgreSQL is available
- [ ] Verify database permissions
- [ ] Test database connection
- [ ] Prepare for schema migration

## 🛠 Deployment Options

### Option 1: Railway Deployment (Recommended)
```bash
# Prerequisites
npm install -g @railway/cli
railway login

# Deploy
./deploy-railway.sh
```

**Railway Benefits:**
- Automatic PostgreSQL provisioning
- Zero-config HTTPS
- Auto-scaling
- Built-in monitoring
- Simple environment variable management

### Option 2: Fly.io Deployment
```bash
# Prerequisites
curl -L https://fly.io/install.sh | sh
fly auth login

# Deploy
./deploy-fly.sh
```

**Fly.io Benefits:**
- Global edge deployment
- Automatic SSL certificates
- Built-in PostgreSQL
- Docker-native
- Edge computing capabilities

### Option 3: Docker Compose (Self-Hosted)
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

**Docker Benefits:**
- Complete control over infrastructure
- Local development environment
- Custom scaling configuration
- Cost-effective for high traffic

## 📋 Post-Deployment Verification

### 1. Health Checks
- [ ] Visit `/health` endpoint
- [ ] Verify 200 OK response
- [ ] Check database connectivity
- [ ] Confirm all services are "healthy"

### 2. Core Functionality Testing
- [ ] Test landing page loads
- [ ] Verify registration/login flow
- [ ] Test magic link authentication
- [ ] Confirm dashboard accessibility
- [ ] Verify contact import functionality
- [ ] Test AI chat features (if OpenAI configured)

### 3. Performance Verification
- [ ] Check page load times < 3 seconds
- [ ] Verify API response times < 1 second
- [ ] Test with multiple concurrent users
- [ ] Monitor error rates < 1%

### 4. Security Validation
- [ ] Verify HTTPS redirection
- [ ] Check security headers
- [ ] Test authentication flows
- [ ] Validate session management
- [ ] Confirm API endpoint protection

## 🔧 Environment-Specific Configuration

### Development Environment
```bash
FLASK_ENV=development
FLASK_DEBUG=1
# Use test API keys
# Enable detailed logging
```

### Staging Environment
```bash
FLASK_ENV=staging
FLASK_DEBUG=0
# Use staging API keys
# Mirror production settings
```

### Production Environment
```bash
FLASK_ENV=production
FLASK_DEBUG=0
# Use production API keys
# Enable error tracking
# Configure monitoring
```

## 📊 Monitoring & Maintenance

### Essential Monitoring
- [ ] Set up uptime monitoring
- [ ] Configure error tracking
- [ ] Monitor database performance
- [ ] Track API response times
- [ ] Monitor resource usage

### Regular Maintenance
- [ ] Weekly dependency updates
- [ ] Monthly security patches
- [ ] Quarterly performance reviews
- [ ] Regular database backups
- [ ] API key rotation schedule

## 🆘 Troubleshooting Guide

### Common Issues

**Database Connection Error**
- Verify `DATABASE_URL` format
- Check network connectivity
- Confirm PostgreSQL is running
- Validate credentials

**OpenAI API Error**
- Verify API key validity
- Check usage limits
- Confirm internet connectivity
- Review rate limiting

**Authentication Issues**
- Verify `SESSION_SECRET` and `JWT_SECRET_KEY`
- Check cookie settings
- Confirm HTTPS configuration
- Review CORS settings

**Build Failures**
- Clear Docker cache: `docker system prune`
- Check Dockerfile syntax
- Verify all dependencies
- Review build logs

### Emergency Rollback
```bash
# Docker rollback
docker-compose down
docker-compose up -d --force-recreate

# Railway rollback
railway rollback

# Fly.io rollback
fly releases list
fly releases rollback <version>
```

## 📞 Support Resources

### Getting Help
1. Check deployment logs first
2. Review error messages carefully
3. Consult this checklist
4. Check platform-specific documentation
5. Contact development team if needed

### Useful Commands
```bash
# Railway
railway logs --follow
railway status
railway variables

# Fly.io
fly logs
fly status
fly secrets list

# Docker
docker-compose logs -f
docker stats
docker system df
```

## ✅ Final Verification

Before marking deployment complete:
- [ ] All checklist items completed
- [ ] Application accessible via HTTPS
- [ ] Core features functional
- [ ] Performance acceptable
- [ ] Monitoring configured
- [ ] Team notified of deployment
- [ ] Documentation updated
- [ ] Backup procedures verified

---

**Deployment Complete! 🎉**

Your Rhiz Platform is now live and ready for relationship intelligence!