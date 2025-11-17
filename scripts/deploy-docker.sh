#!/bin/bash

# 43v3rMore - Docker Deployment Script
# Deploys the complete quantum trading platform with dashboard

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Check if Docker is installed and running
check_docker() {
    print_header "Checking Docker Prerequisites"

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install docker-compose."
        exit 1
    fi

    print_success "Docker is installed and running"
}

# Fix Node version in Dockerfile if needed
fix_node_version() {
    print_header "Checking Frontend Dockerfile"

    if grep -q "FROM node:18-alpine" frontend/Dockerfile; then
        print_warning "Node 18 detected in Dockerfile. Upgrading to Node 20..."
        sed -i 's/FROM node:18-alpine/FROM node:20-alpine/g' frontend/Dockerfile
        print_success "Updated to Node 20"
    else
        print_info "Node version is correct"
    fi
}

# Create necessary directories
create_directories() {
    print_header "Creating Necessary Directories"

    mkdir -p data/db
    mkdir -p data/logs

    print_success "Directories created"
}

# Check and create .env files
check_env_files() {
    print_header "Checking Environment Configuration"

    # Backend .env
    if [ ! -f .env ]; then
        if [ -f .env.template ]; then
            print_info "Creating backend .env from template..."
            cp .env.template .env
            print_success "Backend .env created"
        else
            print_error "No .env.template found for backend"
            exit 1
        fi
    else
        print_info "Backend .env exists"
    fi

    # Frontend .env
    if [ ! -f frontend/.env ]; then
        if [ -f frontend/.env.example ]; then
            print_info "Creating frontend .env from example..."
            cp frontend/.env.example frontend/.env
            print_success "Frontend .env created"
        else
            print_error "No .env.example found for frontend"
            exit 1
        fi
    else
        print_info "Frontend .env exists"
    fi
}

# Stop existing containers
stop_containers() {
    print_header "Stopping Existing Containers"

    if [ "$(docker ps -q)" ]; then
        docker-compose down
        print_success "Containers stopped"
    else
        print_info "No running containers"
    fi
}

# Build all services
build_services() {
    print_header "Building Docker Services"

    print_info "Building frontend..."
    docker-compose build frontend

    print_info "Building backend..."
    docker-compose build app

    print_success "All services built successfully"
}

# Start services
start_services() {
    print_header "Starting Services"

    docker-compose up -d

    print_success "Services started"
}

# Wait for services to be healthy
wait_for_health() {
    print_header "Waiting for Services to be Healthy"

    print_info "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until docker exec quantum-postgres pg_isready -U quantum_user > /dev/null 2>&1; do sleep 2; done'
    print_success "PostgreSQL is healthy"

    print_info "Waiting for Redis..."
    timeout 60 bash -c 'until docker exec quantum-redis redis-cli ping > /dev/null 2>&1; do sleep 2; done'
    print_success "Redis is healthy"

    print_info "Waiting for Backend API..."
    timeout 60 bash -c 'until curl -s http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'
    print_success "Backend API is healthy"

    print_info "Waiting for Frontend..."
    timeout 60 bash -c 'until curl -s http://localhost:3000 > /dev/null 2>&1; do sleep 2; done'
    print_success "Frontend is healthy"
}

# Display service status
show_status() {
    print_header "Deployment Status"

    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=quantum-"

    echo ""
    print_success "🚀 Deployment Complete!"
    echo ""
    echo -e "${GREEN}Access your services:${NC}"
    echo -e "  📊 Dashboard:  ${BLUE}http://localhost:3000${NC}"
    echo -e "  🔧 Backend API: ${BLUE}http://localhost:8000${NC}"
    echo -e "  📚 API Docs:    ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}Database connections:${NC}"
    echo -e "  PostgreSQL: localhost:5432"
    echo -e "  Redis:      localhost:6379"
    echo ""
}

# Main deployment flow
main() {
    print_header "43v3rMore - Docker Deployment"

    check_docker
    fix_node_version
    create_directories
    check_env_files
    stop_containers
    build_services
    start_services
    wait_for_health
    show_status

    print_success "Deployment completed successfully! 🎉"
}

# Run main function
main
