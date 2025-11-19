# Sửa lỗi IndentationError - Hướng dẫn nhanh cho VPS

## Lỗi:
```
File "/home/adsuser/ads-automation/app/api/routes/dashboard.py", line 463
    padding: 0 10px;
IndentationError: unexpected indent
```

## Giải pháp nhanh (chạy trên VPS):

### Copy và chạy toàn bộ script này:

```bash
cd ~/ads-automation

# Tạo script Python để xóa HTML code
python3 << 'EOF'
file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original: {len(lines)} lines")

# Xóa function trùng lặp (431-709) và HTML code (944-4894)
# Giữ: lines 1-430 + lines 4895-end
new_lines = lines[:430] + lines[4894:]

print(f"New: {len(new_lines)} lines")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Done!")
EOF

# Test
source venv/bin/activate
python3 -c "import app.main; print('✅ Import OK')"

# Restart
sudo supervisorctl restart ads-automation
sudo supervisorctl status
```

## Hoặc dùng file backup (nếu có):

```bash
cd ~/ads-automation
cp app/api/routes/dashboard.py app/api/routes/dashboard_broken.py
cp app/api/routes/dashboard_BACKUP_BEFORE_REFACTOR_20251119_175928.py app/api/routes/dashboard.py
source venv/bin/activate
python3 -c "import app.main; print('✅ OK')"
sudo supervisorctl restart ads-automation
```

## Kiểm tra:

```bash
# Check logs
sudo tail -f /var/log/ads-automation.log

# Test endpoint
curl http://localhost:8000/dashboard/health
```

