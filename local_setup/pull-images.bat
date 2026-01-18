@echo off
REM Sunona Voice AI - Pull all pre-built images
REM No build needed - just pulls latest images

echo ========================================
echo    PULLING PRE-BUILT IMAGES
echo ========================================

echo.
echo Pulling Redis...
docker pull redis:7-alpine

echo.
echo Pulling PostgreSQL...
docker pull postgres:15-alpine

echo.
echo Pulling ChromaDB...
docker pull chromadb/chroma:latest

echo.
echo Pulling Ngrok...
docker pull ngrok/ngrok:latest

echo.
echo Pulling Prometheus...
docker pull prom/prometheus:latest

echo.
echo Pulling Grafana...
docker pull grafana/grafana:latest

echo.
echo ========================================
echo    ALL IMAGES PULLED
echo ========================================
echo.
pause
