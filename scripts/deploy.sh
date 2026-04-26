#!/usr/bin/env bash
# Capacium GitHub App — Deployment Script
# Usage: ./scripts/deploy.sh [environment]
# Environment: production (default), staging
set -euo pipefail

ENV="${1:-production}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Capacium GitHub App Deploy: $ENV ==="

# 1. Verify configuration
if [ ! -f "$PROJECT_DIR/.env.$ENV" ]; then
    echo "ERROR: Missing .env.$ENV — copy .env.example and fill in values"
    echo "Required: GITHUB_WEBHOOK_SECRET, GITHUB_APP_ID, GITHUB_PRIVATE_KEY_PATH, EXCHANGE_API_URL"
    exit 1
fi

# 2. Source env file and verify required vars
source "$PROJECT_DIR/.env.$ENV"
: "${GITHUB_WEBHOOK_SECRET:?}"
: "${GITHUB_APP_ID:?}"
: "${GITHUB_PRIVATE_KEY_PATH:?}"
: "${EXCHANGE_API_URL:=https://api.capacium.xyz/v2}"

echo "  App ID: $GITHUB_APP_ID"
echo "  Exchange API: $EXCHANGE_API_URL"

# 3. Verify private key exists
if [ ! -f "$GITHUB_PRIVATE_KEY_PATH" ]; then
    echo "ERROR: Private key not found at $GITHUB_PRIVATE_KEY_PATH"
    exit 1
fi

# 4. Run tests before deploy
echo "--- Running tests ---"
cd "$PROJECT_DIR"
python3 -m pytest tests/ -v
echo "Tests passed."

# 5. Build Docker image
echo "--- Building Docker image ---"
TAG="capacium-github-app:$ENV-$(date +%Y%m%d-%H%M%S)"
docker build -t "$TAG" -t "capacium-github-app:latest" .

# 6. Start container (port 8080)
echo "--- Starting container ---"
docker rm -f "capacium-app-$ENV" 2>/dev/null || true
docker run -d \
    --name "capacium-app-$ENV" \
    --restart unless-stopped \
    -p 8080:8080 \
    -v "$(dirname "$GITHUB_PRIVATE_KEY_PATH"):/etc/capacium/keys:ro" \
    -e GITHUB_WEBHOOK_SECRET="$GITHUB_WEBHOOK_SECRET" \
    -e GITHUB_APP_ID="$GITHUB_APP_ID" \
    -e GITHUB_PRIVATE_KEY_PATH="/etc/capacium/keys/$(basename "$GITHUB_PRIVATE_KEY_PATH")" \
    -e EXCHANGE_API_URL="$EXCHANGE_API_URL" \
    "capacium-github-app:latest"

echo "=== Deploy complete: $ENV ==="
echo "  Container: capacium-app-$ENV"
echo "  Endpoint: http://localhost:8080/webhook"
