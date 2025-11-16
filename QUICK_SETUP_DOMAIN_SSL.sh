#!/bin/bash
# Quick setup script for Domain & SSL
# Domain: updatemetaads.site
# IP: 54.179.208.122

set -e

echo "🚀 Starting Domain & SSL Setup..."
echo "Domain: updatemetaads.site"
echo "IP: 54.179.208.122"
echo ""

# Step 1: Install Nginx
echo "📦 Step 1: Installing Nginx..."
sudo apt update
sudo apt install -y nginx

# Step 2: Install Certbot
echo "📦 Step 2: Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Step 3: Configure Firewall
echo "🔥 Step 3: Configuring Firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable
sudo ufw status

# Step 4: Check DNS
echo "🌐 Step 4: Checking DNS..."
DNS_IP=$(dig +short updatemetaads.site)
if [ "$DNS_IP" == "54.179.208.122" ]; then
    echo "✅ DNS is correct: $DNS_IP"
else
    echo "⚠️  DNS may not be propagated yet: $DNS_IP"
    echo "   Expected: 54.179.208.122"
    echo "   Please wait 5-60 minutes and check again"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 5: Create Nginx config
echo "📝 Step 5: Creating Nginx config..."
sudo tee /etc/nginx/sites-available/updatemetaads.site > /dev/null << 'EOF'
server {
    listen 80;
    server_name updatemetaads.site www.updatemetaads.site;

    access_log /var/log/nginx/updatemetaads.access.log;
    error_log /var/log/nginx/updatemetaads.error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# Step 6: Enable site
echo "🔗 Step 6: Enabling site..."
sudo ln -sf /etc/nginx/sites-available/updatemetaads.site /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Step 7: Setup SSL
echo "🔒 Step 7: Setting up SSL certificate..."
echo "   This will ask for your email and agreement to terms"
echo "   Choose option 2 to redirect HTTP to HTTPS"
echo ""
read -p "Press Enter to continue with SSL setup..."
sudo certbot --nginx -d updatemetaads.site -d www.updatemetaads.site --non-interactive --agree-tos --redirect

# Step 8: Test SSL
echo "🧪 Step 8: Testing SSL..."
sleep 2
curl -s https://updatemetaads.site/health || echo "⚠️  SSL test failed, but certificate may still be valid"

# Step 9: Test auto-renewal
echo "🔄 Step 9: Testing auto-renewal..."
sudo certbot renew --dry-run

echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env with domain: WEBHOOK_URL=https://updatemetaads.site/api/telegram/webhook"
echo "2. Update Telegram webhook: See UPDATE_WEBHOOK_DOMAIN.md"
echo "3. Test from browser: https://updatemetaads.site/health"
echo ""
echo "🔍 Verify:"
echo "  - HTTPS: https://updatemetaads.site/health"
echo "  - SSL: openssl s_client -connect updatemetaads.site:443 -servername updatemetaads.site"
echo ""


