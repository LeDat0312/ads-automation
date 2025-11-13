# 🎨 HƯỚNG DẪN: GIAO DIỆN QUẢN LÝ RULES V2

## 🚀 TỔNG QUAN

Giao diện V2 cải tiến với:
- ✅ **Tree View**: Chọn account và prefix trực quan
- ✅ **Mục tiêu**: Chọn E-commerce hoặc Lead
- ✅ **Condition Builder**: Form trực quan, không cần viết JSON
- ✅ **Sửa lỗi**: Đã fix lỗi "[object Object]"

---

## 📍 TRUY CẬP

Sau khi pull code về VPS:

```
https://updatemetaads.site/rules-v2/
```

Hoặc local:
```
http://localhost:8000/rules-v2/
```

---

## 🎯 TÍNH NĂNG CHÍNH

### **1. Tree View (Bên trái)**

- **Tất cả**: Xem tất cả rules
- **Account**: Click để mở rộng → thấy các prefix
- **Prefix**: Click để chọn account + prefix cụ thể

### **2. Chọn Mục tiêu**

- **🛒 Thương mại điện tử**: Focus vào Purchase, Revenue, ROAS
- **📞 Số lượng khách hàng tiềm năng**: Focus vào Leads, CPL, Checkouts

### **3. Condition Builder**

Không cần viết JSON! Chỉ cần:
1. Chọn metric (Chi tiêu, CPL, CPA, ROAS, etc.)
2. Chọn operator (>, <, >=, <=, ==, !=)
3. Nhập giá trị
4. Chọn timeframe (Hôm nay, Hôm qua, 3 ngày, 7 ngày)
5. Click "+ Thêm điều kiện" để thêm nhiều điều kiện

### **4. Actions**

- **Tăng Budget**: Tăng ngân sách khi điều kiện đúng
- **Giảm Budget**: Giảm ngân sách khi điều kiện đúng
- **Tạm dừng**: Tắt adset khi điều kiện đúng
- **Tiếp tục**: Bật lại adset khi điều kiện đúng

---

## 📝 CÁCH SỬ DỤNG

### **Bước 1: Chọn Account & Prefix**

1. Click vào account trong tree view bên trái
2. Account sẽ mở rộng → thấy các prefix
3. Click vào prefix cần cấu hình
4. Form sẽ tự động điền Account và Prefix

### **Bước 2: Chọn Mục tiêu**

1. Click **"🛒 Thương mại điện tử"** hoặc **"📞 Số lượng khách hàng tiềm năng"**
2. Mục tiêu sẽ được lưu vào rule

### **Bước 3: Điền thông tin**

1. **Tên Rule**: VD: "Tăng budget khi CPL thấp"
2. **Điều kiện**: 
   - Chọn metric (VD: CPL)
   - Chọn operator (VD: <)
   - Nhập giá trị (VD: 50000)
   - Chọn timeframe (VD: Hôm nay)
   - Click "+ Thêm điều kiện" nếu cần nhiều điều kiện
3. **Action**: Chọn action (VD: Tăng Budget)
4. **Action Params** (tùy chọn): VD: `{"percent": 20}`
5. **Trạng thái**: Chọn DRAFT/LIVE/PAUSED

### **Bước 4: Lưu**

Click **"💾 Lưu Rule"**

---

## 📊 VÍ DỤ RULES

### **Ví dụ 1: E-commerce - Tăng budget khi ROAS tốt**

- **Account**: `act_723686686812438`
- **Prefix**: `PX`
- **Mục tiêu**: 🛒 Thương mại điện tử
- **Điều kiện**:
  - Metric: `ROAS`
  - Operator: `>`
  - Value: `2.0`
  - Timeframe: `Hôm nay`
- **Action**: `INCREASE_BUDGET`
- **Action Params**: `{"percent": 20}`

### **Ví dụ 2: Lead - Tạm dừng khi CPL cao**

- **Account**: `act_2827767517395636`
- **Prefix**: `FL`
- **Mục tiêu**: 📞 Số lượng khách hàng tiềm năng
- **Điều kiện**:
  - Metric: `CPL`
  - Operator: `>`
  - Value: `50000`
  - Timeframe: `Hôm nay`
- **Action**: `PAUSE`

### **Ví dụ 3: E-commerce - Tạm dừng khi chi tiêu cao, không có purchase**

- **Account**: `act_1027270998695466`
- **Prefix**: `LAKVDH`
- **Mục tiêu**: 🛒 Thương mại điện tử
- **Điều kiện** (2 điều kiện):
  1. Metric: `spend` > `100000` (Hôm nay)
  2. Metric: `purchases` == `0` (Hôm nay)
- **Action**: `PAUSE`

### **Ví dụ 4: Lead - Tiếp tục khi có checkouts**

- **Account**: `act_723686686812438`
- **Prefix**: `TL`
- **Mục tiêu**: 📞 Số lượng khách hàng tiềm năng
- **Điều kiện**:
  - Metric: `checkouts` > `0`
  - Timeframe: `Hôm nay`
- **Action**: `RESUME`

---

## 🔧 METRICS CÓ SẴN

### **E-commerce Metrics:**
- `spend` - Chi tiêu
- `roas` - Return on ad spend
- `purchases` - Lượt mua
- `purchase_value` - Giá trị chuyển đổi
- `cpa` - Cost per action
- `results` - Kết quả
- `gia_data` - Giá DATA

