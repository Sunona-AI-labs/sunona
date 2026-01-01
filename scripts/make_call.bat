@echo off
REM ============================================================
REM Sunona AI - Make Call Script
REM Makes a phone call using an agent
REM ============================================================

echo.
echo ========================================
echo   SUNONA AI - MAKE CALL
echo ========================================
echo.

set SERVER_URL=http://localhost:8000
set API_KEY=49149399e6b7addee08fc659c9b35944191521b2124b82c7d059beec66690f5e

REM Get parameters
if "%1"=="" (
    set /p PHONE_NUMBER="Enter phone number with country code (e.g., +917075xxxxxx): "
) else (
    set PHONE_NUMBER=%1
)

if "%2"=="" (
    set /p AGENT_ID="Enter agent_id (from create_agent): "
) else (
    set AGENT_ID=%2
)

echo.
echo Making call to: %PHONE_NUMBER%
echo Using agent: %AGENT_ID%
echo.

REM Encode phone number for URL (handles + sign)
for /f "delims=" %%i in ('powershell -Command "[uri]::EscapeDataString('%PHONE_NUMBER%')"') do set ENCODED_PHONE=%%i

REM Make the call
curl.exe -X POST "%SERVER_URL%/make-call?to=%ENCODED_PHONE%&agent_id=%AGENT_ID%" ^
  -H "X-API-Key: %API_KEY%"
echo.
echo.
echo ========================================
echo Call initiated! Check the server logs.
echo ========================================
echo.
pause
