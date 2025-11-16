# 🚀 Deployment Guide - ADS Automation

## Server Info
- **IP**: 54.179.208.122
- **Port**: 22
- **Username**: adsuser
- **Password**: @Levandat0312
- **Project Path**: /home/adsuser/ads-automation/
- **Venv Path**: /home/adsuser/ads-automation/venv/

---

## 📋 Step 1: Kiểm tra Services trên Server

Trước tiên, cần biết services nào đang chạy trên server.

### Cách 1: Sử dụng MobaXterm (Khuyến khích)

```bash
# 1. Mở MobaXterm
# 2. SSH vào server
ssh adsuser@54.179.208.122
# Password: @Levandat0312

# 3. Chạy lệnh kiểm tra
cd /tmp
curl -o check-services.sh https://raw.githubusercontent.com/LeDat0312/ads-automation/main/deploy/check-services.sh
bash check-services.sh

# Hoặc chạy trực tiếp
ps aux | grep -E 'gunicorn|supervisor|uvicorn|nginx|python'
sudo supervisorctl status
sudo systemctl list-units --type=service | grep ads
```

### Cách 2: PowerShell (cần SSH key)

```powershell
# Chưa hỗ trợ password authentication trực tiếp
# Cần SSH key (.pem) hoặc cài đặt sshpass
```

---

## 🚀 Step 2: Deployment Methods

### Method 1: MobaXterm (Easiest)

```bash
# 1. SSH vào server
ssh adsuser@54.179.208.122

# 2. Download deploy script
cd /home/adsuser/ads-automation
wget https://raw.githubusercontent.com/LeDat0312/ads-automation/main/deploy/deploy.sh
chmod +x deploy.sh

# 3. Deploy options
# Option A: Pull code only
bash deploy.sh

# Option B: Pull code + Backup
bash deploy.sh --backup

# Option C: Pull code + Init database
bash deploy.sh --migrate

# Option D: Pull code + Restart services
bash deploy.sh --restart

# Option E: Full deployment (everything)
bash deploy.sh --backup --migrate --restart
```

---

### Method 2: PowerShell (cần SSH key)

#### Setup SSH Key (.pem file)

```bash
# Trên server, tạo SSH key (nếu chưa có)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Copy private key về Windows
cat ~/.ssh/id_rsa
# Copy toàn bộ content và lưu vào file C:\Users\YourUser\.ssh\ads-automation-key.pem
```

#### Deploy từ Windows

```powershell
# 1. Navigate đến deploy folder
cd "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet\deploy"

# 2. Allow script execution (nếu cần)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Check services
.\deploy-remote.ps1 -Action check -KeyPath C:\Users\YourUser\.ssh\ads-automation-key.pem

# 4. Deploy (code pull only)
.\deploy-remote.ps1 -Action deploy -KeyPath C:\Users\YourUser\.ssh\ads-automation-key.pem

# 5. Full deployment
.\deploy-remote.ps1 -Action deploy -KeyPath C:\Users\YourUser\.ssh\ads-automation-key.pem -Backup -Migrate -Restart

# 6. Restart services
.\deploy-remote.ps1 -Action restart -KeyPath C:\Users\YourUser\.ssh\ads-automation-key.pem
```

---

## 📊 Deploy Script Features

### deploy.sh

Script bash chạy trên server Ubuntu. Features:

- ✅ Pull latest code từ GitHub (main branch)
- ✅ Activate Python virtual environment
- ✅ Install/Update pip dependencies
- ✅ Database initialization (--migrate flag)
- ✅ Restart services (--supervisor, --systemd, --nginx)
- ✅ Backup trước deploy (--backup flag)
- ✅ Logging tất cả actions

### deploy-remote.ps1

PowerShell script chạy từ Windows. Features:

- ✅ SSH connection qua SSH key (.pem)
- ✅ Execute remote deploy script
- ✅ Check server services
- ✅ Flexible parameters
- ✅ Color-coded output

---

## 🔍 Common Commands

### Check status
```bash
# Check all running processes
ps aux | grep python

# Check supervisor
sudo supervisorctl status

# Check systemd services
systemctl status ads-automation-api
systemctl status ads-automation-worker
sudo systemctl status nginx

# Check logs
sudo tail -f /var/log/supervisor/ads-automation*.log
sudo journalctl -u ads-automation-api -f
```

### Manual restart
```bash
# Supervisor
sudo supervisorctl restart all

# Systemd
sudo systemctl restart ads-automation-api
sudo systemctl restart ads-automation-worker
sudo systemctl restart nginx

# Nginx reload config
sudo nginx -t
sudo systemctl reload nginx
```

### Rollback
```bash
# Restore from backup
cp -r /home/adsuser/backups/ads-automation-backup-YYYYMMDD_HHMMSS/* /home/adsuser/ads-automation/
cd /home/adsuser/ads-automation && bash deploy.sh --restart
```

---

## 🐛 Troubleshooting

### Problem: "Permission denied" 
```bash
# Thêm quyền sudo cho adsuser (nếu cần)
sudo visudo
# Thêm dòng: adsuser ALL=(ALL) NOPASSWD: /usr/bin/supervisorctl, /usr/bin/systemctl
```

### Problem: "ModuleNotFoundError"
```bash
# Re-install dependencies
source /home/adsuser/ads-automation/venv/bin/activate
pip install --upgrade pip
pip install -r /home/adsuser/ads-automation/requirements.txt
```

### Problem: Service không start
```bash
# Check logs
sudo supervisorctl tail -f ads-automation-api
# Hoặc
sudo journalctl -u ads-automation-api -n 50
```

### Problem: Database connection failed
```bash
# Check environment
cat /home/adsuser/ads-automation/.env | grep DATABASE_URL

# Test connection
cd /home/adsuser/ads-automation && python scripts/init_db.py
```

---

## 📝 Next Steps

1. **Kiểm tra services trên server** (theo Step 1)
2. **Báo cho tôi kết quả** (ps aux, supervisorctl status, v.v.)
3. **Tôi sẽ cập nhật deploy script** dựa trên services thực tế
4. **Deploy lần đầu** và test

---

## ⚠️ Important Notes

- ✅ Luôn **backup trước deploy** (`--backup` flag)
- ✅ Test trên dev trước khi deploy production
- ✅ Keep `.env` file private (không commit lên Git)
- ✅ Kiểm tra logs sau deploy: `tail -f /var/log/ads-automation-deploy.log`
- ✅ Có thể rollback nhanh từ backup nếu có issue

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs
2. Run `bash check-services.sh` để diagnose
3. Báo tôi error message đầy đủ
