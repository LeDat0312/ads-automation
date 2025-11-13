#!/bin/bash
# Script để setup Telegram webhook với secret_token
# Sử dụng: ./scripts/setup_webhook.sh

set -e

echo "🔧 Setting up Telegram webhook..."

# Activate virtual environment
cd ~/ads-automation
source venv/bin/activate

# Lấy thông tin từ .env
echo "📋 Reading configuration from .env..."
BOT_TOKEN=$(python -c "from app.core.config import get_settings; print(get_settings().TELEGRAM_BOT_TOKEN)")
WEBHOOK_SECRET=$(python -c "from app.core.config import get_settings; print(get_settings().TELEGRAM_WEBHOOK_SECRET)")
WEBHOOK_URL=$(python -c "from app.core.config import get_settings; print(get_settings().WEBHOOK_URL)")

if [ -z "$BOT_TOKEN" ] || [ -z "$WEBHOOK_SECRET" ] || [ -z "$WEBHOOK_URL" ]; then
    echo "❌ Error: Missing configuration in .env"
    echo "   BOT_TOKEN: ${BOT_TOKEN:+SET}${BOT_TOKEN:-NOT SET}"
    echo "   WEBHOOK_SECRET: ${WEBHOOK_SECRET:+SET}${WEBHOOK_SECRET:-NOT SET}"
    echo "   WEBHOOK_URL: ${WEBHOOK_URL:+SET}${WEBHOOK_URL:-NOT SET}"
    exit 1
fi

echo "✅ Configuration loaded:"
echo "   WEBHOOK_URL: $WEBHOOK_URL"
echo "   BOT_TOKEN: ${BOT_TOKEN:0:20}..."
echo "   WEBHOOK_SECRET: ${WEBHOOK_SECRET:0:20}..."

# Setup webhook với secret_token
echo ""
echo "🔄 Setting up webhook..."
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"${WEBHOOK_URL}\",
    \"secret_token\": \"${WEBHOOK_SECRET}\",
    \"allowed_updates\": [\"message\"],
    \"drop_pending_updates\": true
  }")

echo "$RESPONSE" | python -m json.tool

# Check result
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo ""
    echo "✅ Webhook setup successfully!"
else
    echo ""
    echo "❌ Failed to setup webhook"
    exit 1
fi

# Verify webhook
echo ""
echo "🔍 Verifying webhook..."
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | python -m json.tool

echo ""
echo "✅ Done!"



