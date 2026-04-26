"""Configuration from environment variables."""
import os


def get_config():
    return {
        "webhook_secret": os.environ.get("GITHUB_WEBHOOK_SECRET", ""),
        "app_id": os.environ.get("GITHUB_APP_ID", ""),
        "private_key_path": os.environ.get("GITHUB_PRIVATE_KEY_PATH", ""),
        "exchange_api_url": os.environ.get("EXCHANGE_API_URL", "https://api.capacium.xyz/v2"),
        "port": int(os.environ.get("PORT", "8080")),
        "host": os.environ.get("HOST", "0.0.0.0"),
    }
