#!/bin/bash
# ============================================================
# setup_groq.sh — Configure Groq API access
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/.env"

echo ""
echo "================================================"
echo "  Groq API Setup"
echo "================================================"
echo ""

# Install Python SDK
echo "[1/3] Installing Groq Python SDK..."
uv pip install groq python-dotenv --quiet
echo "      ✓ groq installed"

# Prompt for API key
echo ""
echo "[2/3] Groq API Key Setup"
echo "      Get your key at: https://console.groq.com/keys"
echo ""
read -rsp "      Paste your GROQ_API_KEY (input hidden): " GROQ_API_KEY
echo ""

if [[ -z "$GROQ_API_KEY" ]]; then
  echo "      ✗ No key provided. Exiting."
  exit 1
fi

# Write to .env
echo ""
echo "[3/3] Saving API key to .env..."

if [[ -f "$ENV_FILE" ]]; then
  # Update existing key if present
  if grep -q "^GROQ_API_KEY=" "$ENV_FILE"; then
    sed -i.bak "s|^GROQ_API_KEY=.*|GROQ_API_KEY=$GROQ_API_KEY|" "$ENV_FILE"
    rm -f "$ENV_FILE.bak"
  else
    echo "GROQ_API_KEY=$GROQ_API_KEY" >> "$ENV_FILE"
  fi
else
  echo "GROQ_API_KEY=$GROQ_API_KEY" > "$ENV_FILE"
fi

echo "      ✓ Key saved to .env"
echo ""
echo "================================================"
echo "  Groq setup complete!"
echo "  Run: python scripts/verify_groq.py"
echo "================================================"
echo ""
