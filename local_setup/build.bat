@echo off
REM Sunona Voice AI - Quick Build Script (Windows)
REM Uses BuildKit for faster Docker builds

echo ========================================
echo    SUNONA VOICE AI - QUICK BUILD
echo ========================================
echo.

REM Enable BuildKit
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    pause
    exit /b 1
)

echo BuildKit enabled for faster builds!
echo.

echo Select build option:
echo   1. Build main app only
echo   2. Build all services
echo   3. Build with no cache (fresh)
echo   4. Build and start
echo.
set /p OPTION="Enter choice (1-4): "

cd ..

if "%OPTION%"=="1" (
    echo.
    echo Building sunona-app...
    docker build -f local_setup/Dockerfile -t sunona-app:latest .
)
if "%OPTION%"=="2" (
    echo.
    echo Building all services...
    docker compose -f local_setup/docker-compose.yml build
)
if "%OPTION%"=="3" (
    echo.
    echo Building fresh (no cache)...
    docker compose -f local_setup/docker-compose.yml build --no-cache
)
if "%OPTION%"=="4" (
    echo.
    echo Building and starting...
    docker compose -f local_setup/docker-compose.yml up -d --build
)

echo.
echo ========================================
echo    BUILD COMPLETE
echo ========================================
echo.
echo To verify: docker images ^| findstr sunona
echo.

pause
