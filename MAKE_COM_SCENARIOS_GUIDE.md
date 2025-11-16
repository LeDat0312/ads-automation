# 🎯 MAKE.COM SCENARIOS GUIDE

## 📋 CÁC SCENARIO CẦN TẠO

### **SCENARIO 1: Automation Schedule (Chạy tự động mỗi 15 phút)**

**Mục đích:** Chạy automation như bình thường, tự động tắt/bật adsets dựa trên logic rules.

**Modules:**
1. **Schedule** 
   - Interval: Every 15 minutes
   - Time range: 6:00 AM - 11:00 PM (theo timezone của bạn)
   
2. **HTTP** (POST to Google Apps Script)
   - URL: `https://script.google.com/macros/s/YOUR_WEB_APP_ID/exec`
   - Method: POST
   - Headers:
     ```
     Content-Type: application/json
     ```
   - Body:
     ```json
     {
       "action": "run_automation"
     }
     ```

3. **Telegram** (Optional - chỉ gửi nếu có lỗi)
   - Bot Token: `{{TELEGRAM_BOT_TOKEN}}`
   - Chat ID: `{{TELEGRAM_CHAT_ID}}`
   - Message: `🚨 Automation error: {{error}}`

---

### **SCENARIO 2: Pause Adsets (Tắt quảng cáo)**

**Mục đích:** Tắt nhiều adsets cùng lúc (từ AI hoặc manual).

**Modules:**
1. **Webhook** hoặc **Manual trigger**
   - Input: `adset_ids` (array), `account_id`

2. **HTTP** (POST to Google Apps Script)
   - URL: `https://script.google.com/macros/s/YOUR_WEB_APP_ID/exec`
   - Method: POST
   - Body:
     ```json
     {
       "action": "pause_adsets",
       "account_id": "{{account_id}}",
       "adset_ids": {{adset_ids}}
     }
     ```
   - Note: `adset_ids` phải là array, ví dụ: `["123456789", "987654321"]`

3. **Telegram** (Notification)
   - Message: `⏸️ Đã tắt {{success_count}} adsets`

---

### **SCENARIO 3: Resume Adsets (Bật quảng cáo)**

**Mục đích:** Bật lại nhiều adsets cùng lúc.

**Modules:**
1. **Webhook** hoặc **Manual trigger**
   - Input: `adset_ids` (array), `account_id`

2. **HTTP** (POST to Google Apps Script)
   - Body:
     ```json
     {
       "action": "resume_adsets",
       "account_id": "{{account_id}}",
       "adset_ids": {{adset_ids}}
     }
     ```

3. **Telegram** (Notification)
   - Message: `▶️ Đã bật {{success_count}} adsets`

---

### **SCENARIO 4: Increase Budget (Tăng ngân sách)**

**Mục đích:** Tăng ngân sách cho adset.

**Modules:**
1. **Webhook** hoặc **Manual trigger**
   - Input: `adset_id`, `account_id`, `amount`

2. **HTTP** (POST to Google Apps Script)
   - Body:
     ```json
     {
       "action": "adjust_budget",
       "account_id": "{{account_id}}",
       "adset_id": "{{adset_id}}",
       "amount": {{amount}},
       "action_type": "increase"
     }
     ```
   - Note: `amount` là số tiền tăng (ví dụ: 50000 = 50,000 ₫)

3. **Telegram** (Notification)
   - Message: `💰 Đã tăng ngân sách {{adset_id}} thêm {{amount}} ₫`

---

### **SCENARIO 5: Decrease Budget (Giảm ngân sách)**

**Mục đích:** Giảm ngân sách cho adset.

**Modules:**
1. **Webhook** hoặc **Manual trigger**
   - Input: `adset_id`, `account_id`, `amount`

2. **HTTP** (POST to Google Apps Script)
   - Body:
     ```json
     {
       "action": "adjust_budget",
       "account_id": "{{account_id}}",
       "adset_id": "{{adset_id}}",
       "amount": {{amount}},
       "action_type": "decrease"
     }
     ```

3. **Telegram** (Notification)
   - Message: `💰 Đã giảm ngân sách {{adset_id}} đi {{amount}} ₫`

---

### **SCENARIO 6: AI-Powered Automation (với Lexi AI hoặc OpenAI)**

**Mục đích:** AI phân tích performance và tự động quyết định pause/resume/adjust.

