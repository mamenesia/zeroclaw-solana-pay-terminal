#!/usr/bin/env python3
"""Watch public Solana RPC for a matching transfer to merchant (Tier-1, no keys)."""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LAMPORTS = 1_000_000_000


def rpc(url: str, method: str, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "zeroclaw-solana-pay-terminal/0.1",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    return data.get("result")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--invoice", required=True)
    p.add_argument("--rpc", default="https://api.mainnet-beta.solana.com")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--poll", type=float, default=8.0)
    p.add_argument(
        "--simulate-paid",
        action="store_true",
        help="Demo only: emit paid without chain confirmation",
    )
    args = p.parse_args()

    inv = json.loads(Path(args.invoice).read_text(encoding="utf-8"))
    merchant = inv["merchant"]
    amount = float(inv["amount"])
    spl = inv.get("spl_token")
    order_id = inv.get("order_id")

    if args.simulate_paid:
        out = {
            "ok": True,
            "status": "paid",
            "order_id": order_id,
            "signature": "SIMULATED_DEMO_SIGNATURE",
            "explorer": "https://solscan.io/",
            "matched_at": datetime.now(timezone.utc).isoformat(),
            "note": "simulate-paid flag set — not a mainnet proof",
        }
        print(json.dumps(out))
        return 0

    start = time.time()
    seen: set[str] = set()
    try:
        sigs = rpc(args.rpc, "getSignaturesForAddress", [merchant, {"limit": 15}]) or []
        for s in sigs:
            if s.get("signature"):
                seen.add(s["signature"])
    except Exception as e:
        print(
            json.dumps(
                {"ok": False, "status": "rpc_error", "error": str(e), "order_id": order_id}
            )
        )
        return 1

    target_lamports = int(round(amount * LAMPORTS)) if not spl else None

    while time.time() - start < args.timeout:
        try:
            sigs = rpc(args.rpc, "getSignaturesForAddress", [merchant, {"limit": 20}]) or []
        except Exception as e:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "status": "rpc_error",
                        "error": str(e),
                        "order_id": order_id,
                    }
                )
            )
            time.sleep(args.poll)
            continue

        for s in sigs:
            sig = s.get("signature")
            if not sig or sig in seen:
                continue
            seen.add(sig)
            try:
                tx = rpc(
                    args.rpc,
                    "getTransaction",
                    [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
                )
            except Exception:
                continue
            if not tx:
                continue

            msg = (tx.get("transaction") or {}).get("message") or {}
            instructions = msg.get("instructions") or []

            if not spl and target_lamports is not None:
                for ix in instructions:
                    parsed = ix.get("parsed") if isinstance(ix, dict) else None
                    if not parsed or parsed.get("type") != "transfer":
                        continue
                    info = parsed.get("info") or {}
                    if info.get("destination") != merchant:
                        continue
                    lamports = int(info.get("lamports") or 0)
                    if abs(lamports - target_lamports) <= max(1, target_lamports // 100):
                        out = {
                            "ok": True,
                            "status": "paid",
                            "order_id": order_id,
                            "signature": sig,
                            "lamports": lamports,
                            "explorer": f"https://solscan.io/tx/{sig}",
                            "matched_at": datetime.now(timezone.utc).isoformat(),
                        }
                        print(json.dumps(out))
                        return 0

            if spl:
                for ix in instructions:
                    parsed = ix.get("parsed") if isinstance(ix, dict) else None
                    if not parsed or parsed.get("type") not in ("transfer", "transferChecked"):
                        continue
                    info = parsed.get("info") or {}
                    mint = info.get("mint")
                    if mint and mint != spl:
                        continue
                    amt = None
                    token_amount = info.get("tokenAmount")
                    if isinstance(token_amount, dict):
                        amt = token_amount.get("uiAmount")
                    if amt is None and info.get("amount") is not None and info.get("decimals") is not None:
                        try:
                            amt = int(info["amount"]) / (10 ** int(info["decimals"]))
                        except Exception:
                            amt = None
                    if amt is not None and abs(float(amt) - amount) <= max(0.000001, amount * 0.01):
                        out = {
                            "ok": True,
                            "status": "paid",
                            "order_id": order_id,
                            "signature": sig,
                            "token_amount_ui": amt,
                            "mint": mint or spl,
                            "explorer": f"https://solscan.io/tx/{sig}",
                            "matched_at": datetime.now(timezone.utc).isoformat(),
                            "note": "SPL match by mint+amount; confirm ATA ownership in production",
                        }
                        print(json.dumps(out))
                        return 0
        time.sleep(args.poll)

    print(
        json.dumps(
            {
                "ok": True,
                "status": "expired",
                "order_id": order_id,
                "timeout_sec": args.timeout,
                "matched_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