### **Lead Metrics:**
- `spend` - Chi tiêu
- `cpl` - Cost per lead
- `leads` - Leads
- `checkouts` - Checkouts Initiated (SĐT)
- `results` - Kết quả
- `gia_data` - Giá DATA

---

## 🎯 MỤC TIÊU VÀ LOGIC

### **Thương mại điện tử (E-commerce):**

**Focus vào:**
- Giá DATA
- Lượt mua (Purchases)
- Giá trị chuyển đổi (Purchase Value)
- ROAS
- % ADS (nếu có)

**Ví dụ rules:**
- Tăng budget khi ROAS > 2.0
- Tạm dừng khi chi tiêu > 100k và purchases = 0
- Giảm budget khi CPA > 50k

### **Số lượng khách hàng tiềm năng (Lead):**

**Focus vào:**
- Giá DATA
- Chi phí trên mỗi lượt bắt đầu thanh toán (CPL)
- Tổng số lượt bắt đầu thanh toán (Checkouts)
- Tổng số lượt mua (Purchases - nếu có)

**Ví dụ rules:**
- Tạm dừng khi CPL > 50k
- Tiếp tục khi checkouts > 0
- Tăng budget khi CPL < 30k và checkouts > 5

---

## 📋 CÁC GIAI ĐOẠN (Từ Google Sheet)

Dựa trên [Google Sheet LogicRules](https://docs.google.com/spreadsheets/d/1U6gMFmXU1_IBeuA_7SnN4ZIxAr4Dp0-aOmjbMyaFFjo/edit?gid=906414426#gid=906414426):

### **GIAI ĐOẠN 1 - LỌC DATA (Stop Loss)**
- **Điều kiện**: `spend > SL_GIAI_DOAN_1_SPEND` AND `results < SL_GIAI_DOAN_1_DATA`
- **Action**: `PAUSE`

### **GIAI ĐOẠN 2 - CẮT LỖ 2 (Spend & Giá DATA)**
- **Điều kiện**: `spend > SL_GIAI_DOAN_2_SPEND` AND `gia_data > SL_GIAI_DOAN_2_GIA_DATA`
- **Action**: `PAUSE`

### **GIAI ĐOẠN 3 - ĐÁNH GIÁ CPL**
- **Điều kiện**: `leads >= SL_GIAI_DOAN_3_MIN_LEADS` AND `cpl > SL_GIAI_DOAN_3_MAX_CPL`
- **Action**: `PAUSE`

### **GIAI ĐOẠN 4 - ĐÁNH GIÁ CPA**
- **Điều kiện**: `purchases >= SL_GIAI_DOAN_4_MIN_PURCHASE` AND `cpa > SL_GIAI_DOAN_4_MAX_CPA`
- **Action**: `PAUSE`

### **CHỐNG MỎI - FREQUENCY**
- **Điều kiện**: `frequency > SL_MAX_FREQUENCY`
- **Action**: `PAUSE`

### **BẬT LẠI QUẢNG CÁO (Resume)**
- **Điều kiện**: `spend > RESUME_SPEND` AND `results >= RESUME_DATA`
- **Action**: `RESUME`

---

## ⚠️ LƯU Ý

1. **Chọn Account/Prefix**: Phải chọn từ tree view trước khi tạo rule
2. **Điều kiện**: Phải có ít nhất 1 điều kiện
3. **Mục tiêu**: Chọn đúng mục tiêu để rule áp dụng đúng logic
4. **Status**: 
   - `DRAFT` - Nháp, không chạy
   - `LIVE` - Đang chạy
   - `PAUSED` - Tạm dừng

---

## 🔄 SO SÁNH V1 vs V2

| Tính năng | V1 (`/rules/`) | V2 (`/rules-v2/`) |
|-----------|----------------|-------------------|
| Chọn Account/Prefix | Checkbox | Tree view trực quan |
| Mục tiêu | Không có | Có (E-commerce/Lead) |
| Condition Builder | Phải viết JSON | Form trực quan |
| Sửa lỗi | Có lỗi "[object Object]" | Đã fix |

**Khuyến nghị**: Dùng V2 (`/rules-v2/`) vì trực quan và dễ dùng hơn!

---

## ✅ CHECKLIST

- [ ] Pull code về VPS
- [ ] Restart API service
- [ ] Truy cập `/rules-v2/`
- [ ] Test tạo rule mới
- [ ] Test chọn account/prefix từ tree view
- [ ] Test chọn mục tiêu
- [ ] Test condition builder
- [ ] Test sửa/xóa rule

---

## 🆘 TROUBLESHOOTING

### **Lỗi: "[object Object]"**
- ✅ Đã fix trong V2
- Nếu vẫn gặp, check browser console để xem chi tiết lỗi

### **Không thấy account trong tree view**
- Kiểm tra `AD_ACCOUNT_IDS` trong `.env`
- Refresh trang

### **Condition builder không hoạt động**
- Kiểm tra JavaScript console
- Đảm bảo đã chọn đầy đủ: metric, operator, value

---

## 🎉 HOÀN TẤT

Bây giờ bạn có giao diện trực quan và mạnh mẽ để quản lý logic rules cho từng account và prefix!



