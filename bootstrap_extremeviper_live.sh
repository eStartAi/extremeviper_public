#!/bin/bash

echo "🔐 Step 1: Validating .env file..."
source .venv/bin/activate
python3 utils/validate_env.py
if [ $? -ne 0 ]; then
  echo "❌ Environment validation failed. Fix .env before proceeding."
  exit 1
fi

echo "📦 Step 2: Creating backup..."
timestamp=$(date +'%Y%m%d_%H%M%S')
mkdir -p backups
tar -czf backups/backup_${timestamp}.tar.gz . --exclude=backups --exclude=.venv

echo "✅ Backup saved to: backups/backup_${timestamp}.tar.gz"

echo "🧪 Step 3: Activating virtual environment..."
source .venv/bin/activate

echo "🚀 Step 4: Restarting ExtremeViper systemd service..."
sudo systemctl daemon-reexec
sudo systemctl restart extremeviper.service
sleep 3

echo "📊 Step 5: Showing live logs (Press CTRL+C to stop tailing)"
sudo journalctl -u extremeviper.service -f
