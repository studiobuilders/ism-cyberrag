#!/bin/bash
# ============================================================
# setup_clearml.sh — Configure ClearML experiment workspace
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/.env"
CLEARML_CONF="$HOME/clearml.conf"

echo ""
echo "================================================"
echo "  ClearML Experiment Workspace Setup"
echo "================================================"
echo ""

# ── Install ClearML ────────────────────────────────
echo "[1/3] Installing ClearML Python SDK..."
uv pip install clearml python-dotenv --quiet
echo "      ✓ clearml installed"

# ── Prompt for credentials ─────────────────────────
echo ""
echo "[2/3] ClearML Credentials"
echo "      Get your credentials at:"
echo "      https://app.clear.ml → Settings → Workspace → Create new credentials"
echo ""
read -rp  "      Access Key: " CLEARML_API_ACCESS_KEY
read -rsp "      Secret Key (input hidden): " CLEARML_API_SECRET_KEY
echo ""

if [[ -z "$CLEARML_API_ACCESS_KEY" || -z "$CLEARML_API_SECRET_KEY" ]]; then
  echo "      ✗ Access key or secret key missing. Exiting."
  exit 1
fi

# ── Write clearml.conf ─────────────────────────────
echo ""
echo "[3/3] Writing configuration..."

cat > "$CLEARML_CONF" <<EOF
api {
    web_server:https://app.clear.ml/
    api_server:https://api.clear.ml
    files_server:https://files.clear.ml
    credentials {
        "access_key" = "$CLEARML_API_ACCESS_KEY"
        "secret_key"  = "$CLEARML_API_SECRET_KEY"
    }
}
EOF

echo "      ✓ Config written to ~/clearml.conf"

# Also persist to .env for Python dotenv usage
update_env() {
  local key="$1"
  local value="$2"
  if [[ -f "$ENV_FILE" ]]; then
    if grep -q "^${key}=" "$ENV_FILE"; then
      sed -i.bak "s|^${key}=.*|${key}=${value}|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
    else
      echo "${key}=${value}" >> "$ENV_FILE"
    fi
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

update_env "CLEARML_API_ACCESS_KEY" "$CLEARML_API_ACCESS_KEY"
update_env "CLEARML_API_SECRET_KEY" "$CLEARML_API_SECRET_KEY"

echo "      ✓ Keys also saved to .env"

echo ""
echo "================================================"
echo "  ClearML setup complete!"
echo "  Run: python scripts/verify_clearml.py"
echo "================================================"
echo ""
