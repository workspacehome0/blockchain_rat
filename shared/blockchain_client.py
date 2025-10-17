"""
Blockchain client for interacting with SessionManager contract on Polygon
"""

import json
import os
import time
from web3 import Web3
from eth_account import Account
from pathlib import Path


class BlockchainClient:
    def __init__(self, config):
        """
        Initialize blockchain client
        
        Args:
            config: dict with keys:
                - rpc_url: Polygon RPC endpoint
                - private_key: Private key for transactions
                - contract_address: SessionManager contract address
        """
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        
        # Setup account
        self.account = Account.from_key(config['private_key'])
        self.address = self.account.address
        
        # Load contract
        self.contract = self._load_contract(config['contract_address'])
        
        print(f"Blockchain client initialized")
        print(f"Wallet address: {self.address}")
        print(f"Contract address: {config['contract_address']}")
        print(f"Connected: {self.w3.is_connected()}")
    
    def _load_contract(self, contract_address):
        """Load contract ABI and create contract instance"""
        # Try to load ABI from file
        abi_path = Path(__file__).parent / 'SessionManager.abi.json'
        
        if abi_path.exists():
            with open(abi_path, 'r') as f:
                abi = json.load(f)
        else:
            # Minimal ABI if file doesn't exist
            abi = [
                {
                    "inputs": [{"internalType": "bytes", "name": "publicKey", "type": "bytes"}],
                    "name": "registerAgent",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
                    "name": "createSession",
                    "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "bytes32", "name": "sessionId", "type": "bytes32"},
                        {"internalType": "bytes", "name": "encryptedPayload", "type": "bytes"},
                        {"internalType": "uint256", "name": "sequenceNumber", "type": "uint256"}
                    ],
                    "name": "sendMessage",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "bytes32", "name": "sessionId", "type": "bytes32"}],
                    "name": "terminateSession",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "bytes32", "name": "sessionId", "type": "bytes32"},
                        {"internalType": "uint256", "name": "fromIndex", "type": "uint256"},
                        {"internalType": "uint256", "name": "count", "type": "uint256"}
                    ],
                    "name": "getMessages",
                    "outputs": [
                        {
                            "components": [
                                {"internalType": "address", "name": "sender", "type": "address"},
                                {"internalType": "bytes", "name": "encryptedPayload", "type": "bytes"},
                                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                                {"internalType": "uint256", "name": "sequenceNumber", "type": "uint256"},
                                {"internalType": "bytes32", "name": "sessionId", "type": "bytes32"}
                            ],
                            "internalType": "struct SessionManager.Message[]",
                            "name": "",
                            "type": "tuple[]"
                        }
                    ],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "bytes32", "name": "sessionId", "type": "bytes32"}],
                    "name": "getMessageCount",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "bytes32", "name": "sessionId", "type": "bytes32"}],
                    "name": "getSession",
                    "outputs": [
                        {
                            "components": [
                                {"internalType": "bytes32", "name": "sessionId", "type": "bytes32"},
                                {"internalType": "address", "name": "admin", "type": "address"},
                                {"internalType": "address", "name": "agent", "type": "address"},
                                {"internalType": "bool", "name": "active", "type": "bool"},
                                {"internalType": "uint256", "name": "createdAt", "type": "uint256"},
                                {"internalType": "uint256", "name": "lastActivity", "type": "uint256"},
                                {"internalType": "uint256", "name": "adminSeqNum", "type": "uint256"},
                                {"internalType": "uint256", "name": "agentSeqNum", "type": "uint256"}
                            ],
                            "internalType": "struct SessionManager.Session",
                            "name": "",
                            "type": "tuple"
                        }
                    ],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
                    "name": "getAgentPublicKey",
                    "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "admin", "type": "address"}],
                    "name": "getAdminSessions",
                    "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
                    "name": "getAgentSessions",
                    "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
        
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
    
    def _send_transaction(self, function_call):
        """Send a transaction and wait for receipt"""
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(self.address)
        
        # Get gas price
        gas_price = self.w3.eth.gas_price
        
        # Build transaction
        transaction = function_call.build_transaction({
            'from': self.address,
            'nonce': nonce,
            'gas': 500000,  # Will be estimated
            'gasPrice': gas_price
        })
        
        # Estimate gas
        try:
            estimated_gas = self.w3.eth.estimate_gas(transaction)
            transaction['gas'] = int(estimated_gas * 1.2)  # Add 20% buffer
        except Exception as e:
            print(f"Gas estimation failed: {e}")
        
        # Sign transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
        
        # Send transaction (compatible with web3.py v6+)
        raw_transaction = signed_txn.raw_transaction if hasattr(signed_txn, 'raw_transaction') else signed_txn.rawTransaction
        tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
        
        print(f"Transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt['status'] == 1:
            print(f"Transaction successful: {tx_hash.hex()}")
        else:
            print(f"Transaction failed: {tx_hash.hex()}")
        
        return receipt
    
    def register_agent(self, public_key_hex):
        """Register agent with public key"""
        function_call = self.contract.functions.registerAgent(
            Web3.to_bytes(hexstr=public_key_hex)
        )
        return self._send_transaction(function_call)
    
    def create_session(self, agent_address):
        """Create a new session with an agent"""
        function_call = self.contract.functions.createSession(
            Web3.to_checksum_address(agent_address)
        )
        receipt = self._send_transaction(function_call)
        
        # Extract session ID from logs
        for log in receipt['logs']:
            try:
                event = self.contract.events.SessionCreated().process_log(log)
                return event['args']['sessionId'].hex()
            except:
                continue
        
        raise Exception("Failed to extract session ID from transaction")
    
    def send_message(self, session_id, encrypted_payload, sequence_number):
        """Send a message in a session"""
        if isinstance(session_id, str):
            session_id = bytes.fromhex(session_id.replace('0x', ''))
        
        function_call = self.contract.functions.sendMessage(
            session_id,
            Web3.to_bytes(hexstr=encrypted_payload),
            sequence_number
        )
        return self._send_transaction(function_call)
    
    def get_messages(self, session_id, from_index, count):
        """Get messages from a session"""
        if isinstance(session_id, str):
            session_id = bytes.fromhex(session_id.replace('0x', ''))
        
        messages = self.contract.functions.getMessages(
            session_id,
            from_index,
            count
        ).call()
        
        return messages
    
    def get_message_count(self, session_id):
        """Get total message count for a session"""
        if isinstance(session_id, str):
            session_id = bytes.fromhex(session_id.replace('0x', ''))
        
        return self.contract.functions.getMessageCount(session_id).call()
    
    def get_session(self, session_id):
        """Get session details"""
        if isinstance(session_id, str):
            session_id = bytes.fromhex(session_id.replace('0x', ''))
        
        session = self.contract.functions.getSession(session_id).call()
        
        return {
            'session_id': session[0].hex(),
            'admin': session[1],
            'agent': session[2],
            'active': session[3],
            'created_at': session[4],
            'last_activity': session[5],
            'admin_seq_num': session[6],
            'agent_seq_num': session[7]
        }
    
    def get_agent_public_key(self, agent_address):
        """Get agent's public key"""
        public_key_bytes = self.contract.functions.getAgentPublicKey(
            Web3.to_checksum_address(agent_address)
        ).call()
        return '0x' + public_key_bytes.hex()
    
    def terminate_session(self, session_id):
        """Terminate a session"""
        if isinstance(session_id, str):
            session_id = bytes.fromhex(session_id.replace('0x', ''))
        
        function_call = self.contract.functions.terminateSession(session_id)
        return self._send_transaction(function_call)
    
    def get_admin_sessions(self):
        """Get all sessions for current wallet (as admin)"""
        sessions = self.contract.functions.getAdminSessions(self.address).call()
        return [s.hex() for s in sessions]
    
    def get_agent_sessions(self):
        """Get all sessions for current wallet (as agent)"""
        sessions = self.contract.functions.getAgentSessions(self.address).call()
        return [s.hex() for s in sessions]
    
    def get_balance(self):
        """Get wallet balance in MATIC"""
        balance_wei = self.w3.eth.get_balance(self.address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def get_gas_price(self):
        """Get current gas price in Gwei"""
        gas_price_wei = self.w3.eth.gas_price
        return self.w3.from_wei(gas_price_wei, 'gwei')
    
    def poll_for_new_messages(self, session_id, last_count, callback):
        """
        Poll for new messages in a session
        
        Args:
            session_id: Session ID
            last_count: Last known message count
            callback: Function to call with new messages
        """
        current_count = self.get_message_count(session_id)
        
        if current_count > last_count:
            new_messages = self.get_messages(session_id, last_count, current_count - last_count)
            if new_messages:
                callback(new_messages)
            return current_count
        
        return last_count


# Example usage
if __name__ == "__main__":
    # Test configuration
    config = {
        'rpc_url': 'https://rpc-mumbai.maticvigil.com',
        'private_key': '0x' + '0' * 64,  # Replace with actual key
        'contract_address': '0x' + '0' * 40  # Replace with actual address
    }
    
    try:
        client = BlockchainClient(config)
        balance = client.get_balance()
        print(f"Balance: {balance} MATIC")
        
        gas_price = client.get_gas_price()
        print(f"Gas price: {gas_price} Gwei")
    except Exception as e:
        print(f"Error: {e}")

