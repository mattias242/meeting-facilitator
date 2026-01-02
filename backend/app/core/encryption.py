"""Database encryption utilities."""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class DatabaseEncryption:
    """Handle encryption/decryption of sensitive database fields."""
    
    def __init__(self):
        """Initialize encryption with key from environment."""
        key = os.getenv("DB_ENCRYPTION_KEY")
        if not key:
            # Generate a key for development (NOT for production)
            key = base64.urlsafe_b64encode(b'development-key-change-in-production-32bytes!')
        
        # Derive encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'meeting_facilitator_salt',  # In production, use random salt per deployment
            iterations=100000,
        )
        key_bytes = kdf.derive(key.encode() if isinstance(key, str) else key)
        
        self.cipher = Fernet(base64.urlsafe_b64encode(key_bytes))
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt binary data."""
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data."""
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_text(self, text: str) -> str:
        """Encrypt text and return base64 encoded string."""
        encrypted_bytes = self.encrypt(text.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded string."""
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted_bytes = self.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')


# Global encryption instance
db_encryption = DatabaseEncryption()
