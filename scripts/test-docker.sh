#!/bin/bash
# Test script for Docker deployment

set -e

echo "🧪 Testing 43v3rMore Docker Deployment"
echo "======================================"
echo ""

# Check Docker Compose command
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose not found"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    echo -n "Testing $name... "

    if response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        if [ "$http_code" = "$expected_code" ]; then
            echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
            ((PASSED++))
        else
            echo -e "${RED}✗ FAILED${NC} (Expected $expected_code, got $http_code)"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Connection failed)"
        ((FAILED++))
    fi
}

# Check if services are running
echo "1. Checking if services are running..."
if ! $COMPOSE_CMD ps | grep -q "Up"; then
    echo -e "${RED}❌ Services are not running${NC}"
    echo "Start services with: $COMPOSE_CMD up -d"
    exit 1
fi
echo -e "${GREEN}✓ Services are running${NC}"
echo ""

# Test Backend API
echo "2. Testing Backend API endpoints..."
test_endpoint "Health Check" "http://localhost:8000/health"
test_endpoint "Root Endpoint" "http://localhost:8000/"
test_endpoint "API Docs" "http://localhost:8000/docs"
echo ""

# Test Frontend
echo "3. Testing Frontend..."
test_endpoint "Frontend Root" "http://localhost:3000/"
test_endpoint "Admin Dashboard" "http://localhost:3000/admin"
echo ""

# Test Dashboard API endpoints (require authentication, so 401 is expected)
echo "4. Testing Dashboard API endpoints..."
test_endpoint "Dashboard Overview (requires auth)" "http://localhost:8000/api/v1/dashboard/overview" "401"
test_endpoint "Signal Performance (requires auth)" "http://localhost:8000/api/v1/dashboard/signals/performance" "401"
echo ""

# Test Database
echo "5. Testing Database connection..."
if $COMPOSE_CMD exec -T postgres pg_isready -U quantum_user > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is accessible${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ PostgreSQL connection failed${NC}"
    ((FAILED++))
fi
echo ""

# Test Redis
echo "6. Testing Redis connection..."
if $COMPOSE_CMD exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is accessible${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Redis connection failed${NC}"
    ((FAILED++))
fi
echo ""

# Check container health
echo "7. Checking container health..."
for service in app frontend postgres redis; do
    echo -n "  $service: "
    health=$($COMPOSE_CMD ps $service --format json 2>/dev/null | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
    state=$($COMPOSE_CMD ps $service --format json 2>/dev/null | grep -o '"State":"[^"]*"' | cut -d'"' -f4 || echo "unknown")

    if [ "$state" = "running" ]; then
        if [ "$health" = "healthy" ] || [ "$health" = "unknown" ]; then
            echo -e "${GREEN}✓ $state ($health)${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ $state ($health)${NC}"
        fi
    else
        echo -e "${RED}✗ $state${NC}"
        ((FAILED++))
    fi
done
echo ""

# Summary
echo "======================================"
echo "Test Results:"
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - View logs: $COMPOSE_CMD logs -f"
    echo "  - Check specific service: $COMPOSE_CMD logs <service_name>"
    echo "  - Restart services: $COMPOSE_CMD restart"
    exit 1
fi
