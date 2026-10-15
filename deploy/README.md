# Deployment Guide & Production Hardening

This directory contains production deployment manifests, reverse proxy templates, firewall scripts, and database lockdown audit verification tools for the **Economic Indicators Dashboard**.

---

## Architecture Overview

```
 [Browser / Client]
        │ HTTPS (TLS 1.3)
        ▼
 [Cloudflare Pages / Caddy / Nginx] (Port 443)
        │
        ├─ Frontend (Static Bundle @ /index.html)
        │
        └─ API Reverse Proxy
                │ HTTP Proxy (Local Loopback)
                ▼
        [FastAPI Uvicorn] (127.0.0.1:8000)
                │ Parameterized SQL (Static Queries)
                ▼
        [PostgreSQL] (Strictly bound to 127.0.0.1 / Loopback)
                ✖ PORT 5432/5434 UNREACHABLE FROM PUBLIC INTERNET
```

---

## 1. Automated Render Deployment (Infrastructure as Code)

A complete Render Blueprint is provided at `deploy/render.yaml`:
- **API Web Service (`economic-indicators-api`):** Python environment running FastAPI via Uvicorn, health check configured on `/health`.
- **Frontend Static Site (`economic-indicators-frontend`):** Auto-built with `npm run build` from `frontend/`, publishing `dist/`.
- **Private PostgreSQL Database (`economic-indicators-db`):** Network-isolated, unreachable from the public internet (`ipAllowList: []`).

### Launching on Render:
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New** -> **Blueprint**.
3. Connect the GitHub repository `agrimsri/economic-indicators-dashboard`.
4. Render detects `deploy/render.yaml` and provisions all 3 resources automatically.

Alternatively, via the authenticated Render CLI:
```bash
render blueprints apply --file deploy/render.yaml
```

---

## 2. VPS Deployment (Systemd + Caddy / Nginx + UFW)

For a dedicated Linux VPS (Ubuntu / Debian / AlmaLinux):

### Step 1: Firewall Lockdown
Enforce least-privilege incoming firewall policies and block database ports externally:
```bash
sudo bash deploy/ufw-rules.sh
```
This permits only:
- `22/tcp` (SSH)
- `80/tcp` (HTTP ACME verification)
- `443/tcp` (HTTPS Web traffic)
- Explicitly drops `5432` and `5434` from `0.0.0.0/0`.

### Step 2: Systemd Service Installation
```bash
sudo cp deploy/systemd/economic-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now economic-api
sudo systemctl status economic-api
```

### Step 3: Reverse Proxy with Auto-TLS
- **Option A (Caddy):** Copy `deploy/Caddyfile` to `/etc/caddy/Caddyfile` and run `sudo systemctl reload caddy`. Caddy automatically obtains ZeroSSL/Let's Encrypt certificates.
- **Option B (Nginx):** Copy `deploy/nginx.conf` to `/etc/nginx/sites-available/economic.conf`, symlink to `sites-enabled`, and issue certs with `certbot --nginx`.

---

## 3. Database Lockdown Audit Evidence

The database port is strictly bound to `127.0.0.1` and protected by firewall rules.

To reproduce the security audit proof:
```bash
./deploy/verify_db_lockdown.sh
```

### Verified Audit Proof (`deploy/evidence_db_lockdown.txt`):
```text
1. Socket Binding:
LISTEN 0 4096 127.0.0.1:5434 0.0.0.0:*

2. Loopback Reachability:
Connection to 127.0.0.1 5434 port [tcp/*] succeeded!
✔ Loopback reachability: 127.0.0.1:5434 is accessible to local backend.

3. External IP Reachability (Public / Subnet Interfaces):
Testing ingress on IP: 10.147.144.106:5434...
nc: connect to 10.147.144.106 port 5434 (tcp) failed: Connection refused
✔ VERIFIED: External IP 10.147.144.106:5434 is CLOSED / Connection Refused.

RESULT: All audit checks passed. Database port is not exposed to the public internet.
```

---

## 4. Evaluation User Provisioning

To provision or reset reviewer access:
```bash
python backend/scripts/create_user.py --username agrim --password <secure_password>
```
Credentials are sent privately and are never stored in version control.
