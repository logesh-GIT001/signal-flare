#!/usr/bin/env python3
"""Simple CLI for SIGNAL-FLARE"""

import sys
import os
from signal_flare.generator import FlareGenerator


def main():
    # Check if user provided credential type
    if len(sys.argv) < 2:
        print("Usage: signal-flare generate --type [aws|database|api]")
        sys.exit(1)
    
    # Get credential type
    if "--type" not in sys.argv:
        print("Error: --type required")
        sys.exit(1)
    
    cred_type = sys.argv[sys.argv.index("--type") + 1]
    
    # Get secret from environment
    secret = os.environ.get('FLARE_SECRET', 'default-test-secret')
    
    # Create generator
    gen = FlareGenerator(secret, "http://localhost:8080")
    
    # Generate credential
    if cred_type == "aws":
        cred = gen.generate_aws_credential()
        print(f"# Fake AWS Credential")
        print(f"AWS_ACCESS_KEY_ID={cred['access_key']}")
        print(f"AWS_SECRET_ACCESS_KEY={cred['secret_key']}")
        print(f"FLARE_ID={cred['flare_id']}")
    else:
        print(f"Type '{cred_type}' not implemented yet")


if __name__ == '__main__':
    main()
