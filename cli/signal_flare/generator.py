#!/usr/bin/env python3
"""
Generates fake credentials with a secret signature
"""

import hmac
import hashlib
import time
import secrets


class FlareGenerator:
    """Creates honey-credentials"""
    
    def __init__(self, secret, listener_url):
        self.secret = secret  # Your secret key
        self.listener_url = listener_url  # Where to send alerts
    
    def generate_flare_id(self):
        """Creates a unique ID with timestamp and signature"""
        timestamp = str(int(time.time()))  # Current time
        
        # Create signature: mix timestamp + your secret
        signature = hmac.new(
            self.secret.encode(),
            timestamp.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    def generate_aws_credential(self):
        """Make a fake AWS key"""
        flare_id = self.generate_flare_id()
        
        # AWS keys start with AKIA
        access_key = f"AKIA{secrets.token_hex(8).upper()}"
        secret_key = secrets.token_urlsafe(30)
        
        return {
            "flare_id": flare_id,
            "access_key": access_key,
            "secret_key": secret_key
        }


# Test function
if __name__ == "__main__":
    # Example usage
    gen = FlareGenerator("my-secret-key", "http://localhost:8080")
    cred = gen.generate_aws_credential()
    
    print("Generated fake AWS credential:")
    print(f"Access Key: {cred['access_key']}")
    print(f"Secret Key: {cred['secret_key']}")
    print(f"Flare ID: {cred['flare_id']}")
