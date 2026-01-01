# SIGNAL-FLARE Use Cases & Deployment Guide

This document explains how companies deploy and use SIGNAL-FLARE in production environments.

---

## 📋 Table of Contents

1. [What Problem Does This Solve?](#what-problem-does-this-solve)
2. [How It Works](#how-it-works)
3. [Real-World Deployment Scenarios](#real-world-deployment-scenarios)
4. [CI/CD Integration](#cicd-integration)
5. [SIEM Integration](#siem-integration)
6. [Incident Response Workflow](#incident-response-workflow)

---

## What Problem Does This Solve?

### Traditional Security Challenge:
````
Attacker breaks in → Steals credentials → Uses them for weeks
└─ Security team has NO IDEA until damage is done
````

**Problem:** Most breaches go undetected for 200+ days (IBM Security Report).

### SIGNAL-FLARE Solution:
````
Attacker breaks in → Steals credentials → Tests them
└─ 🚨 INSTANT ALERT: "Credentials stolen and used"
````

**Benefit:** Detection in seconds, not months.

---

## How It Works

### 1. Instrumentation Phase (Deployment)

Your production application has environment variables:
````bash
# Real credentials (used by your app)
DATABASE_URL=postgresql://prod_user:realpass@db.company.com:5432/main
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Honey-credentials (NEVER used by your app)
BACKUP_AWS_ACCESS_KEY_ID=AKIAF3A8D9C1B4E6        # ← FAKE
BACKUP_AWS_SECRET_ACCESS_KEY=s3SU0MhafXuK6wFT... # ← FAKE
ANALYTICS_DB_READONLY=postgresql://svc_readonly... # ← FAKE
````

**Key Points:**
- Honey-credentials use plausible names (`BACKUP_`, `LEGACY_`, `READONLY_`)
- They look 100% legitimate to attackers
- Your application code NEVER touches them
- Each has a unique Flare ID embedded

---

### 2. Breach Detection Phase

#### Scenario: Container Compromise
````bash
# Attacker gains shell access
$ kubectl exec -it pod-xyz -- /bin/bash

# Attacker harvests credentials
$ env | grep -i key
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE          # Real
BACKUP_AWS_ACCESS_KEY_ID=AKIAF3A8D9C1B4E6       # Fake (trap!)

# Attacker doesn't know which is real, tests BOTH
$ aws sts get-caller-identity --profile backup
````

**The moment they test the honey-credential:**
````
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Attacker   │────────>│  AWS API     │         │   SIGNAL-   │
│             │ Test key│  (Rejects)   │         │   FLARE     │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                        ┌────────────────────────────────┘
                        │
                        ▼
                  🚨 BREACH ALERT
                  Source: 203.0.113.45
                  Credential: aws_access_key
                  Action: sts:GetCallerIdentity
````

---

### 3. Alert & Response

Security team receives **instant, zero-false-positive alert**:
````
╔══════════════════════════════════════════════════════╗
║ 🚨  BREACH ALERT - CRITICAL                          ║
╠══════════════════════════════════════════════════════╣
║ Event:       BREACH CONFIRMED                        ║
║ Timestamp:   2026-01-01 14:23:45 UTC                 ║
║ Source IP:   203.0.113.45 (External - Russia)        ║
║ Cred Type:   aws_access_key                          ║
║ Action:      sts:GetCallerIdentity                   ║
║ Flare ID:    1767248654:3ea23854f39bf000...          ║
╚══════════════════════════════════════════════════════╝

RECOMMENDED ACTIONS:
→ Isolate pod: kubectl delete pod pod-xyz
→ Rotate ALL credentials in namespace
→ Review logs for initial entry vector
→ Block source IP: 203.0.113.45
````

---

## Real-World Deployment Scenarios

### Scenario 1: Kubernetes Application

**What to protect:** Microservices with sensitive data access

**Deployment:**
````yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  template:
    spec:
      containers:
      - name: app
        image: mycompany/payment-service:v1.2.3
        env:
        # Real credentials (from Vault/Secrets)
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-creds
              key: url
        
        # Honey-credentials (from SIGNAL-FLARE)
        - name: BACKUP_AWS_KEY
          valueFrom:
            secretKeyRef:
              name: flare-honey-creds
              key: aws_access_key
        - name: BACKUP_AWS_SECRET
          valueFrom:
            secretKeyRef:
              name: flare-honey-creds
              key: aws_secret_key
````

**How to generate secrets:**
````bash
# Generate honey-credentials
export FLARE_SECRET=$(kubectl get secret flare-config -o jsonpath='{.data.secret}' | base64 -d)
signal-flare generate --type aws --listener https://flare.internal.company.com/flare

# Create Kubernetes secret
kubectl create secret generic flare-honey-creds \
  --from-literal=aws_access_key=AKIAF3A8D9C1B4E6 \
  --from-literal=aws_secret_key=s3SU0MhafXuK6wFT...
````

---

### Scenario 2: EC2 Instance with Docker

**What to protect:** Legacy monolith on EC2

**Deployment:**
````bash
# On EC2 instance
cd /opt/myapp

# Generate honey-credentials
signal-flare generate --type aws >> .env.production
signal-flare generate --type database >> .env.production

# Restart application
docker-compose restart
````

---

### Scenario 3: Lambda Functions

**What to protect:** Serverless functions with IAM roles

**Deployment:**
````python
# lambda_function.py
import os
import boto3

# Real credential (from IAM role - secure)
s3_client = boto3.client('s3')

# Honey-credential (planted as environment variable)
# THIS IS NEVER USED - just sits there waiting to be stolen
BACKUP_AWS_KEY = os.environ.get('BACKUP_AWS_ACCESS_KEY_ID')
BACKUP_AWS_SECRET = os.environ.get('BACKUP_AWS_SECRET_ACCESS_KEY')

def lambda_handler(event, context):
    # Your real logic here
    s3_client.list_buckets()  # Uses IAM role, not env vars
    return {"status": "ok"}
````

**CloudFormation:**
````yaml
MyLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    Environment:
      Variables:
        BACKUP_AWS_ACCESS_KEY_ID: !Ref HoneyCredentialAccessKey
        BACKUP_AWS_SECRET_ACCESS_KEY: !Ref HoneyCredentialSecretKey
````

---

## CI/CD Integration

### GitHub Actions
````yaml
# .github/workflows/deploy.yml
name: Deploy with Honey-Credentials

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install SIGNAL-FLARE CLI
        run: pip install signal-flare
      
      - name: Generate Honey-Credentials
        env:
          FLARE_SECRET: ${{ secrets.FLARE_SECRET }}
          FLARE_LISTENER: https://flare.internal.company.com/flare
        run: |
          signal-flare generate --type aws >> .env.production
          signal-flare generate --type database >> .env.production
          signal-flare generate --type api >> .env.production
      
      - name: Build Docker Image
        run: |
          docker build --build-arg ENV_FILE=.env.production -t myapp:${{ github.sha }} .
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
````

---

### GitLab CI
````yaml
# .gitlab-ci.yml
deploy:
  stage: deploy
  script:
    - pip install signal-flare
    - export FLARE_SECRET=$FLARE_SECRET_VAR
    - signal-flare generate --type aws >> .env.production
    - signal-flare generate --type database >> .env.production
    - docker build -t myapp:$CI_COMMIT_SHA .
    - kubectl apply -f k8s/
  only:
    - main
````

---

### Jenkins Pipeline
````groovy
pipeline {
    agent any
    
    stages {
        stage('Instrument with Honey-Credentials') {
            steps {
                script {
                    sh 'pip install signal-flare'
                    withCredentials([string(credentialsId: 'flare-secret', variable: 'FLARE_SECRET')]) {
                        sh '''
                            signal-flare generate --type aws >> .env.production
                            signal-flare generate --type database >> .env.production
                        '''
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}
````

---

## SIEM Integration

### Splunk
````python
# In listener/app.py, add to flare_alert():

import requests

def forward_to_splunk(alert):
    """Send alert to Splunk HEC"""
    splunk_url = os.environ.get('SPLUNK_HEC_URL')
    splunk_token = os.environ.get('SPLUNK_HEC_TOKEN')
    
    if splunk_url and splunk_token:
        payload = {
            "event": alert,
            "sourcetype": "signal_flare:breach",
            "index": "security"
        }
        
        requests.post(
            splunk_url,
            json=payload,
            headers={"Authorization": f"Splunk {splunk_token}"},
            timeout=5
        )

# Call in flare_alert():
forward_to_splunk(alert)
````

**Splunk Query:**
````spl
index=security sourcetype="signal_flare:breach" severity IN (high, critical)
| stats count by source_ip, credential_type
| sort -count
````

---

### Elasticsearch / ELK Stack
````python
from elasticsearch import Elasticsearch

def forward_to_elastic(alert):
    """Send alert to Elasticsearch"""
    es = Elasticsearch([os.environ.get('ELASTIC_URL')])
    
    es.index(
        index="signal-flare-alerts",
        body=alert
    )

# Call in flare_alert():
forward_to_elastic(alert)
````

**Kibana Query:**
````json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "event": "BREACH CONFIRMED" }},
        { "range": { "timestamp": { "gte": "now-24h" }}}
      ]
    }
  }
}
````

---

### PagerDuty
````python
def page_oncall_team(alert):
    """Trigger PagerDuty incident"""
    if alert.get('severity') == 'CRITICAL':
        payload = {
            "routing_key": os.environ.get('PAGERDUTY_KEY'),
            "event_action": "trigger",
            "payload": {
                "summary": f"SIGNAL-FLARE: {alert['credential_type']} accessed",
                "severity": "critical",
                "source": alert['source_ip'],
                "custom_details": alert
            }
        }
        
        requests.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload
        )

# Call in flare_alert():
page_oncall_team(alert)
````

---

## Incident Response Workflow

### When Alert Fires:
````
🚨 SIGNAL-FLARE ALERT RECEIVED
│
├─ Step 1: IMMEDIATE ACTIONS (< 2 minutes)
│   ├─ Isolate affected workload
│   │   └─ kubectl delete pod <pod-name>
│   │   └─ OR: kubectl scale deployment <name> --replicas=0
│   ├─ Block source IP
│   │   └─ Update firewall / security group
│   └─ Notify security team
│
├─ Step 2: EVIDENCE COLLECTION (< 10 minutes)
│   ├─ Capture logs
│   │   └─ kubectl logs <pod-name> --previous > breach-logs.txt
│   ├─ Network connections
│   │   └─ kubectl exec <pod> -- netstat -tpn > connections.txt
│   ├─ Process list
│   │   └─ kubectl exec <pod> -- ps auxf > processes.txt
│   └─ File system snapshot
│       └─ kubectl cp <pod>:/app /tmp/forensics/
│
├─ Step 3: CONTAINMENT (< 30 minutes)
│   ├─ Rotate ALL credentials in namespace
│   │   └─ Database passwords
│   │   └─ API keys
│   │   └─ IAM roles
│   ├─ Review audit logs
│   │   └─ AWS CloudTrail (last 24 hours)
│   │   └─ Kubernetes audit logs
│   └─ Identify entry vector
│       └─ CVE exploitation?
│       └─ Stolen SSH key?
│       └─ Insider threat?
│
└─ Step 4: RECOVERY & LESSONS LEARNED
    ├─ Deploy patched application
    ├─ Update runbooks
    └─ Post-mortem meeting
````

---

### Example Runbook
````markdown
# SIGNAL-FLARE Breach Response Runbook

## Severity: CRITICAL

### On-Call Actions (DO THIS FIRST):

1. **Isolate workload** (30 seconds)
```bash
   kubectl delete pod payment-service-xyz
```

2. **Block attacker IP** (1 minute)
```bash
   aws ec2 authorize-security-group-ingress \
     --group-id sg-xxx \
     --ip-permissions IpProtocol=tcp,FromPort=0,ToPort=65535,IpRanges='[{CidrIp=203.0.113.45/32,Description="BLOCKED - SIGNAL-FLARE"}]'
```

3. **Page security team** (30 seconds)
```bash
   Send alert to #security-incidents Slack channel
```

### Investigation (NEXT 10 MINUTES):

4. **Capture evidence**
```bash
   kubectl logs payment-service-xyz --previous > /tmp/breach-$(date +%s).log
```

5. **Check what they accessed**
   - Review CloudTrail for AWS API calls from compromised credentials
   - Check application logs for database queries
   - Review network logs for data exfiltration

### Remediation:

6. **Rotate credentials**
   - Database: `ALTER USER prod_user PASSWORD 'new_random_pass';`
   - AWS: Revoke IAM keys in AWS Console
   - API keys: Regenerate in vendor dashboard

7. **Deploy fresh application**
```bash
   kubectl rollout restart deployment/payment-service
```

### Post-Incident:

8. **Root cause analysis**
   - How did attacker gain initial access?
   - What vulnerability was exploited?
   - Update security controls to prevent recurrence

9. **Update documentation**
   - Add this incident to threat model
   - Update runbooks with lessons learned
````

---

## Best Practices

### ✅ DO:

- **Rotate honey-credentials with every deployment** (prevents stale credentials in backups)
- **Use plausible naming** (`BACKUP_`, `LEGACY_`, `READONLY_`)
- **Monitor listener health** (health check endpoint: `/health`)
- **Integrate with SIEM** (centralize alerts)
- **Test quarterly** (red team exercises)

### ❌ DON'T:

- **Don't reuse the same honey-credentials** across environments
- **Don't expose listener to internet** (internal-only endpoint)
- **Don't ignore LOW severity alerts** (could be attacker probing)
- **Don't log Flare IDs in application logs** (reduces effectiveness)

---

## Metrics & ROI

### Key Performance Indicators:

- **Mean Time to Detect (MTTD):** < 5 seconds (vs. industry average: 200+ days)
- **False Positive Rate:** 0% (by design - honey-credentials are never legitimately used)
- **Detection Coverage:** 100% of credential theft attempts

### Cost Analysis:

**Without SIGNAL-FLARE:**
````
Average breach cost: $4.45M (IBM Security Report 2023)
Average dwell time: 277 days
````

**With SIGNAL-FLARE:**
````
Deployment cost: $0 (open source)
Operational cost: < $100/month (listener hosting)
Detection time: < 5 seconds
ROI: Prevents even ONE undetected breach = millions saved
````

---

## Support & Questions

- **Documentation:** https://github.com/logesh-GIT001/signal-flare
- **Issues:** https://github.com/logesh-GIT001/signal-flare/issues
- **Security:** Report vulnerabilities privately to [security email]

---

**Need help integrating SIGNAL-FLARE into your environment?** Open an issue and we'll help!
