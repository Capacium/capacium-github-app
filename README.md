# Capacium GitHub App

[![CI](https://github.com/Capacium/capacium-github-app/actions/workflows/ci.yml/badge.svg)](https://github.com/Capacium/capacium-github-app/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)

GitHub App that syncs capability metadata from GitHub repositories to the Capacium Exchange.

## Architecture

```
GitHub (push/release/webhook)
  │
  ▼
Capacium GitHub App (Python stdlib http.server)
  │
  ├── detect capability.yaml changes
  ├── scan repos for capability manifests
  │
  ▼
Capacium Exchange API (v2)
  │
  ├── sync listings
  └── register publisher claims
```

The app listens for GitHub webhook events (`push`, `release`, `installation`), detects repositories containing `capability.yaml` manifests, and syncs their metadata to the Capacium Exchange.

## Setup

### 1. Create a GitHub App

1. Go to **Settings → Developer settings → GitHub Apps → New GitHub App**
2. Set name: `Capacium Sync` (or your preferred name)
3. Set webhook URL: `https://your-domain.com/webhook`
4. Set webhook secret (generate with `openssl rand -hex 32`)
5. Set permissions (matching `app.yml`):
   - Contents: **Read-only**
   - Metadata: **Read-only**
   - ID Token: **Write**
   - Attestations: **Read**
6. Subscribe to events: `push`, `release`, `create`, `installation`, `installation_repositories`
7. Generate a private key and save it
8. Install the app on your repositories

### 2. Deploy

Deploy with Docker:

```bash
docker build -t capacium-github-app .
docker run -d \
  -e GITHUB_WEBHOOK_SECRET=your-secret \
  -e GITHUB_APP_ID=your-app-id \
  -e GITHUB_PRIVATE_KEY_PATH=/app/key.pem \
  -e EXCHANGE_API_URL=https://api.capacium.xyz/v2 \
  -p 8080:8080 \
  -v /path/to/private-key.pem:/app/key.pem \
  capacium-github-app
```

Or run directly:

```bash
pip install -r requirements.txt
GITHUB_WEBHOOK_SECRET=your-secret GITHUB_APP_ID=1234 python3 src/server.py
```

### 3. Configure Webhook

Point your GitHub App's webhook URL to your deployed instance. The app verifies signatures using the webhook secret.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_WEBHOOK_SECRET` | `""` | Secret for verifying webhook payloads |
| `GITHUB_APP_ID` | `""` | GitHub App ID |
| `GITHUB_PRIVATE_KEY_PATH` | `""` | Path to the app's private key file |
| `EXCHANGE_API_URL` | `https://api.capacium.xyz/v2` | Capacium Exchange API base URL |
| `PORT` | `8080` | Server listen port |
| `HOST` | `0.0.0.0` | Server listen host |

## Development

```bash
# Install
pip install -r requirements.txt

# Run tests
python3 -m pytest tests/ -v

# Run server locally
GITHUB_WEBHOOK_SECRET=dev-secret python3 src/server.py
```

### Triggering Events Locally

Use `curl` to simulate webhook events:

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-Hub-Signature-256: sha256=..." \
  -d '{"repository":{"full_name":"owner/repo"},"ref":"refs/heads/main","commits":[{"added":["capability.yaml"],"modified":[],"removed":[]}]}'
```
