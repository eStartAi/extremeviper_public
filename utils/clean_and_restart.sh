#!/bin/bash
# =====================================================
# 🧹 ExtremeViper Cleaner + Safe Restart Utility
# v1.2 — includes Broker Audit Check before restart
# =====================================================

SERVICE_NAME="extremeviper.service"
PROJECT_DIR="$HOME/extremeviper"
UTILS_DIR="$PROJECT_DIR/utils"
BROKERS_DIR="$PROJECT_DIR/brokers"
AUDIT_SCRIPT="$UTILS_DIR/check_brokers.py"

echo "🚀 Starting ExtremeViper Cleanup & Restart..."
sleep 1

# --- Step 1: Clear Python caches ---
echo "🧹 Removing __pycache__ directories..."
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✅ Cache cleared."

# --- Step 2: Verify broker core functions (via audit script) ---
if [ -f "$AUDIT_SCRIPT" ]; then
  echo ""
  echo "🔍 Running Broker Audit..."
  python3 "$AUDIT_SCRIPT"
  AUDIT_STATUS=$?
  echo "-----------------------------------------"
  if [ $AUDIT_STATUS -ne 0 ]; then
    echo "⚠️  Broker audit detected missing definitions — please review before restart."
    read -p "Continue anyway? (y/N): " CONT
    [[ "$CONT" =~ ^[Yy]$ ]] || exit 1
  fi
else
  echo "⚠️ Broker audit script not found; skipping verification."
fi

# --- Step 3: Manual function scan fallback ---
echo ""
echo "🔍 Double-checking broker files..."
for f in "$BROKERS_DIR"/*.py; do
  [ -f "$f" ] || continue
  echo "-----------------------------------------"
  echo "📄 Checking $(basename "$f")"
  if grep -Eq "def (fetch_candles|get_price|place_order|ping|get_balance)" "$f"; then
    echo "✅ $(basename "$f") has all core functions."
  else
    echo "⚠️ Warning: Some core functions missing in $(basename "$f")"
  fi
done
echo "-----------------------------------------"
echo "✅ Broker integrity check complete."

# --- Step 4: Restart systemd service ---
echo ""
echo "♻️ Restarting $SERVICE_NAME ..."
sudo systemctl restart "$SERVICE_NAME"

# --- Step 5: Stream logs live ---
echo ""
echo "📜 Streaming logs for $SERVICE_NAME (Ctrl+C to exit)"
sudo journalctl -fu "$SERVICE_NAME"

