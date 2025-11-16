# 🔧 NGINX CONFIGURATION

## 📁 FILE: `/etc/nginx/sites-available/updatemetaads.site`

```nginx
server {
    listen 80;
    server_name updatemetaads.site www.updatemetaads.site;

    # Logs
    access_log /var/log/nginx/updatemetaads.access.log;
    error_log /var/log/nginx/updatemetaads.error.log;

    # Reverse proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # WebSocket support (nếu cần)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔒 SAU KHI SETUP SSL (Certbot sẽ tự động thêm):

```nginx
server {
    listen 80;
    server_name updatemetaads.site www.updatemetaads.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name updatemetaads.site www.updatemetaads.site;

    # SSL certificates (Certbot tự động thêm)
    ssl_certificate /etc/letsencrypt/live/updatemetaads.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/updatemetaads.site/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Logs
    access_log /var/log/nginx/updatemetaads.access.log;
    error_log /var/log/nginx/updatemetaads.error.log;

    # Reverse proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🚀 QUICK SETUP COMMANDS

### **1. Create config file:**

```bash
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
```

### **2. Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/updatemetaads.site /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **3. Setup SSL:**

```bash
sudo certbot --nginx -d updatemetaads.site -d www.updatemetaads.site
```

---

## 🔍 TEST CONFIG

```bash
# Test Nginx config
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Test HTTP
curl http://updatemetaads.site/health

# Test HTTPS (sau khi setup SSL)
curl https://updatemetaads.site/health
```

---

## 📋 TROUBLESHOOTING

### **Lỗi: "502 Bad Gateway"**

```bash
# Check API đang chạy
curl http://localhost:8000/health

# Check Supervisor
sudo supervisorctl status

# Check logs
sudo tail -50 /var/log/nginx/updatemetaads.error.log
```

### **Lỗi: "Connection refused"**

```bash
# Check API port
sudo netstat -tlnp | grep 8000

# Restart API
sudo supervisorctl restart ads-automation-api
```

### **Lỗi: DNS not resolved**

```bash
# Check DNS
dig updatemetaads.site +short
nslookup updatemetaads.site

# Đợi DNS propagate (5-60 phút)
```

---

**Sử dụng file config này để setup Nginx! 🚀**


