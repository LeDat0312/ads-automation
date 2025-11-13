# 📋 HƯỚNG DẪN: QUẢN LÝ LOGIC RULES CHO TỪNG TÀI KHOẢN

## 🎯 TỔNG QUAN

Hệ thống đã có giao diện web đơn giản để quản lý logic rules cho từng tài khoản và prefix. Bạn có thể:

- ✅ Tạo rules mới cho từng account/prefix
- ✅ Sửa/xóa rules
- ✅ Bật/tắt rules
- ✅ Xem danh sách rules theo account/prefix

---

## 🚀 CÁCH SỬ DỤNG

### **1. Truy cập giao diện**

Sau khi deploy, truy cập:
```
https://updatemetaads.site/rules/
```

Hoặc local:
```
http://localhost:8000/rules/
```

### **2. Tạo Rule Mới**

1. **Điền thông tin cơ bản:**
   - **Tên Rule**: VD: "Tăng budget khi CPL thấp"
   - **Tài khoản**: Chọn account hoặc "Tất cả"
   - **Prefix**: Chọn prefix hoặc "Tất cả"

2. **Chọn Action:**
   - `INCREASE_BUDGET` - Tăng budget
   - `DECREASE_BUDGET` - Giảm budget
   - `PAUSE` - Tạm dừng
   - `RESUME` - Tiếp tục

3. **Điều kiện (JSON):**
   ```json
   {
     "AND": [
       {
         "metric": "spend",
         "operator": ">",
         "value": 100000
       },
       {
         "metric": "cpl",
         "operator": "<",
         "value": 50000
       }
     ]
   }
   ```

4. **Action Params (JSON - tùy chọn):**
   ```json
   {
     "percent": 20,
     "frequency": "once_a_day"
   }
   ```

5. **Trạng thái:**
   - `DRAFT` - Nháp (chưa chạy)
   - `LIVE` - Đang chạy
   - `PAUSED` - Tạm dừng

6. Click **"💾 Lưu Rule"**

### **3. Sửa Rule**

1. Click **"✏️ Sửa"** trên rule cần sửa
2. Form sẽ tự động điền thông tin
3. Sửa các trường cần thiết
4. Click **"💾 Lưu Rule"**

### **4. Xóa Rule**

1. Click **"🗑️ Xóa"** trên rule cần xóa
2. Xác nhận xóa

---

## 📝 VÍ DỤ RULES

### **Ví dụ 1: Tăng budget khi CPL thấp**

```json
{
  "name": "Tăng budget khi CPL thấp",
  "account_ids": ["act_723686686812438"],
  "prefixes": ["FL", "PX"],
  "action": "INCREASE_BUDGET",
  "conditions": {
    "AND": [
      {
        "metric": "spend",
        "operator": ">",
        "value": 100000
      },
      {
        "metric": "cpl",
        "operator": "<",
        "value": 50000
      }
    ]
  },
  "action_params": {
    "percent": 20
  },
  "status": "LIVE",
  "enabled": true
}
```

### **Ví dụ 2: Tạm dừng khi chi tiêu quá cao**

```json
{
  "name": "Tạm dừng khi chi tiêu quá cao",
  "account_ids": [],
  "prefixes": ["TL"],
  "action": "PAUSE",
  "conditions": {
    "AND": [
      {
        "metric": "spend",
        "operator": ">",
        "value": 500000
      },
      {
        "metric": "results",
        "operator": "<",
        "value": 10
      }
    ]
  },
  "status": "LIVE",
  "enabled": true
}
```

### **Ví dụ 3: Tiếp tục khi CPL tốt**

```json
{
  "name": "Tiếp tục khi CPL tốt",
  "account_ids": ["act_2827767517395636"],
  "prefixes": [],
  "action": "RESUME",
  "conditions": {
    "AND": [
      {
        "metric": "cpl",
        "operator": "<",
        "value": 30000
      }
    ]
  },
  "status": "LIVE",
  "enabled": true
}
```

---

## 🔧 CẤU TRÚC CONDITIONS

### **Metrics có sẵn:**
- `spend` - Số tiền chi tiêu
- `cpl` - Cost per lead
- `cpa` - Cost per action
- `roas` - Return on ad spend
- `results` - Số kết quả
- `impressions` - Số lượt hiển thị
- `clicks` - Số lượt click

