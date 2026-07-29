# Showcase — Family shop Solana Pay terminal on ZeroClaw

## What it does
A **Tier-1** ZeroClaw use case: a small shop (WhatsApp / Telegram / Discord) takes orders, issues a **Solana Pay** transfer request URL, watches public Solana RPC for payment, and confirms in-chat.

**Who it's for:** family warung / micro-merchant who already chats with customers and wants crypto payment **without giving the agent custody**.

## ZeroClaw features used
- **Skills** (`skills/solana-pay-terminal/SKILL.md`) — durable instructions + custody rules
- **SOPs** (`solana-pay-order`, `solana-pay-watch`) — deterministic invoice + watch steps, HITL on high-value
- **Memory** — merchant pubkey, catalog, order state
- **HTTP / shell** — audited Python helpers only (no WASM plugin required)
- **Channels** — any ZeroClaw chat channel as the terminal UI

## What we built
| Artifact | Path |
|---|---|
| Skill | `skills/solana-pay-terminal/SKILL.md` |
| SOP: create invoice | `sops/solana-pay-order/` |
| SOP: watch payment | `sops/solana-pay-watch/` |
| Invoice builder | `scripts/create_invoice.py` |
| Payment watcher | `scripts/watch_payment.py` |
| Config snippet | `config/agent-snippet.toml` |
| Threat model | `docs/THREAT_MODEL.md` |
| Headless demo | `demo/run_demo.sh` |

## Custody tier & threat model
- **Tier 0–1 watch-only** — merchant receive pubkey in memory; **no private keys**
- See `docs/THREAT_MODEL.md`
- Hard caps + approval gates for refunds / over-notional

## Reproduce
```bash
git clone https://github.com/mamenesia/zeroclaw-solana-pay-terminal
cd zeroclaw-solana-pay-terminal

# Headless demo (no ZeroClaw binary required)
MERCHANT_PUBKEY=<your_receive_only_pubkey> ./demo/run_demo.sh

# On a ZeroClaw host (stock binary):
# 1) Copy skills/ + sops/ into workspace
# 2) Seed memory merchant.pubkey + catalog
# 3) Attach skill bundle; message the agent "1 kopi"
# 4) Pay the solana: URL from a phone wallet; agent confirms
```

## Demo video outline (≤3 min, for Discord #solana-bounty)
1. Terminal: run `demo/run_demo.sh` → show pay URL
2. Phone: open Solana Pay / wallet with URL (or QR)
3. Chat: customer order → invoice → ✅ paid with explorer link
4. Flash threat model: no keys on agent

## Why this is a use case (not a component)
Someone can run it **every day** as a shop terminal — chat → invoice → settlement signal → confirmation.
