#!/bin/bash

echo "🧹 Starting ExtremeViper Cleanup..."

cd ~/extremeviper || { echo "❌ Folder not found"; exit 1; }

# === Move flag files ===
echo "📦 Moving kill.flag and mode.flag to control/"
mkdir -p control
[ -f utils/kill.flag ] && mv utils/kill.flag control/kill.flag
[ -f utils/mode.flag ] && mv utils/mode.flag control/mode.flag

# === Remove unnecessary or duplicate files ===
declare -a REMOVE_FILES=(
  "main.py.save"
  "README.md"
  "notify.py"
  ".env.example.bak"
)

for file in "${REMOVE_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "🗑️ Removing: $file"
    rm -f "$file"
  fi
done

# === Optional: Move test/dev files to a test folder ===
mkdir -p tests
if [ -f test_env.py ]; then
  mv test_env.py tests/
  echo "📁 Moved: test_env.py → tests/"
fi
if [ -f utils/test_oanda_key.py ]; then
  mv utils/test_oanda_key.py tests/
  echo "📁 Moved: utils/test_oanda_key.py → tests/"
fi

# === Log cleanup ===
LOGS=("logs/live_service_error.log" "logs/dryrun_service_error.log")

for logfile in "${LOGS[@]}"; do
  if [ -f "$logfile" ]; then
    echo "🧼 Truncating large log: $logfile"
    cp "$logfile" "$logfile.bak.$(date +%F_%H-%M-%S)"
    > "$logfile"
  fi
done

echo "✅ Cleanup complete!"
