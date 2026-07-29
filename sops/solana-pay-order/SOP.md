# solana-pay-order

## Steps

1. **Recall merchant** — Load `merchant.pubkey`, catalog, caps from memory.
   - tools: memory_recall

2. **Build invoice** — Run audited `scripts/create_invoice.py` for the resolved line item.
   - tools: shell

3. **Persist order** — Store `orders.<id>` with status `invoiced`, amount, sku, invoice path.
   - tools: memory_store

4. **Notify channel** — Send Solana Pay URL + order id to the customer thread.
   - tools: channel_reply

5. **Hand off to watch** — Execute or schedule `solana-pay-watch` for this order id.
   - tools: sop_execute
