/**
 * ==================================================================
 * DEPLOY HELPER - Hỗ trợ deploy và test nhanh
 * ==================================================================
 * Các hàm helper để deploy và test code nhanh hơn
 * ==================================================================
 */

/**
 * Clear cache và properties để test lại từ đầu
 * Hữu ích khi test lại từ đầu hoặc debug
 * 
 * CÁCH SỬ DỤNG:
 * 1. Chạy hàm này trong Apps Script Editor
 * 2. Xem log để biết đã xóa bao nhiêu keys
 */
function clearCacheAndProperties() {
  try {
    Logger.log("🧹 Bắt đầu clear cache và properties...");
    
    // Clear CacheService
    try {
      var cache = CacheService.getScriptCache();
      // CacheService không có hàm clear all, nên chúng ta chỉ có thể log
      Logger.log("⚠️ CacheService không hỗ trợ clear all. Cache sẽ tự động expire sau 6 giờ.");
      Logger.log("💡 Để clear cache ngay lập tức, cần biết các keys cụ thể.");
    } catch (e) {
      Logger.log("⚠️ Lỗi clear cache: " + e.message);
    }
    
    // Clear PropertiesService (chỉ clear các key liên quan đến Telegram)
    try {
      var props = PropertiesService.getScriptProperties();
      var allProps = props.getProperties();
      var clearedCount = 0;
      var clearedKeys = [];
      
      for (var key in allProps) {
        // Chỉ xóa các key liên quan đến Telegram (UPD_, PROCESSED_MSG_, etc.)
        if (key.startsWith('UPD_') || 
            key.startsWith('PROCESSED_MSG_') || 
            key.startsWith('COMMAND_RATE_LIMIT_') || 
            key.startsWith('USER_RATE_') ||
            key.startsWith('PENDING_') ||
            key.startsWith('LAST_')) {
          props.deleteProperty(key);
          clearedCount++;
          clearedKeys.push(key);
        }
      }
      
      Logger.log("✅ Đã xóa " + clearedCount + " properties liên quan đến Telegram");
      if (clearedKeys.length > 0) {
        Logger.log("📋 Các keys đã xóa: " + clearedKeys.join(", "));
      }
    } catch (e) {
      Logger.log("🚨 Lỗi clear properties: " + e.message);
    }
    
    Logger.log("✅ Clear cache và properties hoàn thành!");
    
  } catch (e) {
    Logger.log("🚨 Lỗi clear: " + e.message);
    Logger.log("Stack: " + e.stack);
  }
}

/**
 * Kiểm tra trạng thái webhook và các update đang chờ
 * Hữu ích để debug vấn đề webhook
 */
function checkWebhookStatus() {
  try {
    Logger.log("🔍 Kiểm tra trạng thái webhook...");
    
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    
    if (!botToken) {
      Logger.log("❌ Không có Bot Token");
      return;
    }
    
    // Kiểm tra webhook info
    var url = "https://api.telegram.org/bot" + botToken + "/getWebhookInfo";
    var response = UrlFetchApp.fetch(url);
    var result = JSON.parse(response.getContentText());
    
    if (result.ok) {
      var info = result.result;
      Logger.log("📋 Webhook Info:");
      Logger.log("   URL: " + (info.url || "N/A"));
      Logger.log("   Pending updates: " + (info.pending_update_count || 0));
      Logger.log("   Last error date: " + (info.last_error_date || "N/A"));
      Logger.log("   Last error message: " + (info.last_error_message || "N/A"));
      Logger.log("   Max connections: " + (info.max_connections || "N/A"));
    } else {
      Logger.log("❌ Lỗi kiểm tra webhook: " + result.description);
    }
    
  } catch (e) {
    Logger.log("🚨 Lỗi check webhook status: " + e.message);
  }
}

/**
 * Test code locally (không cần deploy)
 * Hàm này sẽ test các hàm chính mà không cần deploy Web App
 * 
 * CÁCH SỬ DỤNG:
 * 1. Chạy hàm này trong Apps Script Editor
 * 2. Hàm sẽ test các hàm chính (doPost, processWebhookUpdate_, etc.)
 * 3. Xem kết quả trong Execution log
 */
