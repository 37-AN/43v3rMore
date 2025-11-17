# 43v3rMore Trading Dashboard

Comprehensive admin dashboard for monitoring and managing the 43v3rMore Quantum Trading System.

## Overview

The dashboard provides real-time visibility and control over all system components, including:

- **System Overview** - Service health monitoring and key metrics
- **Quantum Signal Monitoring** - Real-time quantum circuit status and signal generation
- **MT5 Trading Monitor** - Live trading activity and account management
- **User Management** - Subscriber management and activity tracking
- **Financial Dashboard** - Revenue metrics and financial analytics
- **Configuration** - System-wide configuration management
- **Alerts & Performance** - System alerts and performance monitoring

## Architecture

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **UI Library**: Shadcn/ui + Tailwind CSS
- **State Management**: Zustand
- **Charts**: Recharts
- **Real-time**: Socket.IO client
- **API Client**: Axios

### Backend
- **Framework**: FastAPI
- **WebSocket**: Socket.IO for real-time updates
- **Database**: PostgreSQL (Supabase)
- **Cache**: Redis

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
```

### 3. Start Development Server

```bash
# Frontend
cd frontend
npm run dev

# Backend (in separate terminal)
cd ..
uvicorn src.api.main:app --reload
```

### 4. Access Dashboard

Open your browser to:
- Frontend: http://localhost:3000
- Admin Dashboard: http://localhost:3000/admin/overview

## Dashboard Modules

### System Overview (`/admin/overview`)

Real-time monitoring of all system components:
- Active users count
- Signals generated today
- Current signal accuracy
- Monthly recurring revenue (MRR)
- System uptime
- Service health grid
- Real-time activity feed

### Quantum Signal Monitoring (`/admin/quantum-signals`)

Monitor quantum signal generation:
- Signal accuracy trends
- Active quantum circuits
- Signal confidence metrics
- Signals by trading pair
- Quantum backend status
- Circuit execution metrics

### MT5 Trading Monitor (`/admin/mt5-monitor`)

MetaTrader 5 integration monitoring:
- MT5 connection status
- Account balance and equity
- Open positions table
- Trading history
- Win rate and P/L statistics
- Market data feed

### User Management (`/admin/users`)

Manage subscribers and accounts:
- User table with filters
- Subscription status tracking
- Plan management
- User activity metrics
- MRR contribution per user
- User search and filtering

### Financial Dashboard (`/admin/financial`)

Revenue and financial analytics:
- MRR and ARR metrics
- Revenue trends
- Revenue by plan breakdown
- Payment processing table
- Unit economics (LTV, CAC)
- Revenue projections

### Configuration (`/admin/configuration`)

System-wide settings:
- Quantum engine configuration
- MT5 connector settings
- Notification services
- PayFast integration
- Feature flags

### Alerts & Performance (`/admin/alerts`)

System monitoring and alerts:
- Active alerts dashboard
- Alert severity levels
- Performance metrics (CPU, memory, disk)
- API endpoint monitoring
- Database performance
- Cache hit rates

## API Endpoints

All dashboard endpoints are prefixed with `/api/v1/dashboard`:

- `GET /overview` - System overview metrics
- `GET /signals/performance` - Quantum signal performance
- `GET /mt5/status` - MT5 connection status
- `GET /users` - User management
- `GET /revenue` - Financial metrics
- `GET /config` - System configuration
- `PUT /config` - Update configuration
- `GET /alerts` - System alerts
- `POST /alerts/{id}/acknowledge` - Acknowledge alert
- `POST /alerts/{id}/resolve` - Resolve alert
- `GET /performance` - Performance metrics

## WebSocket Events

Real-time updates via WebSocket:

- `signal_generated` - New quantum signal
- `trade_executed` - Trade executed via MT5
- `user_registered` - New user signup
- `payment_received` - Payment processed
- `alert_triggered` - System alert
- `metric_update` - Metric value updated

## Authentication

Dashboard routes require admin-level authentication. Use the `require_plan("admin")` decorator:

```python
@router.get("/admin-only")
async def admin_endpoint(user: User = Depends(require_plan("admin"))):
    # Only accessible to admin users
    pass
```

## Development

### Adding New Dashboard Module

1. Create component in `frontend/src/pages/admin/`
2. Add route to `frontend/src/App.tsx`
3. Create API endpoint in `src/api/dashboard_routes.py`
4. Update `DASHBOARD_README.md` with new module

### Styling Guidelines

- Use Tailwind utility classes
- Follow dark mode support pattern
- Use Shadcn/ui components
- Maintain responsive design (mobile, tablet, desktop)

### Testing

```bash
# Frontend tests
cd frontend
npm run test

# Backend tests
cd ..
pytest tests/
```

## Deployment

### Docker

Dashboard is included in the main docker-compose configuration:

```bash
docker-compose up -d
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Dashboard: http://localhost:3000/admin

### Production Build

```bash
cd frontend
npm run build
```

Build artifacts will be in `frontend/dist/`

## Configuration

### Frontend Configuration

Edit `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

### Backend Configuration

Edit `.env` file:

```env
# Dashboard
DASHBOARD_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/quantum_trading

# Redis
REDIS_URL=redis://localhost:6379
```

## Security

- All dashboard routes require authentication
- Admin-only routes use `require_plan("admin")` guard
- CORS configured for allowed origins
- Rate limiting enabled (100 req/min per user)
- Input validation on all endpoints
- XSS protection via output sanitization

## Performance

- WebSocket for real-time updates (minimal polling)
- React Query for efficient data fetching
- Optimistic UI updates
- Lazy loading of dashboard modules
- Recharts for efficient chart rendering
- Redis caching for frequently accessed data

## Troubleshooting

### Frontend not connecting to backend

- Check `VITE_API_URL` in `.env`
- Verify CORS settings in backend
- Check browser console for errors

### WebSocket not working

- Ensure `VITE_WS_URL` is correct
- Check firewall allows WebSocket connections
- Verify Socket.IO version compatibility

### Dashboard showing old data

- Clear Redis cache
- Check WebSocket connection status
- Refresh browser and clear cache

## Support

For issues or questions:
- GitHub Issues: https://github.com/37-AN/43v3rMore/issues
- Documentation: `/docs` (when in debug mode)

## License

Proprietary - All rights reserved
