#!/bin/bash
# ============================================================
# setup_ollama.sh — Install Ollama and pull a default model
# ============================================================

set -e

DEFAULT_MODEL=devstral-small-2

echo ""
echo "================================================"
echo "  Ollama Local Environment Setup"
echo "================================================"
echo ""

# ── Detect OS ──────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "[1/4] Detected OS: $OS ($ARCH)"

# ── Install Ollama ─────────────────────────────────
echo ""
echo "[2/4] Installing Ollama..."

if command -v ollama &> /dev/null; then
  CURRENT_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
  echo "      ✓ Ollama already installed ($CURRENT_VERSION)"
else
  if [[ "$OS" == "Darwin" || "$OS" == "Linux" ]]; then
    echo "      Installing via official script..."
    curl -fsSL https://ollama.com/install.sh | sh >/dev/null
  else
    echo "      ✗ Unsupported OS: $OS"
    echo "        Please install manually from https://ollama.com/download"
    exit 1
  fi
  echo "      ✓ Ollama installed"
fi

# ── Install Python client ──────────────────────────
echo ""
echo "[3/4] Installing Ollama Python client..."
uv pip install ollama --quiet
echo "      ✓ ollama Python package installed"

# ── Pull default model ─────────────────────────────
echo ""
echo "[4/4] Pulling default model: $DEFAULT_MODEL"
echo "      (This may take a few minutes on first run)"
echo ""

# Ensure ollama service is running
if [[ "$OS" == "Linux" ]]; then
  sudo systemctl enable --now ollama 2>/dev/null || ollama serve &>/dev/null &
  sleep 2
fi
sleep 2
ollama run $DEFAULT_MODEL
echo ""
echo "      ✓ Model '$DEFAULT_MODEL' ready for messages"

echo ""
echo "================================================"
echo "  Ollama setup complete!"
echo ""
echo "  Useful commands:"
echo "    ollama serve              # Start the server"
echo "    ollama list               # List local models"
echo "    ollama pull <model>       # Download a model"
echo "    ollama run <model>        # Chat interactively"
echo ""
echo "  Run: python scripts/verify_ollama.py"
echo "================================================"
echo ""
