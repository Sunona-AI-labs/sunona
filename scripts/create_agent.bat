@echo off
REM ============================================================
REM Sunona AI - Create Agent Script
REM Creates an agent and displays the agent_id
REM ============================================================

echo.
echo ========================================
echo   SUNONA AI - CREATE AGENT
echo ========================================
echo.

set SERVER_URL=http://localhost:8000
set CONFIG_FILE=agent_data\example_recruiter\config.json
set API_KEY=49149399e6b7addee08fc659c9b35944191521b2124b82c7d059beec66690f5e

echo Creating agent from: %CONFIG_FILE%
echo Server: %SERVER_URL%
echo.

REM Check if config file exists
if not exist "%CONFIG_FILE%" (
    echo ERROR: Config file not found: %CONFIG_FILE%
    echo Please run this from the sunona project root directory.
    pause
    exit /b 1
)

REM Create agent using curl
echo Sending request...
echo.

curl.exe -X POST "%SERVER_URL%/agent" ^
  -H "Content-Type: application/json" ^
  -H "X-API-Key: %API_KEY%" ^
  -d @%CONFIG_FILE%

echo.
echo.
echo ========================================
echo Copy the agent_id from above to use in make_call.bat
echo ========================================
echo.
pause
