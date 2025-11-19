# Hướng dẫn sửa lỗi IndentationError trong dashboard.py

## Vấn đề:
File `dashboard.py` có lỗi IndentationError ở dòng 463 do còn sót HTML/CSS code.

## Giải pháp nhanh (trên VPS):

### Option 1: Dùng file backup (nhanh nhất)
```bash
cd ~/ads-automation
# Backup file hiện tại
cp app/api/routes/dashboard.py app/api/routes/dashboard_broken.py

# Dùng file backup (nếu có)
if [ -f "app/api/routes/dashboard_BACKUP_BEFORE_REFACTOR_20251119_175928.py" ]; then
    # Tạm thời dùng file backup để service chạy được
    cp app/api/routes/dashboard_BACKUP_BEFORE_REFACTOR_20251119_175928.py app/api/routes/dashboard.py
    echo "✅ Đã restore từ backup"
else
    echo "❌ Không tìm thấy backup file"
fi

# Test import
source venv/bin/activate
python3 -c "import app.main; print('✅ Import OK')" || echo "❌ Vẫn còn lỗi"

# Restart service
sudo supervisorctl restart ads-automation
```

### Option 2: Xóa HTML code bằng Python script
```bash
cd ~/ads-automation

# Tạo script Python để xóa HTML code
cat > fix_dashboard.py << 'EOF'
#!/usr/bin/env python3
file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original: {len(lines)} lines")

# Xóa từ dòng 944 đến 4894 (indices 943-4893)
new_lines = lines[:943] + lines[4894:]

print(f"New: {len(new_lines)} lines")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Done!")
EOF

python3 fix_dashboard.py

# Test
source venv/bin/activate
python3 -c "import app.main; print('✅ Import OK')"

# Restart
sudo supervisorctl restart ads-automation
```

### Option 3: Pull code mới từ GitHub (nếu đã fix và push)
```bash
cd ~/ads-automation
git pull origin main
source venv/bin/activate
python3 -c "import app.main; print('✅ Import OK')"
sudo supervisorctl restart ads-automation
```

## Kiểm tra sau khi sửa:
```bash
# Test import
python3 -c "import app.main; print('✅ OK')"

# Check logs
sudo tail -f /var/log/ads-automation.log

# Test endpoint
curl http://localhost:8000/dashboard/health
```

