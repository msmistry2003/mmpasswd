import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class SecurityManager:
    def __init__(self, master_password: str = None, salt: bytes = None, key: bytes = None):
        self.master_password = master_password
        self.salt = salt
        self.key = key
        self.cipher = None
        
        if key:
            self.cipher = Fernet(key)
        elif master_password and salt:
            self.derive_key()

    def derive_key(self):
        """Derives a Fernet key from the master password using PBKDF2."""
        if not self.master_password or not self.salt:
            raise ValueError("Master password and salt are required to derive key")
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        self.key = key
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypts a string."""
        if not self.cipher:
            raise RuntimeError("Cipher not initialized. Key derivation failed.")
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """Decrypts a string."""
        if not self.cipher:
            raise RuntimeError("Cipher not initialized. Key derivation failed.")
        if not data:
            return ""
        try:
            return self.cipher.decrypt(data.encode()).decode()
        except Exception:
            # Return original if decryption fails (fallback/corruption)
            # In a strict security model we might want to raise, 
            # but for a password manager usage, showing 'error' is sometimes better than crash
            return "[Decryption Error]"

    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(16)
