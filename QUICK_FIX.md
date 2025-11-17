# 🔧 Quick Fix Commands for VPS

## Chạy các lệnh này trên VPS ngay:

```bash
# Fix git ownership issue
sudo git config --global --add safe.directory /var/www/ads-automation

# Fix ownership
sudo chown -R adsuser:adsuser /var/www/ads-automation
cd /var/www/ads-automation

# Pull latest changes
git pull origin main

# Now run update script
sudo bash update-vps.sh
```

## Nếu scripts vẫn không có, tạo trực tiếp:

```bash
# Download scripts trực tiếp từ GitHub
cd /var/www/ads-automation
wget https://raw.githubusercontent.com/LeDat0312/ads-automation/main/update-vps.sh
wget https://raw.githubusercontent.com/LeDat0312/ads-automation/main/fix-502.sh
chmod +x *.sh

# Run fix script
sudo bash fix-502.sh
```

## Hoặc fix manual nhanh:

```bash
# 1. Fix ownership và pull code
sudo chown -R adsuser:adsuser /var/www/ads-automation
cd /var/www/ads-automation
git pull origin main

# 2. Update Python dependencies  
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Restart services
sudo supervisorctl stop ads-automation
sudo supervisorctl start ads-automation

# 4. Check status
sudo supervisorctl status
curl http://localhost:8000/health
```