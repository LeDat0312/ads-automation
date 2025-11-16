# 🔗 MAKE.COM + GOOGLE APPS SCRIPT INTEGRATION

## 🎯 MỤC TIÊU

Sử dụng 100% Make.com kết hợp với Google Apps Script hiện tại để:
- ✅ Tắt/bật quảng cáo (pause/resume adsets)
- ✅ Tăng/giảm ngân sách (increase/decrease budget)
- ✅ Hỗ trợ nhiều tài khoản và nhiều chiến dịch
- ✅ Thông báo qua Telegram

**KHÔNG CẦN VPS!** Chỉ cần Make.com + Google Apps Script.

---

## 🏗️ KIẾN TRÚC

```
┌─────────────────────────────────────────┐
│         MAKE.COM SCENARIO               │
│                                         │
│  1. Schedule Trigger (Every 15 min)     │
│  2. HTTP Request → Google Apps Script   │
│  3. Google Apps Script xử lý:           │
│     - Pull Facebook data                │
│     - Check logic rules                 │
│     - Pause/Resume adsets               │
│     - Increase/Decrease budget          │
│  4. Telegram Notification               │
└──────────────┬──────────────────────────┘
               │
               ├─→ GOOGLE APPS SCRIPT
               │   - doPost() endpoint
               │   - runAutomation()
               │   - pauseAdsets()
               │   - resumeAdsets()
               │   - adjustBudget()
               │
               ├─→ FACEBOOK API
               │   - Get insights
               │   - Pause/Resume adsets
               │   - Update budget
               │
               └─→ TELEGRAM
                   - Send notifications
```

---

## 📋 SETUP GOOGLE APPS SCRIPT

### **BƯỚC 1: Tạo Web App Endpoint cho Make.com**

Thêm vào `Code.gs`:

```javascript
/**
 * Web App endpoint cho Make.com
 * Make.com sẽ gọi endpoint này để trigger automation
 */
function doPost(e) {
  try {
    var params = JSON.parse(e.postData.contents);
    var action = params.action || 'run_automation';
    
    Logger.log("📥 Make.com request received: " + action);
    
    var result = {};
    
    switch(action) {
      case 'run_automation':
        // Chạy automation như bình thường
        runAutomation();
        result = { success: true, message: "Automation started" };
        break;
        
      case 'pause_adsets':
        // Tắt adsets
        var adsetIds = params.adset_ids || [];
        var accountId = params.account_id;
        result = pauseAdsetsBatch(accountId, adsetIds);
        break;
        
      case 'resume_adsets':
        // Bật adsets
        var adsetIds = params.adset_ids || [];
        var accountId = params.account_id;
        result = resumeAdsetsBatch(accountId, adsetIds);
        break;
        
      case 'adjust_budget':
        // Tăng/giảm ngân sách
        var adsetId = params.adset_id;
        var accountId = params.account_id;
        var amount = params.amount; // Số tiền tăng/giảm (có thể âm)
        var action_type = params.action_type; // 'increase' hoặc 'decrease'
        result = adjustAdsetBudget(accountId, adsetId, amount, action_type);
        break;
        
      case 'get_status':
        // Lấy trạng thái
        result = getAutomationStatus();
        break;
        
      default:
        result = { success: false, message: "Unknown action" };
    }
    
    return ContentService.createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    Logger.log("🚨 Error in doPost: " + error.message);
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * GET endpoint (optional, để test)
 */
function doGet(e) {
  var action = e.parameter.action || 'status';
  
  if (action === 'status') {
    var status = getAutomationStatus();
    return ContentService.createTextOutput(JSON.stringify(status))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput("OK");
}
```

### **BƯỚC 2: Thêm Functions cho Make.com**

Thêm vào `Code.gs` hoặc file riêng:

