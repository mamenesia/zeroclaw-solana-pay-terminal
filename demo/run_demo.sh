#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MERCHANT="${MERCHANT_PUBKEY:-So11111111111111111111111111111111111111112}"
OUT="${TMPDIR:-/tmp}/zc_demo_ord.json"

echo "== create invoice =="
python3 "$ROOT/scripts/create_invoice.py" \
  --merchant "$MERCHANT" \
  --amount 0.001 \
  --label "Demo Warung" \
  --message "Kopi susu demo" \
  --demo \
  --out "$OUT"

echo
echo "== simulate watch (no mainnet wait) =="
python3 "$ROOT/scripts/watch_payment.py" --invoice "$OUT" --simulate-paid

echo
echo "Invoice file: $OUT"
echo "Pay URL:"
python3 -c "import json; print(json.load(open(r'$OUT'))['pay_url'])"
