# 🐍 VENV COMMANDS - HƯỚNG DẪN

## 🔄 CÁC LỆNH VENV

### **Thoát khỏi venv:**

```bash
deactivate
```

**Sau khi chạy, prompt sẽ không còn `(venv)` ở đầu:**
```
adsuser@ip-172-26-10-102:~/ads-automation$
```

### **Vào lại venv:**

```bash
source venv/bin/activate
```

**Prompt sẽ có `(venv)` ở đầu:**
```
(venv) adsuser@ip-172-26-10-102:~/ads-automation$
```

---

## 📋 CÁC LỆNH KHÁC

### **Check đang trong venv hay không:**

```bash
# Check Python path
which python
# Nếu trong venv: /home/adsuser/ads-automation/venv/bin/python
# Nếu không: /usr/bin/python3

# Hoặc check biến môi trường
echo $VIRTUAL_ENV
# Nếu trong venv: /home/adsuser/ads-automation/venv
# Nếu không: (trống)
```

### **Tạo venv mới:**

```bash
# Tạo venv
python3.11 -m venv venv

# Activate
source venv/bin/activate
```

### **Xóa venv:**

```bash
# Thoát venv trước
deactivate

# Xóa thư mục
rm -rf venv
```

---

## ✅ QUICK REFERENCE

| Lệnh | Mô tả |
|------|-------|
| `source venv/bin/activate` | Vào venv |
| `deactivate` | Thoát venv |
| `which python` | Check Python path |
| `pip list` | List packages (chỉ trong venv) |

---

**Chạy `deactivate` để thoát khỏi venv! 🚀**


