# 💾 NANO - LƯU VÀ THOÁT

## 🔧 CÁCH LƯU VÀ THOÁT NANO

### **Sau khi đã paste config vào file:**

1. **Lưu file:**
   - Nhấn: `Ctrl + O`
   - Nhấn: `Enter` (để confirm)
   - Sẽ thấy: `[ Wrote X lines ]`

2. **Thoát nano:**
   - Nhấn: `Ctrl + X`
   - Sẽ quay về terminal prompt

---

## 📋 CÁC PHÍM TẮT NANO

| Phím | Chức năng |
|------|-----------|
| `Ctrl + O` | Save (Write Out) |
| `Enter` | Confirm save |
| `Ctrl + X` | Exit nano |
| `Ctrl + K` | Cut line |
| `Ctrl + U` | Paste |
| `Ctrl + W` | Search |

---

## ✅ SAU KHI THOÁT

### **Tiếp tục các bước:**

```bash
# Tạo log directory
sudo mkdir -p /var/log/ads-automation
sudo chown adsuser:adsuser /var/log/ads-automation

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation-api
sudo supervisorctl start ads-automation-worker:*

# Check status
sudo supervisorctl status
```

---

**Nhấn `Ctrl + O`, sau đó `Enter`, rồi `Ctrl + X`! 💾**


