"""QuantumScan client for Olas (Autonolas) autonomous agents.

Designed to be called from any Olas skill/behaviour (open-autonomy FSM apps)
or any other Python-based autonomous agent — it's a plain HTTP client, no
Autonolas-specific dependencies required beyond what you already have.

Usage inside a skill/behaviour:

    from quantumscan_olas import QuantumScanClient

    client = QuantumScanClient(wallet_private_key=self.params.quantumscan_wallet_key)
    result = client.check_transaction_safety(address="0x...", calldata="0x...", network=8453)
    if not result["safe"]:
        # abort the transaction — do not submit to the safe/multisig
        ...
"""

from .client import QuantumScanClient

__all__ = ["QuantumScanClient"]
__version__ = "0.1.0"
