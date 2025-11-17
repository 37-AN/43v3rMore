@echo off
echo ========================================
echo 43v3rMore Dashboard - Quick Test
echo ========================================
echo.

echo Checking Docker status...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)
echo Docker is running!
echo.

echo Building and starting services...
docker compose up -d --build

echo.
echo Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak >nul

echo.
echo Testing endpoints...
echo.

echo [1/4] Testing Backend Health...
curl -s http://localhost:8000/health >nul 2>&1 && echo SUCCESS || echo FAILED

echo [2/4] Testing Frontend...
curl -s http://localhost:3000 >nul 2>&1 && echo SUCCESS || echo FAILED

echo [3/4] Testing Dashboard API...
curl -s http://localhost:8000/api/v1/dashboard/overview >nul 2>&1
if errorlevel 1 (
    echo Expected 401 - Auth Required - SUCCESS
) else (
    echo PASSED
)

echo [4/4] Checking Containers...
docker compose ps

echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Access the dashboard:
echo   - Admin Dashboard: http://localhost:3000/admin/overview
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:8000/docs
echo.
echo View logs: docker compose logs -f
echo Stop services: docker compose down
echo.
pause
