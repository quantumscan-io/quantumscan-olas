"""HTTP client for QuantumScan's agent-facing endpoints.

Three ways to pay, tried in this order:

  1. wallet_private_key given -> real x402 micropayment (autonomous, no signup,
     a fraction of a cent in USDC on Base per call)
  2. api_key given -> prepaid credits (free at POST /api/agent/register)
  3. neither given -> plain requests, relies on QuantumScan's small free
     daily trial per IP (fine for testing, not for production agents)
"""

from __future__ import annotations

import os
from typing import Any, Optional

import requests

DEFAULT_BASE_URL = "https://quantumscan.io"
DEFAULT_NETWORK = "eip155:8453"  # Base mainnet, CAIP-2 format used by x402 v2
MAX_AUTO_PAY_ATOMIC = 50_000  # $0.05 USDC (6 decimals) cap per call


class QuantumScanPaymentRequired(Exception):
    """Raised when a call needs payment and none of the 3 payment modes is configured."""


class QuantumScanClient:
    def __init__(
        self,
        wallet_private_key: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.wallet_private_key = wallet_private_key or os.environ.get(
            "QUANTUMSCAN_WALLET_PRIVATE_KEY"
        )
        self.api_key = api_key or os.environ.get("QUANTUMSCAN_API_KEY")
        self.base_url = base_url or os.environ.get("QUANTUMSCAN_API_URL") or DEFAULT_BASE_URL
        self._session = self._build_session()

    @property
    def payment_mode(self) -> str:
        if self.wallet_private_key:
            return "x402"
        if self.api_key:
            return "api-key"
        return "free-trial"

    def _build_session(self) -> requests.Session:
        session = requests.Session()

        if self.wallet_private_key:
            # x402 auto-pay path. Imported lazily so `requests`-only users
            # (relying on api_key or free trial) don't need eth_account/x402.
            from eth_account import Account
            from x402 import x402ClientSync
            from x402.http.clients import wrapRequestsWithPayment
            from x402.mechanisms.evm.exact import ExactEvmScheme

            signer = Account.from_key(self.wallet_private_key)
            x402_client = x402ClientSync()
            x402_client.register(DEFAULT_NETWORK, ExactEvmScheme(signer=signer))
            wrapRequestsWithPayment(session, x402_client)
        elif self.api_key:
            session.headers["X-API-Key"] = self.api_key

        return session

    def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        url = f"{self.base_url}{path}"
        res = self._session.request(method, url, timeout=30, **kwargs)

        if res.status_code == 402:
            raise QuantumScanPaymentRequired(
                "QuantumScan requires payment for this call. Pass wallet_private_key "
                "(autonomous micropayment) or api_key (free at "
                f"{self.base_url}/api/agent/register) to QuantumScanClient()."
            )
        res.raise_for_status()
        return res.json()

    def check_transaction_safety(
        self, address: str, calldata: str = "0x", network: int = 1
    ) -> dict:
        """Pre-flight check for a single transaction before signing it.

        Returns a dict with at least {"verdict": "safe"|"caution"|"block", "safe": bool}.
        """
        result = self._request(
            "POST",
            "/api/scan/transaction",
            json={"address": address, "calldata": calldata, "network": network},
        )
        verdict = result.get("verdict", "unknown")
        result["safe"] = verdict == "safe"
        return result

    def check_contract_safety(self, address: str, network: int = 1) -> dict:
        """Full QuantumScan scan of a contract: source verification, scam
        patterns, post-quantum cryptography risk. Returns riskScore + agentDecision.
        """
        return self._request(
            "GET", f"/api/scan/contract?address={address}&network={network}"
        )
