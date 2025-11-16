# 🚀 QUICK START - GIT & GITHUB SETUP

## ⚡ TÓM TẮT NHANH

### **1. TRÊN MÁY LOCAL (Windows):**

```bash
# 1. Tạo GitHub repository (trên web)
# Vào https://github.com → New repository
# Tên: facebook-ads-automation
# Chọn: Private

# 2. Mở terminal trong thư mục project
cd "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet"

# 3. Initialize Git
git init
git add .
git commit -m "Initial commit: Facebook Ads Automation System"

# 4. Add remote repository
git remote add origin https://github.com/your-username/facebook-ads-automation.git

# 5. Push to GitHub
git branch -M main
git push -u origin main
```

### **2. TRÊN VPS (AWS Lightsail):**

```bash
# 1. SSH vào VPS
ssh -i your-key.pem ubuntu@your-lightsail-ip

# 2. Install Git
sudo apt update
sudo apt install git -y

# 3. Clone repository
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/your-username/facebook-ads-automation.git
cd facebook-ads-automation

# 4. Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Setup .env
cp env.example .env
nano .env  # Edit with your actual values

# 6. Deploy
chmod +x deploy.sh
./deploy.sh
```

---

## 📋 CÁC FILE ĐÃ TẠO

### **✅ ĐÃ CÓ SẴN:**
- ✅ `.gitignore` - Ignore secrets và files không cần thiết
- ✅ `env.example` - Template cho environment variables
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Documentation
- ✅ `deploy.sh` - Deployment script
- ✅ `GIT_DEPLOYMENT_GUIDE.md` - Hướng dẫn chi tiết

---

## 🔄 WORKFLOW HÀNG NGÀY

### **DEVELOP TRÊN LOCAL:**
```bash
# 1. Làm việc trên code
# ... edit files ...

# 2. Check status
git status

# 3. Add changes
git add .

# 4. Commit
git commit -m "Add new feature: dashboard overview"

# 5. Push to GitHub
git push origin main
```

### **DEPLOY TRÊN VPS:**
```bash
# 1. SSH vào VPS
ssh -i your-key.pem ubuntu@your-lightsail-ip

# 2. Vào thư mục project
cd ~/projects/facebook-ads-automation

# 3. Pull latest code
git pull origin main

# 4. Deploy
./deploy.sh
```

---

## 🔒 SECURITY

### **⚠️ QUAN TRỌNG:**
- ✅ **File `.env`** được ignore bởi `.gitignore` - KHÔNG commit
- ✅ **File `env.example`** sẽ được commit - chỉ có template
- ✅ **Secrets** chỉ lưu trên VPS trong file `.env`
- ✅ **Repository** nên là **Private** để bảo mật

---

## 📋 CHECKLIST

### **✅ SETUP GIT:**
- [ ] Đã tạo GitHub repository (Private)
- [ ] Đã initialize Git trong project
- [ ] Đã commit code
- [ ] Đã push lên GitHub

### **✅ DEPLOYMENT:**
- [ ] Đã install Git trên VPS
- [ ] Đã clone repository
- [ ] Đã setup virtual environment
- [ ] Đã install dependencies
- [ ] Đã setup .env file
- [ ] Đã deploy và test

---

## 🎯 LỢI ÍCH

### **✅ KHI DÙNG GIT/GITHUB:**
- ✅ **Backup code** trên cloud
- ✅ **Deploy dễ dàng** - chỉ cần `git clone`
- ✅ **Version control** - theo dõi thay đổi
- ✅ **Rollback** - quay lại version cũ nếu có lỗi
- ✅ **Collaboration** - nhiều người làm việc cùng

---

## 📚 TÀI LIỆU THAM KHẢO

- [GIT_DEPLOYMENT_GUIDE.md](./GIT_DEPLOYMENT_GUIDE.md) - Hướng dẫn chi tiết
- [AWS_LIGHTSAIL_SETUP_GUIDE.md](./AWS_LIGHTSAIL_SETUP_GUIDE.md) - Setup VPS

---

**Chúc bạn setup thành công! 🚀**


