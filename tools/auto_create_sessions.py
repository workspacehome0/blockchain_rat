#!/usr/bin/env python3
"""
Auto Session Creator
Monitors for new registered agents and automatically creates sessions
"""

import sys
import json
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.blockchain_client import BlockchainClient


def auto_create_sessions(config_path, check_interval=30):
    """
    Automatically create sessions for newly registered agents
    
    Args:
        config_path: Path to admin config file
        check_interval: How often to check for new agents (seconds)
    """
    
    print("=" * 70)
    print("AUTO SESSION CREATOR")
    print("=" * 70)
    print()
    print("This tool automatically creates sessions for newly registered agents.")
    print(f"Checking every {check_interval} seconds...")
    print("Press Ctrl+C to stop")
    print()
    
    # Load admin config
    with open(config_path) as f:
        config = json.load(f)
    
    # Connect to blockchain
    print(f"Connecting to blockchain...")
    print(f"  RPC: {config['rpc_url']}")
    print(f"  Contract: {config['contract_address']}")
    
    blockchain = BlockchainClient(config)
    
    print(f"  Admin: {blockchain.address}")
    print()
    
    # Track which agents we've already created sessions for
    processed_agents = set()
    
    # Load existing sessions
    try:
        existing_sessions = blockchain.get_admin_sessions()
        for session_id in existing_sessions:
            session = blockchain.get_session(session_id)
            processed_agents.add(session['agent'])
        print(f"Found {len(existing_sessions)} existing session(s)")
        print(f"Tracking {len(processed_agents)} agent(s)")
        print()
    except Exception as e:
        print(f"Warning: Could not load existing sessions: {e}")
        print()
    
    # Monitor loop
    check_count = 0
    while True:
        try:
            check_count += 1
            print(f"[Check #{check_count}] Looking for new agents...")
            
            # Get all registered agents (this would need a contract function)
            # For now, we'll check if there's a way to enumerate agents
            # Since the contract doesn't have this, we'll use a different approach
            
            # Alternative: Check a known list of agent addresses
            # Or: Have agents write their address to a shared file/server
            
            print("  Note: Contract doesn't expose agent enumeration")
            print("  Waiting for agent addresses to be provided...")
            print()
            print("  To create session manually:")
            print(f"    python -c \"from shared.blockchain_client import BlockchainClient; bc = BlockchainClient({config}); print('Session:', bc.create_session('AGENT_ADDRESS'))\"")
            print()
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\n\nStopping auto session creator...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(check_interval)


def create_session_for_agent(admin_config_path, agent_address):
    """
    Create a session for a specific agent
    
    Args:
        admin_config_path: Path to admin config
        agent_address: Agent's wallet address
    """
    
    print("=" * 70)
    print("CREATE SESSION FOR AGENT")
    print("=" * 70)
    print()
    
    # Load admin config
    with open(admin_config_path) as f:
        config = json.load(f)
    
    # Connect
    print(f"Connecting as admin...")
    blockchain = BlockchainClient(config)
    print(f"  Admin: {blockchain.address}")
    print()
    
    # Create session
    print(f"Creating session for agent: {agent_address}")
    try:
        session_id = blockchain.create_session(agent_address)
        print()
        print("✓ Session created successfully!")
        print()
        print(f"Session ID: {session_id}")
        print()
        print("Agent can now start with:")
        print(f"  python agent.py --session {session_id}")
        print()
        return session_id
    except Exception as e:
        print(f"\n❌ Failed to create session: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-create sessions for agents')
    parser.add_argument('--config', default='administrator/admin_config.json', help='Admin config file')
    parser.add_argument('--agent', help='Create session for specific agent address')
    parser.add_argument('--auto', action='store_true', help='Auto-create sessions (monitoring mode)')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print()
        print("Create config file with:")
        print('{')
        print('  "rpc_url": "https://polygon-rpc.com",')
        print('  "contract_address": "0x...",')
        print('  "private_key": "..."')
        print('}')
        sys.exit(1)
    
    if args.agent:
        # Create session for specific agent
        create_session_for_agent(config_path, args.agent)
    elif args.auto:
        # Auto-create mode
        auto_create_sessions(config_path, args.interval)
    else:
        # Interactive mode
        print("=" * 70)
        print("SESSION CREATOR")
        print("=" * 70)
        print()
        agent_address = input("Enter agent wallet address: ").strip()
        if agent_address:
            create_session_for_agent(config_path, agent_address)
        else:
            print("No address provided")


if __name__ == "__main__":
    main()

