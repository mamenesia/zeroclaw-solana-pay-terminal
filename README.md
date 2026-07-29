# ZeroClaw × Solana Pay Terminal

Tier-1 **family shop payment terminal** for [ZeroClaw](https://github.com/zeroclaw-labs/zeroclaw): take an order on chat, issue a [Solana Pay](https://docs.solanapay.com/) transfer URL, watch public RPC, confirm in-channel.

**Custody:** watch-only merchant pubkey — the agent never holds keys.

Built for Superteam listing [*Build Solana-native plugins for Zeroclaw*](https://superteam.fun/earn/listing/zeroclaw) (**Global**). This is a **use case** on stock skills/SOPs/HTTP (Tier 1). Optional Tier-3 WASM plugin can wrap the same scripts later.

## Quick demo
```bash
# Use any receive-only mainnet pubkey you control
MERCHANT_PUBKEY=YourBase58Pubkey ./demo/run_demo.sh
```

## Layout
```
skills/solana-pay-terminal/SKILL.md
sops/solana-pay-order/
sops/solana-pay-watch/
scripts/create_invoice.py
scripts/watch_payment.py
config/agent-snippet.toml
docs/THREAT_MODEL.md
SHOWCASE.md
SUBMISSION.md
```

## License
MIT
