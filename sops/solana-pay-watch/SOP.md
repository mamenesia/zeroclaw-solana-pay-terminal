# solana-pay-watch

## Steps

1. **Load invoice** — Read order id + invoice JSON path from run context / memory.
   - tools: memory_recall

2. **Watch payment** — Run `scripts/watch_payment.py` with timeout (default 180s).
   - tools: shell

3. **Update state** — Mark order `paid` or `expired` in memory.
   - tools: memory_store

4. **Notify** — Confirm with signature + explorer link, or invite re-issue on timeout.
   - tools: channel_reply

5. **High-value gate** — If paid amount exceeds shop soft-cap anomaly, flag for human review (do not move funds).
   - tools: memory_store
   - requires_confirmation: true
