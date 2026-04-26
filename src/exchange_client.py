"""Exchange API client for Capacium GitHub App."""
import json
import urllib.request
import urllib.error


class ExchangeClient:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")

    def sync_listing(self, metadata: dict) -> dict:
        url = f"{self.api_url}/listings"
        data = json.dumps(metadata).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}", "body": e.read().decode()}
        except urllib.error.URLError as e:
            return {"error": str(e.reason)}

    def register_claim(self, claim: dict) -> dict:
        url = f"{self.api_url}/claims"
        data = json.dumps(claim).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}", "body": e.read().decode()}
        except urllib.error.URLError as e:
            return {"error": str(e.reason)}
