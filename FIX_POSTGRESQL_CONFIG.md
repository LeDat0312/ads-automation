# 🔧 FIX POSTGRESQL CONFIG - PERMISSION DENIED

## 🚨 VẤN ĐỀ: Permission denied khi edit `/etc/postgresql/14/main/postgresql.conf`

### **NGUYÊN NHÂN:**
- File `/etc/postgresql/14/main/postgresql.conf` thuộc về user `postgres` hoặc `root`
- User `metaupdateads` không có quyền edit file này trực tiếp
- Cần dùng `sudo` để edit file

---

## ✅ GIẢI PHÁP

### **CÁCH 1: Dùng sudo với nano (trong terminal)**

#### **Bước 1: Edit file với sudo**

```bash
# Edit file với sudo và nano (trong terminal MobaXterm)
sudo nano /etc/postgresql/14/main/postgresql.conf

# Sẽ hỏi password của user metaupdateads
# Nhập password khi được hỏi
```

#### **Bước 2: Tìm và sửa các dòng cần thiết**

Trong nano, dùng `Ctrl+W` để search các dòng sau:

```bash
# Tìm: shared_buffers
# Sửa thành: shared_buffers = 512MB

# Tìm: effective_cache_size
# Sửa thành: effective_cache_size = 1GB

# Tìm: maintenance_work_mem
# Sửa thành: maintenance_work_mem = 128MB

# Tìm: work_mem
# Sửa thành: work_mem = 10MB

# Tìm: max_connections
# Sửa thành: max_connections = 50
```

#### **Bước 3: Save và exit**

```bash
# Save: Ctrl+O (viết chữ O, không phải số 0)
# Enter để confirm

# Exit: Ctrl+X
```

#### **Bước 4: Restart PostgreSQL**

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql
```

---

### **CÁCH 2: Dùng sed để sửa tự động (Nhanh hơn)**

#### **Bước 1: Backup file config**

```bash
# Backup file config
sudo cp /etc/postgresql/14/main/postgresql.conf /etc/postgresql/14/main/postgresql.conf.backup
```

#### **Bước 2: Sửa các dòng cần thiết**

```bash
# Sửa shared_buffers
sudo sed -i "s/#shared_buffers = 128MB/shared_buffers = 512MB/" /etc/postgresql/14/main/postgresql.conf
sudo sed -i "s/^shared_buffers = .*/shared_buffers = 512MB/" /etc/postgresql/14/main/postgresql.conf

# Sửa effective_cache_size
sudo sed -i "s/#effective_cache_size = 4GB/effective_cache_size = 1GB/" /etc/postgresql/14/main/postgresql.conf
sudo sed -i "s/^effective_cache_size = .*/effective_cache_size = 1GB/" /etc/postgresql/14/main/postgresql.conf

# Sửa maintenance_work_mem
sudo sed -i "s/#maintenance_work_mem = 64MB/maintenance_work_mem = 128MB/" /etc/postgresql/14/main/postgresql.conf
sudo sed -i "s/^maintenance_work_mem = .*/maintenance_work_mem = 128MB/" /etc/postgresql/14/main/postgresql.conf

# Sửa work_mem
sudo sed -i "s/#work_mem = 4MB/work_mem = 10MB/" /etc/postgresql/14/main/postgresql.conf
sudo sed -i "s/^work_mem = .*/work_mem = 10MB/" /etc/postgresql/14/main/postgresql.conf

# Sửa max_connections
sudo sed -i "s/#max_connections = 100/max_connections = 50/" /etc/postgresql/14/main/postgresql.conf
sudo sed -i "s/^max_connections = .*/max_connections = 50/" /etc/postgresql/14/main/postgresql.conf
```

#### **Bước 3: Verify các thay đổi**

```bash
# Xem các dòng đã sửa
sudo grep -E "shared_buffers|effective_cache_size|maintenance_work_mem|work_mem|max_connections" /etc/postgresql/14/main/postgresql.conf
```

#### **Bước 4: Restart PostgreSQL**

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql
```

---

### **CÁCH 3: Tạo file config mới và copy (An toàn nhất)**

#### **Bước 1: Tạo file config mới**

```bash
# Tạo file config mới trong thư mục home
nano ~/postgresql.conf.custom

# Thêm các dòng sau:
shared_buffers = 512MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
work_mem = 10MB
max_connections = 50
```

#### **Bước 2: Append vào file config chính**

