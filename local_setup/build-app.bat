@echo off
REM Sunona Voice AI - Build sunona-app only
REM Uses BuildKit for faster builds

echo ========================================
echo    BUILDING: sunona-app
echo ========================================

set DOCKER_BUILDKIT=1
cd ..
docker build -f local_setup/Dockerfile -t sunona-app:latest .

echo.
echo Build complete! Run with: docker compose up -d sunona-app
pause
