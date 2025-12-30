#!/usr/bin/env python3
"""
SIGNAL-FLARE Listener
Receives and validates breach alerts
"""

from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import os

app = Flask(__name__)

# Get secret from environment
FLARE_SECRET = os.environ.get('FLARE_SECRET', 'default-test-secret')
TTL_HOURS = 24
TTL_SECONDS = TTL_HOURS * 3600


def validate_flare_id(flare_id):
    """
    Verify the HMAC signature and check if not expired.
    Format: timestamp:signature
    """
    try:
        timestamp_str, signature = flare_id.split(':', 1)
        timestamp = int(timestamp_str)
        
        # Check if expired
        if time.time() - timestamp > TTL_SECONDS:
            return False, "Expired"
        
        # Verify HMAC signature
        expected = hmac.new(
            FLARE_SECRET.encode(),
            timestamp_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(signature, expected):
            return True, "Valid"
        else:
            return False, "Invalid signature"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/flare', methods=['POST'])
def flare_alert():
    """
    Receives breach alerts when honey-credentials are used.
    """
    data = request.get_json()
    
    if not data or 'flare_id' not in data:
        return jsonify({"error": "Missing flare_id"}), 400
    
    flare_id = data.get('flare_id')
    cred_type = data.get('credential_type', 'unknown')
    action = data.get('action_attempted', 'none')
    
    # Validate the flare ID
    is_valid, reason = validate_flare_id(flare_id)
    
    if not is_valid:
        return jsonify({
            "status": "rejected",
            "reason": reason
        }), 401
    
    # Get request info
    source_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    # Log the breach alert
    alert = {
        "event": "BREACH CONFIRMED",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        "flare_id": flare_id,
        "source_ip": source_ip,
        "user_agent": user_agent,
        "credential_type": cred_type,
        "action_attempted": action
    }
    
    # Print to console
    print("\n" + "="*60)
    print("🚨 SIGNAL-FLARE ALERT 🚨")
    print("="*60)
    for key, value in alert.items():
        print(f"{key}: {value}")
    print("="*60 + "\n")
    
    return jsonify({
        "status": "confirmed",
        "message": "Breach alert logged"
    }), 200


if __name__ == '__main__':
    print("🚨 SIGNAL-FLARE Listener starting...")
    print(f"TTL: {TTL_HOURS} hours")
    app.run(host='0.0.0.0', port=8080, debug=True)
