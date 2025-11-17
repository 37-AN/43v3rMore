# Docker Test Guide

Quick test to verify everything works.

## Test 1: Frontend Build
```bash
cd frontend
npm run build
```

Expected: Build completes successfully

## Test 2: Start Services (Development)
```bash
docker-compose -f docker-compose.dev.yml up -d
```

Wait 30 seconds, then:
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

## Test 3: Check All Services
```bash
docker-compose ps
```

All services should be "Up" and "healthy"

## Test 4: View Logs
```bash
docker-compose logs app
docker-compose logs frontend
```

No errors should be present

## Clean Up
```bash
docker-compose down
```
