# Deployment Guide

## Quick Start (1 Minute)

```bash
# 1. Clone and enter directory
git clone https://github.com/37-AN/43v3rMore.git
cd 43v3rMore

# 2. Run setup wizard
chmod +x start.sh
./start.sh
```

## What Gets Deployed

### Services
- ✅ **Frontend** (React + TypeScript): http://localhost:3000
- ✅ **Backend API** (FastAPI): http://localhost:8000
- ✅ **API Docs**: http://localhost:8000/docs
- ✅ **PostgreSQL**: Port 5432
- ✅ **Redis**: Port 6379

### Features
- Authentication (Login/Signup)
- Trading Dashboard
- Signal Monitoring
- Subscription Management
- Dark Mode
- Responsive Design

## Manual Deployment

### Option 1: Development Mode (Hot Reload)
```bash
cp .env.template .env
cp frontend/.env.example frontend/.env
docker-compose -f docker-compose.dev.yml up
```

### Option 2: Production Mode (Optimized)
```bash
cp .env.template .env
docker-compose up -d
```

## Verify Deployment

```bash
# Check services
docker-compose ps

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# View logs
docker-compose logs -f
```

## Default Credentials

For development (configure in .env):
- Database: quantum_user / quantum_pass_dev_only
- All other services: Configure in .env

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "3001:80"  # Frontend
  - "8001:8000"  # Backend
```

### Services Won't Start
```bash
# Clean and restart
docker-compose down -v
docker-compose up --build
```

### See Detailed Logs
```bash
docker-compose logs -f app
docker-compose logs -f frontend
```

## Next Steps

1. Edit `.env` with real credentials
2. Access http://localhost:3000
3. Create an account
4. Explore the dashboard
5. View API docs at http://localhost:8000/docs

## Production Deployment

For production deployment:
1. Update environment variables
2. Configure SSL/TLS
3. Set up reverse proxy
4. Configure backups
5. Enable monitoring

See DOCKER.md for complete documentation.
