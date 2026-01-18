@echo off
REM Sunona Voice AI - Build twilio-server only
REM Uses BuildKit for faster builds

echo ========================================
echo    BUILDING: twilio-server
echo ========================================

set DOCKER_BUILDKIT=1
cd ..
docker build -f local_setup/Dockerfile.twilio -t sunona-twilio:latest .

echo.
echo Build complete! Run with: docker compose up -d twilio-server
pause
