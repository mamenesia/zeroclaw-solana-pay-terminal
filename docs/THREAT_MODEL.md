# Threat model — Solana Pay Terminal (ZeroClaw Tier 1)

## Custody tier
**Tier 0–1: watch-only merchant pubkey.** The agent never holds a private key.

## Assets
- Merchant receive address (public)
- Order metadata in agent memory
- Channel messages (customer PII risk)

## Trust boundaries
| Component | Trust |
|---|---|
| ZeroClaw host OS | Trusted operator machine |
| Skill scripts | Audited, fixed paths |
| Public Solana RPC | Untrusted — can lie/censor; pin multiple RPCs in production |
| Customer wallet | Untrusted |
| Chat channel | Untrusted input |

## Threats & mitigations
1. **Agent steals funds** — Impossible without key. No signer in process.
2. **Fake paid notification** — Watch script requires matching tx via RPC; human verifies explorer link.
3. **Prompt injection via chat** — Skill forbids key handling / trading; SOP approval on refunds and over-cap.
4. **Invoice amount tampering** — Amount from catalog memory, not free-form customer string alone.
5. **RPC eclipse** — Optional multi-RPC quorum (extension); demo uses one public endpoint.
6. **SPL ATA confusion** — Production should derive ATA for merchant+mint; script notes limitation.

## Explicit non-goals
- Autonomous trading / sniping
- Custodial hot wallet
- Gas sponsorship by agent
