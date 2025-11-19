# Sửa lỗi Git Permission trên VPS

## Lỗi:
```
error: insufficient permission for adding an object to repository database .git/objects
fatal: failed to write object
fatal: unpack-objects failed
```

## Nguyên nhân:
Quyền sở hữu hoặc quyền truy cập của thư mục `.git` không đúng.

## Cách sửa:

### Bước 1: Kiểm tra quyền hiện tại
```bash
cd ~/ads-automation
ls -la .git/objects
whoami
```

### Bước 2: Sửa quyền sở hữu (nếu cần)
```bash
# Nếu thư mục thuộc về root hoặc user khác, chuyển về adsuser
sudo chown -R adsuser:adsuser ~/ads-automation/.git
```

### Bước 3: Đảm bảo quyền truy cập đúng
```bash
# Đặt quyền cho thư mục .git
chmod -R u+w ~/ads-automation/.git
chmod 755 ~/ads-automation/.git
chmod 755 ~/ads-automation/.git/objects
```

### Bước 4: Thử pull lại
```bash
cd ~/ads-automation
git pull origin main
```

## Nếu vẫn lỗi:

### Option 1: Xóa và clone lại (nếu không có thay đổi local quan trọng)
```bash
cd ~
mv ads-automation ads-automation-backup
git clone https://github.com/LeDat0312/ads-automation.git
cd ads-automation
# Copy lại các file config nếu cần
```

### Option 2: Sửa quyền toàn bộ thư mục
```bash
cd ~/ads-automation
sudo chown -R adsuser:adsuser .
chmod -R u+w .
```

### Option 3: Kiểm tra và sửa quyền cụ thể cho .git/objects
```bash
cd ~/ads-automation
find .git/objects -type d -exec chmod 755 {} \;
find .git/objects -type f -exec chmod 644 {} \;
```

## Sau khi sửa xong, pull lại:
```bash
cd ~/ads-automation
git pull origin main
```

## Nếu vẫn gặp vấn đề, kiểm tra:
```bash
# Kiểm tra quyền sở hữu
ls -la ~/ads-automation | head -5

# Kiểm tra quyền .git
ls -la ~/ads-automation/.git | head -10

# Kiểm tra disk space
df -h

# Kiểm tra SELinux (nếu có)
getenforce
```

