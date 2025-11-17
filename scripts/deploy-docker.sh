#!/bin/bash
# Deployment script for 43v3rMore Trading Dashboard with Docker

set -e

echo "🚀 43v3rMore Trading Dashboard - Docker Deployment"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"
echo -e "${GREEN}✓ Docker Compose found: $COMPOSE_CMD${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env from template..."
    cp .env.template .env
    echo -e "${YELLOW}Please edit .env with your credentials before continuing${NC}"
    echo "Press Enter to continue after editing .env, or Ctrl+C to exit"
    read
fi

# Build services
echo "🔨 Building Docker images..."
$COMPOSE_CMD build

# Start services
echo ""
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."

# Check backend
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API is healthy${NC}"
else
    echo -e "${RED}❌ Backend API is not responding${NC}"
    echo "Check logs: $COMPOSE_CMD logs app"
fi

# Check frontend
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}❌ Frontend is not responding${NC}"
    echo "Check logs: $COMPOSE_CMD logs frontend"
fi

# Check database
if $COMPOSE_CMD exec -T postgres pg_isready -U quantum_user > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL may not be ready yet${NC}"
fi

# Check Redis
if $COMPOSE_CMD exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Redis may not be ready yet${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "📱 Access the dashboard:"
echo "   Frontend:       http://localhost:3000"
echo "   Admin Dashboard: http://localhost:3000/admin/overview"
echo "   Backend API:    http://localhost:8000/docs"
echo "   Health Check:   http://localhost:8000/health"
echo ""
echo "📊 View logs:"
echo "   All services:   $COMPOSE_CMD logs -f"
echo "   Frontend:       $COMPOSE_CMD logs -f frontend"
echo "   Backend:        $COMPOSE_CMD logs -f app"
echo ""
echo "🛑 Stop services:"
echo "   $COMPOSE_CMD down"
echo ""
echo "=================================================="
