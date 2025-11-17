# Docker Deployment Guide for 43v3rMore Dashboard

Complete guide for deploying the quantum trading dashboard using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/37-AN/43v3rMore.git
cd 43v3rMore

# Copy environment template
cp .env.template .env

# Edit .env with your credentials
nano .env
```

### 2. Build and Start Services

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the Dashboard

- **Frontend Dashboard**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3000/admin/overview
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Docker Services

### Architecture

```
┌─────────────────────────────────────────┐
│           Nginx (Port 80)               │
│  ┌──────────────────────────────────┐   │
│  │   React Frontend + Dashboard     │   │
│  │   - User Interface               │   │
│  │   - Admin Dashboard              │   │
│  │   - Real-time Updates            │   │
│  └──────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌────▼────┐
    │ FastAPI │      │  Redis  │
    │ Backend │──────│  Cache  │
    │Port 8000│      │Port 6379│
    └────┬────┘      └─────────┘
         │
    ┌────▼─────┐
    │PostgreSQL│
    │ Database │
    │Port 5432 │
    └──────────┘
```

### Service Details

#### 1. Frontend (quantum-frontend)
- **Image**: Multi-stage Node 18 + Nginx Alpine
- **Port**: 3000 → 80
- **Features**:
  - Production-optimized React build
  - Nginx reverse proxy for API/WebSocket
  - SPA routing for admin dashboard
  - Gzip compression
  - Static asset caching

#### 2. Backend (quantum-app)
- **Image**: Python 3.11 Slim
- **Port**: 8000
- **Features**:
  - FastAPI application
  - Dashboard API routes
  - WebSocket support
  - Health checks

#### 3. PostgreSQL (quantum-postgres)
- **Image**: PostgreSQL 15 Alpine
- **Port**: 5432
- **Storage**: Persistent volume `postgres_data`

#### 4. Redis (quantum-redis)
- **Image**: Redis 7 Alpine
- **Port**: 6379
- **Storage**: Persistent volume `redis_data`

## Environment Configuration

### Required Environment Variables

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
APP_ENV=production

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost

# Database (PostgreSQL)
DATABASE_URL=postgresql://quantum_user:quantum_pass@postgres:5432/quantum_trading

# Redis Cache
REDIS_URL=redis://redis:6379

# Quantum Engine
IBM_QUANTUM_TOKEN=your_ibm_quantum_token

# MT5 Configuration
MT5_SERVER=your_mt5_server
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password

# Notifications
TELEGRAM_BOT_TOKEN=your_telegram_token
SENDGRID_API_KEY=your_sendgrid_key

# PayFast
PAYFAST_MERCHANT_ID=your_merchant_id
PAYFAST_MERCHANT_KEY=your_merchant_key
PAYFAST_PASSPHRASE=your_passphrase
PAYFAST_SANDBOX=true
```

## Docker Commands

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d frontend

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f app
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop frontend
```

### Rebuilding

```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build frontend

# Rebuild and restart
docker-compose up -d --build
```

### Monitoring

```bash
# View running containers
docker-compose ps

# View resource usage
docker stats

# View container logs
docker-compose logs --tail=100 -f app

# Execute commands in container
docker-compose exec app bash
docker-compose exec frontend sh
```

## Production Deployment

### 1. Security Hardening

Update `.env` for production:

```env
DEBUG=false
APP_ENV=production
PAYFAST_SANDBOX=false

# Use strong passwords
POSTGRES_PASSWORD=<strong-password>

# Restrict CORS
CORS_ORIGINS=https://yourdomain.com
```

### 2. SSL/TLS Configuration

Add Nginx SSL configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # ... rest of config
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

Update `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./ssl:/etc/nginx/ssl:ro
```

### 3. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  frontend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 4. Backup Strategy

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U quantum_user quantum_trading > backup.sql

# Restore PostgreSQL
docker-compose exec -T postgres psql -U quantum_user quantum_trading < backup.sql

# Backup Redis
docker-compose exec redis redis-cli SAVE
docker cp quantum-redis:/data/dump.rdb ./redis-backup.rdb
```

## Troubleshooting

### Frontend not loading

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Clear browser cache and try http://localhost:3000
```

### API connection errors

```bash
# Check backend logs
docker-compose logs app

# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
docker-compose exec app env | grep CORS
```

### Database connection issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U quantum_user -d quantum_trading -c "SELECT 1;"
```

### WebSocket not connecting

```bash
# Check nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Verify WebSocket proxy settings
# Look for: proxy_set_header Upgrade $http_upgrade;

# Restart frontend
docker-compose restart frontend
```

### Container keeps restarting

```bash
# Check container logs
docker-compose logs --tail=50 <service-name>

# Check container health
docker inspect quantum-app | grep Health -A 20

# Debug inside container
docker-compose exec app bash
```

## Performance Optimization

### 1. Enable Redis Caching

Ensure Redis is properly configured in `.env`:

```env
REDIS_URL=redis://redis:6379
REDIS_CACHE_TTL=3600
```

### 2. Database Connection Pooling

Configure in `.env`:

```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

### 3. Nginx Caching

Add to `nginx.conf`:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

location /api {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_use_stale error timeout updating;
    # ... other proxy settings
}
```

## Monitoring

### Health Checks

All services include health checks:

```bash
# Check all services
docker-compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000/
```

### Prometheus + Grafana (Optional)

Add monitoring services to `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Scaling

### Horizontal Scaling

Scale backend instances:

```bash
# Scale to 3 backend instances
docker-compose up -d --scale app=3

# Add load balancer (nginx) configuration
```

### Vertical Scaling

Increase container resources:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

## Maintenance

### Update Containers

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build

# Cleanup old images
docker image prune -a
```

### Cleanup

```bash
# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Full cleanup
docker system prune -a --volumes
```

## Support

- **Documentation**: See DASHBOARD_README.md
- **Issues**: https://github.com/37-AN/43v3rMore/issues
- **Logs**: Always check logs first: `docker-compose logs -f`

## Security Checklist

- [ ] Changed default database password
- [ ] Disabled debug mode in production
- [ ] Configured SSL/TLS
- [ ] Set restrictive CORS origins
- [ ] Enabled firewall rules
- [ ] Regular security updates
- [ ] Backup strategy implemented
- [ ] Monitoring enabled
- [ ] Rate limiting configured
- [ ] Secrets not in git repository
