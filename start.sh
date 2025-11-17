#!/bin/bash

# Quantum Trading AI - Quick Start Script
# This script helps you get started with the application quickly

set -e

echo "======================================"
echo "Quantum Trading AI - Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.template .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file with your actual credentials${NC}"
    echo ""
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
    echo ""
fi

# Check if frontend/.env exists
if [ ! -f frontend/.env ]; then
    echo -e "${YELLOW}Creating frontend/.env file...${NC}"
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✓ frontend/.env file created${NC}"
    echo ""
else
    echo -e "${GREEN}✓ frontend/.env file already exists${NC}"
    echo ""
fi

# Menu
echo "Choose setup mode:"
echo "1) Development (with hot reload)"
echo "2) Production (optimized builds)"
echo "3) Backend only"
echo "4) Frontend only"
echo "5) Clean all Docker containers and volumes"
echo "6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo -e "${GREEN}Starting in Development mode...${NC}"
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    2)
        echo -e "${GREEN}Starting in Production mode...${NC}"
        docker-compose up --build -d
        echo ""
        echo -e "${GREEN}Services started!${NC}"
        echo "Frontend: http://localhost:3000"
        echo "Backend API: http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
        ;;
    3)
        echo -e "${GREEN}Starting Backend only...${NC}"
        docker-compose up postgres redis app --build -d
        echo ""
        echo -e "${GREEN}Backend services started!${NC}"
        echo "Backend API: http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        ;;
    4)
        echo -e "${GREEN}Starting Frontend only...${NC}"
        cd frontend
        if [ ! -d "node_modules" ]; then
            echo "Installing dependencies..."
            npm install
        fi
        npm run dev
        ;;
    5)
        echo -e "${RED}Cleaning all Docker containers and volumes...${NC}"
        read -p "Are you sure? This will delete all data! (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            docker-compose down -v
            docker-compose -f docker-compose.dev.yml down -v
            echo -e "${GREEN}✓ Cleaned successfully${NC}"
        else
            echo "Cancelled"
        fi
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