**Modules:**
1. **Schedule** → Every 30 minutes

2. **HTTP** → GET Ad Performance Data
   - URL: `https://script.google.com/macros/s/YOUR_WEB_APP_ID/exec?action=get_ad_performance&account_id={{account_id}}&date_preset=yesterday`
   - Method: GET

3. **OpenAI** hoặc **Lexi AI** → Analyze
   - Prompt:
     ```
     Analyze these Facebook ad performance metrics and suggest actions:
     - Which adsets should be paused? (low ROAS, high spend, no results)
     - Which adsets should be resumed? (previously paused but now performing well)
     - Which adsets need budget adjustment? (increase or decrease)
     
     Data: {{ad_performance_data}}
     
     Return JSON format:
     {
       "pause": ["adset_id_1", "adset_id_2"],
       "resume": ["adset_id_3"],
       "increase_budget": [{"adset_id": "adset_id_4", "amount": 50000}],
       "decrease_budget": [{"adset_id": "adset_id_5", "amount": 30000}]
     }
     ```

4. **Router** → Based on AI recommendations
   - If `pause` array not empty → HTTP POST pause_adsets
   - If `resume` array not empty → HTTP POST resume_adsets
   - If `increase_budget` array not empty → HTTP POST adjust_budget (increase)
   - If `decrease_budget` array not empty → HTTP POST adjust_budget (decrease)

5. **Telegram** → Send AI recommendations summary

---

## 🔧 SETUP CHI TIẾT

### **1. Deploy Google Apps Script Web App:**

1. Mở Google Apps Script Editor
2. Thêm file `MakeCom_GoogleScript_Integration.gs` (đã tạo)
3. Vào **Deploy** → **Manage deployments**
4. Click **New deployment**
5. Chọn type: **Web app**
6. Settings:
   - **Execute as:** Me
   - **Who has access:** Anyone
7. Click **Deploy**
8. **Copy Web app URL** (sẽ dùng trong Make.com)

### **2. Tạo Make.com Scenarios:**

#### **Scenario 1: Automation Schedule**
1. Tạo scenario mới
2. Add module: **Schedule**
3. Add module: **HTTP** → POST
4. Add module: **Telegram** (optional)
5. Connect modules
6. Configure từng module

#### **Scenario 2-5: Manual Actions**
1. Tạo scenario mới
2. Add module: **Webhook** hoặc **Manual trigger**
3. Add module: **HTTP** → POST
4. Add module: **Telegram**
5. Connect modules

#### **Scenario 6: AI-Powered**
1. Tạo scenario mới
2. Add module: **Schedule**
3. Add module: **HTTP** → GET
4. Add module: **OpenAI** hoặc **Lexi AI**
5. Add module: **Router**
6. Add modules: **HTTP** → POST (cho từng action)
7. Add module: **Telegram**

---

## 📝 TESTING

### **Test từ Make.com:**

1. **Test Automation:**
   - Trigger scenario 1
   - Check Google Apps Script logs
   - Check Telegram notifications

2. **Test Pause Adsets:**
   - Manual trigger với:
     ```json
     {
       "account_id": "act_123456789",
       "adset_ids": ["123456789012345"]
     }
     ```
   - Verify adset đã bị pause trên Facebook
   - Check Telegram notification

3. **Test Adjust Budget:**
   - Manual trigger với:
     ```json
     {
       "account_id": "act_123456789",
       "adset_id": "123456789012345",
       "amount": 50000,
       "action_type": "increase"
     }
     ```
   - Verify budget đã thay đổi trên Facebook
   - Check Telegram notification

---

## ✅ LỢI ÍCH

### **✅ KHÔNG CẦN VPS:**
- ✅ Chạy 100% trên Make.com + Google Apps Script
- ✅ Không cần maintain server
- ✅ Không cần setup database

### **✅ TẬN DỤNG CODE CŨ:**
- ✅ Dùng lại Google Apps Script hiện tại
- ✅ Logic rules vẫn dùng Google Sheets
- ✅ Không cần migrate

### **✅ AI INTEGRATION:**
- ✅ Dễ tích hợp AI (OpenAI, Lexi AI)
- ✅ AI có thể quyết định actions
- ✅ Thông báo qua Telegram

---

**Bạn muốn tôi tạo Make.com scenario template JSON không? 🚀**

