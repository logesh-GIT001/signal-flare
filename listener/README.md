# SIGNAL-FLARE Listener

Flask-based breach detection service that receives and validates honey-credential usage alerts.

## Features

- ✅ HMAC signature validation
- ✅ TTL expiration checks
- ✅ Real-time breach alerts
- ✅ Health check endpoint
- ✅ Detailed logging (IP, timestamp, action)

## Running Locally
```bash
# Install dependencies
pip install Flask

# Set secret key
export FLARE_SECRET=$(openssl rand -hex 32)

# Run listener
python3 app.py
```

Listener starts on `http://0.0.0.0:8080`

## Endpoints

### Health Check
```bash
GET /health
```

### Breach Alert
```bash
POST /flare
Content-Type: application/json

{
  "flare_id": "1767092992:3d2accbcd...",
  "credential_type": "aws_access_key",
  "action_attempted": "iam:ListUsers"
}
```

## Testing

See main repository for end-to-end testing guide: https://github.com/logesh-GIT001/signal-flare