```javascript
/**
 * Pause adsets batch (cho Make.com)
 */
function pauseAdsetsBatch(accountId, adsetIds) {
  try {
    var settings = layCaiDatHeThong();
    var accessToken = settings['FACEBOOK_ACCESS_TOKEN'];
    
    if (!accessToken) {
      return { success: false, message: "No access token" };
    }
    
    var successCount = 0;
    var errorCount = 0;
    var errors = [];
    
    for (var i = 0; i < adsetIds.length; i++) {
      var adsetId = adsetIds[i];
      try {
        var url = `https://graph.facebook.com/v18.0/${adsetId}`;
        var payload = {
          status: 'PAUSED'
        };
        
        var options = {
          method: 'post',
          headers: {
            'Authorization': 'Bearer ' + accessToken,
            'Content-Type': 'application/json'
          },
          payload: JSON.stringify(payload)
        };
        
        var response = UrlFetchApp.fetch(url, options);
        var result = JSON.parse(response.getContentText());
        
        if (result.success) {
          successCount++;
        } else {
          errorCount++;
          errors.push({ adset_id: adsetId, error: result.error });
        }
      } catch (e) {
        errorCount++;
        errors.push({ adset_id: adsetId, error: e.message });
      }
    }
    
    // Gửi thông báo Telegram
    var message = `⏸️ Đã tắt ${successCount} adsets\n`;
    if (errorCount > 0) {
      message += `⚠️ Lỗi: ${errorCount} adsets\n`;
    }
    guiThongBaoTelegram(message, settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID']);
    
    return {
      success: true,
      success_count: successCount,
      error_count: errorCount,
      errors: errors
    };
    
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Resume adsets batch (cho Make.com)
 */
function resumeAdsetsBatch(accountId, adsetIds) {
  try {
    var settings = layCaiDatHeThong();
    var accessToken = settings['FACEBOOK_ACCESS_TOKEN'];
    
    if (!accessToken) {
      return { success: false, message: "No access token" };
    }
    
    var successCount = 0;
    var errorCount = 0;
    var errors = [];
    
    for (var i = 0; i < adsetIds.length; i++) {
      var adsetId = adsetIds[i];
      try {
        var url = `https://graph.facebook.com/v18.0/${adsetId}`;
        var payload = {
          status: 'ACTIVE'
        };
        
        var options = {
          method: 'post',
          headers: {
            'Authorization': 'Bearer ' + accessToken,
            'Content-Type': 'application/json'
          },
          payload: JSON.stringify(payload)
        };
        
        var response = UrlFetchApp.fetch(url, options);
        var result = JSON.parse(response.getContentText());
        
        if (result.success) {
          successCount++;
        } else {
          errorCount++;
          errors.push({ adset_id: adsetId, error: result.error });
        }
      } catch (e) {
        errorCount++;
        errors.push({ adset_id: adsetId, error: e.message });
      }
    }
    
    // Gửi thông báo Telegram
    var message = `▶️ Đã bật ${successCount} adsets\n`;
    if (errorCount > 0) {
      message += `⚠️ Lỗi: ${errorCount} adsets\n`;
    }
    guiThongBaoTelegram(message, settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID']);
    
    return {
      success: true,
      success_count: successCount,
      error_count: errorCount,
      errors: errors
    };
    
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Adjust adset budget (tăng/giảm ngân sách)
 */
function adjustAdsetBudget(accountId, adsetId, amount, actionType) {
  try {
    var settings = layCaiDatHeThong();
    var accessToken = settings['FACEBOOK_ACCESS_TOKEN'];
    
    if (!accessToken) {
      return { success: false, message: "No access token" };
    }
    
    // Lấy budget hiện tại
    var url = `https://graph.facebook.com/v18.0/${adsetId}?fields=daily_budget,lifetime_budget&access_token=${accessToken}`;
    var response = UrlFetchApp.fetch(url);
    var adsetData = JSON.parse(response.getContentText());
    
    var currentBudget = parseFloat(adsetData.daily_budget || adsetData.lifetime_budget || 0);
    var newBudget = currentBudget;
    
    if (actionType === 'increase') {
      newBudget = currentBudget + Math.abs(amount);
    } else if (actionType === 'decrease') {
      newBudget = Math.max(0, currentBudget - Math.abs(amount));
    } else {
      // Set absolute value
      newBudget = amount;
    }
    
    // Update budget
    var updateUrl = `https://graph.facebook.com/v18.0/${adsetId}`;
    var payload = {
      daily_budget: Math.round(newBudget * 100) / 100  // Round to 2 decimals
    };
    
    var options = {
      method: 'post',
      headers: {
        'Authorization': 'Bearer ' + accessToken,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload)
    };
    
    var updateResponse = UrlFetchApp.fetch(updateUrl, options);
    var result = JSON.parse(updateResponse.getContentText());
    
    if (result.success) {
      var message = `💰 Ngân sách adset ${adsetId}:\n`;
      message += `Từ: ${currentBudget.toLocaleString()} ₫\n`;
      message += `Thành: ${newBudget.toLocaleString()} ₫\n`;
      message += `Thay đổi: ${(newBudget - currentBudget).toLocaleString()} ₫`;
      
      guiThongBaoTelegram(message, settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID']);
      
      return {
        success: true,
        adset_id: adsetId,
        old_budget: currentBudget,
        new_budget: newBudget,
        change: newBudget - currentBudget
      };
    } else {
      return { success: false, error: result.error };
    }
    
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Get automation status (cho Make.com)
 */
function getAutomationStatus() {
  try {
    var settings = layCaiDatHeThong();
    var status = getAllAutomationStatus();
    
    return {
      success: true,
      settings: {
        has_token: !!settings['FACEBOOK_ACCESS_TOKEN'],
        has_accounts: !!settings['AD_ACCOUNT_IDS'],
        has_telegram: !!(settings['TELEGRAM_BOT_TOKEN'] && settings['TELEGRAM_CHAT_ID'])
      },
      automation_status: status,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

### **BƯỚC 3: Deploy Web App**

1. Vào **Deploy** → **Manage deployments**
2. Click **New deployment**
3. Chọn type: **Web app**
4. Settings:
   - **Execute as:** Me
   - **Who has access:** Anyone
5. Click **Deploy**
6. Copy **Web app URL** (sẽ dùng trong Make.com)

---

## 🔧 SETUP MAKE.COM SCENARIO

### **SCENARIO 1: Automation Schedule (Chạy tự động)**

**Modules:**
1. **Schedule** → Every 15 minutes (6:00 AM - 11:00 PM)
2. **HTTP** → POST to Google Apps Script
   - URL: `https://script.google.com/macros/s/YOUR_WEB_APP_ID/exec`
   - Method: POST
   - Body:
     ```json
     {
       "action": "run_automation"
     }
     ```
3. **Telegram** → Send message (nếu có lỗi)

### **SCENARIO 2: Pause Adsets (Manual hoặc từ AI)**

**Modules:**
1. **Webhook** hoặc **Manual trigger**
2. **HTTP** → POST to Google Apps Script
   - URL: `https://script.google.com/macros/s/YOUR_WEB_APP_ID/exec`
   - Method: POST
   - Body:
     ```json
     {
       "action": "pause_adsets",
       "account_id": "act_123456789",
       "adset_ids": ["adset_id_1", "adset_id_2"]
     }
     ```
3. **Telegram** → Send notification

### **SCENARIO 3: Resume Adsets**

**Modules:**
1. **Webhook** hoặc **Manual trigger**
2. **HTTP** → POST to Google Apps Script
   - Body:
     ```json
     {
       "action": "resume_adsets",
       "account_id": "act_123456789",
       "adset_ids": ["adset_id_1", "adset_id_2"]
     }
     ```
3. **Telegram** → Send notification

### **SCENARIO 4: Adjust Budget**

**Modules:**
1. **Webhook** hoặc **Manual trigger**
2. **HTTP** → POST to Google Apps Script
   - Body:
     ```json
     {
       "action": "adjust_budget",
       "account_id": "act_123456789",
       "adset_id": "adset_id_1",
       "amount": 50000,
       "action_type": "increase"
     }
     ```
3. **Telegram** → Send notification

### **SCENARIO 5: AI-Powered Automation (với Lexi AI hoặc OpenAI)**

**Modules:**
1. **Schedule** → Every 30 minutes
2. **HTTP** → GET Facebook Insights (hoặc gọi Google Apps Script để lấy data)
3. **OpenAI** hoặc **Lexi AI** → Analyze data
   - Prompt: "Analyze these ad performance metrics and suggest which adsets to pause, resume, or adjust budget"
4. **Data Store** → Store AI recommendations
5. **Router** → Based on AI recommendation
   - If pause → HTTP POST pause_adsets
   - If resume → HTTP POST resume_adsets
   - If adjust budget → HTTP POST adjust_budget
6. **Telegram** → Send AI recommendations

---

## 📋 MAKE.COM MODULE CONFIGURATION

### **HTTP Module (POST to Google Apps Script):**

```
URL: https://script.google.com/macros/s/YOUR_WEB_APP_ID/exec
Method: POST
Headers:
  Content-Type: application/json
Body:
  {
    "action": "{{action}}",
    "account_id": "{{account_id}}",
    "adset_ids": {{adset_ids}},
    "amount": {{amount}},
    "action_type": "{{action_type}}"
  }
```

### **Telegram Module:**

```
Bot Token: {{TELEGRAM_BOT_TOKEN}}
Chat ID: {{TELEGRAM_CHAT_ID}}
Message: {{message}}
```

---

## 🎯 USAGE EXAMPLES

### **1. Chạy Automation tự động:**
Make.com sẽ gọi Google Apps Script mỗi 15 phút:
```json
{
  "action": "run_automation"
}
```

### **2. Tắt adsets từ Make.com:**
```json
{
  "action": "pause_adsets",
  "account_id": "act_123456789",
  "adset_ids": ["123456789012345", "987654321098765"]
}
```

### **3. Tăng ngân sách:**
```json
{
  "action": "adjust_budget",
  "account_id": "act_123456789",
  "adset_id": "123456789012345",
  "amount": 50000,
  "action_type": "increase"
}
```

### **4. Giảm ngân sách:**
```json
{
  "action": "adjust_budget",
  "account_id": "act_123456789",
  "adset_id": "123456789012345",
  "amount": 30000,
  "action_type": "decrease"
}
```

---

## ✅ LỢI ÍCH

### **✅ KHÔNG CẦN VPS:**
- ✅ Chạy 100% trên Make.com + Google Apps Script
- ✅ Không cần maintain server
- ✅ Không cần setup database

### **✅ TẬN DỤNG CODE CŨ:**
- ✅ Dùng lại Google Apps Script hiện tại
- ✅ Không cần migrate code
- ✅ Logic rules vẫn dùng Google Sheets

### **✅ AI INTEGRATION:**
- ✅ Dễ tích hợp AI (OpenAI, Lexi AI)
- ✅ AI có thể quyết định pause/resume/adjust
- ✅ Thông báo qua Telegram

---

## 📝 NEXT STEPS

1. ✅ Thêm functions vào Google Apps Script
2. ✅ Deploy Web App
3. ✅ Tạo Make.com scenarios
4. ✅ Test từng scenario
5. ✅ Setup schedule automation

---

**Bạn muốn tôi tạo file Google Apps Script code đầy đủ không? 🚀**

