@echo off
REM ============================================================
REM Sunona AI - View Agent Details Script (Windows)
REM Displays agent name, prompt, and user profiles
REM ============================================================

set CONFIG_FILE=agent_data\example_recruiter\config.json
set USERS_FILE=agent_data\example_recruiter\users.json

echo.
echo ========================================
echo   SUNONA AI - AGENT VIEWER (LOCAL)
echo ========================================
echo.

REM Check if files exist
if not exist "%CONFIG_FILE%" (
    echo ERROR: Config file not found: %CONFIG_FILE%
    exit /b 1
)

REM 1. Display Agent Name
echo --- [ AGENT NAME ] ---
powershell -Command "$json = Get-Content '%CONFIG_FILE%' | ConvertFrom-Json; $json.agent_config.agent_name"
echo.

REM 2. Display System Prompt
echo --- [ SYSTEM PROMPT ] ---
powershell -Command "$json = Get-Content '%CONFIG_FILE%' | ConvertFrom-Json; $json.agent_prompts.task_1.system_prompt"
echo.

REM 3. Display Recognized Users
echo --- [ RECOGNIZED USERS ] ---
if exist "%USERS_FILE%" (
    powershell -Command "Get-Content '%USERS_FILE%'"
) else (
    echo Users file not found.
)

echo.
echo ========================================
echo View complete!
echo ========================================
echo.
pause
