# Docker Setup Guide

## Overview

This project uses Docker for containerized deployment. Due to platform limitations, there are two requirements files:

- `requirements.txt` - For local development (includes all dependencies)
- `requirements-docker.txt` - For Docker builds (excludes Windows-only packages)

## MetaTrader5 Limitation

**Important:** MetaTrader5 is a Windows-only package and cannot be installed in Linux-based Docker containers.

### Solution

The application handles this gracefully:
- When MetaTrader5 is not available, the system automatically uses mock data
- See `src/quantum_engine/mt5_connector.py` for the fallback implementation
- All functionality works in Docker, but with simulated market data

### For Production Trading

If you need real MetaTrader5 connectivity:
1. Run the application directly on Windows (not in Docker)
2. Use `requirements.txt` for installation
3. Or set up a Windows-based trading bridge service

## Building the Docker Image

```bash
docker-compose build
```

Or build manually:
```bash
docker build -t quantum-trading .
```

## Running with Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Quantum Trading API (port 8000)

## System Dependencies

The Dockerfile includes system dependencies required for:
- **Quantum computing packages** (qiskit): gcc, g++, gfortran, libopenblas-dev
- **Cryptography packages**: libssl-dev, libffi-dev
- **Build tools**: build-essential, cmake, git

## Environment Variables

Copy `.env.template` to `.env` and configure:
```bash
cp .env.template .env
# Edit .env with your settings
```

## Health Check

The container includes a health check endpoint:
```bash
curl http://localhost:8000/health
```

## Development vs Production

- **Development**: Use docker-compose with volume mounts for hot-reloading
- **Production**: Build optimized image with multi-stage build (already configured)

## Troubleshooting

### Pip Install Fails

If you see pip install errors:
1. Ensure you're using `requirements-docker.txt` in the Dockerfile
2. Check that all system dependencies are installed
3. Verify you're not trying to install Windows-only packages

### MetaTrader5 Errors

If you see MetaTrader5 warnings in logs:
- This is expected in Docker
- The system will use mock data automatically
- For real trading, deploy on Windows

### Build Cache Issues

Clear Docker build cache:
```bash
docker-compose build --no-cache
```
