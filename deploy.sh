#!/bin/bash

# Deployment script for Facebook Ads Automation System
# Usage: ./deploy.sh

set -e

echo "🚀 Starting deployment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3.11 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    echo "🗄️ Running database migrations..."
    alembic upgrade head
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found!"
    echo "📝 Creating .env from env.example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env file. Please edit it with your actual values."
        echo "   Run: nano .env"
    else
        echo "❌ Error: env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Restart service (if using systemd)
if systemctl is-active --quiet facebook-ads-api; then
    echo "🔄 Restarting service..."
    sudo systemctl restart facebook-ads-api
    
    # Wait a bit for service to start
    sleep 2
    
    # Check status
    echo "✅ Checking service status..."
    sudo systemctl status facebook-ads-api --no-pager -l
else
    echo "⚠️ Service 'facebook-ads-api' is not running or not installed."
    echo "   To setup systemd service, see: AWS_LIGHTSAIL_SETUP_GUIDE.md"
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Check service logs: sudo journalctl -u facebook-ads-api -f"
echo "   2. Test API: curl http://localhost:8000/docs"
echo "   3. Check status: sudo systemctl status facebook-ads-api"


