# Docker Setup Guide

Complete guide for running Quantum Trading AI with Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

## Quick Start

### Using the Start Script (Recommended)

```bash
chmod +x start.sh
./start.sh
```

### Manual Start

#### Development Mode
```bash
docker-compose -f docker-compose.dev.yml up
```

#### Production Mode
```bash
docker-compose up -d
```

## Services

- **Backend**: Port 8000 (FastAPI)
- **Frontend**: Port 3000 (React + nginx)
- **PostgreSQL**: Port 5432
- **Redis**: Port 6379

## Environment Setup

```bash
# Backend
cp .env.template .env

# Frontend
cp frontend/.env.example frontend/.env
```

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild
docker-compose build
```

See full documentation at: https://docs.docker.com
