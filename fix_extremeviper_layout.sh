#!/bin/bash
# ============================================================
# 🚀 ExtremeViper One-Click Recovery & Auto-Launch
# Fixes structure → validates .env → starts live bot
# Safe to run anytime
# ============================================================

set -e
cd ~/extremeviper || { echo "❌ Folder ~/extremeviper not found."; exit 1; }

echo "🔧 Checking ExtremeViper folder structure..."

mkdir -p control logs utils

# --- Move misplaced files ---
for file in main.py requirements.txt bootstrap_extremeviper_live.sh; do
  if [ -f "logs/$file" ]; then
    echo "→ Moving $file from logs/ to root..."
    mv "logs/$file" .
  fi
done

# --- Ensure .env exists ---
if [ ! -f ".env" ]; then
  if [ -f "control/.env.example" ]; then
    echo "→ Copying control/.env.example → .env"
    cp control/.env.example .env
  else
    echo "⚠️ No .env or .env.example found — please create one manually."
  fi
else
  echo "✅ .env already present."
fi

# --- Ensure Python package marker ---
[ -f "utils/__init__.py" ] || { echo "→ Creating utils/__init__.py"; touch utils/__init__.py; }

# --- Ensure control flags exist ---
for f in kill.flag stop_today.flag; do
  [ -f "control/$f" ] || { echo "→ Creating control/$f"; touch "control/$f"; }
done

# --- Show current layout ---
echo "✅ Layout fix complete."
echo "📂 Structure overview:"
ls -R --group-directories-first | sed 's/^/   /'

# --- Validate environment ---
echo
echo "🔍 Validating .env..."
if python3 utils/validate_env.py; then
  echo "✅ Environment validated successfully!"
else
  echo "❌ Validation failed — please fix your .env before continuing."
  exit 1
fi

# --- Start the bot ---
echo
echo "🚀 Launching ExtremeViper Live Mode..."
if [ -x "./bootstrap_extremeviper_live.sh" ]; then
  ./bootstrap_extremeviper_live.sh
else
  echo "⚠️ bootstrap_extremeviper_live.sh not found or not executable."
  echo "   Make sure it’s in root and run: chmod +x bootstrap_extremeviper_live.sh"
  exit 1
fi

echo
echo "🎯 All done — ExtremeViper is now LIVE and auto-recovered!"
