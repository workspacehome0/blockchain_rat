@echo off
echo ============================================
echo Blockchain RAT - Windows Installation
echo ============================================
echo.

echo [Step 1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

echo [Step 2/3] Installing Python dependencies...
echo This may take a few minutes...
echo.
pip install web3 cryptography pycryptodome PyQt5 pillow requests
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running as Administrator
    pause
    exit /b 1
)
echo.
echo ✓ Python dependencies installed successfully!
echo.

echo [Step 3/3] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js not found
    echo Node.js is only needed for smart contract deployment
    echo If you already deployed the contract, you can skip this
    echo.
) else (
    node --version
    echo ✓ Node.js found
)
echo.

echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Configure administrator/admin_config.json
echo 2. Configure agent/agent_config.json
echo 3. Run: python administrator/admin_gui.py
echo.
echo See WINDOWS_SETUP.md for detailed instructions
echo.
pause

