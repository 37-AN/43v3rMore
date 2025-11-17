# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Quantum Trading AI** - Autonomous AI trading system for the South African market using quantum computing and advanced machine learning. The goal is to achieve R100K MRR in 6 months with zero startup capital.

### Tech Stack
- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Quantum Computing**: Qiskit, NumPy
- **Trading**: MetaTrader 5 (Windows only)
- **Database**: Supabase (PostgreSQL), Redis
- **Communication**: Telegram, WhatsApp (Twilio), Email (SendGrid), SMS
- **Payments**: PayFast (South African payment gateway)
- **AI**: Anthropic Claude with MCP servers
- **DevOps**: Docker, Docker Compose

## Important Platform Limitations

### MetaTrader5 Windows-Only Limitation
**Critical**: MetaTrader5 is a Windows-only package and cannot be installed in Linux Docker containers.

**Workaround**: The application automatically falls back to mock data when MT5 is unavailable (see `src/quantum_engine/mt5_connector.py`). This allows Docker deployment but with simulated market data.

**For Production Trading**:
- Run directly on Windows (not in Docker)
- Use `requirements.txt` (includes MT5)
- Or implement a Windows-based trading bridge service

### Docker Requirements Files
- `requirements.txt` - Local development (includes all dependencies including MT5)
- `requirements-docker.txt` - Docker builds (excludes Windows-only packages)

Always use `requirements-docker.txt` in Dockerfiles.

## Development Setup

### Local Development (Windows with MT5)
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your credentials

# Run application
uvicorn src.api.main:app --reload
```

### Docker Development (No MT5)
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Rebuild after dependency changes
docker-compose build --no-cache

# Stop services
docker-compose down
```

## Common Commands

### Running the Application
```bash
# Development server with hot reload
uvicorn src.api.main:app --reload

# Production server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-compose up -d
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_quantum_engine.py -v

# Run specific test
pytest tests/test_api.py::test_health_check -v
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

### Docker Operations
```bash
# Start services
docker-compose up -d

# View service status
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f app

# Restart service
docker-compose restart app

# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

## Architecture

### Directory Structure
```
src/
├── quantum_engine/     # Quantum Phase Estimation trading engine
├── api/                # FastAPI REST API & WebSocket
├── database/           # Supabase integration & models
├── communication/      # Multi-channel delivery (Telegram, WhatsApp, Email, SMS)
├── payments/           # PayFast billing integration
├── mcp_servers/        # Claude AI automation servers
├── beta_program/       # Beta testing management
└── utils/              # Shared utilities & configuration
```

### Key Components

**Quantum Trading Engine** (`src/quantum_engine/`)
- Uses Qiskit's Quantum Phase Estimation (QPE) algorithm
- Targets 95%+ signal accuracy
- Real-time and historical market analysis
- Graceful fallback to mock data when MT5 unavailable

**API Gateway** (`src/api/`)
- FastAPI with async support
- JWT authentication
- Rate limiting (60/min, 1000/hour per user)
- WebSocket support for real-time signals
- Swagger docs at `/docs` (development only)

**Database Layer** (`src/database/`)
- Supabase (PostgreSQL) for persistent data
- Redis for caching and sessions
- Tables: users, subscriptions, signals, signal_deliveries, payments, analytics_events

**Communication Layer** (`src/communication/`)
- Telegram: Bot API for instant messaging
- WhatsApp: Twilio Business API
- Email: SendGrid with HTML templates
- SMS: Twilio messaging
- Parallel multi-channel delivery with retry logic

**MCP Servers** (`src/mcp_servers/`)
- Claude AI automation for business operations
- Lead qualification, customer support, content generation
- Marketing automation and analytics

### Data Flow: Signal Generation to Delivery
```
1. MT5/Mock Market Data → Quantum Engine
2. QPE Analysis → Signal Generation
3. Quality Validation (confidence > 75%)
4. Database Storage
5. User Filtering (by plan/preferences)
6. Multi-Channel Delivery (Telegram, WhatsApp, Email, SMS)
7. Delivery Confirmation & Tracking
8. Performance Analytics
```

## Configuration

### Environment Variables
Copy `.env.template` to `.env` and configure:

**Required for Basic Operation**:
- `SECRET_KEY` - Change in production
- `DATABASE_URL` or Supabase credentials
- `REDIS_HOST`, `REDIS_PORT`

**Required for Trading**:
- `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` (Windows only)
- `IBM_QUANTUM_TOKEN` (optional, for real quantum hardware)

