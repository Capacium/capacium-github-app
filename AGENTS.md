# Capacium GitHub App — Agents Guide

## Language
**English is REQUIRED for ALL Capacium content.**

## Project
GitHub App webhook server that detects `capability.yaml` repos and syncs metadata to Capacium Exchange.

## Tech Stack
- Python 3.12+ (stdlib `http.server` — no framework)
- Docker deployment
- Single dependency: `capacium>=0.7.0`

## Key Files
| File | Purpose |
|------|---------|
| `app.py` | Webhook server, event routing |
| `config.py` | Configuration (no env vars) |
| `discovery.py` | Repository discovery logic |
| `claim.py` | Claim/prep workflow |
| `requirements.txt` | Single line: `capacium>=0.7.0` |
| `Dockerfile` | Container build |

## Events Handled
- `push` / `release` — detect changed `capability.yaml` files
- `installation` — register repos, scan for capability manifests

## Deployment
```bash
docker build -t capacium-github-app .
docker run -e GITHUB_APP_ID=... -e GITHUB_APP_PRIVATE_KEY=... capacium-github-app
```

Config via `config.py` constants (not environment variables).
