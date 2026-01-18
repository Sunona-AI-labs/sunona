@echo off
REM Sunona Voice AI - Windows Start Script
REM Production-ready local setup

echo ========================================
echo    SUNONA VOICE AI - LOCAL SETUP
echo ========================================
echo.

REM Check if .env exists
if not exist "..\.env" (
    echo [WARNING] .env file not found!
    echo Creating from .env.example...
    copy "..\.env.example" "..\.env"
    echo.
    echo [ACTION REQUIRED] Edit .env with your API keys!
    echo.
    pause
    notepad "..\.env"
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)

echo.
echo Select deployment mode:
echo   1. Basic (App + Redis only)
echo   2. Full (App + Redis + PostgreSQL)
echo   3. Development (All + Ngrok)
echo   4. Production (All + Monitoring)
echo.
set /p MODE="Enter choice (1-4): "

if "%MODE%"=="1" (
    echo.
    echo Starting Basic Setup...
    docker compose up -d sunona-app redis
)
if "%MODE%"=="2" (
    echo.
    echo Starting Full Setup...
    docker compose up -d sunona-app redis postgres
)
if "%MODE%"=="3" (
    echo.
    echo Starting Development Setup...
    docker compose --profile dev up -d
)
if "%MODE%"=="4" (
    echo.
    echo Starting Production Setup...
    docker compose --profile monitoring up -d
)

echo.
echo ========================================
echo    SERVICES STARTED
echo ========================================
echo.
echo Sunona API:    http://localhost:8000
echo Health Check:  http://localhost:8000/health
echo.
if "%MODE%"=="3" (
    echo Ngrok Console: http://localhost:4040
)
if "%MODE%"=="4" (
    echo Prometheus:    http://localhost:9090
    echo Grafana:       http://localhost:3000
)
echo.
echo To view logs:  docker compose logs -f
echo To stop:       docker compose down
echo.

pause
