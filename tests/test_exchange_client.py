"""Tests for Exchange API client."""
import io
import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.exchange_client import ExchangeClient


class TestExchangeClient:
    def setup_method(self):
        self.client = ExchangeClient("https://api.capacium.xyz/v2")

    @patch("urllib.request.urlopen")
    def test_sync_listing_success(self, mock_urlopen):
        expected = {"id": "listing-123", "status": "created"}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(expected).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = self.client.sync_listing({"name": "test-capability"})
        assert result["status"] == "created"
        assert result["id"] == "listing-123"

    @patch("urllib.request.urlopen")
    def test_sync_listing_http_error(self, mock_urlopen):
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            "https://api.capacium.xyz/v2/listings",
            400,
            "Bad Request",
            {},
            io.BytesIO(b'{"error":"invalid"}'),
        )

        result = self.client.sync_listing({"name": "test-capability"})
        assert "error" in result
        assert "HTTP 400" in result["error"]

    @patch("urllib.request.urlopen")
    def test_register_claim_success(self, mock_urlopen):
        expected = {"id": "claim-456", "status": "pending"}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(expected).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = self.client.register_claim({"repo": "owner/repo"})
        assert result["status"] == "pending"

    @patch("urllib.request.urlopen")
    def test_register_claim_network_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        result = self.client.register_claim({"repo": "owner/repo"})
        assert "error" in result
        assert "Connection refused" in result["error"]


if __name__ == "__main__":
    import io
    t = TestExchangeClient()
    t.setup_method()
    for method_name in dir(t):
        if method_name.startswith("test_"):
            getattr(t, method_name)()
            print(f"{method_name} passed!")