```bash
# Append vào cuối file config
sudo sh -c 'echo "" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "# Custom settings for 2GB RAM" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "shared_buffers = 512MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "effective_cache_size = 1GB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "maintenance_work_mem = 128MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "work_mem = 10MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "max_connections = 50" >> /etc/postgresql/14/main/postgresql.conf'
```

#### **Bước 3: Verify và restart**

```bash
# Verify
sudo tail -10 /etc/postgresql/14/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql
```

---

## 📋 HƯỚNG DẪN CHI TIẾT (MobaXterm Terminal)

### **BƯỚC 1: Mở terminal trong MobaXterm**

1. Đảm bảo bạn đang login với user `metaupdateads`
2. Mở terminal (nếu chưa mở)

### **BƯỚC 2: Edit file với sudo nano**

```bash
# Edit file với sudo
sudo nano /etc/postgresql/14/main/postgresql.conf

# Sẽ hỏi password, nhập password của metaupdateads
```

### **BƯỚC 3: Tìm và sửa các dòng**

Trong nano editor:

1. **Tìm `shared_buffers`:**
   - Nhấn `Ctrl+W` (search)
   - Gõ: `shared_buffers`
   - Enter
   - Tìm dòng: `#shared_buffers = 128MB`
   - Xóa dấu `#` và sửa thành: `shared_buffers = 512MB`

2. **Tìm `effective_cache_size`:**
   - Nhấn `Ctrl+W`
   - Gõ: `effective_cache_size`
   - Enter
   - Tìm dòng: `#effective_cache_size = 4GB`
   - Xóa dấu `#` và sửa thành: `effective_cache_size = 1GB`

3. **Tìm `maintenance_work_mem`:**
   - Nhấn `Ctrl+W`
   - Gõ: `maintenance_work_mem`
   - Enter
   - Tìm dòng: `#maintenance_work_mem = 64MB`
   - Xóa dấu `#` và sửa thành: `maintenance_work_mem = 128MB`

4. **Tìm `work_mem`:**
   - Nhấn `Ctrl+W`
   - Gõ: `work_mem`
   - Enter
   - Tìm dòng: `#work_mem = 4MB`
   - Xóa dấu `#` và sửa thành: `work_mem = 10MB`

5. **Tìm `max_connections`:**
   - Nhấn `Ctrl+W`
   - Gõ: `max_connections`
   - Enter
   - Tìm dòng: `#max_connections = 100`
   - Xóa dấu `#` và sửa thành: `max_connections = 50`

### **BƯỚC 4: Save và exit**

```bash
# Save: Ctrl+O (chữ O)
# Enter để confirm filename

# Exit: Ctrl+X
```

### **BƯỚC 5: Restart PostgreSQL**

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql

# Nếu thấy "active (running)" → Thành công!
```

---

## 🎯 LỆNH NHANH (Copy và paste - KHUYẾN NGHỊ)

### **Cách nhanh nhất: Dùng sed để sửa tự động**

```bash
# Backup file config
sudo cp /etc/postgresql/14/main/postgresql.conf /etc/postgresql/14/main/postgresql.conf.backup

# Sửa shared_buffers
sudo sed -i 's/^#shared_buffers = 128MB/shared_buffers = 512MB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^shared_buffers = 128MB/shared_buffers = 512MB/' /etc/postgresql/14/main/postgresql.conf

# Sửa effective_cache_size
sudo sed -i 's/^#effective_cache_size = 4GB/effective_cache_size = 1GB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^effective_cache_size = 4GB/effective_cache_size = 1GB/' /etc/postgresql/14/main/postgresql.conf

# Sửa maintenance_work_mem
sudo sed -i 's/^#maintenance_work_mem = 64MB/maintenance_work_mem = 128MB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^maintenance_work_mem = 64MB/maintenance_work_mem = 128MB/' /etc/postgresql/14/main/postgresql.conf

# Sửa work_mem
sudo sed -i 's/^#work_mem = 4MB/work_mem = 10MB/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^work_mem = 4MB/work_mem = 10MB/' /etc/postgresql/14/main/postgresql.conf

# Sửa max_connections
sudo sed -i 's/^#max_connections = 100/max_connections = 50/' /etc/postgresql/14/main/postgresql.conf
sudo sed -i 's/^max_connections = 100/max_connections = 50/' /etc/postgresql/14/main/postgresql.conf

