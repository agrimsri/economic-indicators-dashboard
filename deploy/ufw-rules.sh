#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo " Economic Indicators Dashboard - Host Firewall Setup (UFW)"
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root (e.g. sudo bash deploy/ufw-rules.sh)"
  exit 1
fi

echo "==> Setting default traffic policies..."
ufw default deny incoming
ufw default allow outgoing

echo "==> Permitting SSH and HTTPS ingress..."
ufw allow 22/tcp comment "SSH management"
ufw allow 80/tcp comment "HTTP for ACME / TLS challenge"
ufw allow 443/tcp comment "HTTPS Web traffic"

echo "==> Explicitly blocking Postgres ports from public ingress..."
ufw deny 5432/tcp comment "Postgres standard port blocked externally"
ufw deny 5434/tcp comment "Postgres custom port blocked externally"

echo "==> Enabling firewall..."
ufw --force enable

echo "==> UFW Active Status:"
ufw status verbose
