# Production Deployment Guide - Quantum Trading AI

This guide covers deploying Quantum Trading AI to production using Docker, nginx, and automated CI/CD.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Initial Deployment](#initial-deployment)
4. [CI/CD Configuration](#cicd-configuration)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 22.04 LTS (recommended) or similar Linux distribution
- **CPU**: Minimum 4 cores (8+ recommended for production)
- **RAM**: Minimum 8GB (16GB+ recommended)
- **Storage**: Minimum 50GB SSD
- **Network**: Static IP address and domain name

### Required Software

- Docker Engine 24.0+
- Docker Compose 2.20+
- Git 2.40+
- Nginx (handled by Docker)
- SSL certificates (Let's Encrypt recommended)

### Required Accounts

- **IBM Quantum**: For quantum computing access
- **Anthropic**: For Claude AI API
- **Supabase**: For database hosting
- **SendGrid**: For email service
- **Twilio**: For SMS/WhatsApp
- **PayFast**: For payments (South African)
- **Telegram**: Bot API token

---

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create application user
sudo useradd -m -s /bin/bash quantum
sudo usermod -aG docker quantum

# Create application directory
sudo mkdir -p /opt/quantum-trading-ai
sudo chown quantum:quantum /opt/quantum-trading-ai

# Create backup directory
sudo mkdir -p /opt/quantum-trading-ai-backups
sudo chown quantum:quantum /opt/quantum-trading-ai-backups
```

### 2. SSL Certificates (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot

# Obtain SSL certificates
sudo certbot certonly --standalone -d quantumtrading.ai -d www.quantumtrading.ai

# Copy certificates to nginx directory
sudo mkdir -p /opt/quantum-trading-ai/nginx/ssl
sudo cp /etc/letsencrypt/live/quantumtrading.ai/fullchain.pem /opt/quantum-trading-ai/nginx/ssl/
sudo cp /etc/letsencrypt/live/quantumtrading.ai/privkey.pem /opt/quantum-trading-ai/nginx/ssl/
sudo chown -R quantum:quantum /opt/quantum-trading-ai/nginx/ssl
```

### 3. Firewall Configuration

```bash
# Allow HTTP, HTTPS, SSH
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## Initial Deployment

### 1. Clone Repository

```bash
# Switch to application user
sudo su - quantum

# Clone repository
cd /opt/quantum-trading-ai
git clone https://github.com/yourusername/quantum-trading-ai.git .

# Checkout main branch
git checkout main
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.production.template .env.production

# Edit environment variables
nano .env.production

# IMPORTANT: Fill in all required values:
# - Database credentials
# - API keys (Anthropic, IBM Quantum, SendGrid, Twilio, PayFast)
# - Secret keys (generate strong random values)
# - Telegram bot token
```

**Generate strong secrets:**

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32

# Generate REDIS_PASSWORD
openssl rand -base64 32

# Generate POSTGRES_PASSWORD
openssl rand -base64 32
```

### 3. Build and Start Services

```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Run Database Migrations

```bash
# Run migrations
docker exec quantum-trading-api python -m src.database.migrations

# Verify database
docker exec quantum-trading-postgres psql -U quantum_admin -d quantum_trading -c "\dt"
```

### 5. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Test API
curl http://localhost:8000/api/v1/status

# Test website
curl http://localhost

# SSL test
curl https://quantumtrading.ai
```

---

## CI/CD Configuration

### GitHub Actions Setup

1. **Add Repository Secrets**

Go to GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

```
PRODUCTION_HOST=your-server-ip
PRODUCTION_USER=quantum
PRODUCTION_SSH_KEY=<your-private-key>
PRODUCTION_PORT=22
```

2. **Generate SSH Key**

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub quantum@your-server-ip

# Add private key to GitHub secrets
cat ~/.ssh/id_ed25519
```

3. **Trigger Deployment**

```bash
# Push to main branch triggers automatic deployment
git push origin main

# Or manually trigger from GitHub Actions UI
```

### Automated Deployment Flow

1. Code pushed to `main` branch
2. Run tests
3. Build Docker images
4. Push images to registry
5. SSH to production server
6. Pull latest code
7. Pull latest Docker images
8. Restart services
9. Run health checks
10. Send notifications

---

## Monitoring & Maintenance

### Access Monitoring Dashboards

**Prometheus**: http://your-server-ip:9090
**Grafana**: http://your-server-ip:3000
- Username: `admin`
- Password: From `GRAFANA_PASSWORD` in `.env.production`

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 api
```

### Database Backups

**Automatic backups** run daily at 2 AM (configured in docker-compose.prod.yml).

**Manual backup:**

```bash
# Backup database
docker exec quantum-trading-postgres pg_dump -U quantum_admin quantum_trading > backup_$(date +%Y%m%d).sql

# Backup data directory
tar -czf data_backup_$(date +%Y%m%d).tar.gz /opt/quantum-trading-ai/data
```

**Restore backup:**

```bash
# Restore database
cat backup_20250116.sql | docker exec -i quantum-trading-postgres psql -U quantum_admin quantum_trading

# Restore data
tar -xzf data_backup_20250116.tar.gz -C /opt/quantum-trading-ai/
```

### SSL Certificate Renewal

```bash
# Renew certificates (run monthly)
sudo certbot renew

# Copy new certificates
sudo cp /etc/letsencrypt/live/quantumtrading.ai/fullchain.pem /opt/quantum-trading-ai/nginx/ssl/
sudo cp /etc/letsencrypt/live/quantumtrading.ai/privkey.pem /opt/quantum-trading-ai/nginx/ssl/

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Update Deployment

```bash
# Use deployment script
sudo chmod +x scripts/deploy.sh
sudo ./scripts/deploy.sh production
```

The script automatically:
- Creates backup
- Pulls latest code
- Rebuilds images
- Restarts services
- Runs health checks
- Cleans up old images

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service-name

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Restart specific service
docker-compose -f docker-compose.prod.yml restart service-name
```

### Database Connection Issues

```bash
# Test database connection
docker exec quantum-trading-api python -c "from src.database.supabase import SupabaseClient; client = SupabaseClient(); print('Connected!')"

# Check PostgreSQL
docker exec quantum-trading-postgres pg_isready -U quantum_admin
```

### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart memory-heavy services
docker-compose -f docker-compose.prod.yml restart api signal-generator
```

### SSL Certificate Issues

```bash
# Test SSL
openssl s_client -connect quantumtrading.ai:443 -servername quantumtrading.ai

# Check certificate expiry
echo | openssl s_client -servername quantumtrading.ai -connect quantumtrading.ai:443 2>/dev/null | openssl x509 -noout -dates
```

### Performance Issues

```bash
# Check CPU/Memory
htop

# Check Docker resource usage
docker stats

# Check API response time
curl -w "@curl-format.txt" -o /dev/null -s https://quantumtrading.ai/api/v1/health
```

---

## Rollback Procedures

### Automatic Rollback (GitHub Actions)

1. Go to GitHub Actions
2. Find "Deploy to Production" workflow
3. Click "Run workflow"
4. Select "rollback" option
5. Confirm

### Manual Rollback

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git log --oneline  # Find previous commit
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Restore database from backup (if needed)
cat /opt/quantum-trading-ai-backups/backup_YYYYMMDD/database.sql | docker exec -i quantum-trading-postgres psql -U quantum_admin quantum_trading
```

### Emergency Shutdown

```bash
# Stop all services immediately
docker-compose -f docker-compose.prod.yml down

# Or stop entire Docker
sudo systemctl stop docker
```

---

## Security Checklist

- [ ] Strong passwords for all services (32+ characters)
- [ ] SSH key-only authentication (disable password auth)
- [ ] Firewall configured (UFW or iptables)
- [ ] SSL certificates installed and auto-renewing
- [ ] Environment variables secured (not in version control)
- [ ] Database backups automated and tested
- [ ] Monitoring and alerting configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers enabled in nginx
- [ ] Regular security updates scheduled

---

## Performance Optimization

### Nginx Tuning

```nginx
# In nginx.conf
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### Docker Resource Limits

```yaml
# In docker-compose.prod.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Database Optimization

```bash
# PostgreSQL tuning
docker exec quantum-trading-postgres psql -U quantum_admin -c "ALTER SYSTEM SET shared_buffers = '256MB';"
docker exec quantum-trading-postgres psql -U quantum_admin -c "ALTER SYSTEM SET effective_cache_size = '1GB';"
docker-compose -f docker-compose.prod.yml restart postgres
```

---

## Support

For deployment issues:

- Email: devops@quantumtrading.ai
- Documentation: https://github.com/yourusername/quantum-trading-ai/wiki
- Issues: https://github.com/yourusername/quantum-trading-ai/issues

---

**Last Updated**: 2025-11-16
**Version**: 3.0.0
