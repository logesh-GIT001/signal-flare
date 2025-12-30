# SIGNAL-FLARE 🚨

> **Post-exploitation breach confirmation through honey-credential instrumentation**
[![Status: Development](https://img.shields.io/badge/status-development-yellow.svg)](https://github.com/logesh-GIT001/signal-flare)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

---

## 🚧 Project Status: Initial Development

SIGNAL-FLARE is currently under active development. Check back soon for the first release!

## What is SIGNAL-FLARE?

A lightweight deception engine that provides **zero-false-positive breach confirmation** by instrumenting your application with honey-credentials. When an attacker accesses these credentials, you get instant alerts.

### Why SIGNAL-FLARE?

- ✅ **Zero false positives** - Legitimate users never touch honey-credentials
- ✅ **Instant ground truth** - Know immediately when credentials are stolen
- ✅ **Forces attacker uncertainty** - Every credential becomes suspect
- ✅ **Integrates with existing tools** - Enriches your SIEM/EDR alerts


## Quick Start

### Installation
```bash
pip install signal-flare
```

### Generate Credentials
```bash
# Set your secret key
export FLARE_SECRET=$(openssl rand -hex 32)

# Generate fake AWS credential
signal-flare generate --type aws
```

**Output:**
```
# Fake AWS Credential
AWS_ACCESS_KEY_ID=AKIAE14E8AE374F6665C
AWS_SECRET_ACCESS_KEY=950K_Wbl-ZLJmeApGaiOcbDGVWybr3lIjh66o2ho
FLARE_ID=1766816788:72018eb3f5cb75779ae152f79a323372fd6c5069c4042a42d02475fd712282e9
```

## Features

- ✅ **Zero false positives** - Legitimate users never touch honey-credentials
- ✅ **Instant ground truth** - Know immediately when credentials are stolen
- ✅ **CLI tool** - Easy credential generation
- ✅ **Pip installable** - Standard Python package

## Project Status

- [x] Project structure ✅
- [x] CLI tool for generating honey-credentials ✅
- [x] Pip installable package ✅
- [x] Listener service with breach detection ✅
- [ ] Docker Compose deployment
- [ ] Kubernetes manifests
- [ ] Complete documentation

## Stay Updated

⭐ **Star this repo** to follow development progress!

## License

MIT License - see [LICENSE](LICENSE) file for details.
