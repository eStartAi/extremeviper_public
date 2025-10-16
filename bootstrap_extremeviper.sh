#!/bin/bash

echo "🚀 Bootstrapping ExtremeViper Bot..."

# Step 1: Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Step 2: Create .env from example if missing
if [ ! -f .env ]; then
  echo "📄 .env not found — copying from .env.example..."
  cp .env.example .env
fi

# Step 3: Auto-generate WEBHOOK_SECRET if missing
echo "🔐 Checking for WEBHOOK_SECRET..."
SECRET_LINE=$(grep '^WEBHOOK_SECRET=' .env || echo "")

if [[ -z "$SECRET_LINE" ]] || [[ "$SECRET_LINE" =~ ^WEBHOOK_SECRET=$ ]] || [[ "$SECRET_LINE" =~ ^WEBHOOK_SECRET=[[:space:]]*$ ]]; then
  echo "🔐 Generating secure WEBHOOK_SECRET..."
  RANDOM_SECRET=$(openssl rand -hex 16)
  if grep -q '^WEBHOOK_SECRET=' .env; then
    sed -i "s|^WEBHOOK_SECRET=.*|WEBHOOK_SECRET=$RANDOM_SECRET|" .env
  else
    echo "WEBHOOK_SECRET=$RANDOM_SECRET" >> .env
  fi
  echo "✅ WEBHOOK_SECRET generated and set in .env"
else
  echo "✅ Valid WEBHOOK_SECRET found. Skipping generation."
fi

# Step 4: Validate environment variables
echo "🔎 Validating .env variables..."
python3 utils/validate_env.py || {
  echo "🛑 Environment validation failed. Fix .env before proceeding."
  exit 1
}

# Step 5: Auto-launch systemd services per broker
echo "🧠 Starting broker services based on ENABLED_BROKERS..."

# Read brokers list from .env
ENABLED_BROKERS=$(grep '^ENABLED_BROKERS=' .env | cut -d '=' -f2 | tr -d ' ')
IFS=',' read -ra BROKERS <<< "$ENABLED_BROKERS"

for broker in "${BROKERS[@]}"; do
  SERVICE_NAME="extremeviper-${broker}.service"
  echo "🔁 Enabling & starting: $SERVICE_NAME"
  sudo systemctl enable $SERVICE_NAME
  sudo systemctl restart $SERVICE_NAME
  sleep 1
  STATUS=$(systemctl is-active $SERVICE_NAME)
  echo "  ⏱️  Status: $STATUS"
done

echo "✅ All brokers started. Use 'systemctl status extremeviper-*.service' to monitor."
# ✅ All brokers started. Use 'systemctl status extremeviper-*.service' to monitor.

# === Sync .env.example from real .env ===
echo "🧼 Generating clean .env.example..."
python3 utils/generate_env_example.py || echo "⚠️ Skipped: .env not found"
echo "🧼 Generating clean .env.example (safe mode)..."
python3 utils/generate_env_example.py --safe || echo "⚠️ Skipped: .env not found"
