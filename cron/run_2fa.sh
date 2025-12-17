#!/bin/bash
set -e

CODE_JSON=$(curl -s http://localhost:8080/generate-2fa || true)
CODE=$(echo "$CODE_JSON" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('code', ''))" 2>/dev/null || echo "")

if [ -n "$CODE" ]; then
  mkdir -p /cron
  TS=$(date -u +"%Y-%m-%d %H:%M:%S")
  echo "$TS - 2FA Code: $CODE" > /cron/last_code.txt
fi
