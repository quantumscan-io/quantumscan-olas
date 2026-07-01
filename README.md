# quantumscan-olas

QuantumScan client for [Olas (Autonolas)](https://olas.network) skills and other Python-based autonomous agents — pre-transaction safety checks and contract scans, billed per call.

Not a heavyweight Autonolas FSM component — it's a plain HTTP client any skill/behaviour can import. Wire it into your `Behaviour.act()` before submitting a transaction to the Safe/multisig.

## Install

```bash
pip install quantumscan-olas
# or, with autonomous x402 micropayments:
pip install "quantumscan-olas[x402]"
```

## Usage

```python
from quantumscan_olas import QuantumScanClient

client = QuantumScanClient(
    wallet_private_key=self.params.quantumscan_wallet_key,  # optional, see below
)

result = client.check_transaction_safety(address="0x...", calldata="0x...", network=8453)
if not result["safe"]:
    self.context.logger.warning(f"QuantumScan blocked tx: {result.get('reason')}")
    return  # do not submit to the Safe

contract_scan = client.check_contract_safety(address="0x...", network=8453)
```

## Paying for calls

Three modes, checked in this order:

1. **`wallet_private_key`** (recommended — install with `[x402]` extra) — pays a fraction of a cent in USDC per call via the [x402 protocol](https://x402.org), automatically, capped at $0.05/call.
2. **`api_key`** — prepaid credits, free at `POST https://quantumscan.io/api/agent/register`.
3. **Neither** — falls back to QuantumScan's small free daily trial per IP. Fine for development.

Both can also be set via environment variables: `QUANTUMSCAN_WALLET_PRIVATE_KEY`, `QUANTUMSCAN_API_KEY`, `QUANTUMSCAN_API_URL`.

## Status

This is a plain Python HTTP client, tested and published independently of the Autonolas package registry. A registered Autonolas component (with an on-chain IPFS package hash, for use via `autonomy packages add`) is a natural next step once there's real usage — open an issue if that's what you need.

## License

MIT
