#!/bin/bash
# Production Deployment Script for Quantum Trading AI
# Usage: ./scripts/deploy.sh [environment]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
PROJECT_DIR="/opt/quantum-trading-ai"
BACKUP_DIR="/opt/quantum-trading-ai-backups"
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Quantum Trading AI - Deployment Script${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

# Function: Create backup
create_backup() {
    echo -e "${YELLOW}Creating backup...${NC}"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="${BACKUP_DIR}/backup_${TIMESTAMP}"

    mkdir -p "${BACKUP_PATH}"

    # Backup database
    docker exec quantum-trading-postgres pg_dump -U quantum_admin quantum_trading > "${BACKUP_PATH}/database.sql"

    # Backup data directory
    cp -r "${PROJECT_DIR}/data" "${BACKUP_PATH}/"

    # Backup configuration
    cp "${PROJECT_DIR}/.env.production" "${BACKUP_PATH}/"

    echo -e "${GREEN}Backup created: ${BACKUP_PATH}${NC}"
}

# Function: Pull latest code
pull_code() {
    echo -e "${YELLOW}Pulling latest code from Git...${NC}"
    cd "${PROJECT_DIR}"
    git fetch --all
    git pull origin main
    echo -e "${GREEN}Code updated${NC}"
}

# Function: Build images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    cd "${PROJECT_DIR}"
    docker-compose -f "${COMPOSE_FILE}" build --no-cache
    echo -e "${GREEN}Images built${NC}"
}

# Function: Stop services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    cd "${PROJECT_DIR}"
    docker-compose -f "${COMPOSE_FILE}" down
    echo -e "${GREEN}Services stopped${NC}"
}

# Function: Start services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"
    cd "${PROJECT_DIR}"
    docker-compose -f "${COMPOSE_FILE}" up -d
    echo -e "${GREEN}Services started${NC}"
}

# Function: Run migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    docker exec quantum-trading-api python -m src.database.migrations
    echo -e "${GREEN}Migrations complete${NC}"
}

# Function: Health check
health_check() {
    echo -e "${YELLOW}Running health check...${NC}"
    sleep 10  # Wait for services to start

    # Check API health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is healthy${NC}"
    else
        echo -e "${RED}✗ API health check failed${NC}"
        exit 1
    fi

    # Check Redis
    if docker exec quantum-trading-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is healthy${NC}"
    else
        echo -e "${RED}✗ Redis health check failed${NC}"
        exit 1
    fi

    # Check PostgreSQL
    if docker exec quantum-trading-postgres pg_isready -U quantum_admin > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
    else
        echo -e "${RED}✗ PostgreSQL health check failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}All health checks passed!${NC}"
}

# Function: Cleanup
cleanup() {
    echo -e "${YELLOW}Cleaning up old images and containers...${NC}"
    docker image prune -f
    docker container prune -f
    docker volume prune -f
    echo -e "${GREEN}Cleanup complete${NC}"
}

# Main deployment flow
main() {
    echo -e "${YELLOW}Starting deployment...${NC}"

    # Create backup before deployment
    create_backup

    # Pull latest code
    pull_code

    # Stop services
    stop_services

    # Build new images
    build_images

    # Start services
    start_services

    # Run migrations
    run_migrations

    # Health check
    health_check

    # Cleanup
    cleanup

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Website: https://quantumtrading.ai"
    echo -e "API: https://quantumtrading.ai/api/v1"
    echo -e "Monitoring: http://$(hostname -I | awk '{print $1}'):3000"
    echo ""
    echo -e "${YELLOW}Check logs with:${NC}"
    echo -e "  docker-compose -f ${COMPOSE_FILE} logs -f"
}

# Handle errors
trap 'echo -e "${RED}Deployment failed! Check logs above.${NC}"; exit 1' ERR

# Run main deployment
main "$@"
