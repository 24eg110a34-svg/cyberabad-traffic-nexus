"""
CYBERABAD TRAFFIC NEXUS - AES Encryption Module
Encrypts sensitive traffic data and emergency alerts
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json
import os

# Encryption key (in production, store securely in environment variable)
ENCRYPTION_KEY = os.environ.get('TRAFFIC_NEXUS_KEY', 'cyberabad_traffic_nexus_secret_key_2024')

class TrafficEncryptor:
    def __init__(self, key=None):
        if key is None:
            key = ENCRYPTION_KEY
        self.key = self._derive_key(key)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password):
        """Derive encryption key from password"""
        salt = b'cyberabad_traffic_nexus_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data):
        """Encrypt data"""
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt data"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode()).decode()
            try:
                return json.loads(decrypted)
            except:
                return decrypted
        except Exception as e:
            return None
    
    def encrypt_prediction_data(self, prediction_result):
        """Encrypt prediction result for secure storage"""
        sensitive_data = {
            "prediction": prediction_result.get("prediction"),
            "confidence": prediction_result.get("confidence"),
            "score": prediction_result.get("score"),
            "timestamp": prediction_result.get("timestamp")
        }
        return self.encrypt(sensitive_data)
    
    def decrypt_prediction_data(self, encrypted_data):
        """Decrypt prediction data"""
        return self.decrypt(encrypted_data)
    
    def encrypt_alert_data(self, alert):
        """Encrypt alert data for secure transmission"""
        sensitive_fields = ["location", "score", "message", "action"]
        encrypted_alert = alert.copy()
        
        for field in sensitive_fields:
            if field in encrypted_alert:
                encrypted_alert[field] = self.encrypt(str(encrypted_alert[field]))
        
        return encrypted_alert
    
    def encrypt_emergency_route(self, route_data):
        """Encrypt emergency route data"""
        sensitive_data = {
            "route": route_data.get("route"),
            "affected_junctions": route_data.get("affected_junctions"),
            "eta": route_data.get("eta"),
            "vehicle_id": route_data.get("vehicle_id")
        }
        return self.encrypt(sensitive_data)
    
    def generate_token(self, data, expiry_hours=24):
        """Generate encrypted token for API authentication"""
        import time
        token_data = {
            "data": data,
            "timestamp": time.time(),
            "expiry": time.time() + (expiry_hours * 3600)
        }
        return self.encrypt(token_data)
    
    def validate_token(self, token):
        """Validate encrypted token"""
        import time
        try:
            token_data = self.decrypt(token)
            if token_data and "expiry" in token_data:
                if time.time() < token_data["expiry"]:
                    return token_data["data"]
        except:
            pass
        return None


def hash_sensitive_data(data):
    """Create one-way hash of sensitive data"""
    import hashlib
    return hashlib.sha256(str(data).encode()).hexdigest()


def mask_sensitive_info(info, visible_chars=4):
    """Mask sensitive information for display"""
    if not info:
        return "****"
    if len(info) <= visible_chars * 2:
        return "*" * len(info)
    return info[:visible_chars] + "*" * (len(info) - visible_chars * 2) + info[-visible_chars:]


def encrypt_file(filepath, output_path=None):
    """Encrypt a file"""
    encryptor = TrafficEncryptor()
    
    if output_path is None:
        output_path = filepath + ".enc"
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    encrypted = encryptor.cipher.encrypt(data)
    
    with open(output_path, 'wb') as f:
        f.write(encrypted)
    
    return output_path


def decrypt_file(encrypted_path, output_path=None):
    """Decrypt a file"""
    encryptor = TrafficEncryptor()
    
    if output_path is None:
        output_path = encrypted_path.replace('.enc', '')
    
    with open(encrypted_path, 'rb') as f:
        encrypted = f.read()
    
    decrypted = encryptor.cipher.decrypt(encrypted)
    
    with open(output_path, 'wb') as f:
        f.write(decrypted)
    
    return output_path


# Global encryptor instance
_global_encryptor = None

def get_encryptor():
    """Get global encryptor instance"""
    global _global_encryptor
    if _global_encryptor is None:
        _global_encryptor = TrafficEncryptor()
    return _global_encryptor


# Test encryption module
if __name__ == "__main__":
    encryptor = TrafficEncryptor()
    
    # Test encryption
    test_data = {"message": "Emergency at Charminar", "score": 95.5}
    encrypted = encryptor.encrypt(test_data)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = encryptor.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Test token generation
    token = encryptor.generate_token({"user": "admin", "role": "operator"})
    print(f"Token: {token[:50]}...")
    
    validated = encryptor.validate_token(token)
    print(f"Validated: {validated}")