### **Operators:**
- `>` - Lớn hơn
- `<` - Nhỏ hơn
- `>=` - Lớn hơn hoặc bằng
- `<=` - Nhỏ hơn hoặc bằng
- `==` - Bằng
- `!=` - Khác

### **Timeframes:**
- `today` - Hôm nay
- `yesterday` - Hôm qua
- `last_3days` - 3 ngày gần nhất
- `last_7days` - 7 ngày gần nhất

### **Logic Groups:**
- `AND` - Tất cả điều kiện phải đúng
- `OR` - Ít nhất 1 điều kiện đúng

---

## 📊 QUẢN LÝ THEO ACCOUNT/PREFIX

### **Account IDs:**
- **Rỗng `[]`**: Áp dụng cho tất cả accounts
- **Có giá trị**: Chỉ áp dụng cho accounts được chọn
- VD: `["act_723686686812438", "act_2827767517395636"]`

### **Prefixes:**
- **Rỗng `[]`**: Áp dụng cho tất cả prefixes
- **Có giá trị**: Chỉ áp dụng cho prefixes được chọn
- VD: `["FL", "PX", "TL"]`

### **Priority:**
Khi có nhiều rules match:
1. Rules với account_id cụ thể > Rules cho tất cả accounts
2. Rules với prefix cụ thể > Rules cho tất cả prefixes
3. Rules mới tạo > Rules cũ (theo `created_at`)

---

## 🎨 GIAO DIỆN

Giao diện bao gồm:

1. **Form tạo/sửa rule** - Ở trên cùng
2. **Danh sách rules** - Ở dưới, hiển thị:
   - Tên rule
   - Trạng thái (Bật/Tắt, Status)
   - Accounts và Prefixes áp dụng
   - Nút Sửa/Xóa

### **Badges:**
- 🟢 **Bật** / 🔴 **Tắt** - Trạng thái enabled
- **DRAFT/LIVE/PAUSED** - Status
- **Account badges** - Màu xanh dương
- **Prefix badges** - Màu tím

---

## ⚠️ LƯU Ý

1. **JSON Format**: Đảm bảo JSON đúng format, nếu không sẽ báo lỗi
2. **Conditions**: Phải có ít nhất 1 điều kiện trong `AND` hoặc `OR`
3. **Action Params**: Tùy chọn, nhưng nên điền nếu action cần params
4. **Status**: 
   - `DRAFT` - Rule chưa chạy
   - `LIVE` - Rule đang chạy (automation sẽ check)
   - `PAUSED` - Rule tạm dừng

---

## 🔄 CẬP NHẬT SAU KHI TẠO/SỬA

Sau khi tạo/sửa rule:
- Rule sẽ được lưu vào database ngay
- Automation sẽ tự động load rules mới khi chạy
- Không cần restart server

---

## 📚 API ENDPOINTS

Nếu muốn dùng API trực tiếp:

- `GET /api/rules` - List rules
- `POST /api/rules` - Tạo rule mới
- `GET /api/rules/{id}` - Lấy chi tiết rule
- `PUT /api/rules/{id}` - Cập nhật rule
- `DELETE /api/rules/{id}` - Xóa rule
- `POST /api/rules/{id}/toggle` - Bật/tắt rule

---

## ✅ CHECKLIST

- [ ] Truy cập `/rules/` để mở giao diện
- [ ] Tạo rule mới cho account cụ thể
- [ ] Test với prefix cụ thể
- [ ] Sửa rule đã tạo
- [ ] Xóa rule không cần
- [ ] Kiểm tra automation có chạy đúng rules không

---

## 🆘 TROUBLESHOOTING

### **Lỗi: "Invalid JSON"**
- Kiểm tra lại format JSON trong Conditions và Action Params
- Dùng JSON validator online để check

### **Rule không chạy**
- Kiểm tra `enabled = true` và `status = "LIVE"`
- Kiểm tra account_ids và prefixes có match không
- Kiểm tra conditions có đúng không

### **Không thấy rule trong danh sách**
- Refresh trang
- Kiểm tra filters (nếu có)
- Kiểm tra database có rule không

---

## 🎉 HOÀN TẤT

Bây giờ bạn đã có thể quản lý logic rules một cách dễ dàng và trực quan qua giao diện web!



