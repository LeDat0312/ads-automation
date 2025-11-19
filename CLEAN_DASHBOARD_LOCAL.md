# Hướng dẫn xóa HTML code từ dashboard.py trên LOCAL

## Vấn đề:
File `dashboard.py` có HTML/CSS/JS code từ dòng 1019 đến 4941 cần xóa.

## Giải pháp:

### Chạy script Python này trên LOCAL:

```python
file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original: {len(lines)} lines")

# Xóa HTML code từ dòng 1019 đến 4941 (indices 1018-4940)
# Giữ: lines 1-1018 + lines 4942-end
new_lines = lines[:1018] + lines[4941:]

print(f"Removed {4941 - 1018} lines of HTML/CSS/JS")
print(f"New: {len(new_lines)} lines")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Done!")
```

### Hoặc copy và chạy file Python:

Tạo file `clean_dashboard.py` với nội dung trên, sau đó chạy:
```bash
python clean_dashboard.py
```

### Sau khi xóa, kiểm tra:

```bash
# Test import
python -c "import app.main; print('✅ OK')"

# Check số dòng
python -c "with open('app/api/routes/dashboard.py', 'r', encoding='utf-8') as f: print(f'Total lines: {len(f.readlines())}')"
```

### Push lên GitHub:

```bash
git add app/api/routes/dashboard.py
git commit -m "Fix: Remove HTML/CSS/JS code from dashboard.py"
git push origin main
```

### Trên VPS, pull về:

```bash
cd ~/ads-automation
git pull origin main
source venv/bin/activate
python3 -c "import app.main; print('✅ OK')"
sudo supervisorctl restart ads-automation
```

