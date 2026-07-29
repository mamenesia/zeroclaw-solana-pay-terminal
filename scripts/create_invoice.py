#!/usr/bin/env python3
"""Build a Solana Pay transfer request URL (Tier-1, no keys)."""
from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode

BASE58_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


def main() -> int:
    p = argparse.ArgumentParser(description="Create Solana Pay transfer invoice JSON + URL")
    p.add_argument("--merchant", required=True, help="Merchant base58 pubkey (receive-only)")
    p.add_argument("--amount", required=True, type=float, help="Amount in UI units (SOL or token)")
    p.add_argument("--label", default="Shop order")
    p.add_argument("--message", default="")
    p.add_argument("--spl-token", default="", help=f"Optional SPL mint (USDC={USDC_MINT})")
    p.add_argument("--order-id", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--demo", action="store_true", help="Allow demo mode markers")
    args = p.parse_args()

    if not BASE58_RE.match(args.merchant):
        print(json.dumps({"ok": False, "error": "merchant_pubkey_invalid"}))
        return 2
    if args.amount <= 0:
        print(json.dumps({"ok": False, "error": "amount_must_be_positive"}))
        return 2
    if not args.demo and args.amount > 10_000:
        print(json.dumps({"ok": False, "error": "amount_suspiciously_large_pass_demo_or_lower"}))
        return 2

    order_id = args.order_id or (
        f"ord_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{secrets.token_hex(2)}"
    )
    params = {
        "amount": f"{args.amount:.6f}".rstrip("0").rstrip("."),
        "label": args.label[:32],
        "message": (args.message or order_id)[:64],
    }
    if args.spl_token:
        if not BASE58_RE.match(args.spl_token):
            print(json.dumps({"ok": False, "error": "spl_token_invalid"}))
            return 2
        params["spl-token"] = args.spl_token

    query = urlencode(params, quote_via=quote)
    pay_url = f"solana:{args.merchant}?{query}"

    inv = {
        "ok": True,
        "schema": "zeroclaw-solana-pay-invoice/v1",
        "order_id": order_id,
        "merchant": args.merchant,
        "amount": args.amount,
        "spl_token": args.spl_token or None,
        "label": args.label,
        "message": args.message,
        "pay_url": pay_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "invoiced",
        "demo": bool(args.demo),
        "match": {
            "recipient": args.merchant,
            "amount_ui": args.amount,
            "spl_token": args.spl_token or None,
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inv, indent=2), encoding="utf-8")
    print(json.dumps(inv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
