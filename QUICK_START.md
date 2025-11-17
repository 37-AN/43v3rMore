# 43v3rMore Trading Dashboard - Quick Start Guide

Get the admin dashboard running in 5 minutes using Docker.

## 🚀 Prerequisites

- Docker Desktop installed ([Download](https://docs.docker.com/get-docker/))
- Git installed
- 4GB RAM minimum
- 20GB disk space

## 📦 Quick Start (Docker - Recommended)

### 1. Clone Repository

```bash
git clone https://github.com/37-AN/43v3rMore.git
cd 43v3rMore
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit with your credentials (use any text editor)
nano .env  # or vim .env or code .env
```

**Minimum required configuration in `.env`:**

```env
# IBM Quantum (required for quantum signals)
IBM_QUANTUM_TOKEN=your_ibm_quantum_token_here

# Database (can use defaults for development)
DATABASE_URL=postgresql://quantum_user:quantum_pass@postgres:5432/quantum_trading

# Redis (can use defaults)
REDIS_URL=redis://redis:6379
```

### 3. Deploy with One Command

```bash
# Automated deployment script
./scripts/deploy-docker.sh
```

**OR manually:**

```bash
# Build images
docker compose build

# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

### 4. Access the Dashboard

Once services are running (takes ~30 seconds):

| Service | URL | Description |
|---------|-----|-------------|
| **Admin Dashboard** | http://localhost:3000/admin/overview | 🎯 Start here! |
| Frontend | http://localhost:3000 | User interface |
| Backend API | http://localhost:8000/docs | API documentation |
| Health Check | http://localhost:8000/health | Service status |

## 🎯 Dashboard Modules

Navigate to these URLs in your browser:

1. **System Overview**: http://localhost:3000/admin/overview
   - Service health monitoring
   - Key metrics dashboard
   - Real-time activity feed

2. **Quantum Signals**: http://localhost:3000/admin/quantum-signals
   - Live signal generation
   - Accuracy metrics
   - Circuit monitoring

3. **MT5 Monitor**: http://localhost:3000/admin/mt5-monitor
   - Trading activity
   - Position management
   - Account statistics

4. **User Management**: http://localhost:3000/admin/users
   - Subscriber list
   - User activity
   - Subscription management

5. **Financial Dashboard**: http://localhost:3000/admin/financial
   - Revenue tracking
   - MRR/ARR metrics
   - Projections

6. **Configuration**: http://localhost:3000/admin/configuration
   - System settings
   - Service configuration
   - Feature flags

7. **Alerts & Performance**: http://localhost:3000/admin/alerts
   - System alerts
   - Performance metrics
   - Monitoring

## 🧪 Test Deployment

```bash
# Run automated tests
./scripts/test-docker.sh
```

## 🛠 Common Commands

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f frontend
docker compose logs -f app
docker compose logs -f postgres
docker compose logs -f redis
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart frontend
docker compose restart app
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```

### Rebuild After Changes

```bash
# Rebuild and restart
docker compose up -d --build

# Rebuild specific service
docker compose build frontend
docker compose up -d frontend
```

## 🐛 Troubleshooting

### Frontend not loading

```bash
# Check frontend logs
docker compose logs frontend

# Rebuild frontend
docker compose build --no-cache frontend
docker compose up -d frontend

# Clear browser cache and refresh
```

### API not responding

```bash
# Check backend logs
docker compose logs app

# Verify backend is running
curl http://localhost:8000/health

# Restart backend
docker compose restart app
```

### Database connection issues

```bash
# Check database
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U quantum_user -d quantum_trading -c "SELECT 1;"

# Restart database
docker compose restart postgres
```

### Port already in use

```bash
# Check what's using the port
lsof -i :3000  # or :8000

# Stop the conflicting service or change ports in docker-compose.yml
```

## 📊 Initial Setup

### 1. Create Admin User (via Backend)

```bash
# Access backend container
docker compose exec app bash

# Run Python shell
python

# Create admin user
from src.database.queries import UserQueries
from src.database.models import User

queries = UserQueries()
admin_user = queries.create_user({
    "email": "admin@example.com",
    "name": "Admin User",
    "plan": "admin",
    "status": "active"
})
print(f"Admin user created: {admin_user.email}")
```

### 2. Generate Test Data (Optional)

```bash
# Access backend container
docker compose exec app python

# Generate test signals
from src.quantum_engine import QuantumTradingEngine
engine = QuantumTradingEngine(symbols=["EURUSD", "GBPUSD"])
engine.start()
signals = engine.analyze_all_symbols()
print(f"Generated {len(signals)} test signals")
```

## 🔒 Production Deployment

For production deployment, see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for:

- SSL/TLS configuration
- Security hardening
- Resource limits
- Backup strategies
- Monitoring setup

## 📚 Documentation

- **Full Dashboard Guide**: [DASHBOARD_README.md](DASHBOARD_README.md)
- **Docker Deployment**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **API Documentation**: http://localhost:8000/docs (when running)

## 🆘 Getting Help

- **Check logs first**: `docker compose logs -f`
- **GitHub Issues**: https://github.com/37-AN/43v3rMore/issues
- **Health Check**: http://localhost:8000/health

## ✅ Verification Checklist

After deployment, verify:

- [ ] All containers running: `docker compose ps`
- [ ] Backend healthy: `curl http://localhost:8000/health`
- [ ] Frontend accessible: http://localhost:3000
- [ ] Admin dashboard loads: http://localhost:3000/admin/overview
- [ ] Database connected: Check logs
- [ ] Redis connected: Check logs
- [ ] No error logs: `docker compose logs --tail=50`

## 🎉 Next Steps

1. ✅ Dashboard is running
2. 📱 Open http://localhost:3000/admin/overview
3. 🔐 Set up authentication (see DASHBOARD_README.md)
4. 📊 Explore all 7 dashboard modules
5. ⚙️ Configure quantum engine settings
6. 🚀 Connect MT5 account (optional)
7. 💰 Set up PayFast payments (optional)

---

**Need more details?** See [DASHBOARD_README.md](DASHBOARD_README.md) and [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
