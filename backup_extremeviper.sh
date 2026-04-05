#!/bin/bash

# backup_extremeviper.sh
# 🔁 Auto-backup for ExtremeViper (Private + Public GitHub + Local Archive)

set -e

PROJECT_NAME="extremeviper"
PROJECT_DIR="$HOME/$PROJECT_NAME"
BACKUP_DIR="$HOME/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVE_NAME="${PROJECT_NAME}_backup_${TIMESTAMP}.tar.gz"

cd "$PROJECT_DIR"

echo "🧠 [1/6] Generating safe .env.example..."
source .venv/bin/activate
python3 generate_env_example.py

echo "📦 [2/6] Creating .tar.gz archive..."
mkdir -p "$BACKUP_DIR"
tar --exclude='.env' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='*.pyc' \
    --exclude='backups' \
    --exclude='.git' \
    -czf "$BACKUP_DIR/$ARCHIVE_NAME" .

echo "✅ Archive saved to: $BACKUP_DIR/$ARCHIVE_NAME"

echo "📝 [3/6] Git add & commit changes..."
git add .
git commit -m "📦 [Backup] Synced DRYRUNmain + env.example @ $TIMESTAMP" || echo "⚠️ Nothing to commit."

echo "🔐 [4/6] Pushing to PRIVATE repo..."
git push origin main || echo "❌ Failed to push to origin."

if git remote | grep -q "public"; then
  echo "🌍 [5/6] Pushing to PUBLIC mirror..."
  git push public main || echo "⚠️ Failed to push to public mirror."
else
  echo "ℹ️ No 'public' remote found. Skipping."
fi

echo "✅ [6/6] Backup complete. All systems synced."