**Required for Communication**:
- `TELEGRAM_BOT_TOKEN` (Telegram)
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` (WhatsApp/SMS)
- `SENDGRID_API_KEY` (Email)

**Required for Payments**:
- `PAYFAST_MERCHANT_ID`, `PAYFAST_MERCHANT_KEY`, `PAYFAST_PASSPHRASE`
- Set `PAYFAST_SANDBOX=True` for testing

### Settings Management
Application settings are managed via Pydantic Settings (`src/utils/config.py`). Settings are loaded from environment variables with validation.

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /` - API information
- `GET /docs` - Swagger UI (development only)

### Trading Signals
- `GET /api/v1/signals` - List recent signals
- `GET /api/v1/signals/{signal_id}` - Get specific signal
- `POST /api/v1/analyze` - On-demand quantum analysis (Pro+ plans)

### User Management
- `POST /api/v1/users` - Create user account
- `GET /api/v1/users/me` - Current user info

### Subscriptions
- `POST /api/v1/subscriptions` - Create subscription
- `GET /api/v1/subscriptions/me` - Current subscription

### WebSocket
- `WS /ws` - Real-time signal delivery

See [docs/API.md](docs/API.md) for complete API documentation.

## Subscription Tiers
- **Basic** (R500/month): 5 signals/day, major pairs
- **Pro** (R1000/month): 10 signals/day, all pairs
- **Premium** (R2000/month): Unlimited signals, priority support
- **Bot License** (R3000/month): Automated trading bot
- **Enterprise** (R10K/month): Custom solutions, API access

## Testing Strategy

### Test Files
- `tests/test_quantum_engine.py` - Quantum engine tests
- `tests/test_api.py` - API endpoint tests

### Running Specific Tests
```bash
# Single test file
pytest tests/test_api.py -v

# Single test function
pytest tests/test_api.py::test_health_check -v

# With coverage report
pytest --cov=src --cov-report=html tests/
```

### Test Coverage Target
Maintain 80%+ test coverage for all new code.

## Docker Services

The `docker-compose.yml` defines four services:

1. **postgres** - PostgreSQL 15 database (port 5432)
2. **redis** - Redis 7 cache (port 6379)
3. **app** - Main FastAPI application (port 8000)
4. **frontend** - Nginx frontend (port 3000)

All services include health checks and dependency management.

## Deployment

### Production Checklist
1. Set `APP_ENV=production` and `DEBUG=False` in `.env`
2. Generate secure `SECRET_KEY`
3. Configure production database credentials
4. Set `PAYFAST_SANDBOX=False` for live payments
5. Configure production CORS origins
6. Set up monitoring (Sentry DSN if using)

### Production Build
```bash
# Build optimized Docker image
docker build -t quantum-trading:latest .

# Or use docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

- JWT tokens expire after 30 minutes (configurable)
- Passwords hashed with bcrypt
- Rate limiting on all endpoints (60/min, 1000/hour)
- CORS configured per environment
- API keys and secrets via environment variables only
- SSL/TLS required in production

## Performance Targets

- API response time: <200ms (p95)
- Signal generation: <5s per symbol
- Database queries: <100ms (p95)
- Uptime: 99.9%

## Monitoring & Observability

- **Logging**: Loguru with structured logging
- **Metrics**: Prometheus client (port 9090)
- **Errors**: Sentry SDK (optional, configure `SENTRY_DSN`)
- **Health Checks**: Built into Docker containers

### Request Logging
All HTTP requests are automatically logged with:
- Method, path, status code
- Response time
- Structured metadata

## Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
pytest tests/

# Format and lint
black src/ tests/
flake8 src/ tests/

# Commit
git add .
git commit -m "feat: your feature description"

# Push
git push origin feature/your-feature
```

### Commit Message Convention
Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test updates
- `chore:` - Build/tooling changes

## Code Standards

- Follow PEP 8
- Use type hints for all functions
- Write docstrings (Google style)
- Keep functions focused and small
- Use Black formatter (line length 88)
- Handle errors gracefully with proper logging

## Known Issues & Workarounds

### MetaTrader5 in Docker
As mentioned above, MT5 cannot run in Linux containers. The application detects this and uses mock data automatically. For real trading, deploy on Windows.

### System Dependencies for Qiskit
Qiskit requires several system dependencies (gcc, g++, gfortran, libopenblas-dev) which are included in the Dockerfile. If building locally on a minimal system, install these first.

## Additional Documentation

- [README.md](README.md) - Project overview and quick start
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed architecture
- [docs/API.md](docs/API.md) - Complete API reference
- [DOCKER.md](DOCKER.md) - Docker setup and limitations
- [CHANGELOG.md](CHANGELOG.md) - Version history