function testLocal() {
  try {
    Logger.log("🧪 Bắt đầu test local...");
    
    // Test 1: Test parse update
    Logger.log("📝 Test 1: Parse update...");
    var mockUpdate = {
      update_id: 123456789,
      message: {
        message_id: 100,
        chat: {
          id: -1003177284243,
          type: "supergroup",
          title: "Test Group"
        },
        from: {
          id: 1150577493,
          first_name: "Test",
          username: "testuser"
        },
        text: "/test",
        date: Math.floor(Date.now() / 1000)
      }
    };
    
    var mockEvent = {
      postData: {
        contents: JSON.stringify(mockUpdate)
      }
    };
    
    Logger.log("✅ Mock update created: " + JSON.stringify(mockUpdate));
    
    // Test 2: Test processWebhookUpdate_
    Logger.log("📝 Test 2: Test processWebhookUpdate_...");
    try {
      var result = processWebhookUpdate_(mockEvent);
      Logger.log("✅ processWebhookUpdate_ returned: " + result + " (type: " + typeof result + ")");
    } catch (e) {
      Logger.log("🚨 processWebhookUpdate_ error: " + e.message);
      Logger.log("Stack: " + e.stack);
    }
    
    // Test 3: Test doPost (simulate full flow)
    Logger.log("📝 Test 3: Test doPost (full flow)...");
    try {
      // Clear cache trước khi test
      var cache = CacheService.getScriptCache();
      var key = 'UPD_' + String(mockUpdate.update_id);
      cache.remove(key);
      Logger.log("✅ Đã xóa cache cho Update ID: " + mockUpdate.update_id);
      
      // Test doPost
      var response = doPost(mockEvent);
      Logger.log("✅ doPost returned: " + (response ? "Response object" : "null"));
      
      // Kiểm tra xem update_id có được đánh dấu không
      var cached = cache.get(key);
      if (cached) {
        Logger.log("✅ Update ID đã được đánh dấu trong cache: " + key);
      } else {
        Logger.log("⚠️ Update ID CHƯA được đánh dấu trong cache (có thể xử lý thất bại)");
      }
    } catch (e) {
      Logger.log("🚨 doPost error: " + e.message);
      Logger.log("Stack: " + e.stack);
    }
    
    // Test 4: Test multiple updates (simulate multiple commands)
    Logger.log("📝 Test 4: Test multiple updates (simulate /test, /help, /status)...");
    try {
      var updates = [
        { update_id: 123456790, text: "/test" },
        { update_id: 123456791, text: "/help" },
        { update_id: 123456792, text: "/status" }
      ];
      
      for (var i = 0; i < updates.length; i++) {
        var upd = updates[i];
        var mockUpd = {
          update_id: upd.update_id,
          message: {
            message_id: 100 + i,
            chat: {
              id: -1003177284243,
              type: "supergroup",
              title: "Test Group"
            },
            from: {
              id: 1150577493,
              first_name: "Test",
              username: "testuser"
            },
            text: upd.text,
            date: Math.floor(Date.now() / 1000) + i
          }
        };
        
        var mockEvt = {
          postData: {
            contents: JSON.stringify(mockUpd)
          }
        };
        
        // Clear cache trước
        var cacheKey = 'UPD_' + String(upd.update_id);
        cache.remove(cacheKey);
        
        Logger.log("🔄 Test update " + (i + 1) + ": " + upd.text + " (Update ID: " + upd.update_id + ")");
        var result = doPost(mockEvt);
        Logger.log("✅ Update " + (i + 1) + " processed. Response: " + (result ? "OK" : "null"));
        
        // Kiểm tra cache
        var cached = cache.get(cacheKey);
        if (cached) {
          Logger.log("✅ Update ID " + upd.update_id + " đã được đánh dấu");
        } else {
          Logger.log("⚠️ Update ID " + upd.update_id + " CHƯA được đánh dấu");
        }
      }
    } catch (e) {
      Logger.log("🚨 Test multiple updates error: " + e.message);
      Logger.log("Stack: " + e.stack);
    }
    
    Logger.log("✅ Test local hoàn thành!");
    
  } catch (e) {
    Logger.log("🚨 Lỗi test local: " + e.message);
    Logger.log("Stack: " + e.stack);
  }
}