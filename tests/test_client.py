from quantumscan_olas import QuantumScanClient


def test_default_payment_mode_is_free_trial(monkeypatch):
    monkeypatch.delenv("QUANTUMSCAN_WALLET_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("QUANTUMSCAN_API_KEY", raising=False)
    client = QuantumScanClient()
    assert client.payment_mode == "free-trial"
    assert client.base_url == "https://quantumscan.io"


def test_api_key_payment_mode():
    client = QuantumScanClient(api_key="qs_testkey")
    assert client.payment_mode == "api-key"
    assert client._session.headers["X-API-Key"] == "qs_testkey"


def test_custom_base_url(monkeypatch):
    monkeypatch.setenv("QUANTUMSCAN_API_URL", "https://staging.quantumscan.io")
    client = QuantumScanClient()
    assert client.base_url == "https://staging.quantumscan.io"
