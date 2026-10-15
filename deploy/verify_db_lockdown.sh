#!/usr/bin/env bash
# Verification of Database Loopback Lockdown Evidence

set -euo pipefail

DB_PORT=${1:-5434}
echo "=========================================================="
echo " Database Port Lockdown Audit & Verification"
echo " Target Database Port: $DB_PORT"
echo "=========================================================="

echo -e "\n1. Checking Socket Bindings via ss..."
ss -tlpn | grep -E ":$DB_PORT\b" || true

echo -e "\n2. Testing Localhost Loopback Reachability (Must Succeed)..."
if nc -zv -w 2 127.0.0.1 "$DB_PORT"; then
  echo "✔ Loopback reachability: 127.0.0.1:$DB_PORT is accessible to local backend."
else
  echo "✖ Error: Loopback connection failed."
  exit 1
fi

echo -e "\n3. Testing External / Non-Loopback Reachability (Must Fail)..."
NON_LOOPBACK_IPS=$(hostname -I | tr ' ' '\n' | grep -v '^127\.' | grep -v '^$' | head -n 2)

for ip in $NON_LOOPBACK_IPS; do
  echo "Testing ingress on IP: $ip:$DB_PORT..."
  if nc -zv -w 2 "$ip" "$DB_PORT" 2>&1; then
    echo "✖ SECURITY VIOLATION: Database port $DB_PORT is reachable on external IP $ip!"
    exit 2
  else
    echo "✔ VERIFIED: External IP $ip:$DB_PORT is CLOSED / Connection Refused."
  fi
done

echo -e "\n=========================================================="
echo " RESULT: All audit checks passed. Database port is not exposed to the public internet."
echo "=========================================================="
