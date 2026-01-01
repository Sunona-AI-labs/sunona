@echo off
REM ============================================================
REM Sunona AI - Test API Health
REM Quick health check for all endpoints
REM ============================================================

echo.
echo ========================================
echo   SUNONA AI - API HEALTH CHECK
echo ========================================
echo.

set SERVER_URL=http://localhost:8000
set API_KEY=49149399e6b7addee08fc659c9b35944191521b2124b82c7d059beec66690f5e

echo Testing: %SERVER_URL%
echo.

echo [1/4] Root endpoint...
curl.exe -s %SERVER_URL%/
echo.
echo.

echo [2/4] Health check...
curl.exe -s %SERVER_URL%/health
echo.
echo.

echo [3/4] Liveness probe...
curl.exe -s %SERVER_URL%/health/liveness
echo.
echo.

echo [4/4] List agents...
curl.exe -s -H "X-API-Key: %API_KEY%" %SERVER_URL%/agents
echo.
echo.

echo ========================================
echo Health check complete!
echo ========================================
echo.
pause
