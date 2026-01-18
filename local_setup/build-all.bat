@echo off
REM Sunona Voice AI - Build ALL services in parallel
REM Fastest way to build everything with BuildKit

echo ========================================
echo    BUILDING ALL SERVICES (PARALLEL)
echo ========================================
echo.

REM Enable BuildKit
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1

cd ..

echo Step 1: Pulling pre-built images...
docker pull redis:7-alpine
docker pull postgres:15-alpine

echo.
echo Step 2: Building custom images in parallel...
docker compose -f local_setup/docker-compose.yml build --parallel

echo.
echo ========================================
echo    BUILD COMPLETE
echo ========================================
echo.
echo To start: docker compose -f local_setup/docker-compose.yml up -d
echo.
pause
