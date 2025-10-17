#!/usr/bin/env python3
"""
Blockchain State Checker
Verifies contract deployment, agents, and sessions
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web3 import Web3


def check_blockchain_state(rpc_url, contract_address):
    """Check the state of the blockchain contract"""
    
    print("=" * 70)
    print("BLOCKCHAIN STATE CHECKER")
    print("=" * 70)
    print()
    
    # Connect to blockchain
    print(f"[1] Connecting to blockchain...")
    print(f"    RPC: {rpc_url}")
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print("    ❌ FAILED: Cannot connect to blockchain")
        return False
    
    print(f"    ✓ Connected")
    print(f"    Block number: {w3.eth.block_number}")
    print()
    
    # Check contract
    print(f"[2] Checking contract...")
    print(f"    Address: {contract_address}")
    
    contract_address = Web3.to_checksum_address(contract_address)
    code = w3.eth.get_code(contract_address)
    
    if code == b'' or code == '0x':
        print("    ❌ FAILED: No contract at this address")
        return False
    
    print(f"    ✓ Contract exists")
    print(f"    Code size: {len(code)} bytes")
    print()
    
    # Load ABI
    print(f"[3] Loading contract ABI...")
    abi_path = Path(__file__).parent.parent / "shared" / "SessionManager.abi.json"
    
    if not abi_path.exists():
        print(f"    ❌ FAILED: ABI file not found at {abi_path}")
        return False
    
    with open(abi_path) as f:
        abi = json.load(f)
    
    contract = w3.eth.contract(address=contract_address, abi=abi)
    print(f"    ✓ ABI loaded ({len(abi)} functions)")
    print()
    
    # Check admin address
    print(f"[4] Enter admin wallet address to check sessions:")
    admin_address = input("    Admin address: ").strip()
    
    if not admin_address:
        print("    Skipping session check")
        return True
    
    try:
        admin_address = Web3.to_checksum_address(admin_address)
    except:
        print("    ❌ Invalid address format")
        return False
    
    print()
    print(f"[5] Checking admin sessions...")
    
    try:
        session_ids = contract.functions.getAdminSessions(admin_address).call()
        
        print(f"    ✓ Found {len(session_ids)} sessions")
        print()
        
        if len(session_ids) == 0:
            print("    No sessions found for this admin")
            print("    Create a session in the admin GUI first")
            return True
        
        # Check each session
        for i, session_id in enumerate(session_ids, 1):
            print(f"    Session {i}:")
            print(f"      ID: {session_id.hex()}")
            
            session = contract.functions.getSession(session_id).call()
            
            print(f"      Admin: {session[0]}")
            print(f"      Agent: {session[1]}")
            print(f"      Active: {session[2]}")
            print(f"      Created: {session[3]}")
            print(f"      Last Activity: {session[4]}")
            print(f"      Admin Seq: {session[5]}")
            print(f"      Agent Seq: {session[6]}")
            
            # Check messages
            try:
                message_count = contract.functions.getMessageCount(session_id).call()
                print(f"      Messages: {message_count}")
            except:
                print(f"      Messages: Unable to fetch")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        return False


def main():
    """Main entry point"""
    
    # Load config
    config_path = Path(__file__).parent.parent / "administrator" / "admin_config.json"
    
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        rpc_url = config.get('rpc_url', '')
        contract_address = config.get('contract_address', '')
    else:
        rpc_url = input("RPC URL: ").strip()
        contract_address = input("Contract Address: ").strip()
    
    if not rpc_url or not contract_address:
        print("ERROR: RPC URL and Contract Address required")
        sys.exit(1)
    
    success = check_blockchain_state(rpc_url, contract_address)
    
    print()
    print("=" * 70)
    if success:
        print("✓ Blockchain state check completed")
    else:
        print("❌ Blockchain state check failed")
    print("=" * 70)


if __name__ == "__main__":
    main()

