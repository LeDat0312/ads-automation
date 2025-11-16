# Hướng dẫn Push Code lên GitHub

## Bước 1: Kiểm tra Git Repository

Đảm bảo bạn đang ở trong thư mục git repository. Nếu chưa có, cần clone repository từ GitHub:

```bash
cd ~
git clone https://github.com/LeDat0312/ads-automation.git
cd ads-automation
```

## Bước 2: Copy file đã sửa vào git repository

Nếu bạn đang làm việc ở thư mục khác, cần copy file `app/api/routes/dashboard.py` vào git repository:

```bash
# Copy file từ thư mục hiện tại sang git repository
cp "C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet\app\api\routes\dashboard.py" "C:\path\to\ads-automation\app\api\routes\dashboard.py"
```

## Bước 3: Commit và Push

```bash
# Di chuyển vào thư mục git repository
cd C:\path\to\ads-automation

# Kiểm tra status
git status

# Add file đã thay đổi
git add app/api/routes/dashboard.py

# Commit với message
git commit -m "Fix dashboard: Replace JS template literals with string concatenation, add stats grid, fix date picker functions"

# Push lên GitHub
git push origin main
```

## Bước 4: Pull trên VPS

Sau khi push thành công, chạy script trên VPS:

```bash
bash PULL_VPS_DASHBOARD_FIX.sh
```

Hoặc chạy thủ công:

```bash
cd ~/ads-automation
git stash
git pull origin main
python3 -m py_compile app/api/routes/dashboard.py app/core/ui_helpers.py app/api/routes/home.py app/main.py
sudo supervisorctl restart all
sudo supervisorctl status
```

## Kiểm tra Logs

Nếu có lỗi, xem logs:

```bash
sudo supervisorctl tail -200 ads-automation-api | grep -A 10 -B 10 "Error\|Exception\|Traceback"
```