# Nếu các dòng chưa được uncomment, thêm vào cuối file
sudo sh -c 'echo "" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "# Custom settings for 2GB RAM" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "shared_buffers = 512MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "effective_cache_size = 1GB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "maintenance_work_mem = 128MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "work_mem = 10MB" >> /etc/postgresql/14/main/postgresql.conf'
sudo sh -c 'echo "max_connections = 50" >> /etc/postgresql/14/main/postgresql.conf'

# Verify
sudo grep -E "shared_buffers|effective_cache_size|maintenance_work_mem|work_mem|max_connections" /etc/postgresql/14/main/postgresql.conf | tail -10

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql
```

---

## 🔍 VERIFY CÁC THAY ĐỔI

### **Kiểm tra các dòng đã sửa:**

```bash
# Xem các dòng config
sudo grep -E "shared_buffers|effective_cache_size|maintenance_work_mem|work_mem|max_connections" /etc/postgresql/14/main/postgresql.conf | grep -v "^#"

# Kết quả mong đợi:
# shared_buffers = 512MB
# effective_cache_size = 1GB
# maintenance_work_mem = 128MB
# work_mem = 10MB
# max_connections = 50
```

### **Kiểm tra PostgreSQL đã restart:**

```bash
# Check status
sudo systemctl status postgresql

# Kết quả mong đợi: active (running)
```

### **Test PostgreSQL:**

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Check config
SHOW shared_buffers;
SHOW effective_cache_size;
SHOW maintenance_work_mem;
SHOW work_mem;
SHOW max_connections;

# Exit
\q
```

---

## 🔒 LƯU Ý QUAN TRỌNG

### **1. Phải dùng sudo:**
- ✅ File config thuộc về user `postgres` hoặc `root`
- ✅ Cần quyền sudo để edit
- ❌ Không thể edit trực tiếp từ GUI editor của MobaXterm

### **2. Backup trước khi sửa:**
- ✅ Luôn backup file config trước khi sửa
- ✅ Có thể restore nếu có lỗi

### **3. Restart sau khi sửa:**
- ✅ Phải restart PostgreSQL để áp dụng thay đổi
- ✅ Check status để đảm bảo PostgreSQL đã restart thành công

---

## 🚨 TROUBLESHOOTING

### **Lỗi: "PostgreSQL failed to start"**

**Nguyên nhân:** Config có lỗi syntax

**Giải pháp:**
```bash
# Restore backup
sudo cp /etc/postgresql/14/main/postgresql.conf.backup /etc/postgresql/14/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check logs
sudo journalctl -u postgresql -n 50
```

### **Lỗi: "Permission denied" khi dùng sed**

**Giải pháp:**
```bash
# Dùng sudo sh -c thay vì sudo sed
sudo sh -c 'echo "shared_buffers = 512MB" >> /etc/postgresql/14/main/postgresql.conf'
```

### **Lỗi: "File not found"**

**Nguyên nhân:** PostgreSQL version khác

**Giải pháp:**
```bash
# Tìm file config
sudo find /etc -name "postgresql.conf" 2>/dev/null

# Hoặc check PostgreSQL version
sudo -u postgres psql -c "SELECT version();"
```

---

## 📋 CHECKLIST

### **✅ SAU KHI HOÀN THÀNH:**

- [ ] Đã backup file config
- [ ] Đã sửa `shared_buffers = 512MB`
- [ ] Đã sửa `effective_cache_size = 1GB`
- [ ] Đã sửa `maintenance_work_mem = 128MB`
- [ ] Đã sửa `work_mem = 10MB`
- [ ] Đã sửa `max_connections = 50`
- [ ] Đã verify các thay đổi
- [ ] Đã restart PostgreSQL
- [ ] Đã check status PostgreSQL
- [ ] Đã test PostgreSQL

---

## 🎯 TÓM TẮT

### **VẤN ĐỀ:**
- Permission denied khi edit `/etc/postgresql/14/main/postgresql.conf`

### **GIẢI PHÁP:**
1. Dùng `sudo nano` trong terminal (không dùng GUI editor)
2. Hoặc dùng `sudo sed` để sửa tự động
3. Hoặc append vào cuối file với `sudo sh -c`

### **KHUYẾN NGHỊ:**
- Dùng cách 2 (sed) - nhanh nhất và an toàn
- Luôn backup trước khi sửa
- Verify sau khi sửa
- Restart PostgreSQL sau khi sửa

---

**Chúc bạn setup thành công! 🚀**

