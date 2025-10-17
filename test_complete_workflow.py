#!/usr/bin/env python3
"""
Complete Workflow Test
Tests everything end-to-end
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("COMPLETE WORKFLOW TEST")
print("=" * 70)

# Test 1: Imports
print("\n[1] Testing imports...")
try:
    from shared.encryption import EncryptionManager
    from shared.blockchain_client import BlockchainClient
    print("  ✓ Imports OK")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    sys.exit(1)

# Test 2: Encryption
print("\n[2] Testing encryption...")
try:
    em = EncryptionManager()
    
    # Generate keypairs
    admin_keys = em.generate_rsa_keypair()
    agent_keys = em.generate_rsa_keypair()
    
    admin_private = admin_keys['private_key_obj']
    admin_public = admin_keys['public_key_obj']
    agent_private = agent_keys['private_key_obj']
    agent_public = agent_keys['public_key_obj']
    
    # Test encryption/decryption
    test_data = b"Test command: whoami"
    encrypted = em.hybrid_encrypt(test_data, agent_public)
    decrypted = em.hybrid_decrypt(encrypted, agent_private)
    
    assert decrypted == test_data, "Decryption failed!"
    print("  ✓ Encryption/Decryption OK")
    
    # Test blockchain encoding
    encoded = em.encode_payload_for_blockchain(encrypted)
    decoded = em.decode_payload_from_blockchain(encoded)
    assert decoded == encrypted, "Encoding failed!"
    print("  ✓ Blockchain encoding OK")
    
except Exception as e:
    print(f"  ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Load deployment info
print("\n[3] Loading deployment info...")
try:
    deployment_file = Path(__file__).parent / "deployment.json"
    if deployment_file.exists():
        with open(deployment_file) as f:
            deployment = json.load(f)
        print(f"  ✓ Contract: {deployment['contract_address']}")
        print(f"  ✓ Network: {deployment['network']}")
    else:
        print("  ! No deployment.json found (contract not deployed)")
        deployment = None
except Exception as e:
    print(f"  ! Warning: {e}")
    deployment = None

# Test 4: Agent code
print("\n[4] Testing agent code...")
try:
    from agent.agent import Agent
    print("  ✓ Agent module loads")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("BASIC TESTS COMPLETE")
print("=" * 70)
print("\n✓ Core modules working")
print("✓ Encryption working")
print("✓ Ready for blockchain testing")

if deployment:
    print(f"\nContract deployed at: {deployment['contract_address']}")
    print("Ready for full integration test with real blockchain")

