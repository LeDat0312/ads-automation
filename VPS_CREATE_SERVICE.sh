#!/bin/bash
# Create systemd service for MetaUpdate backend

SERVICE_NAME="metaupdate"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PROJECT_DIR="/home/adsuser/ads-automation"
VENV_PYTHON="${PROJECT_DIR}/venv/bin/python"
USER="adsuser"
GROUP="adsuser"

echo "📝 Creating systemd service: ${SERVICE_NAME}"

# Create service file
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=MetaUpdate FastAPI Backend (Facebook Ads Automation)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=${USER}
Group=${GROUP}
WorkingDirectory=${PROJECT_DIR}

# Environment variables
Environment="PATH=${PROJECT_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=${PROJECT_DIR}/.env

# Start command - use venv python and uvicorn
ExecStart=${VENV_PYTHON} -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Restart policy
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true

# Resource limits
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created at: $SERVICE_FILE"
echo ""
echo "📋 Service file content:"
cat $SERVICE_FILE

echo ""
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo ""
echo "✅ Enabling service to start on boot..."
sudo systemctl enable ${SERVICE_NAME}

echo ""
echo "🚀 Starting service..."
sudo systemctl start ${SERVICE_NAME}

echo ""
echo "📊 Service status:"
sudo systemctl status ${SERVICE_NAME} --no-pager

echo ""
echo "✅ Service created and started!"
echo ""
echo "📝 Useful commands:"
echo "  - Check status:  sudo systemctl status ${SERVICE_NAME}"
echo "  - View logs:     sudo journalctl -u ${SERVICE_NAME} -f"
echo "  - Restart:       sudo systemctl restart ${SERVICE_NAME}"
echo "  - Stop:          sudo systemctl stop ${SERVICE_NAME}"
echo "  - Disable:       sudo systemctl disable ${SERVICE_NAME}"
