/**
 * ==================================================================
 * Telegram.gs - QUẢN LÝ THÔNG BÁO TELEGRAM
 * ==================================================================
 * Hàm gửi thông báo đến Telegram Bot
 * Hỗ trợ Markdown formatting và error handling
 * ==================================================================
 */

/**
 * Chuyển đổi Markdown sang HTML để tránh lỗi parse
 * HTML an toàn hơn Markdown vì chỉ cần escape & < > và không có vấn đề với ký tự đặc biệt
 * @param {string} text - Text có thể chứa Markdown
 * @returns {string} - Text đã chuyển sang HTML
 */
function markdownToHtml(text) {
  if (!text) return '';
  var str = String(text);
  
  // Bước 1: Escape HTML entities trước (để tránh conflict với HTML tags)
  str = str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  
  // Bước 2: Chuyển đổi Markdown sang HTML
  // Pattern 1: **text** (bold với 2 dấu sao) - ưu tiên trước
  str = str.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
  
  // Pattern 2: *text* (bold với 1 dấu sao) - chỉ khi không phải là dấu sao đơn lẻ
  str = str.replace(/\*([^*\n]+?)\*/g, function(match, content) {
    if (content.trim().length > 0 && !content.match(/^\s*$/)) {
      return '<b>' + content + '</b>';
    }
    return match;
  });
  
  // Pattern 3: _text_ (italic)
  str = str.replace(/_([^_\n]+?)_/g, function(match, content) {
    if (content.trim().length > 0 && !content.match(/^\s*$/)) {
      return '<i>' + content + '</i>';
    }
    return match;
  });
  
  // Pattern 4: `text` (code)
  str = str.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  return str;
}

/**
 * Chuẩn hóa lệnh Telegram: lấy /command và bỏ phần @BotName nếu có
 * Ví dụ: "/reset_webhook@drkim_ads_bot" → "/reset_webhook"
 * @param {string} text - Text có thể chứa lệnh với @BotName
 * @returns {string} - Lệnh đã được chuẩn hóa (chỉ có /command)
 */
function extractCommand_(text) {
  if (!text) return '';
  
  // Lấy token đầu tiên bắt đầu bằng / và chỉ lấy phần chữ-số-gạch dưới (bỏ @BotName)
  var m = text.match(/^\/([a-zA-Z0-9_]+)(@\S+)?/);
  if (!m) return '';
  
  // Trả về /command (bỏ phần @BotName nếu có)
  return '/' + m[1].toLowerCase();
}

/**
 * Gửi một tin nhắn đến kênh/chat Telegram
 * @param {string} message - Tin nhắn cần gửi (hỗ trợ Markdown)
 * @param {string} botToken - Mã Token của Bot Telegram (từ BotFather)
 * @param {string} chatId - ID của nhóm/kênh/người nhận
 * @returns {boolean} - true nếu gửi thành công, false nếu thất bại
 */
function guiThongBaoTelegram(message, botToken, chatId, replyToMessageId) {
  // Kiểm tra tham số đầu vào
  if (!message || !botToken || !chatId) {
    Logger.log("⚠️ LỖI TELEGRAM: Thiếu Bot Token, Chat ID hoặc Message. BotToken=" + (botToken ? "✓" : "✗") + ", ChatID=" + (chatId ? "✓" : "✗") + ", Message=" + (message ? "✓" : "✗"));
    return false;
  }
  
  // ⚠️ QUAN TRỌNG: KHÔNG BAO GIỜ gửi message vào chat cá nhân (Chat ID dương)
  // Bot chỉ hoạt động trong nhóm (Chat ID âm)
  var chatIdNum = parseInt(String(chatId).trim(), 10);
  if (chatIdNum > 0) {
    // Chat ID dương = chat cá nhân → KHÔNG GỬI
    Logger.log("⚠️ CHẶN GỬI MESSAGE: Chat ID " + chatId + " là chat cá nhân. Bot chỉ gửi message vào nhóm (Chat ID âm).");
    return false; // Không gửi, không log error
  }
  
  // URL API của Telegram Bot
  var url = "https://api.telegram.org/bot" + botToken + "/sendMessage";

  // Chuyển đổi Markdown sang HTML để tránh lỗi parse
  // HTML an toàn hơn vì chỉ cần escape & < > và không có vấn đề với ký tự đặc biệt
  var htmlMessage = markdownToHtml(String(message));
  
  // Chuẩn bị payload
  var payload = {
    'chat_id': String(chatId).trim(),
    'text': htmlMessage,
    'parse_mode': 'HTML', // Dùng HTML thay vì Markdown (an toàn hơn, ít lỗi parse)
    'disable_web_page_preview': false // Cho phép preview link
  };
  
  // ⚠️ QUAN TRỌNG: Thêm reply_to_message_id nếu có (để bot có thể @ người gửi)
  if (replyToMessageId) {
    payload['reply_to_message_id'] = parseInt(replyToMessageId, 10);
  }
  
  // Cấu hình request
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true // Không throw exception, chỉ log
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    // Kiểm tra response
    if (responseCode === 200) {
      var json = JSON.parse(responseText);
      if (json.ok === true) {
        // Logger.log("✅ Đã gửi Telegram thành công");
        return true;
      } else {
        // Nếu lỗi parse HTML, thử gửi lại với plain text (không format)
        if (json.error_code === 400 && json.description && (json.description.indexOf("parse") >= 0 || json.description.indexOf("entities") >= 0)) {
          Logger.log("⚠️ LỖI PARSE HTML, thử gửi lại với plain text (không format)...");
          var plainPayload = {
            'chat_id': String(chatId).trim(),
            'text': String(message), // Giữ nguyên nội dung, chỉ bỏ parse_mode
            'disable_web_page_preview': false
            // Không có parse_mode → gửi plain text
          };
          var plainOptions = {
            'method': 'post',
            'contentType': 'application/json',
            'payload': JSON.stringify(plainPayload),
            'muteHttpExceptions': true
          };
          try {
            var plainResponse = UrlFetchApp.fetch(url, plainOptions);
            var plainJson = JSON.parse(plainResponse.getContentText());
            if (plainJson.ok === true) {
              Logger.log("✅ Đã gửi Telegram thành công (plain text)");
              return true;
            }
          } catch (e2) {
            Logger.log("⚠️ LỖI GỬI PLAIN TEXT: " + e2.message);
          }
        }
        Logger.log("⚠️ LỖI TELEGRAM API: " + (json.description || responseText));
        return false;
      }
    } else {
      Logger.log("⚠️ LỖI TELEGRAM HTTP: Code " + responseCode + " - " + responseText);
      return false;
    }
  } catch (e) {
    Logger.log("🚨 LỖI GỬI TELEGRAM (Exception): " + e.message + " | Stack: " + (e.stack || "N/A"));
    return false;
  }
}

/**
 * Gửi tin nhắn với format đẹp hơn (wrapper)
 * @param {string} title - Tiêu đề thông báo
 * @param {string} content - Nội dung chi tiết
 * @param {string} botToken - Bot Token
 * @param {string} chatId - Chat ID
 */
function guiThongBaoTelegramFormatted(title, content, botToken, chatId) {
  var message = "*" + title + "*\n\n" + content;
  return guiThongBaoTelegram(message, botToken, chatId);
}

/**
 * Gửi thông báo lỗi (format đặc biệt cho lỗi)
 * @param {string} errorMessage - Thông điệp lỗi
 * @param {string} botToken - Bot Token
 * @param {string} chatId - Chat ID
 */
function guiThongBaoLoi(errorMessage, botToken, chatId) {
  var message = "🚨 *LỖI HỆ THỐNG*\n\n`" + errorMessage + "`";
  return guiThongBaoTelegram(message, botToken, chatId);
}

/**
 * Gửi thông báo thành công (format đặc biệt)
 * @param {string} successMessage - Thông điệp thành công
 * @param {string} botToken - Bot Token
 * @param {string} chatId - Chat ID
 */
function guiThongBaoThanhCong(successMessage, botToken, chatId) {
  var message = "✅ *THÀNH CÔNG*\n\n" + successMessage;
  return guiThongBaoTelegram(message, botToken, chatId);
}

/**
 * ==================================================================
 * QUẢN LÝ TRẠNG THÁI ENABLE/DISABLE CHO TỪNG ACCOUNT|PREFIX
 * ==================================================================
 * Format key trong PropertiesService: AUTOMATION_ENABLED_<accountId>|<prefix>
 * Value: "true" = enabled, "false" hoặc không có = disabled (mặc định)
 * ==================================================================
 */

/**
 * Kiểm tra xem automation có được bật cho account|prefix không
 * @param {string} accountId - Account ID (có thể có hoặc không có "act_" prefix)
 * @param {string} prefix - Prefix của campaign
 * @returns {boolean} - true nếu enabled, false nếu disabled (mặc định)
 */
function isAutomationEnabled(accountId, prefix) {
  try {
    if (!accountId || !prefix) {
      return true; // Mặc định enabled nếu không có thông tin
    }
    
    // Chuẩn hóa accountId (loại bỏ "act_" nếu có)
    var normalizedAccountId = String(accountId).trim();
    if (normalizedAccountId.indexOf('act_') === 0) {
      normalizedAccountId = normalizedAccountId.substring(4);
    }
    
    // Chuẩn hóa prefix (uppercase)
    var normalizedPrefix = String(prefix).trim().toUpperCase();
    
    var props = PropertiesService.getScriptProperties();
    var allProps = props.getProperties();
    var prefixKey = "AUTOMATION_ENABLED_" + normalizedAccountId + "|";
    
    // Tìm tất cả keys có cùng accountId
    var matchingKeys = [];
    for (var key in allProps) {
      if (key.indexOf(prefixKey) === 0) {
        var keyPrefix = key.substring(prefixKey.length);
        // Kiểm tra match linh hoạt: normalizedPrefix bắt đầu bằng keyPrefix hoặc ngược lại
        // Ví dụ: "LAKVDHNT221" (normalizedPrefix) bắt đầu bằng "LAKVDH" (keyPrefix)
        if (normalizedPrefix.indexOf(keyPrefix) === 0 || keyPrefix.indexOf(normalizedPrefix) === 0) {
          matchingKeys.push({ key: key, keyPrefix: keyPrefix, value: allProps[key] });
        }
      }
    }
    
    // Nếu không có key nào match, mặc định enabled
    if (matchingKeys.length === 0) {
      return true;
    }
    
    // Ưu tiên prefix dài nhất (ví dụ: "LAKVDH" tốt hơn "LAK")
    matchingKeys.sort(function(a, b) {
      return b.keyPrefix.length - a.keyPrefix.length;
    });
    
    // Kiểm tra key đầu tiên (dài nhất) - nếu disabled thì return false
    var firstMatch = matchingKeys[0];
    var value = firstMatch.value;
    
    // Chỉ disabled nếu value = "false"
    if (value === "false") {
      return false;
    }
    
    // Mặc định enabled
    return true;
  } catch (e) {
    Logger.log("⚠️ Lỗi kiểm tra trạng thái enable/disable: " + e.message);
    return true; // Mặc định enabled khi có lỗi
  }
}

/**
 * Bật automation cho account|prefix
 * @param {string} accountId - Account ID
 * @param {string} prefix - Prefix của campaign
 * @returns {boolean} - true nếu thành công
 */
function enableAutomation(accountId, prefix) {
  try {
    if (!accountId || !prefix) {
      return false;
    }
    
    // Chuẩn hóa accountId
    var normalizedAccountId = String(accountId).trim();
    if (normalizedAccountId.indexOf('act_') === 0) {
      normalizedAccountId = normalizedAccountId.substring(4);
    }
    
    // Chuẩn hóa prefix
    var normalizedPrefix = String(prefix).trim().toUpperCase();
    
    // Key format: AUTOMATION_ENABLED_<accountId>|<prefix>
    var key = "AUTOMATION_ENABLED_" + normalizedAccountId + "|" + normalizedPrefix;
    
    var props = PropertiesService.getScriptProperties();
    props.setProperty(key, "true");
    
    Logger.log("✅ Đã bật automation cho " + normalizedAccountId + "|" + normalizedPrefix);
    return true;
  } catch (e) {
    Logger.log("⚠️ Lỗi bật automation: " + e.message);
    return false;
  }
}

/**
 * Tắt automation cho account|prefix
 * @param {string} accountId - Account ID
 * @param {string} prefix - Prefix của campaign
 * @returns {boolean} - true nếu thành công
 */
function disableAutomation(accountId, prefix) {
  try {
    if (!accountId || !prefix) {
      return false;
    }
    
    // Chuẩn hóa accountId
    var normalizedAccountId = String(accountId).trim();
    if (normalizedAccountId.indexOf('act_') === 0) {
      normalizedAccountId = normalizedAccountId.substring(4);
    }
    
    // Chuẩn hóa prefix
    var normalizedPrefix = String(prefix).trim().toUpperCase();
    
    // Key format: AUTOMATION_ENABLED_<accountId>|<prefix>
    var key = "AUTOMATION_ENABLED_" + normalizedAccountId + "|" + normalizedPrefix;
    
    var props = PropertiesService.getScriptProperties();
    props.setProperty(key, "false");
    
    Logger.log("✅ Đã tắt automation cho " + normalizedAccountId + "|" + normalizedPrefix);
    return true;
  } catch (e) {
    Logger.log("⚠️ Lỗi tắt automation: " + e.message);
    return false;
  }
}

/**
 * Lấy danh sách tất cả các account|prefix đã được cấu hình enable/disable
 * @returns {Array} - Array of { accountId: string, prefix: string, enabled: boolean }
 */
function getAllAutomationStatus() {
  try {
    // ⚠️ TỐI ƯU: Cache kết quả trong 30 giây để tránh đọc PropertiesService nhiều lần
    var cache = CacheService.getScriptCache();
    var cacheKey = 'AUTOMATION_STATUS_CACHE';
    var cached = cache.get(cacheKey);
    
    if (cached !== null && cached !== '') {
      try {
        var statusList = JSON.parse(cached);
        Logger.log("✅ Đã lấy automation status từ cache");
        return statusList;
      } catch (parseErr) {
        Logger.log("⚠️ Lỗi parse cache, đọc lại từ PropertiesService");
      }
    }
    
    // Đọc từ PropertiesService
    var props = PropertiesService.getScriptProperties();
    var allProps = props.getProperties();
    var statusList = [];
    var prefix = "AUTOMATION_ENABLED_";
    
    for (var key in allProps) {
      if (key.indexOf(prefix) === 0) {
        var suffix = key.substring(prefix.length);
        var parts = suffix.split("|");
        if (parts.length === 2) {
          statusList.push({
            accountId: parts[0],
            prefix: parts[1],
            enabled: allProps[key] === "true"
          });
        }
      }
    }
    
    // Cache kết quả trong 30 giây
    try {
      cache.put(cacheKey, JSON.stringify(statusList), 30);
    } catch (cacheErr) {
      Logger.log("⚠️ Lỗi cache automation status: " + cacheErr.message);
    }
    
    return statusList;
  } catch (e) {
    Logger.log("⚠️ Lỗi lấy danh sách automation status: " + e.message);
    return [];
  }
}


/**
 * ==================================================================
 * TELEGRAM BOT WEBHOOK HANDLER
 * ==================================================================
 */

// URL Web App deployment (mặc định - chỉ dùng khi không có trong sheet)
// QUAN TRỌNG: Ưu tiên đọc WEBHOOK_URL từ sheet CaiDat (hàng 13, cột C)
// Nếu không có trong sheet, mới dùng biến này làm fallback
// LƯU Ý: Nên cập nhật URL mới vào sheet CaiDat thay vì sửa ở đây
var WEBHOOK_URL_DEFAULT = "https://script.google.com/macros/s/AKfycbyuPEzIdqvWP1tMPF8v5Yui20EfJd4PvLo7PtdCL186-WFIqzae8sfm_ROFbVOSv-eA/exec";

/**
 * Kiểm tra Bot Token có hợp lệ không
 * @param {string} botToken - Bot Token cần kiểm tra
 * @returns {Object} - { valid: boolean, error: string, botInfo: Object }
 */
function testBotToken(botToken) {
  try {
    if (!botToken) {
      return { valid: false, error: "Bot Token rỗng" };
    }
    
    botToken = String(botToken).trim();
    
    // Kiểm tra format
    if (!botToken.match(/^\d+:[A-Za-z0-9_-]+$/)) {
      return { valid: false, error: "Bot Token không đúng format. Phải có dạng: số:dấu:chuỗi" };
    }
    
    // Test với Telegram API
    var testUrl = 'https://api.telegram.org/bot' + botToken + '/getMe';
    var testResponse = UrlFetchApp.fetch(testUrl, { muteHttpExceptions: true });
    var testResult = JSON.parse(testResponse.getContentText());
    
    if (!testResult.ok) {
      return { valid: false, error: testResult.description || "Unknown error", errorCode: testResult.error_code };
    }
    
    return { valid: true, botInfo: testResult.result };
  } catch (e) {
    return { valid: false, error: "Lỗi khi kiểm tra Bot Token: " + e.message };
  }
}

/**
 * Kiểm tra user có phải là admin hoặc creator trong nhóm không
 * @param {string} botToken - Bot Token
 * @param {string} chatId - Chat ID của nhóm
 * @param {string} userId - User ID cần kiểm tra
 * @returns {Object} - { isAdmin: boolean, isCreator: boolean, status: string, error: string }
 */
function checkUserIsAdmin(botToken, chatId, userId) {
  try {
    if (!botToken || !chatId || !userId) {
      return { isAdmin: false, isCreator: false, status: 'unknown', error: 'Missing parameters' };
    }
    
    // Chỉ kiểm tra trong nhóm/supergroup
    var chatIdNum = parseInt(chatId);
    if (chatIdNum >= 0) {
      // Chat ID dương = không phải nhóm
      return { isAdmin: false, isCreator: false, status: 'private', error: 'Not a group chat' };
    }
    
    var apiUrl = 'https://api.telegram.org/bot' + botToken + '/getChatMember';
    var params = {
      'chat_id': chatId,
      'user_id': userId
    };
    
    var url = apiUrl + '?chat_id=' + encodeURIComponent(chatId) + '&user_id=' + encodeURIComponent(userId);
    var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var result = JSON.parse(response.getContentText());
    
    if (!result.ok) {
      Logger.log("⚠️ Lỗi kiểm tra admin: " + (result.description || "Unknown"));
      return { isAdmin: false, isCreator: false, status: 'error', error: result.description || 'Unknown error' };
    }
    
    var status = result.result.status || 'member';
    var isCreator = status === 'creator';
    var isAdmin = status === 'administrator' || isCreator;
    
    Logger.log("🔍 User " + userId + " trong nhóm " + chatId + ": status=" + status + ", isAdmin=" + isAdmin + ", isCreator=" + isCreator);
    
    return { isAdmin: isAdmin, isCreator: isCreator, status: status, error: null };
  } catch (e) {
    Logger.log("🚨 Lỗi kiểm tra admin: " + e.message);
    return { isAdmin: false, isCreator: false, status: 'error', error: e.message };
  }
}

/**
 * Webhook handler để nhận messages từ Telegram Bot
 * Cần deploy như Web App và set webhook URL: https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
 * 
 * QUAN TRỌNG: Hàm này phải trả về response NGAY LẬP TỨC để Telegram không retry
 * Xử lý message sẽ chạy trong background (không chặn response)
 */
/**
 * Webhook handler - TRẢ LỜI NGAY LẬP TỨC (ACK) và đẩy vào queue để xử lý async
 * Đảm bảo Telegram không timeout và không retry
 */
function doPost(e) {
  // ⚠️ QUAN TRỌNG: Luôn trả OK ngay lập tức (trong < 1 giây)
  var ok;
  try {
    ok = ContentService.createTextOutput('{"ok":true}');
    ok.setMimeType(ContentService.MimeType.JSON);
  } catch (createErr) {
    ok = ContentService.createTextOutput('OK');
  }
  
  try {
    if (!e || !e.postData || !e.postData.contents) {
      Logger.log("⚠️ [doPost] Không có postData hoặc contents");
      return ok;
    }
    
    // Parse update
    var raw = e.postData.contents;
    var update;
    try {
      update = JSON.parse(raw);
    } catch (parseErr) {
      Logger.log("⚠️ [doPost] Lỗi parse JSON: " + parseErr.message);
      return ok; // Vẫn trả OK để Telegram không retry
    }
    
    // 1) DEDUPE THEO update_id (đúng chuẩn Telegram)
    var updId = (typeof update.update_id !== 'undefined') ? String(update.update_id) : '';
    if (updId) {
      var cache = CacheService.getScriptCache();
      var cacheKey = "UPD_" + updId;
      if (cache.get(cacheKey)) {
        // Đã thấy update này -> ACK ngay, không xử lý nữa
        Logger.log("⚠️ [doPost] BỎ QUA: Update ID " + updId + " đã được xử lý (từ Cache)");
        return ok;
      }
      // Đánh dấu ngay (5 phút là đủ - Telegram không retry quá lâu)
      cache.put(cacheKey, "1", 300);
    }
    
    // 2) PHÂN LOẠI LỆNH: Lệnh nhẹ xử lý trực tiếp, lệnh nặng đẩy vào queue
    var message = update.message || update.edited_message || update.channel_post || update.edited_channel_post;
    if (message && message.text) {
      var command = extractCommand_(message.text);
      
      // Danh sách lệnh nhẹ (xử lý trực tiếp, không qua queue)
      var lightCommands = ['/help', '/start', '/test', '/myid'];
      
      // Danh sách lệnh nặng (đẩy vào queue)
      // Lưu ý: /dashboard có thể nặng nếu có nhiều data, nên đẩy vào queue
      
      if (lightCommands.indexOf(command) !== -1) {
        // Lệnh nhẹ: Xử lý trực tiếp bằng trigger ngay (0.5 giây)
        Logger.log("✅ [doPost] Lệnh nhẹ: " + command + " - Xử lý trực tiếp");
        try {
          PropertiesService.getScriptProperties().setProperty('TG_DIRECT_' + updId, raw);
          ScriptApp.newTrigger('_processDirectCommand_').timeBased().after(500).create();
        } catch (triggerErr) {
          Logger.log("⚠️ [doPost] Lỗi tạo trigger cho lệnh nhẹ: " + triggerErr.message);
          // Fallback: đẩy vào queue
          enqueueTelegramUpdate_(raw);
          ensureQueueWorker_();
        }
        return ok; // Trả OK ngay
      }
    }
    
    // 3) LỆNH NẶNG: Đẩy vào queue (async processing)
    Logger.log("✅ [doPost] Lệnh nặng hoặc không phải lệnh - Đẩy vào queue");
    enqueueTelegramUpdate_(raw);
    ensureQueueWorker_();
    
  } catch (err) {
    // Chỉ log, không throw để không chặn ACK
    try {
      Logger.log("🚨 [doPost] Lỗi: " + (err.stack || err.message || err));
    } catch (logErr) {}
  }
  
  return ok; // Trả OK ngay lập tức (< 1 giây)
}

/**
 * Xử lý webhook update (được gọi bởi doPost)
 * Hàm này được wrap trong try-catch, không bao giờ throw exception
 * XỬ LÝ TRỰC TIẾP để trả lời ngay lập tức (không dùng trigger async)
 * @returns {boolean} - true nếu xử lý thành công, false nếu có lỗi
 */
function processWebhookUpdate_(e) {
  // ⚠️ QUAN TRỌNG: LOG NGAY TỪ ĐẦU để đảm bảo logs được ghi
  try {
    Logger.log("🔄 [processWebhookUpdate_] Bắt đầu xử lý...");
    console.log("🔄 [processWebhookUpdate_] Bắt đầu xử lý...");
  } catch (logErr) {}
  
  // Bảo vệ tối đa: kiểm tra từng bước một cách cẩn thận
  try {
    // Kiểm tra e và e.postData
    if (!e) {
      try {
        var errMsg = "⚠️ processWebhookUpdate_: e is null/undefined";
        Logger.log(errMsg);
        console.log(errMsg);
      } catch (logErr) {}
      return false; // Lỗi: không có event object
    }
    if (typeof e.postData === 'undefined' || e.postData === null) {
      try {
        var errMsg = "⚠️ processWebhookUpdate_: e.postData is null/undefined";
        Logger.log(errMsg);
        console.log(errMsg);
      } catch (logErr) {}
      return false; // Lỗi: không có postData
    }
    if (typeof e.postData.contents === 'undefined' || e.postData.contents === null || e.postData.contents === '') {
      try {
        var errMsg = "⚠️ processWebhookUpdate_: e.postData.contents is empty/null";
        Logger.log(errMsg);
        console.log(errMsg);
      } catch (logErr) {}
      return false; // Lỗi: không có contents
    }
    
    try {
      console.log("🔄 [processWebhookUpdate_] Đã có dữ liệu, bắt đầu parse JSON...");
    } catch (logErr) {}
    
    // Parse JSON - bắt mọi lỗi có thể
    var update;
    var messageId = null; // Extract message ID NGAY SAU KHI PARSE
    
    try {
      var contents = String(e.postData.contents);
      if (contents.length === 0) {
        try {
          Logger.log("⚠️ processWebhookUpdate_: contents is empty string");
          console.log("⚠️ processWebhookUpdate_: contents is empty string");
        } catch (logErr) {}
        return false; // Lỗi: contents rỗng
      }
      update = JSON.parse(contents);
      
      // ⚠️ QUAN TRỌNG: Update_id đã được đánh dấu trong doPost rồi
      // Nếu đến đây, có nghĩa là update_id chưa được xử lý (hoặc có lỗi trong doPost)
      // Nhưng vì doPost đã kiểm tra update_id trước, nên đến đây chắc chắn update_id đã được đánh dấu
      // Chỉ cần extract message ID và command để xử lý
      if (update && update.message && update.message.message_id) {
        messageId = update.message.message_id;
        
        // Extract command để log (chuẩn hóa, bỏ @BotName)
        var command = 'unknown';
        try {
          if (update.message && update.message.text) {
            var text = String(update.message.text).trim();
            command = extractCommand_(text);
            if (!command) {
              command = 'unknown';
            }
          }
        } catch (cmdErr) {
          command = 'unknown';
        }
        
        console.log("🔍 [processWebhookUpdate_] Đã extract Message ID: " + messageId + ", Command: " + command);
        Logger.log("🔍 [processWebhookUpdate_] Đã extract Message ID: " + messageId + ", Command: " + command);
      } else {
        try {
          Logger.log("⚠️ processWebhookUpdate_: Không có message_id trong update.message");
          console.log("⚠️ processWebhookUpdate_: Không có message_id trong update.message");
        } catch (logErr) {}
      }
      
      try {
        Logger.log("✅ processWebhookUpdate_: Đã parse JSON thành công, có update.message: " + (update && update.message ? "yes" : "no"));
        console.log("✅ processWebhookUpdate_: Đã parse JSON thành công");
      } catch (logErr) {}
      
    } catch (parseErr) {
      try {
        Logger.log("🚨 processWebhookUpdate_: Lỗi parse JSON: " + parseErr.message + " | Content: " + String(e.postData.contents).substring(0, 200));
        console.log("🚨 processWebhookUpdate_: Lỗi parse JSON: " + parseErr.message);
      } catch (logErr) {}
      return false; // Lỗi parse = lỗi, không xử lý được
    }
    
    // Kiểm tra update hợp lệ
    if (!update) {
      try {
        Logger.log("⚠️ processWebhookUpdate_: update is null/undefined");
      } catch (logErr) {}
      return true; // Không có update = không phải lỗi (có thể là edited_message, etc.)
    }
    if (typeof update.message === 'undefined' || update.message === null) {
      try {
        Logger.log("⚠️ processWebhookUpdate_: update.message is null/undefined (có thể là edited_message, channel_post, etc.)");
      } catch (logErr) {}
      return true; // Không có message = không phải lỗi (có thể là edited_message, etc.)
    }
    
    // Xử lý message nếu có
    try {
      // ⚠️ QUAN TRỌNG: Message ID và command đã được extract và đánh dấu ở trên
      // Nếu đến đây, message đã được kiểm tra và đánh dấu, có thể xử lý an toàn
      // Không cần kiểm tra lại nữa
      
      var chatId = update.message && update.message.chat ? update.message.chat.id : "N/A";
      var chatType = update.message && update.message.chat ? (update.message.chat.type || "unknown") : "N/A";
      var chatTitle = update.message && update.message.chat ? (update.message.chat.title || "(no title)") : "N/A";
      
      // ⚠️ QUAN TRỌNG: Chặn chat cá nhân NGAY TỪ ĐẦU (trước khi xử lý message)
      // Chat ID dương = chat cá nhân, Chat ID âm = nhóm/supergroup
      var chatIdNum = parseInt(String(chatId), 10);
      
      // Chặn chat cá nhân
      if (chatType === 'private' || chatIdNum > 0 || isNaN(chatIdNum) || chatIdNum === 0) {
        // Chat cá nhân hoặc chat ID không hợp lệ → KHÔNG XỬ LÝ, KHÔNG GỬI THÔNG BÁO GÌ CẢ
        Logger.log("⚠️ CHẶN: Chat cá nhân hoặc không hợp lệ. Chat ID: " + chatId + " (type: " + chatType + ", số: " + chatIdNum + "). Bot chỉ hoạt động trong nhóm (Chat ID âm).");
        // Đánh dấu message đã xử lý để tránh retry từ Telegram
        // QUAN TRỌNG: Phải truyền command để key match
        if (messageId) {
          markMessageAsProcessed_(messageId, command);
        }
        return true; // Bỏ qua (không phải lỗi, chỉ là không xử lý)
      }
      
      // ⚠️ QUAN TRỌNG: Chỉ cho phép nhóm (group) và supergroup
      // Không cho phép channel (vì channel không có members để gửi commands)
      if (chatType !== 'group' && chatType !== 'supergroup') {
        Logger.log("⚠️ CHẶN: Chat type '" + chatType + "' không được phép. Chỉ cho phép 'group' hoặc 'supergroup'.");
        // Đánh dấu message đã xử lý để tránh retry
        // QUAN TRỌNG: Phải truyền command để key match
        if (messageId) {
          markMessageAsProcessed_(messageId, command);
        }
        return true; // Không xử lý (không phải lỗi)
      }
      
      // ✅ Đây là nhóm/supergroup (Chat ID âm) → Xử lý message
      // Log chi tiết trước khi xử lý
      try {
        Logger.log("✅ Bắt đầu xử lý message từ nhóm. Message ID: " + messageId + ", Chat ID: " + chatId + ", Chat Type: " + chatType);
        var messageText = update.message.text || "(no text)";
        Logger.log("📝 Message text: " + messageText.substring(0, 100));
      } catch (logErr) {
        // Bỏ qua lỗi log
      }
      
      var handleResult = handleTelegramMessageSafe_(update.message);
      
      // Trả về kết quả xử lý
      if (handleResult === true) {
        Logger.log("✅ [processWebhookUpdate_] Xử lý message thành công");
        return true;
      } else {
        Logger.log("⚠️ [processWebhookUpdate_] Xử lý message thất bại (handleTelegramMessageSafe_ trả về false)");
        return false;
      }
    } catch (msgErr) {
      // Log lỗi để debug
      Logger.log("🚨 [processWebhookUpdate_] Lỗi xử lý message: " + msgErr.message);
      console.log("🚨 [processWebhookUpdate_] Lỗi xử lý message: " + msgErr.message);
      return false; // Trả về false để doPost biết xử lý thất bại
    }
  } catch (outerErr) {
      // Log lỗi ngoài cùng
      Logger.log("🚨 [processWebhookUpdate_] Lỗi ngoài cùng: " + outerErr.message);
      console.log("🚨 [processWebhookUpdate_] Lỗi ngoài cùng: " + outerErr.message);
      return false; // Trả về false để doPost biết xử lý thất bại
  }
  
  // Nếu không có message, trả về true (không phải lỗi)
  return true;
}

/**
 * Wrapper an toàn cho handleTelegramMessage
 * Đảm bảo mọi lỗi đều được bắt và không lan ra ngoài
 * @returns {boolean} - true nếu xử lý thành công, false nếu có lỗi
 */
function handleTelegramMessageSafe_(message) {
  try {
    if (!message) {
      Logger.log("⚠️ [handleTelegramMessageSafe_] Message is null/undefined");
      return false; // Không có message = lỗi
    }
    var result = handleTelegramMessage(message);
    // handleTelegramMessage trả về true nếu xử lý thành công, false nếu bị chặn (rate limit, no permission), undefined nếu có lỗi
    if (result === true) {
      return true; // Xử lý thành công
    } else if (result === false) {
      // Bị chặn (rate limit hoặc không có quyền) - KHÔNG đánh dấu update_id để Telegram có thể retry
      Logger.log("⚠️ [handleTelegramMessageSafe_] Command bị chặn (rate limit hoặc không có quyền)");
      return false; // Trả về false để không đánh dấu update_id
    } else {
      // result = undefined (có lỗi hoặc không return)
      // Giả định xử lý thành công nếu không có exception
      return true;
    }
  } catch (e) {
    // LOG lỗi để debug (không bỏ qua nữa)
    Logger.log("🚨 [handleTelegramMessageSafe_] Lỗi xử lý message: " + e.message + " | Stack: " + (e.stack || "N/A"));
    console.log("🚨 [handleTelegramMessageSafe_] Lỗi xử lý message: " + e.message);
    return false; // Trả về false để biết xử lý thất bại
  }
}

/**
 * Lưu trữ message_id + command đã xử lý để tránh spam
 * Sử dụng Cache Service (NHANH HƠN) làm lớp đầu tiên, Properties Service làm lớp lưu trữ lâu dài
 * Key format: PROCESSED_MSG_<message_id>_<command>
 * Value: timestamp (để có thể cleanup sau)
 */
/**
 * Lưu trữ message_id + command đã xử lý để tránh spam
 * SỬA ĐỔI: CHỈ dùng CacheService (NHANH) để tránh Race Condition.
 * PropertiesService (CHẬM) đã bị loại bỏ khỏi luồng kiểm tra này.
 * 
 * QUAN TRỌNG: Hàm này phải chạy CỰC KỲ NHANH (vài mili giây) để tránh
 * Telegram timeout và retry. PropertiesService.getProperty() quá chậm
 * (có thể mất 100-500ms) và gây ra race condition khi có nhiều request
 * đồng thời.
 */
function isMessageProcessed_(messageId, command) {
  if (!messageId) return false;
  try {
    // ⚠️ QUAN TRỌNG: Sử dụng messageId + command để tracking chính xác hơn
    // Đảm bảo command luôn có giá trị (default 'unknown') để key tracking nhất quán
    var commandKey = (command && String(command).trim() !== '') ? String(command).toLowerCase().trim() : "unknown";
    var key = "PROCESSED_MSG_" + String(messageId) + "_" + commandKey;
    
    // ⚠️ QUAN TRỌNG: CHỈ KIỂM TRA CacheService (Rất nhanh - vài mili giây)
    // Bỏ PropertiesService vì nó quá chậm (100-500ms) và gây race condition
    try {
      var cache = CacheService.getScriptCache();
      var cached = cache.get(key);
      if (cached !== null && cached !== '') {
        console.log("🔍 [isMessageProcessed_] Message ID " + messageId + " + Command " + commandKey + " ĐÃ ĐƯỢC XỬ LÝ (từ Cache)");
        return true; // Đã được xử lý, bỏ qua
      }
    } catch (cacheErr) {
      // Nếu Cache lỗi, giả định message chưa được xử lý (tránh mất message)
      Logger.log("⚠️ Lỗi kiểm tra Cache: " + cacheErr.message);
      return false;
    }
    
    // KHÔNG kiểm tra PropertiesService ở đây nữa vì nó quá chậm và gây ra Race Condition
    // CacheService đủ nhanh và đủ tin cậy để chặn duplicate trong vòng 6 giờ
    return false; // Chưa được xử lý, cho phép xử lý
  } catch (e) {
    Logger.log("⚠️ Lỗi kiểm tra message processed: " + e.message);
    console.log("⚠️ Lỗi kiểm tra message processed: " + e.message);
    // ⚠️ QUAN TRỌNG: Nếu có lỗi, giả định message chưa được xử lý (tránh mất message)
    // Nhưng điều này có thể gây spam nếu Cache bị lỗi liên tục
    return false;
  }
}

function markMessageAsProcessed_(messageId, command) {
  if (!messageId) return;
  try {
    // ⚠️ QUAN TRỌNG: Sử dụng messageId + command để tracking chính xác hơn
    // Đảm bảo command luôn có giá trị (default 'unknown') để key tracking nhất quán
    var commandKey = (command && String(command).trim() !== '') ? String(command).toLowerCase().trim() : "unknown";
    var key = "PROCESSED_MSG_" + String(messageId) + "_" + commandKey;
    var timestamp = new Date().getTime().toString();
    
    // ⚠️ QUAN TRỌNG: Lưu vào Cache Service TRƯỚC (NHANH HƠN, giúp tránh race condition)
    // Cache Service có latency thấp, giúp đánh dấu nhanh chóng
    try {
      var cache = CacheService.getScriptCache();
      cache.put(key, timestamp, 21600); // Cache 6 giờ (đủ lâu để tránh duplicate)
      console.log("✅ [markMessageAsProcessed_] Đã đánh dấu Message ID " + messageId + " + Command " + commandKey + " vào Cache (timestamp: " + timestamp + ")");
    } catch (cacheErr) {
      Logger.log("⚠️ Lỗi lưu vào Cache: " + cacheErr.message);
      // Tiếp tục lưu vào Properties ngay cả khi Cache lỗi
    }
    
    // ⚠️ QUAN TRỌNG: Lưu vào Properties Service (PERSISTENT, để lưu lâu dài)
    // Properties Service có latency cao hơn, nhưng persistent
    try {
      var props = PropertiesService.getScriptProperties();
      props.setProperty(key, timestamp);
      console.log("✅ [markMessageAsProcessed_] Đã đánh dấu Message ID " + messageId + " + Command " + commandKey + " vào Properties (timestamp: " + timestamp + ")");
      Logger.log("✅ [markMessageAsProcessed_] Đã đánh dấu Message ID " + messageId + " + Command " + commandKey + " (timestamp: " + timestamp + ")");
    } catch (propsErr) {
      Logger.log("⚠️ Lỗi lưu vào Properties: " + propsErr.message);
      // Nếu Properties lỗi, vẫn có Cache (đủ để tránh duplicate trong 6 giờ)
    }
    
    // Cleanup old entries (giữ tối đa 5000 entries, xóa entries cũ hơn 24h)
    // Chỉ cleanup mỗi 500 lần để tối ưu performance (KHÔNG cleanup mỗi lần)
    try {
      var props = PropertiesService.getScriptProperties();
      var cleanupCounter = parseInt(props.getProperty("PROCESSED_MSG_CLEANUP_COUNTER") || "0", 10);
      var newCounter = cleanupCounter + 1;
      props.setProperty("PROCESSED_MSG_CLEANUP_COUNTER", newCounter.toString());
      
      // Chỉ cleanup khi counter chia hết cho 500 (giảm số lần cleanup)
      if (newCounter % 500 === 0) {
        try {
          var allProps = props.getProperties();
          var allKeys = Object.keys(allProps);
          var processedKeys = [];
          for (var pkIdx = 0; pkIdx < allKeys.length; pkIdx++) {
            var k = allKeys[pkIdx];
            if (k.startsWith("PROCESSED_MSG_") && k !== "PROCESSED_MSG_CLEANUP_COUNTER") {
              processedKeys.push(k);
            }
          }
          if (processedKeys.length > 5000) {
            var now = new Date().getTime();
            var oneDay = 24 * 60 * 60 * 1000;
            var deletedCount = 0;
            // Xóa tối đa 500 entries mỗi lần cleanup
            for (var i = 0; i < processedKeys.length && deletedCount < 500; i++) {
              var ts = parseInt(allProps[processedKeys[i]] || "0", 10);
              if (now - ts > oneDay) {
                props.deleteProperty(processedKeys[i]);
                deletedCount++;
              }
            }
            if (deletedCount > 0) {
              Logger.log("🧹 Đã xóa " + deletedCount + " processed message entries cũ");
              console.log("🧹 Đã xóa " + deletedCount + " processed message entries cũ");
            }
          }
        } catch (cleanupErr) {
          // Bỏ qua lỗi cleanup
          Logger.log("⚠️ Lỗi cleanup processed messages: " + cleanupErr.message);
          console.log("⚠️ Lỗi cleanup processed messages: " + cleanupErr.message);
        }
      }
    } catch (cleanupCounterErr) {
      // Bỏ qua lỗi cleanup counter
    }
  } catch (e) {
    Logger.log("⚠️ Lỗi đánh dấu message processed: " + e.message);
    console.log("⚠️ Lỗi đánh dấu message processed: " + e.message);
  }
}

/**
 * Rate limiting cho thông báo lỗi (tránh spam)
 * Key format: ERROR_MSG_<chatId>_<command>
 * Value: timestamp
 * QUAN TRỌNG: KHÔNG BAO GIỜ gửi thông báo lỗi vào chat cá nhân (Chat ID dương)
 */
function shouldSendErrorNotification_(chatId, command) {
  if (!chatId || !command) return false; // Không gửi nếu thiếu thông tin
  
  // ⚠️ QUAN TRỌNG: KHÔNG BAO GIỜ gửi thông báo lỗi vào chat cá nhân
  var chatIdNum = parseInt(String(chatId).trim(), 10);
  if (chatIdNum > 0) {
    // Chat ID dương = chat cá nhân → KHÔNG GỬI
    Logger.log("⚠️ CHẶN ERROR NOTIFICATION: Chat ID " + chatId + " là chat cá nhân. Không gửi thông báo lỗi.");
    return false; // Không gửi
  }
  
  var key = "ERROR_MSG_" + String(chatId) + "_" + String(command);
  var props = PropertiesService.getScriptProperties();
  var lastSent = props.getProperty(key);
  
  if (!lastSent) {
    props.setProperty(key, new Date().getTime().toString());
    return true;
  }
  
  var lastSentTime = parseInt(lastSent, 10);
  var now = new Date().getTime();
  var cooldown = 60 * 1000; // 60 giây = 1 phút
  
  if (now - lastSentTime > cooldown) {
    props.setProperty(key, now.toString());
    return true;
  }
  
  return false; // Chưa đến lúc gửi lại
}

/**
 * Handler cho GET request (để test webhook)
 * ⚠️ ĐÃ ĐỔI TÊN: doGet() → doGetTelegram() để tránh conflict với TemplatesUI.gs
 * QUAN TRỌNG: Phải trả về response đơn giản để tránh 302 redirect
 */
function doGetTelegram(e) {
  // Trả về response đơn giản, không redirect
  try {
    var output = ContentService.createTextOutput("Telegram Bot Webhook đang hoạt động!");
    output.setMimeType(ContentService.MimeType.TEXT);
    return output;
  } catch (err) {
    // Nếu có lỗi, trả về response đơn giản nhất
    return ContentService.createTextOutput("OK");
  }
}

/**
 * Hàm test đơn giản để kiểm tra webhook
 * LƯU Ý: Hàm này chỉ để test logic, không gửi message thật
 */
function testWebhook() {
  try {
    var settings = getSettingsSafe_();
    var authorizedChatId = settings['TELEGRAM_AUTHORIZED_CHAT_ID'] || settings['TELEGRAM_CHAT_ID'];
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    
    if (!authorizedChatId || !botToken) {
      Logger.log("⚠️ Thiếu cấu hình: authorizedChatId=" + (authorizedChatId ? "✓" : "✗") + ", botToken=" + (botToken ? "✓" : "✗"));
      return "Test thất bại: Thiếu cấu hình";
    }
    
    // Giả lập một webhook update từ nhóm (không phải chat cá nhân)
    var testUpdate = {
      message: {
        chat: { 
          id: authorizedChatId, // Dùng Chat ID thật từ cấu hình
          type: "supergroup", // Nhóm, không phải private
          title: "Test Group"
        },
        from: {
          id: "1150577493", // User ID được whitelist
          first_name: "Test User"
        },
        message_id: 999999,
        text: "/test"
      }
    };
    
    var mockEvent = {
      postData: {
        contents: JSON.stringify(testUpdate)
      }
    };
    
    var result = doPost(mockEvent);
    Logger.log("✅ Test webhook result: " + result.getContent());
    return "Test thành công! (Chat ID: " + authorizedChatId + ")";
  } catch (e) {
    Logger.log("❌ Test webhook lỗi: " + e.message);
    return "Test thất bại: " + e.message;
  }
}

/**
 * Xử lý message từ Telegram
 * @param {Object} message - Telegram message object
 */
function handleTelegramMessage(message) {
  try {
    // Kiểm tra message hợp lệ
    if (!message || !message.chat) {
      Logger.log("⚠️ Message không hợp lệ: " + (message ? "missing chat" : "null"));
      return false; // Message không hợp lệ = lỗi
    }
    
    // ⚠️ QUAN TRỌNG: BỎ QUA messages từ bot (tránh vòng lặp spam)
    // Bot không nên xử lý lại messages của chính nó
    if (message.from && message.from.is_bot === true) {
      Logger.log("⚠️ BỎ QUA: Message từ bot (is_bot=true). Tránh vòng lặp spam.");
      console.log("⚠️ BỎ QUA: Message từ bot (is_bot=true). Tránh vòng lặp spam.");
      return true; // Bỏ qua messages từ bot (không phải lỗi, chỉ là không xử lý)
    }
    
    // ⚠️ QUAN TRỌNG: Kiểm tra xem message có phải từ chính bot này không
    // Lấy Bot ID từ Bot Token và so sánh với User ID của message
    try {
      var settings = getSettingsSafe_();
      var botToken = settings['TELEGRAM_BOT_TOKEN'];
      if (botToken && message.from && message.from.id) {
        // Lấy Bot Info từ Telegram API
        var botInfoUrl = 'https://api.telegram.org/bot' + botToken + '/getMe';
        var botInfoResponse = UrlFetchApp.fetch(botInfoUrl, { muteHttpExceptions: true });
        var botInfoResult = JSON.parse(botInfoResponse.getContentText());
        if (botInfoResult.ok && botInfoResult.result) {
          var botId = botInfoResult.result.id;
          var messageFromId = message.from.id;
          if (botId === messageFromId) {
            Logger.log("⚠️ BỎ QUA: Message từ chính bot này (Bot ID: " + botId + "). Tránh vòng lặp spam.");
            console.log("⚠️ BỎ QUA: Message từ chính bot này (Bot ID: " + botId + "). Tránh vòng lặp spam.");
            return; // Bỏ qua message từ chính bot
          }
        }
      }
    } catch (botCheckErr) {
      // Bỏ qua lỗi kiểm tra bot ID, tiếp tục xử lý
      Logger.log("⚠️ Không thể kiểm tra Bot ID: " + botCheckErr.message);
    }
    
    // QUAN TRỌNG: Lấy chat ID từ message.chat.id (chat mà message được gửi đến)
    // Đây có thể là chat cá nhân hoặc nhóm, tùy vào nơi user gửi lệnh
    var fromChatId = String(message.chat.id);
    var text = message.text || '';
    // ⚠️ QUAN TRỌNG: Chuẩn hóa command (bỏ @BotName nếu có)
    var command = extractCommand_(text);
    if (!command) {
      // Không phải lệnh, bỏ qua
      Logger.log("⚠️ Message không phải lệnh: " + text.substring(0, 50));
      return true; // Không phải lệnh = không phải lỗi
    }
    
    // Log thông tin chat để debug
    var chatType = message.chat.type || 'unknown'; // 'private', 'group', 'supergroup', 'channel'
    var chatTitle = message.chat.title || '(no title)';
    var fromUserId = message.from ? message.from.id : 'unknown';
    var fromUserName = message.from ? (message.from.username || message.from.first_name || 'unknown') : 'unknown';
    var isBot = message.from ? (message.from.is_bot === true) : false;
    
    Logger.log("📨 Xử lý message - Chat ID: " + fromChatId + ", Chat Type: " + chatType + ", Chat Title: " + chatTitle);
    Logger.log("📨 Người gửi - User ID: " + fromUserId + ", Username: " + fromUserName + ", Is Bot: " + isBot + ", Command: " + command);
    
    // ⚠️ QUAN TRỌNG: Bỏ qua hoàn toàn messages từ chat cá nhân (KHÔNG REPLY GÌ CẢ)
    // Bot chỉ hoạt động trong nhóm, KHÔNG BAO GIỜ reply vào chat cá nhân
    var chatIdNum = parseInt(String(fromChatId), 10);
    if (chatType === 'private' || chatIdNum > 0) {
      // Chat ID dương = chat cá nhân → KHÔNG XỬ LÝ
      Logger.log("⚠️ CHẶN COMMAND: Chat ID " + fromChatId + " là chat cá nhân (type: " + chatType + ", số: " + chatIdNum + "). Bot chỉ hoạt động trong nhóm (Chat ID âm).");
      // KHÔNG REPLY GÌ CẢ - KHÔNG GỬI THÔNG BÁO - KHÔNG SPAM
      return true; // Bỏ qua chat cá nhân (không phải lỗi, chỉ là không xử lý)
    }
    
    // ⚠️ QUAN TRỌNG: Chỉ cho phép nhóm (group) và supergroup
    // Không cho phép channel (vì channel không có members để gửi commands)
    if (chatType !== 'group' && chatType !== 'supergroup') {
      Logger.log("⚠️ CHẶN COMMAND: Chat type '" + chatType + "' không được phép. Chỉ cho phép 'group' hoặc 'supergroup'.");
      return true; // Không xử lý (không phải lỗi)
    }
    
    // ✅ Đây là nhóm/supergroup (Chat ID âm) → Tiếp tục xử lý
    // Xác định reply chat ID (luôn reply vào nhóm)
    var replyChatId = fromChatId;
    
    // Lấy settings (có thể gây lỗi nếu sheet không tồn tại)
    var settings;
    try {
      settings = getSettingsSafe_();
    } catch (settingsErr) {
      Logger.log("🚨 Lỗi lấy settings: " + settingsErr.message);
      // KHÔNG GỬI THÔNG BÁO LỖI VÀO NHÓM (tránh spam)
      return false; // Lỗi lấy settings = lỗi
    }
    
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = settings['TELEGRAM_CHAT_ID'];
    var authorizedChatId = settings['TELEGRAM_AUTHORIZED_CHAT_ID'] || chatId;
    
    if (!botToken) {
      Logger.log("⚠️ Không có Bot Token để xử lý command");
      return false; // Không có Bot Token = lỗi
    }
    
    // Chuẩn hóa Chat ID để so sánh (chuyển về string và trim)
    // QUAN TRỌNG: Đảm bảo cả hai đều là string và không có khoảng trắng
    var normalizedFromChatId = String(fromChatId).trim();
    var normalizedAuthorizedChatId = String(authorizedChatId).trim();
    
    // ⚠️ QUAN TRỌNG: Kiểm tra Chat ID phải khớp với nhóm được phép
    // Nếu không khớp → KHÔNG XỬ LÝ, KHÔNG GỬI THÔNG BÁO GÌ CẢ
    Logger.log("🔍 Đang kiểm tra Chat ID...");
    Logger.log("   - Chat ID từ message: '" + normalizedFromChatId + "' (length: " + normalizedFromChatId.length + ", type: " + typeof normalizedFromChatId + ")");
    Logger.log("   - Chat ID được phép: '" + normalizedAuthorizedChatId + "' (length: " + normalizedAuthorizedChatId.length + ", type: " + typeof normalizedAuthorizedChatId + ")");
    Logger.log("   - So sánh: " + (normalizedFromChatId === normalizedAuthorizedChatId ? "KHỚP ✅" : "KHÔNG KHỚP ❌"));
    
    if (normalizedFromChatId !== normalizedAuthorizedChatId) {
      Logger.log("⚠️ CHẶN COMMAND: Chat ID không khớp!");
      Logger.log("   - Chat ID từ message: '" + normalizedFromChatId + "' (length: " + normalizedFromChatId.length + ", type: " + typeof normalizedFromChatId + ")");
      Logger.log("   - Chat ID được phép: '" + normalizedAuthorizedChatId + "' (length: " + normalizedAuthorizedChatId.length + ", type: " + typeof normalizedAuthorizedChatId + ")");
      Logger.log("   - Chat Type: " + chatType);
      Logger.log("   - Command: " + command);
      Logger.log("   → Bot chỉ hoạt động trong nhóm được phép. KHÔNG XỬ LÝ command này.");
      // KHÔNG reply gì cả nếu Chat ID không khớp (tránh spam)
      // Đặc biệt: Không gửi thông báo lỗi vào chat cá nhân
      return true; // Chat ID không khớp (không phải lỗi, chỉ là không xử lý)
    }
    
    // ✅ Chat ID khớp → Đây là nhóm được phép
    Logger.log("✅ Chat ID khớp. Đây là nhóm được phép: " + normalizedAuthorizedChatId);
    
    // Đảm bảo reply vào nhóm
    replyChatId = normalizedAuthorizedChatId;
    
    // QUAN TRỌNG: Whitelist User IDs (cho phép user cụ thể sử dụng bot)
    // User ID 1150577493 được phép sử dụng bot (nhưng chỉ khi gửi từ nhóm)
    var allowedUserIds = ['1150577493']; // Thêm user IDs được phép vào đây
    var userIdStr = String(fromUserId).trim();
    var isWhitelisted = allowedUserIds.indexOf(userIdStr) !== -1;
    
    // QUAN TRỌNG: Kiểm tra quyền admin/creator trong nhóm
    // Chỉ admin/creator hoặc whitelisted user mới được phép sử dụng bot
    Logger.log("🔍 Đang kiểm tra quyền user...");
    Logger.log("   - User ID: " + userIdStr);
    Logger.log("   - Chat ID: " + normalizedFromChatId);
    Logger.log("   - Bot Token: " + (botToken ? botToken.substring(0, 10) + "..." : "null"));
    
    var adminCheck = checkUserIsAdmin(botToken, normalizedFromChatId, userIdStr);
    var isAdmin = adminCheck.isAdmin;
    var isCreator = adminCheck.isCreator;
    var hasPermission = isAdmin || isCreator || isWhitelisted;
    
    Logger.log("🔍 Kết quả kiểm tra quyền:");
    Logger.log("   - User: " + fromUserName + " (ID: " + userIdStr + ")");
    Logger.log("   - isAdmin: " + isAdmin);
    Logger.log("   - isCreator: " + isCreator);
    Logger.log("   - isWhitelisted: " + isWhitelisted);
    Logger.log("   - status: " + adminCheck.status);
    Logger.log("   - hasPermission: " + hasPermission);
    if (adminCheck.error) {
      Logger.log("   - Error: " + adminCheck.error);
    }
    
    // Xử lý command /myid (cho phép tất cả thành viên trong nhóm xem thông tin)
    if (command === '/myid') {
      try {
        var myIdMsg = "🆔 *THÔNG TIN CHAT*\n\n";
        myIdMsg += "📱 *Chat hiện tại:*\n";
        myIdMsg += "  • Chat ID: `" + fromChatId + "`\n";
        myIdMsg += "  • Loại chat: " + chatType + "\n";
        if (chatTitle !== '(no title)') {
          myIdMsg += "  • Tên nhóm: " + chatTitle + "\n";
        }
        myIdMsg += "\n👤 *Người gửi:*\n";
        myIdMsg += "  • User ID: `" + fromUserId + "`\n";
        myIdMsg += "  • Tên: " + fromUserName + "\n";
        myIdMsg += "  • Quyền: " + (isCreator ? "👑 Creator" : (isAdmin ? "⭐ Admin" : "👤 Member")) + "\n";
        myIdMsg += "\n🔐 *Quyền truy cập bot:*\n";
        myIdMsg += "  • Chat ID được phép: `" + normalizedAuthorizedChatId + "`\n";
        myIdMsg += "  • Bot chỉ hoạt động trong nhóm này\n";
        if (isAdmin || isCreator || isWhitelisted) {
          myIdMsg += "  • ✅ Bạn có quyền sử dụng bot";
          if (isCreator) myIdMsg += " (Creator)";
          else if (isAdmin) myIdMsg += " (Admin)";
          else if (isWhitelisted) myIdMsg += " (Whitelisted User)";
          myIdMsg += "\n";
        } else {
          myIdMsg += "  • ⚠️ Bạn không có quyền sử dụng bot (chỉ Admin/Creator/Whitelisted mới được phép)\n";
        }
        
        // Reply vào nhóm
        guiThongBaoTelegram(myIdMsg, botToken, replyChatId);
      } catch (e) {
        Logger.log("🚨 Lỗi xử lý /myid: " + e.message);
      }
      return; // /myid luôn được phép xem
    }
    
    // QUAN TRỌNG: Chỉ admin/creator hoặc whitelisted user mới được phép sử dụng các commands khác
    // LƯU Ý: Chúng ta đã chặn chat cá nhân ở đầu hàm, nên đến đây chắc chắn là nhóm
    if (!hasPermission) {
      Logger.log("⚠️ User không có quyền. Status: " + adminCheck.status + ", isWhitelisted: " + isWhitelisted);
      
      // Chống spam - chỉ gửi thông báo 1 lần mỗi 60 giây
      if (!shouldSendErrorNotification_(normalizedFromChatId, command)) {
        Logger.log("⚠️ Đã gửi thông báo lỗi gần đây, bỏ qua để tránh spam");
        // ⚠️ QUAN TRỌNG: Vẫn trả về true để đánh dấu update_id (tránh retry từ Telegram)
        // Nhưng không xử lý command (không có quyền)
        return true; // Đánh dấu update_id đã được xử lý (bỏ qua do no permission)
      }
      
      try {
        var denyMsg = "❌ *KHÔNG CÓ QUYỀN SỬ DỤNG BOT*\n\n";
        denyMsg += "⚠️ Bot chỉ dành cho **Admin/Creator** của nhóm.\n\n";
        denyMsg += "👤 *Thông tin của bạn:*\n";
        denyMsg += "  • User ID: `" + userIdStr + "`\n";
        denyMsg += "  • Tên: " + fromUserName + "\n";
        denyMsg += "  • Quyền hiện tại: " + (adminCheck.status === 'member' ? "👤 Member" : adminCheck.status) + "\n\n";
        denyMsg += "💡 *Lưu ý:*\n";
        denyMsg += "   • Chỉ **Admin** hoặc **Creator** của nhóm mới được phép sử dụng bot\n";
        denyMsg += "   • Vui lòng liên hệ Admin của nhóm nếu cần sử dụng bot\n\n";
        denyMsg += "ℹ️ Gửi lệnh `/myid` để xem thông tin chat và quyền của bạn";
        
        // CHỈ gửi thông báo vào nhóm (không bao giờ gửi vào chat cá nhân)
        // normalizedFromChatId đã được kiểm tra là số âm (nhóm) ở đầu hàm
        guiThongBaoTelegram(denyMsg, botToken, replyChatId);
      } catch (e) {
        Logger.log("🚨 Không thể gửi thông báo từ chối: " + e.message);
      }
      // ⚠️ QUAN TRỌNG: Vẫn trả về true để đánh dấu update_id (tránh retry từ Telegram)
      // Nhưng không xử lý command (không có quyền)
      return true; // Đánh dấu update_id đã được xử lý (bỏ qua do no permission)
    }
    
    // ✅ User có quyền (admin/creator hoặc whitelisted) → Cho phép sử dụng bot
    Logger.log("✅ User có quyền sử dụng bot (isAdmin: " + isAdmin + ", isCreator: " + isCreator + ", isWhitelisted: " + isWhitelisted + ").");
    
    // ⚠️ QUAN TRỌNG: Lấy message ID để reply và rate limiting
    var messageId = message.message_id || null;
    var replyToMessageId = messageId; // Reply vào message gốc
    
    // ⚠️ QUAN TRỌNG: Rate limiting theo USER + COMMAND, dùng CacheService cho nhanh
    // Key format: CMD_RL_<chatId>_<userId>_<command>
    // Sử dụng CacheService thay vì PropertiesService để tránh I/O chậm và race condition
    var fromUserId = (message.from && message.from.id) ? String(message.from.id).trim() : "unknown";
    var rateLimitKey = "CMD_RL_" + normalizedFromChatId + "_" + fromUserId + "_" + command;
    
    // Dùng CacheService để hết hạn nhanh và tránh lưu dai dẳng
    var cache = CacheService.getScriptCache();
    var last = cache.get(rateLimitKey);
    
    // ⚠️ QUAN TRỌNG: Rate limit khác nhau cho lệnh nhẹ và lệnh nặng
    // Lệnh nhẹ: 2 giây (đủ mượt)
    // Lệnh nặng: 8 giây (tránh spam và giảm tải)
    var rateLimitSeconds = 2; // Mặc định 2 giây cho lệnh nhẹ
    if (command === '/report' || command === '/statusads' || command === '/status' || 
        command === '/enable_all' || command === '/disable_all' || 
        command === '/check_webhook' || command === '/reset_webhook') {
      rateLimitSeconds = 8; // 8 giây cho lệnh nặng
    }
    
    if (last !== null && last !== '') {
      // BỎ QUA lệnh spam từ chính user này với cùng command
      // ⚠️ QUAN TRỌNG: Báo rõ khi bị rate-limit để user biết
      try {
        // Tính thời gian còn lại (giây)
        // last có thể là timestamp (số) hoặc "1" (string cũ)
        var lastTime = 0;
        try {
          lastTime = parseInt(last, 10);
          if (isNaN(lastTime) || lastTime === 0) {
            // Nếu last không phải timestamp, giả định vừa mới đánh dấu
            lastTime = new Date().getTime();
          }
        } catch (parseErr) {
          // Nếu không parse được, giả định vừa mới đánh dấu
          lastTime = new Date().getTime();
        }
        
        var now = new Date().getTime();
        var elapsed = Math.floor((now - lastTime) / 1000);
        var wait = Math.max(1, rateLimitSeconds - elapsed);
        
        var waitMsg = "⏳ *LỆNH ĐANG ĐƯỢC XỬ LÝ*\n\n";
        waitMsg += "Lệnh `" + command + "` đã được gửi gần đây.\n\n";
        if (wait > 0) {
          waitMsg += "⏰ Vui lòng thử lại sau ~" + wait + " giây.\n\n";
        } else {
          waitMsg += "⏰ Vui lòng đợi một chút...\n\n";
        }
        waitMsg += "💡 *Lưu ý:*\n";
        waitMsg += "• Lệnh nhẹ: 2 giây\n";
        waitMsg += "• Lệnh nặng (/report, /statusads, /status...): 8 giây";
        
        guiThongBaoTelegram(waitMsg, botToken, replyChatId, replyToMessageId);
        Logger.log("⚠️ BỎ QUA (rate-limit user): " + rateLimitKey + " - Command đã được gửi " + elapsed + " giây trước, còn " + wait + " giây nữa");
      } catch (e) {
        Logger.log("⚠️ BỎ QUA (rate-limit user): " + rateLimitKey + " - Không thể gửi thông báo: " + e.message);
      }
      
      // ⚠️ QUAN TRỌNG: Vẫn trả về true để đánh dấu update_id (tránh retry từ Telegram)
      // Nhưng không xử lý command (đã bị rate limit chặn)
      return true; // Đánh dấu update_id đã được xử lý (bỏ qua do rate limit)
    }
    
    // Đánh dấu ngay (expires sau rateLimitSeconds)
    // Lưu timestamp thay vì "1" để tính thời gian còn lại
    var timestamp = new Date().getTime().toString();
    cache.put(rateLimitKey, timestamp, rateLimitSeconds);
    Logger.log("✅ Đã đánh dấu rate limit cho user " + fromUserId + " với command " + command + " (window: " + rateLimitSeconds + "s)");
    
    // Xử lý các commands (mỗi command được wrap trong try-catch riêng)
    // ⚠️ QUAN TRỌNG: Truyền replyToMessageId để bot có thể @ người gửi
    switch (command) {
      case '/start':
      case '/help':
        Logger.log("✅ Xử lý command: " + command);
        try {
          handleHelpCommand(botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /help: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi xử lý command: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/test':
        Logger.log("✅ Xử lý command: /test");
        try {
          handleTestCommand(botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /test: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi xử lý command: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/myid':
        // Đã xử lý ở trên, không cần xử lý lại
        break;
      case '/check_webhook':
        Logger.log("✅ Xử lý command: /check_webhook");
        try {
          handleCheckWebhookCommand(botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /check_webhook: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi kiểm tra webhook: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/reset_webhook':
        Logger.log("✅ Xử lý command: /reset_webhook");
        try {
          handleResetWebhookCommand(botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /reset_webhook: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi reset webhook: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/enable':
        Logger.log("✅ Xử lý command: /enable");
        try {
          handleEnableCommand(message, botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /enable: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi bật automation: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/disable':
        Logger.log("✅ Xử lý command: /disable");
        try {
          handleDisableCommand(message, botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /disable: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi tắt automation: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/status':
        Logger.log("✅ Xử lý command: /status");
        try {
          // Xử lý trực tiếp (đã được tối ưu để chạy nhanh)
          handleStatusCommand(botToken, replyChatId, replyToMessageId, false);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /status: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi xem trạng thái: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/disable_all':
        Logger.log("✅ Xử lý command: /disable_all");
        try {
          handleDisableAllCommand(botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /disable_all: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi tắt tất cả automation: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/enable_all':
        Logger.log("✅ Xử lý command: /enable_all");
        try {
          handleEnableAllCommand(botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /enable_all: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi bật tất cả automation: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/report':
        Logger.log("✅ Xử lý command: /report");
        try {
          // Xử lý trực tiếp (đã được tối ưu để chạy nhanh)
          handleReportCommand(botToken, replyChatId, replyToMessageId, false);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /report: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi tạo báo cáo tài chính: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/statusads':
        Logger.log("✅ Xử lý command: /statusads");
        try {
          // Xử lý trực tiếp (đã được tối ưu để chạy nhanh)
          handleStatusAdsCommand(botToken, replyChatId, replyToMessageId, false);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /statusads: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi tạo báo cáo trạng thái: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      case '/dashboard':
        Logger.log("✅ Xử lý command: /dashboard");
        try {
          // Xử lý trực tiếp (đã được tối ưu để chạy nhanh)
          sendDashboardOverview(botToken, replyChatId, replyToMessageId);
        } catch (e) {
          Logger.log("🚨 Lỗi xử lý /dashboard: " + e.message);
          guiThongBaoTelegram("❌ Lỗi khi tạo Dashboard Overview: " + e.message, botToken, replyChatId, replyToMessageId);
        }
        break;
      default:
        if (text.startsWith('/')) {
          Logger.log("⚠️ Command không hợp lệ: " + command);
          try {
            guiThongBaoTelegram("❌ Command không hợp lệ: `" + command + "`\n\nDùng /help để xem hướng dẫn.", botToken, replyChatId, replyToMessageId);
          } catch (e) {
            Logger.log("🚨 Không thể gửi thông báo command không hợp lệ: " + e.message);
          }
        }
    }
    
    // ⚠️ QUAN TRỌNG: Trả về true nếu đã xử lý thành công (không bị chặn)
    return true;
  } catch (e) {
    // Bắt mọi lỗi không mong đợi (không được bắt trong switch)
    Logger.log("🚨 Lỗi nghiêm trọng trong handleTelegramMessage: " + e.message + " | Stack: " + (e.stack || "N/A"));
    // KHÔNG GỬI THÔNG BÁO LỖI VÀO CHAT CÁ NHÂN
    // Chỉ log lỗi, không gửi message để tránh spam
    // Nếu cần gửi thông báo lỗi, chỉ gửi vào nhóm được phép
    try {
      var errorBotToken = null;
      var errorChatId = null;
      
      // Chỉ gửi thông báo lỗi vào nhóm được phép, KHÔNG vào chat cá nhân
      try {
        var errorSettings = getSettingsSafe_();
        errorBotToken = errorSettings['TELEGRAM_BOT_TOKEN'];
        // Chỉ dùng authorized chat ID (nhóm), KHÔNG dùng chat ID từ message (có thể là chat cá nhân)
        errorChatId = errorSettings['TELEGRAM_AUTHORIZED_CHAT_ID'] || errorSettings['TELEGRAM_CHAT_ID'];
      } catch (e3) {
        Logger.log("🚨 Không thể lấy settings để gửi thông báo lỗi: " + e3.message);
      }
      
      // Chỉ gửi nếu có bot token và chat ID là nhóm (âm)
      if (errorBotToken && errorChatId) {
        var chatIdNum = parseInt(String(errorChatId).trim(), 10);
        if (chatIdNum < 0) {
          // Chỉ gửi vào nhóm, không gửi vào chat cá nhân
          guiThongBaoTelegram("🚨 *LỖI XỬ LÝ COMMAND*\n\n" + e.message, errorBotToken, errorChatId);
        } else {
          Logger.log("⚠️ Bỏ qua gửi thông báo lỗi vào chat cá nhân (Chat ID: " + errorChatId + ")");
        }
      }
    } catch (e2) {
      Logger.log("🚨 Không thể gửi thông báo lỗi: " + e2.message);
    }
    // KHÔNG throw lại exception
  }
}

/**
 * Xử lý command /help
 */
function handleHelpCommand(botToken, chatId, replyToMessageId) {
  // ⚠️ QUAN TRỌNG: Rate limiting đã được xử lý ở handleTelegramMessage (toàn cục)
  // Không cần rate limiting riêng ở đây nữa
  
  var helpText = "🤖 *BOT TELEGRAM*\n\n";
  helpText += "*Các lệnh có sẵn:*\n\n";
  helpText += "• `/test`\n";
  helpText += "  Kiểm tra webhook có hoạt động không\n\n";
  helpText += "• `/myid`\n";
  helpText += "  Xem Chat ID của bạn (để cấu hình quyền)\n\n";
  helpText += "• `/check_webhook`\n";
  helpText += "  Kiểm tra trạng thái webhook hiện tại\n\n";
  helpText += "• `/reset_webhook`\n";
  helpText += "  Reset và cài đặt lại webhook\n\n";
  helpText += "• `/enable <account_id> <prefix>`\n";
  helpText += "  Bật automation cho account và prefix cụ thể\n";
  helpText += "  Ví dụ: `/enable 1027270998695466 LAKVDH`\n\n";
  helpText += "• `/disable <account_id> <prefix>`\n";
  helpText += "  Tắt automation cho account và prefix cụ thể\n";
  helpText += "  Ví dụ: `/disable 1027270998695466 LAKVDH`\n\n";
  helpText += "• `/status`\n";
  helpText += "  Xem trạng thái enable/disable của tất cả account|prefix\n\n";
  helpText += "• `/disable_all`\n";
  helpText += "  Tắt tất cả automation (chỉ chạy account|prefix được enable cụ thể)\n\n";
  helpText += "• `/enable_all`\n";
  helpText += "  Bật lại tất cả automation (trừ những cái bị disable cụ thể)\n\n";
  helpText += "• `/dashboard`\n";
  helpText += "  Xem dashboard tổng quan performance (tương tự Madgicx)\n\n";
  helpText += "• `/report`\n";
  helpText += "  Xem báo cáo tài chính cuối ngày (chi tiêu, tương tác, giá DATA, giá SĐT)\n\n";
  helpText += "• `/statusads`\n";
  helpText += "  Xem báo cáo trạng thái: số ads bật, số adsets tắt, số adsets đang bật\n\n";
  helpText += "• `/help`\n";
  helpText += "  Hiển thị hướng dẫn này\n\n";
  
  guiThongBaoTelegram(helpText, botToken, chatId, replyToMessageId);
}

/**
 * Xử lý command /test - Kiểm tra webhook
 */
function handleTestCommand(botToken, chatId, replyToMessageId) {
  // ⚠️ QUAN TRỌNG: Rate limiting đã được xử lý ở handleTelegramMessage (toàn cục)
  // Không cần rate limiting riêng ở đây nữa
  
  var testMsg = "✅ *WEBHOOK ĐANG HOẠT ĐỘNG!*\n\n";
  testMsg += "Bot đã nhận được command `/test` thành công.\n\n";
  testMsg += "🎉 *Điều này chứng tỏ:*\n";
  testMsg += "• Webhook đã được cài đặt đúng\n";
  testMsg += "• Bot có thể nhận và xử lý commands\n";
  testMsg += "• Commands hoạt động độc lập với automation\n\n";
  testMsg += "⏰ *Thời gian:* " + Utilities.formatDate(new Date(), Session.getScriptTimeZone() || 'Asia/Ho_Chi_Minh', "HH:mm:ss dd/MM/yyyy");
  
  guiThongBaoTelegram(testMsg, botToken, chatId, replyToMessageId);
}

/**
 * Xử lý command /enable <account_id> <prefix>
 * Ví dụ: /enable 1027270998695466 LAKVDH
 */
function handleEnableCommand(message, botToken, chatId) {
  try {
    var text = message.text || '';
    // ⚠️ QUAN TRỌNG: Tách text thành các phần (đã bỏ @BotName ở extractCommand_)
    var parts = text.split(/\s+/);
    // Loại bỏ phần command đầu tiên (đã được extract ở handleTelegramMessage)
    if (parts.length > 0 && parts[0].startsWith('/')) {
      parts = parts.slice(1); // Bỏ phần command, chỉ giữ lại arguments
    }
    
    if (parts.length < 2) {
      var errorMsg = "❌ *LỖI CÚ PHÁP*\n\n";
      errorMsg += "Cú pháp: `/enable <account_id> <prefix>`\n\n";
      errorMsg += "Ví dụ:\n";
      errorMsg += "`/enable 1027270998695466 LAKVDH`\n";
      errorMsg += "`/enable act_1027270998695466 PX`\n\n";
      errorMsg += "💡 *Lưu ý:*\n";
      errorMsg += "• Account ID có thể có hoặc không có prefix `act_`\n";
      errorMsg += "• Prefix sẽ được tự động chuyển thành chữ hoa\n";
      guiThongBaoTelegram(errorMsg, botToken, chatId);
      return;
    }
    
    var accountId = parts[0].trim();
    var prefix = parts[1].trim();
    
    if (!accountId || !prefix) {
      guiThongBaoTelegram("❌ Account ID hoặc Prefix không hợp lệ", botToken, chatId);
      return;
    }
    
    // Bật automation
    var success = enableAutomation(accountId, prefix);
    
    if (success) {
      // Chuẩn hóa để hiển thị
      var normalizedAccountId = accountId;
      if (normalizedAccountId.indexOf('act_') === 0) {
        normalizedAccountId = normalizedAccountId.substring(4);
      }
      var normalizedPrefix = prefix.toUpperCase();
      
      var successMsg = "✅ *ĐÃ BẬT AUTOMATION*\n\n";
      successMsg += "📛 *Account:* `" + normalizedAccountId + "`\n";
      successMsg += "🏷️ *Prefix:* `" + normalizedPrefix + "`\n\n";
      successMsg += "💡 Automation sẽ chạy logic tắt/bật quảng cáo cho account và prefix này.";
      guiThongBaoTelegram(successMsg, botToken, chatId);
    } else {
      guiThongBaoTelegram("❌ Không thể bật automation. Vui lòng thử lại.", botToken, chatId);
    }
  } catch (e) {
    Logger.log("🚨 Lỗi xử lý /enable: " + e.message);
    guiThongBaoTelegram("❌ Lỗi khi bật automation: " + e.message, botToken, chatId);
  }
}

/**
 * Xử lý command /disable <account_id> <prefix>
 * Ví dụ: /disable 1027270998695466 LAKVDH
 */
function handleDisableCommand(message, botToken, chatId, replyToMessageId) {
  try {
    var text = message.text || '';
    // ⚠️ QUAN TRỌNG: Tách text thành các phần (đã bỏ @BotName ở extractCommand_)
    var parts = text.split(/\s+/);
    // Loại bỏ phần command đầu tiên (đã được extract ở handleTelegramMessage)
    if (parts.length > 0 && parts[0].startsWith('/')) {
      parts = parts.slice(1); // Bỏ phần command, chỉ giữ lại arguments
    }
    
    if (parts.length < 2) {
      var errorMsg = "❌ *LỖI CÚ PHÁP*\n\n";
      errorMsg += "Cú pháp: `/disable <account_id> <prefix>`\n\n";
      errorMsg += "Ví dụ:\n";
      errorMsg += "`/disable 1027270998695466 LAKVDH`\n";
      errorMsg += "`/disable act_1027270998695466 PX`\n\n";
      errorMsg += "💡 *Lưu ý:*\n";
      errorMsg += "• Account ID có thể có hoặc không có prefix `act_`\n";
      errorMsg += "• Prefix sẽ được tự động chuyển thành chữ hoa\n";
      errorMsg += "• Khi tắt, automation sẽ BỎ QUA account|prefix này khi chạy logic";
      guiThongBaoTelegram(errorMsg, botToken, chatId, replyToMessageId);
      return;
    }
    
    var accountId = parts[0].trim();
    var prefix = parts[1].trim();
    
    if (!accountId || !prefix) {
      guiThongBaoTelegram("❌ Account ID hoặc Prefix không hợp lệ", botToken, chatId, replyToMessageId);
      return;
    }
    
    // Tắt automation
    var success = disableAutomation(accountId, prefix);
    
    if (success) {
      // Chuẩn hóa để hiển thị
      var normalizedAccountId = accountId;
      if (normalizedAccountId.indexOf('act_') === 0) {
        normalizedAccountId = normalizedAccountId.substring(4);
      }
      var normalizedPrefix = prefix.toUpperCase();
      
      var successMsg = "⛔ *ĐÃ TẮT AUTOMATION*\n\n";
      successMsg += "📛 *Account:* `" + normalizedAccountId + "`\n";
      successMsg += "🏷️ *Prefix:* `" + normalizedPrefix + "`\n\n";
      successMsg += "💡 Automation sẽ BỎ QUA account và prefix này khi chạy logic.\n";
      successMsg += "Dùng `/enable " + normalizedAccountId + " " + normalizedPrefix + "` để bật lại.";
      guiThongBaoTelegram(successMsg, botToken, chatId, replyToMessageId);
    } else {
      guiThongBaoTelegram("❌ Không thể tắt automation. Vui lòng thử lại.", botToken, chatId, replyToMessageId);
    }
  } catch (e) {
    Logger.log("🚨 Lỗi xử lý /disable: " + e.message);
    guiThongBaoTelegram("❌ Lỗi khi tắt automation: " + e.message, botToken, chatId, replyToMessageId);
  }
}

/**
 * Tắt tất cả automation (chỉ chạy những account|prefix được enable cụ thể)
 */
function disableAllAutomation() {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('AUTOMATION_DISABLE_ALL', 'true');
    Logger.log("✅ Đã tắt tất cả automation (disable_all = true)");
    return true;
  } catch (e) {
    Logger.log("⚠️ Lỗi tắt tất cả automation: " + e.message);
    return false;
  }
}

/**
 * Bật lại tất cả automation (trừ những cái bị disable cụ thể)
 */
function enableAllAutomation() {
  try {
    var props = PropertiesService.getScriptProperties();
    props.setProperty('AUTOMATION_DISABLE_ALL', 'false');
    Logger.log("✅ Đã bật lại tất cả automation (disable_all = false)");
    return true;
  } catch (e) {
    Logger.log("⚠️ Lỗi bật tất cả automation: " + e.message);
    return false;
  }
}

/**
 * Xử lý command /disable_all
 */
function handleDisableAllCommand(botToken, chatId, replyToMessageId) {
  try {
    var success = disableAllAutomation();
    
    if (success) {
      var statusList = getAllAutomationStatus();
      var enabledCount = 0;
      for (var i = 0; i < statusList.length; i++) {
        if (statusList[i].enabled) {
          enabledCount++;
        }
      }
      
      var msg = "⛔ *ĐÃ TẮT TẤT CẢ AUTOMATION*\n\n";
      msg += "💡 *Lưu ý:*\n";
      msg += "• Tất cả automation đã bị tắt\n";
      msg += "• Chỉ những account|prefix được enable cụ thể mới được chạy\n\n";
      
      if (enabledCount > 0) {
        msg += "✅ Hiện có " + enabledCount + " account|prefix được enable cụ thể và sẽ tiếp tục chạy.\n\n";
      } else {
        msg += "⚠️ Không có account|prefix nào được enable cụ thể.\n";
        msg += "→ Automation sẽ không chạy cho bất kỳ account|prefix nào.\n\n";
      }
      
      msg += "📝 *Để bật lại tất cả:*\n";
      msg += "`/enable_all`\n\n";
      msg += "📝 *Để enable từng account|prefix:*\n";
      msg += "`/enable <account_id> <prefix>`";
      
      guiThongBaoTelegram(msg, botToken, chatId, replyToMessageId);
    } else {
      guiThongBaoTelegram("❌ Không thể tắt tất cả automation. Vui lòng thử lại.", botToken, chatId, replyToMessageId);
    }
  } catch (e) {
    Logger.log("🚨 Lỗi xử lý /disable_all: " + e.message);
    guiThongBaoTelegram("❌ Lỗi khi tắt tất cả automation: " + e.message, botToken, chatId, replyToMessageId);
  }
}

/**
 * Xử lý command /enable_all
 */
function handleEnableAllCommand(botToken, chatId, replyToMessageId) {
  try {
    var success = enableAllAutomation();
    
    if (success) {
      var statusList = getAllAutomationStatus();
      var disabledCount = 0;
      for (var i = 0; i < statusList.length; i++) {
        if (!statusList[i].enabled) {
          disabledCount++;
        }
      }
      
      var msg = "✅ *ĐÃ BẬT LẠI TẤT CẢ AUTOMATION*\n\n";
      msg += "💡 *Lưu ý:*\n";
      msg += "• Tất cả automation đã được bật lại\n";
      
      if (disabledCount > 0) {
        msg += "• Có " + disabledCount + " account|prefix bị disable cụ thể và sẽ KHÔNG chạy\n\n";
      } else {
        msg += "• Không có account|prefix nào bị disable cụ thể\n";
        msg += "→ Tất cả account|prefix sẽ được chạy\n\n";
      }
      
      msg += "📝 *Để disable từng account|prefix:*\n";
      msg += "`/disable <account_id> <prefix>`";
      
      guiThongBaoTelegram(msg, botToken, chatId, replyToMessageId);
    } else {
      guiThongBaoTelegram("❌ Không thể bật tất cả automation. Vui lòng thử lại.", botToken, chatId, replyToMessageId);
    }
  } catch (e) {
    Logger.log("🚨 Lỗi xử lý /enable_all: " + e.message);
    guiThongBaoTelegram("❌ Lỗi khi bật tất cả automation: " + e.message, botToken, chatId, replyToMessageId);
  }
}

/**
 * Xử lý command /status - Xem trạng thái enable/disable của tất cả account|prefix
 */
function handleStatusCommand(botToken, chatId, replyToMessageId, skipProcessingMsg) {
  // ⚠️ QUAN TRỌNG: Rate limiting đã được xử lý ở handleTelegramMessage (toàn cục)
  // Không cần rate limiting riêng ở đây nữa
  // skipProcessingMsg: Nếu true, không gửi message "Đang xử lý..." (đã có thông báo "Đang chờ" rồi)
  
  try {
    // ⚠️ TỐI ƯU: Cache kết quả từ LogicRules trong 60 giây
    var cache = CacheService.getScriptCache();
    var accountIdsCacheKey = 'LOGIC_RULES_ACCOUNT_IDS';
    var prefixesCacheKey = 'LOGIC_RULES_PREFIXES';
    
    var allAccountIds = [];
    var allPrefixes = [];
    
    // Lấy Account IDs từ cache hoặc đọc từ sheet
    try {
      var cachedAccountIds = cache.get(accountIdsCacheKey);
      if (cachedAccountIds !== null && cachedAccountIds !== '') {
        try {
          allAccountIds = JSON.parse(cachedAccountIds);
          Logger.log("✅ Đã lấy account IDs từ cache (" + allAccountIds.length + " accounts)");
        } catch (parseErr) {
          Logger.log("⚠️ Lỗi parse cache account IDs, đọc lại từ sheet");
          if (typeof extractAccountIdsFromLogicRules_ === 'function') {
            allAccountIds = extractAccountIdsFromLogicRules_();
            cache.put(accountIdsCacheKey, JSON.stringify(allAccountIds), 60);
          }
        }
      } else {
        if (typeof extractAccountIdsFromLogicRules_ === 'function') {
          allAccountIds = extractAccountIdsFromLogicRules_();
          cache.put(accountIdsCacheKey, JSON.stringify(allAccountIds), 60);
        }
      }
    } catch (e) {
      Logger.log("⚠️ Lỗi khi lấy account IDs: " + e.message);
    }
    
    // Lấy Prefixes từ cache hoặc đọc từ sheet
    try {
      var cachedPrefixes = cache.get(prefixesCacheKey);
      if (cachedPrefixes !== null && cachedPrefixes !== '') {
        try {
          allPrefixes = JSON.parse(cachedPrefixes);
          Logger.log("✅ Đã lấy prefixes từ cache (" + allPrefixes.length + " prefixes)");
        } catch (parseErr) {
          Logger.log("⚠️ Lỗi parse cache prefixes, đọc lại từ sheet");
          if (typeof extractPrefixesFromLogicRules_ === 'function') {
            allPrefixes = extractPrefixesFromLogicRules_();
            cache.put(prefixesCacheKey, JSON.stringify(allPrefixes), 60);
          }
        }
      } else {
        if (typeof extractPrefixesFromLogicRules_ === 'function') {
          allPrefixes = extractPrefixesFromLogicRules_();
          cache.put(prefixesCacheKey, JSON.stringify(allPrefixes), 60);
        }
      }
    } catch (e) {
      Logger.log("⚠️ Lỗi khi lấy prefixes: " + e.message);
    }
    
    // Lấy trạng thái enable/disable đã cấu hình (đã có cache trong getAllAutomationStatus)
    var statusList = getAllAutomationStatus();
    var statusMap = {}; // { "accountId|prefix": { enabled: boolean } }
    for (var i = 0; i < statusList.length; i++) {
      var item = statusList[i];
      var key = item.accountId + "|" + item.prefix;
      statusMap[key] = { enabled: item.enabled };
    }
    
    // Kiểm tra trạng thái disable_all
    var props = PropertiesService.getScriptProperties();
    var disableAll = props.getProperty('AUTOMATION_DISABLE_ALL');
    var isDisableAll = (disableAll === 'true');
    
    var statusMsg = "📊 *TRẠNG THÁI AUTOMATION*\n\n";
    
    // Hiển thị trạng thái disable_all
    if (isDisableAll) {
      statusMsg += "⛔ *CHẾ ĐỘ DISABLE_ALL: BẬT*\n";
      statusMsg += "→ Chỉ những account|prefix được enable cụ thể mới chạy\n\n";
    } else {
      statusMsg += "✅ *CHẾ ĐỘ DISABLE_ALL: TẮT*\n";
      statusMsg += "→ Tất cả account|prefix đều chạy (trừ những cái bị disable cụ thể)\n\n";
    }
    
    statusMsg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n";
    
    // Nếu không có account|prefix từ LogicRules, chỉ hiển thị những cái đã cấu hình
    if (allAccountIds.length === 0 && allPrefixes.length === 0) {
      if (statusList.length === 0) {
        var noStatusMsg = "📊 *TRẠNG THÁI AUTOMATION*\n\n";
        noStatusMsg += "Không có account|prefix nào được cấu hình enable/disable.\n\n";
        noStatusMsg += "💡 *Mặc định:* Tất cả account|prefix đều được BẬT automation.\n\n";
        noStatusMsg += "Dùng `/enable <account_id> <prefix>` để bật hoặc `/disable <account_id> <prefix>` để tắt.";
        guiThongBaoTelegram(noStatusMsg, botToken, chatId);
        return;
      }
      
      // Chỉ hiển thị những cái đã cấu hình
      var byAccount = {};
      for (var i = 0; i < statusList.length; i++) {
        var item = statusList[i];
        var accId = item.accountId;
        if (!byAccount[accId]) {
          byAccount[accId] = [];
        }
        byAccount[accId].push(item);
      }
      
      var accountIds = Object.keys(byAccount).sort();
      for (var accIdx = 0; accIdx < accountIds.length; accIdx++) {
        var accId = accountIds[accIdx];
        var prefixes = byAccount[accId];
        
        statusMsg += "📛 *Account:* `" + accId + "`\n";
        
        // Sắp xếp prefix
        prefixes.sort(function(a, b) {
          if (a.enabled !== b.enabled) {
            return a.enabled ? -1 : 1; // Enabled trước
          }
          return a.prefix.localeCompare(b.prefix);
        });
        
        for (var pIdx = 0; pIdx < prefixes.length; pIdx++) {
          var prefixItem = prefixes[pIdx];
          var statusIcon = prefixItem.enabled ? "✅" : "⛔";
          var statusText = prefixItem.enabled ? "BẬT" : "TẮT";
          statusMsg += "  " + statusIcon + " *" + prefixItem.prefix + "*: " + statusText + "\n";
        }
        
        statusMsg += "\n";
      }
    } else {
      // Hiển thị TẤT CẢ account|prefix từ LogicRules
      // Tạo ma trận account x prefix
      var accountPrefixMatrix = {}; // { accountId: { prefix: enabled } }
      
      // Khởi tạo ma trận với tất cả account|prefix từ LogicRules
      for (var accIdx = 0; accIdx < allAccountIds.length; accIdx++) {
        var accId = allAccountIds[accIdx];
        // Loại bỏ "act_" prefix để hiển thị
        var displayAccId = accId.indexOf('act_') === 0 ? accId.substring(4) : accId;
        if (!accountPrefixMatrix[displayAccId]) {
          accountPrefixMatrix[displayAccId] = {};
        }
        for (var pIdx = 0; pIdx < allPrefixes.length; pIdx++) {
          var prefix = allPrefixes[pIdx];
          var key = accId + "|" + prefix;
          // Kiểm tra trạng thái enable/disable
          var enabled = true; // Mặc định enabled
          if (isDisableAll) {
            // Chế độ disable_all: CHỈ enabled nếu có flag "true"
            enabled = (statusMap[key] && statusMap[key].enabled === true);
          } else {
            // Chế độ bình thường: enabled TRỪ khi có flag "false"
            enabled = !(statusMap[key] && statusMap[key].enabled === false);
          }
          accountPrefixMatrix[displayAccId][prefix] = enabled;
        }
      }
      
      // Hiển thị theo từng account
      var sortedAccountIds = Object.keys(accountPrefixMatrix).sort();
      for (var accIdx = 0; accIdx < sortedAccountIds.length; accIdx++) {
        var displayAccId = sortedAccountIds[accIdx];
        var prefixStatus = accountPrefixMatrix[displayAccId];
        
        statusMsg += "📛 *Account:* `" + displayAccId + "`\n";
        
        // Sắp xếp prefix
        var sortedPrefixes = Object.keys(prefixStatus).sort();
        for (var pIdx = 0; pIdx < sortedPrefixes.length; pIdx++) {
          var prefix = sortedPrefixes[pIdx];
          var enabled = prefixStatus[prefix];
          var statusIcon = enabled ? "✅" : "⛔";
          var statusText = enabled ? "BẬT" : "TẮT";
          statusMsg += "  " + statusIcon + " *" + prefix + "*: " + statusText + "\n";
        }
        
        statusMsg += "\n";
      }
    }
    
    statusMsg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n";
    
    statusMsg += "💡 *Lưu ý:*\n";
    if (isDisableAll) {
      statusMsg += "• Account|prefix có ⛔ = KHÔNG CHẠY\n";
      statusMsg += "• Chỉ account|prefix có ✅ mới được chạy\n";
      statusMsg += "• Dùng `/enable <account_id> <prefix>` để bật từng cái\n";
      statusMsg += "• Dùng `/enable_all` để bật lại tất cả\n";
    } else {
      statusMsg += "• Account|prefix có ✅ = ĐANG CHẠY\n";
      statusMsg += "• Account|prefix có ⛔ = BỊ TẮT (disable cụ thể)\n";
      statusMsg += "• Dùng `/enable <account_id> <prefix>` để bật\n";
      statusMsg += "• Dùng `/disable <account_id> <prefix>` để tắt\n";
    }
    statusMsg += "• Dùng `/disable_all` để tắt tất cả";
    
    guiThongBaoTelegram(statusMsg, botToken, chatId, replyToMessageId);
  } catch (e) {
    Logger.log("🚨 Lỗi xử lý /status: " + e.message);
    guiThongBaoTelegram("❌ Lỗi khi xem trạng thái: " + e.message, botToken, chatId, replyToMessageId);
  }
}

/**
 * Xử lý command /report - Xem báo cáo tài chính cuối ngày
 * Gọi hàm tongKetCuoiNgay(): Báo cáo tài chính (chi tiêu, tương tác, giá DATA, giá SĐT)
 */
function handleReportCommand(botToken, chatId, replyToMessageId, skipProcessingMsg) {
  // ⚠️ QUAN TRỌNG: Rate limiting đã được xử lý ở handleTelegramMessage (toàn cục)
  // Không cần rate limiting riêng ở đây nữa
  // skipProcessingMsg: Nếu true, không gửi message "Đang xử lý..." (đã có thông báo "Đang chờ" rồi)
  
  try {
    // ⚠️ QUAN TRỌNG: Gửi message "Đang xử lý..." nếu chưa có thông báo trước đó
    if (!skipProcessingMsg) {
      var processingMsg = "⏳ *ĐANG XỬ LÝ BÁO CÁO...*\n\n";
      processingMsg += "📊 Đang tạo báo cáo tài chính cuối ngày...\n";
      processingMsg += "⏰ Vui lòng đợi, có thể mất 10-20 giây...\n\n";
      processingMsg += "💡 Báo cáo sẽ được gửi ngay khi hoàn thành.";
      guiThongBaoTelegram(processingMsg, botToken, chatId, replyToMessageId);
    }
    
    // Kiểm tra xem hàm tongKetCuoiNgay có tồn tại không
    if (typeof tongKetCuoiNgay !== 'function') {
      guiThongBaoTelegram("❌ Hàm tongKetCuoiNgay không tồn tại. Vui lòng kiểm tra code.", botToken, chatId, replyToMessageId);
      return;
    }
    
    // Gọi hàm tongKetCuoiNgay với botToken và chatId được chỉ định
    // Hàm này sẽ tự gửi báo cáo tài chính vào chatId được chỉ định
    // LƯU Ý: tongKetCuoiNgay có thể không hỗ trợ replyToMessageId, nhưng vẫn gọi để gửi báo cáo
    // Hàm này có thể mất 10-20 giây, nhưng đã gửi "Đang xử lý..." rồi (hoặc "Đang chờ" từ async task), nên user biết lệnh đã được nhận
    tongKetCuoiNgay(botToken, chatId);
    
  } catch (e) {
    Logger.log("🚨 Lỗi xử lý /report: " + e.message);
    guiThongBaoTelegram("❌ Lỗi khi tạo báo cáo tài chính: " + e.message, botToken, chatId, replyToMessageId);
  }
}

/**
 * Xử lý command /statusads - Xem báo cáo trạng thái ads
 * Gọi hàm generateSummaryReport(): Báo cáo trạng thái (số ads bật, số adsets tắt, số adsets đang bật)
 */
function handleStatusAdsCommand(botToken, chatId, replyToMessageId, skipProcessingMsg) {
  // ⚠️ QUAN TRỌNG: Rate limiting đã được xử lý ở handleTelegramMessage (toàn cục)
  // Không cần rate limiting riêng ở đây nữa
  // skipProcessingMsg: Nếu true, không gửi message "Đang xử lý..." (đã có thông báo "Đang chờ" rồi)
  
  try {
    // ⚠️ QUAN TRỌNG: Gửi message "Đang xử lý..." nếu chưa có thông báo trước đó
    if (!skipProcessingMsg) {
      var processingMsg = "⏳ *ĐANG XỬ LÝ BÁO CÁO...*\n\n";
      processingMsg += "📊 Đang tạo báo cáo trạng thái ads...\n";
      processingMsg += "⏰ Vui lòng đợi...\n\n";
      processingMsg += "💡 Báo cáo sẽ được gửi ngay khi hoàn thành.";
      guiThongBaoTelegram(processingMsg, botToken, chatId, replyToMessageId);
    }
    
    // Lấy settings
    var settings = getSettingsSafe_();
    if (!settings) {
      guiThongBaoTelegram("❌ Không thể lấy cài đặt hệ thống.", botToken, chatId, replyToMessageId);
      return;
    }
    
    // Lấy thông tin sheet
    var ss = getSpreadsheet_();
    if (!ss) {
      guiThongBaoTelegram("❌ Không thể mở spreadsheet.", botToken, chatId, replyToMessageId);
      return;
    }
    
    var dataSheet = ss.getSheetByName('Data_FB');
    if (!dataSheet) {
      guiThongBaoTelegram("❌ Không tìm thấy sheet 'Data_FB'.", botToken, chatId, replyToMessageId);
      return;
    }
    
    // Đọc dữ liệu và tạo colMap
    var data = dataSheet.getDataRange().getValues();
    if (data.length < 3) {
      guiThongBaoTelegram("❌ Sheet 'Data_FB' không có dữ liệu.", botToken, chatId, replyToMessageId);
      return;
    }
    
    data.shift(); // Bỏ qua hàng 1
    var headers = data.shift(); // Hàng 2 (Headers)
    
    var colMap = {};
    for (var i = 0; i < headers.length; i++) {
      if (headers[i]) {
        colMap[String(headers[i]).trim()] = i;
      }
    }
    
    // Gọi generateSummaryReport (báo cáo trạng thái)
    // Hàm này có thể mất vài giây, nhưng đã trả response cho Telegram rồi, nên không bị timeout
    var report = generateSummaryReport(dataSheet, colMap, 0);
    
    if (report) {
      guiThongBaoTelegram(report, botToken, chatId, replyToMessageId);
    } else {
      guiThongBaoTelegram("❌ Không thể tạo báo cáo trạng thái. Vui lòng kiểm tra log để biết chi tiết.", botToken, chatId, replyToMessageId);
    }
  } catch (e) {
    Logger.log("🚨 Lỗi xử lý /statusads: " + e.message);
    guiThongBaoTelegram("❌ Lỗi khi tạo báo cáo trạng thái: " + e.message, botToken, chatId, replyToMessageId);
  }
}


/**
 * Cài đặt webhook cho Telegram Bot với URL cụ thể
 * HÀM CHÍNH: Thực hiện toàn bộ logic setup webhook
 * 
 * @param {string} webhookUrl - URL webhook (nếu null/undefined sẽ tự động lấy từ sheet/Script Properties/mặc định)
 * @returns {boolean} - true nếu thành công, false nếu thất bại
 */
function setupTelegramWebhookWithUrl(webhookUrl, chatId) {
  try {
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = settings['TELEGRAM_CHAT_ID'];
    
    // Kiểm tra Bot Token
    if (!botToken) {
      Logger.log("❌ Không có Bot Token trong settings");
      if (chatId) {
        guiThongBaoTelegram("❌ Không có Bot Token. Vui lòng kiểm tra lại cài đặt trong sheet CaiDat.", botToken, chatId);
      }
      return false;
    }
    
    // Chuẩn hóa Bot Token (trim và kiểm tra format)
    botToken = String(botToken).trim();
    
    // Kiểm tra format Bot Token (phải có dạng: số:dấu:chuỗi)
    if (!botToken.match(/^\d+:[A-Za-z0-9_-]+$/)) {
      Logger.log("❌ Bot Token không đúng format. Token: " + botToken.substring(0, 10) + "... (length: " + botToken.length + ")");
      Logger.log("❌ Bot Token phải có format: số:dấu:chuỗi (ví dụ: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz)");
      if (chatId) {
        guiThongBaoTelegram("❌ *BOT TOKEN KHÔNG HỢP LỆ*\n\nBot Token không đúng format.\n\nVui lòng kiểm tra lại Bot Token trong sheet CaiDat.\n\nBot Token phải có format: `số:dấu:chuỗi`\nVí dụ: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`", botToken, chatId);
      }
      return false;
    }
    
    Logger.log("✅ Bot Token hợp lệ (format đúng), length: " + botToken.length);
    
    // Lấy URL từ settings (sheet CaiDat) nếu không có URL được truyền vào
    if (!webhookUrl) {
      // Ưu tiên 1: Đọc từ sheet CaiDat
      var webhookUrlFromSheet = settings['WEBHOOK_URL'];
      if (webhookUrlFromSheet && String(webhookUrlFromSheet).trim() !== '') {
        webhookUrl = String(webhookUrlFromSheet).trim();
        Logger.log("✅ Đã lấy WEBHOOK_URL từ sheet CaiDat: " + webhookUrl);
      } else {
        // Ưu tiên 2: Đọc từ Script Properties (nếu đã lưu trước đó)
        var props = PropertiesService.getScriptProperties();
        var savedUrl = props.getProperty('WEBHOOK_URL_CURRENT');
        if (savedUrl && String(savedUrl).trim() !== '') {
          webhookUrl = String(savedUrl).trim();
          Logger.log("✅ Đã lấy WEBHOOK_URL từ Script Properties: " + webhookUrl);
        } else {
          // Ưu tiên 3: Dùng biến mặc định (fallback)
          webhookUrl = WEBHOOK_URL_DEFAULT;
          Logger.log("⚠️ Sử dụng WEBHOOK_URL mặc định (không có trong sheet): " + webhookUrl);
          Logger.log("💡 LƯU Ý: Hãy thêm WEBHOOK_URL vào sheet CaiDat (hàng 13, cột C) để dễ quản lý!");
        }
      }
    }
    
    // Kiểm tra URL hợp lệ
    if (!webhookUrl || webhookUrl.indexOf('/exec') < 0) {
      var errorMsg = "❌ *LỖI: URL KHÔNG HỢP LỆ*\n\n";
      errorMsg += "URL: `" + (webhookUrl || "null") + "`\n\n";
      errorMsg += "URL phải chứa `/exec` endpoint.\n";
      Logger.log(errorMsg);
      if (chatId) {
        guiThongBaoTelegram(errorMsg, botToken, chatId);
      }
      return false;
    }
    
    Logger.log("🔄 Đang set webhook với URL: " + webhookUrl);
    Logger.log("🔄 Bot Token (5 ký tự đầu): " + botToken.substring(0, 5) + "...");
    
    // Test Bot Token trước khi set webhook
    var tokenTest = testBotToken(botToken);
    if (!tokenTest.valid) {
      Logger.log("❌ Bot Token không hợp lệ. Lỗi: " + tokenTest.error);
      if (chatId) {
        var tokenErrorMsg = "❌ *BOT TOKEN KHÔNG HỢP LỆ*\n\n";
        tokenErrorMsg += "Lỗi: " + tokenTest.error + "\n\n";
        tokenErrorMsg += "Vui lòng kiểm tra:\n";
        tokenErrorMsg += "1. Bot Token trong sheet CaiDat có đúng không\n";
        tokenErrorMsg += "2. Bot Token có bị revoke hoặc đã thay đổi không\n";
        tokenErrorMsg += "3. Lấy Bot Token mới từ @BotFather nếu cần\n\n";
        tokenErrorMsg += "💡 *Hướng dẫn lấy Bot Token:*\n";
        tokenErrorMsg += "1. Mở Telegram, tìm @BotFather\n";
        tokenErrorMsg += "2. Gửi lệnh /token\n";
        tokenErrorMsg += "3. Chọn bot cần lấy token\n";
        tokenErrorMsg += "4. Copy token và cập nhật vào sheet CaiDat";
        guiThongBaoTelegram(tokenErrorMsg, botToken, chatId);
      }
      return false;
    }
    
    Logger.log("✅ Bot Token hợp lệ. Bot username: @" + (tokenTest.botInfo ? tokenTest.botInfo.username : "N/A"));
    
    // Set webhook
    var telegramUrl = 'https://api.telegram.org/bot' + botToken + '/setWebhook';
    var payload = {
      'url': webhookUrl,
      // ⚠️ QUAN TRỌNG: Chỉ nhận message updates (không nhận edited_message, channel_post, etc.)
      // Điều này giúp giảm số lượng updates không cần thiết và tránh xử lý nhầm
      'allowed_updates': ["message"],
      // ⚠️ QUAN TRỌNG: Xóa tất cả pending updates khi set webhook (tránh backlog)
      // Điều này giúp tránh xử lý các updates cũ đang chờ trong hàng đợi
      'drop_pending_updates': true
    };
    
    Logger.log("🔄 Đang set webhook với payload: " + JSON.stringify(payload));
    
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true
    };
    
    var response = UrlFetchApp.fetch(telegramUrl, options);
    var result = JSON.parse(response.getContentText());
    
    if (result.ok) {
      // Lưu URL vào Script Properties để backup (nếu URL không có trong sheet)
      try {
        var props = PropertiesService.getScriptProperties();
        // Chỉ lưu backup nếu URL không phải từ sheet (để tránh conflict)
        var settingsCheck = getSettingsSafe_();
        var urlFromSheet = settingsCheck && settingsCheck['WEBHOOK_URL'] ? String(settingsCheck['WEBHOOK_URL']).trim() : '';
        if (webhookUrl !== urlFromSheet) {
          props.setProperty('WEBHOOK_URL_CURRENT', webhookUrl);
          Logger.log("✅ Đã lưu webhook URL vào Script Properties (backup): " + webhookUrl);
        } else {
          Logger.log("ℹ️ URL đã có trong sheet CaiDat, không cần lưu backup");
        }
      } catch (saveErr) {
        Logger.log("⚠️ Không thể lưu backup URL: " + saveErr.message);
      }
      
      var successMsg = "✅ *ĐÃ CÀI ĐẶT WEBHOOK THÀNH CÔNG*\n\n";
      successMsg += "Webhook URL: `" + webhookUrl + "`\n\n";
      successMsg += "🔧 *Cấu hình:*\n";
      successMsg += "• Chỉ nhận `message` updates\n";
      successMsg += "• Đã xóa tất cả pending updates\n\n";
      successMsg += "🎉 *Bây giờ bạn có thể dùng các lệnh Telegram:*\n";
      successMsg += "• `/help` - Xem hướng dẫn\n";
      successMsg += "• `/status` - Xem trạng thái\n";
      successMsg += "• `/enable <account_id> <prefix>` - Bật automation\n";
      successMsg += "• `/disable <account_id> <prefix>` - Tắt automation\n";
      successMsg += "• `/report` - Xem báo cáo\n\n";
      successMsg += "✅ *Lưu ý:* Webhook hoạt động ĐỘC LẬP với automation. Commands sẽ hoạt động ngay cả khi script đang nghỉ hoặc automation bị tắt!";
      
      Logger.log("✅ Đã cài đặt webhook thành công: " + webhookUrl);
      Logger.log("✅ Webhook config: allowed_updates=['message'], drop_pending_updates=true");
      
      if (chatId) {
        guiThongBaoTelegram(successMsg, botToken, chatId);
      }
      return true;
    } else {
      var errorMsg = "❌ *LỖI CÀI ĐẶT WEBHOOK*\n\n";
      errorMsg += "Lỗi: " + (result.description || "Unknown error") + "\n\n";
      errorMsg += "Vui lòng kiểm tra lại Bot Token và thử lại.";
      
      Logger.log("❌ Lỗi cài đặt webhook: " + result.description);
      if (chatId) {
        guiThongBaoTelegram(errorMsg, botToken, chatId);
      }
      return false;
    }
  } catch (e) {
    Logger.log("🚨 Lỗi setup webhook: " + e.message);
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = settings['TELEGRAM_CHAT_ID'];
    if (botToken && chatId) {
      guiThongBaoTelegram("🚨 *LỖI SETUP WEBHOOK*\n\n" + e.message, botToken, chatId);
    }
    return false;
  }
}

/**
 * Hàm debug: Kiểm tra Bot Token từ sheet
 * Chạy hàm này để xem Bot Token có được đọc đúng không
 */
function debugBotToken() {
  try {
    Logger.log("🔍 DEBUG BOT TOKEN:");
    
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    
    if (!botToken) {
      Logger.log("❌ Không có Bot Token trong settings");
      
      // Thử đọc trực tiếp từ sheet
      try {
        var ss = SpreadsheetApp.getActiveSpreadsheet();
        var sheet = ss.getSheetByName('CaiDat');
        if (sheet) {
          var data = sheet.getDataRange().getValues();
          Logger.log("📋 Đọc trực tiếp từ sheet CaiDat:");
          for (var i = 1; i < data.length; i++) {
            if (data[i][0] && String(data[i][0]).trim() === 'TELEGRAM_BOT_TOKEN') {
              var rawValue = data[i][2];
              Logger.log("   Cột A: " + data[i][0]);
              Logger.log("   Cột C (raw): '" + rawValue + "'");
              Logger.log("   Cột C (type): " + typeof rawValue);
              Logger.log("   Cột C (length): " + (rawValue ? String(rawValue).length : 0));
              if (rawValue) {
                var trimmed = String(rawValue).trim();
                Logger.log("   Cột C (trimmed): '" + trimmed.substring(0, 10) + "..." + trimmed.substring(trimmed.length - 5) + "'");
                Logger.log("   Cột C (trimmed length): " + trimmed.length);
              }
            }
          }
        }
      } catch (e) {
        Logger.log("⚠️ Lỗi đọc sheet: " + e.message);
      }
      
      return;
    }
    
    Logger.log("✅ Bot Token từ settings: '" + botToken.substring(0, 10) + "..." + botToken.substring(botToken.length - 5) + "'");
    Logger.log("✅ Bot Token length: " + botToken.length);
    
    // Test Bot Token
    var tokenTest = testBotToken(botToken);
    if (tokenTest.valid) {
      Logger.log("✅ Bot Token hợp lệ!");
      Logger.log("   Bot username: @" + (tokenTest.botInfo ? tokenTest.botInfo.username : "N/A"));
      Logger.log("   Bot first name: " + (tokenTest.botInfo ? tokenTest.botInfo.first_name : "N/A"));
    } else {
      Logger.log("❌ Bot Token không hợp lệ!");
      Logger.log("   Lỗi: " + tokenTest.error);
    }
  } catch (e) {
    Logger.log("🚨 Lỗi debug Bot Token: " + e.message);
  }
}

/**
 * Cài đặt webhook cho Telegram Bot
 * Tự động lấy URL từ Script Properties hoặc dùng WEBHOOK_URL mặc định
 * 
 * LƯU Ý QUAN TRỌNG:
 * - Webhook hoạt động ĐỘC LẬP với automation triggers
 * - Commands Telegram vẫn hoạt động ngay cả khi script đang nghỉ hoặc automation bị tắt
 * - Webhook được gọi trực tiếp bởi Telegram server khi có message, không cần script chạy
 * 
 * QUAN TRỌNG: Hàm này sẽ tự động lấy URL từ Script Properties (nếu có) hoặc dùng WEBHOOK_URL
 * Nếu muốn set URL cụ thể, dùng setupTelegramWebhookWithUrl(url) thay vì hàm này
 */
function setupTelegramWebhook() {
  try {
    // Ưu tiên: Lấy URL từ sheet CaiDat
    var settings = getSettingsSafe_();
    var webhookUrl = null;
    var urlSource = '';
    
    // Ưu tiên 1: Đọc từ sheet CaiDat
    if (settings && settings['WEBHOOK_URL'] && String(settings['WEBHOOK_URL']).trim() !== '') {
      webhookUrl = String(settings['WEBHOOK_URL']).trim();
      urlSource = 'sheet CaiDat';
    } else {
      // Ưu tiên 2: Lấy từ Script Properties (nếu đã lưu trước đó)
      var props = PropertiesService.getScriptProperties();
      var savedUrl = props.getProperty('WEBHOOK_URL_CURRENT');
      if (savedUrl && String(savedUrl).trim() !== '') {
        webhookUrl = String(savedUrl).trim();
        urlSource = 'Script Properties';
      } else {
        // Ưu tiên 3: Dùng biến mặc định (fallback)
        webhookUrl = WEBHOOK_URL_DEFAULT;
        urlSource = 'biến mặc định (WEBHOOK_URL_DEFAULT)';
      }
    }
    
    Logger.log("🔄 Đang cài đặt webhook với URL từ " + urlSource + ": " + webhookUrl);
    
    if (urlSource === 'biến mặc định (WEBHOOK_URL_DEFAULT)') {
      Logger.log("⚠️ LƯU Ý: WEBHOOK_URL không có trong sheet CaiDat!");
      Logger.log("💡 Hãy thêm WEBHOOK_URL vào sheet CaiDat (hàng 13, cột C) để dễ quản lý!");
    }
    
    // Gọi hàm chính với URL đã lấy được
    var result = setupTelegramWebhookWithUrl(webhookUrl);
    
    // Nếu thành công và URL từ sheet, lưu vào Script Properties để backup
    if (result && webhookUrl && urlSource === 'sheet CaiDat') {
      try {
        var props = PropertiesService.getScriptProperties();
        props.setProperty('WEBHOOK_URL_CURRENT', webhookUrl);
        Logger.log("✅ Đã lưu webhook URL vào Script Properties (backup): " + webhookUrl);
      } catch (saveErr) {
        Logger.log("⚠️ Không thể lưu backup URL: " + saveErr.message);
      }
    }
    
    return result;
  } catch (e) {
    Logger.log("🚨 Lỗi trong setupTelegramWebhook: " + e.message);
    // Fallback: Dùng biến mặc định
    Logger.log("🔄 Fallback: Dùng WEBHOOK_URL_DEFAULT");
    return setupTelegramWebhookWithUrl(WEBHOOK_URL_DEFAULT);
  }
}


/**
 * Xử lý command /check_webhook
 */
function handleCheckWebhookCommand(botToken, chatId, replyToMessageId) {
  // Lưu ý: checkTelegramWebhook() tự gửi message, không cần replyToMessageId
  checkTelegramWebhook();
}

/**
 * Xóa webhook hiện tại của Telegram Bot
 * Chạy hàm này trước khi setup webhook mới để tránh conflict
 * 
 * Cách sử dụng:
 * 1. Chạy deleteWebhook() để xóa webhook cũ
 * 2. Đợi 1-2 giây
 * 3. Chạy setupTelegramWebhook() để cài đặt webhook mới
 */
function deleteWebhook() {
  try {
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    
    if (!botToken) {
      Logger.log("❌ Không có Bot Token trong settings");
      console.log("❌ Không có Bot Token trong settings");
      return false;
    }
    
    Logger.log("🔄 Đang xóa webhook cũ...");
    console.log("🔄 Đang xóa webhook cũ...");
    
    var deleteUrl = 'https://api.telegram.org/bot' + botToken + '/deleteWebhook?drop_pending_updates=true';
    var deleteOptions = {
      'method': 'get',
      'muteHttpExceptions': true
    };
    
    var deleteResponse = UrlFetchApp.fetch(deleteUrl, deleteOptions);
    var deleteResult = JSON.parse(deleteResponse.getContentText());
    
    if (deleteResult.ok) {
      Logger.log("✅ Đã xóa webhook cũ thành công");
      console.log("✅ Đã xóa webhook cũ thành công");
      Logger.log("✅ Đã xóa tất cả pending updates (drop_pending_updates=true)");
      console.log("✅ Đã xóa tất cả pending updates (drop_pending_updates=true)");
      return true;
    } else {
      var errorMsg = "⚠️ Lỗi xóa webhook: " + (deleteResult.description || "Unknown error");
      Logger.log(errorMsg);
      console.log(errorMsg);
      return false;
    }
  } catch (e) {
    var errorMsg = "🚨 Lỗi khi xóa webhook: " + e.message;
    Logger.log(errorMsg);
    console.log(errorMsg);
    return false;
  }
}

/**
 * Xử lý command /reset_webhook - Reset và cài đặt lại webhook
 */
function handleResetWebhookCommand(botToken, chatId, replyToMessageId) {
  try {
    // ⚠️ QUAN TRỌNG: Chỉ gửi 1 message duy nhất, không gửi nhiều messages
    guiThongBaoTelegram("⏳ Đang reset webhook và xóa pending updates...\n\n⏳ Vui lòng đợi, có thể mất vài giây...", botToken, chatId, replyToMessageId);
    
    // Xóa webhook cũ trước
    var settings = getSettingsSafe_();
    var resetBotToken = settings['TELEGRAM_BOT_TOKEN'];
    
    if (!resetBotToken) {
      guiThongBaoTelegram("❌ Không có Bot Token.", botToken, chatId, replyToMessageId);
      return;
    }
    
    // ⚠️ QUAN TRỌNG: Xóa webhook với drop_pending_updates=true để xóa TẤT CẢ pending messages
    // Điều này giúp tránh spam từ các messages cũ
    var deleteUrl = 'https://api.telegram.org/bot' + resetBotToken + '/deleteWebhook?drop_pending_updates=true';
    var deleteResponse = UrlFetchApp.fetch(deleteUrl, { muteHttpExceptions: true });
    var deleteResult = JSON.parse(deleteResponse.getContentText());
    
    Logger.log("Xóa webhook kết quả: " + JSON.stringify(deleteResult));
    console.log("Xóa webhook kết quả: " + JSON.stringify(deleteResult));
    
    if (deleteResult.ok) {
      Logger.log("✅ Đã xóa webhook và pending updates thành công");
      console.log("✅ Đã xóa webhook và pending updates thành công");
      
      // Đợi 2 giây để đảm bảo webhook đã được xóa hoàn toàn
      Utilities.sleep(2000);
      
      // Cài đặt lại webhook (KHÔNG gửi message tự động - truyền null cho chatId)
      // ⚠️ QUAN TRỌNG: setupTelegramWebhook sẽ tự lấy chatId từ settings, nhưng chúng ta không muốn nó gửi message
      // Vì vậy, chúng ta sẽ gọi setupTelegramWebhookWithUrl trực tiếp với chatId = null
      var webhookUrl = settings['WEBHOOK_URL'] || WEBHOOK_URL_DEFAULT;
      var setupResult = setupTelegramWebhookWithUrl(webhookUrl, null); // Không gửi message tự động
      
      // Đợi 3 giây để webhook được cài đặt
      Utilities.sleep(3000);
      
      // Gửi message tổng hợp cuối cùng (CHỈ 1 MESSAGE)
      var finalMsg = "✅ *ĐÃ RESET WEBHOOK THÀNH CÔNG!*\n\n";
      finalMsg += "💡 *Đã thực hiện:*\n";
      finalMsg += "• ✅ Xóa webhook cũ\n";
      finalMsg += "• ✅ Xóa tất cả pending updates\n";
      finalMsg += "• ✅ Cài đặt lại webhook mới\n\n";
      finalMsg += "📝 *Lưu ý:*\n";
      finalMsg += "• Nếu vẫn thấy lỗi 302, hãy mở URL webhook trong browser để authorize Web App\n";
      finalMsg += "• URL: `" + webhookUrl + "`\n";
      finalMsg += "• Sau khi authorize, webhook sẽ hoạt động bình thường\n\n";
      finalMsg += "💡 *Test webhook:*\n";
      finalMsg += "• Gửi lệnh `/test` để kiểm tra webhook có hoạt động không";
      
      guiThongBaoTelegram(finalMsg, botToken, chatId, replyToMessageId);
    } else {
      var errorMsg = "⚠️ *KHÔNG THỂ XÓA WEBHOOK*\n\n";
      errorMsg += "Lỗi: " + (deleteResult.description || "Unknown error") + "\n\n";
      errorMsg += "💡 *Thử lại:*\n";
      errorMsg += "• Kiểm tra Bot Token có đúng không\n";
      errorMsg += "• Thử chạy lại lệnh `/reset_webhook`";
      Logger.log(errorMsg);
      guiThongBaoTelegram(errorMsg, botToken, chatId, replyToMessageId);
    }
    
  } catch (e) {
    Logger.log("🚨 Lỗi reset webhook: " + e.message);
    console.log("🚨 Lỗi reset webhook: " + e.message);
    guiThongBaoTelegram("❌ *LỖI RESET WEBHOOK*\n\nLỗi: " + e.message + "\n\nVui lòng thử lại sau.", botToken, chatId, replyToMessageId);
  }
}

/**
 * Kiểm tra trạng thái webhook hiện tại
 */
function checkTelegramWebhook() {
  try {
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = settings['TELEGRAM_CHAT_ID'];
    
    if (!botToken) {
      Logger.log("⚠️ Không có Bot Token");
      return;
    }
    
    var telegramUrl = 'https://api.telegram.org/bot' + botToken + '/getWebhookInfo';
    var response = UrlFetchApp.fetch(telegramUrl, { muteHttpExceptions: true });
    var result = JSON.parse(response.getContentText());
    
    if (result.ok && result.result) {
      var webhookInfo = result.result;
      var statusMsg = "📊 *TRẠNG THÁI WEBHOOK*\n\n";
      var webhookUrl = webhookInfo.url || "Chưa có";
      statusMsg += "URL: `" + webhookUrl + "`\n";
      statusMsg += "Pending updates: " + (webhookInfo.pending_update_count || 0) + "\n";
      
      // Kiểm tra nếu URL dùng /dev
      if (webhookUrl.indexOf('/dev') >= 0) {
        statusMsg += "\n⚠️ *CẢNH BÁO:* URL đang dùng `/dev` endpoint!\n";
        statusMsg += "Điều này sẽ gây lỗi 401 Unauthorized.\n";
        statusMsg += "👉 Dùng lệnh `/reset_webhook` để sửa.\n";
      }
      
      if (webhookInfo.last_error_date) {
        var errorDate = new Date(webhookInfo.last_error_date * 1000);
        statusMsg += "\n❌ *LỖI GẦN NHẤT:*\n";
        statusMsg += "Thời gian: " + errorDate.toLocaleString('vi-VN') + "\n";
        statusMsg += "Chi tiết: " + (webhookInfo.last_error_message || "N/A") + "\n";
        
        // Nếu là lỗi 401, đề xuất giải pháp
        if (webhookInfo.last_error_message && webhookInfo.last_error_message.indexOf('401') >= 0) {
          statusMsg += "\n💡 *GIẢI PHÁP LỖI 401:*\n";
          statusMsg += "1. Kiểm tra Web App đã deploy với quyền 'Anyone'\n";
          statusMsg += "2. Đảm bảo URL dùng endpoint `/exec` (không phải `/dev`)\n";
          statusMsg += "3. Dùng lệnh `/reset_webhook` để reset\n";
        }
        
        // Nếu là lỗi 302, đề xuất authorize Web App
        if (webhookInfo.last_error_message && webhookInfo.last_error_message.indexOf('302') >= 0) {
          statusMsg += "\n💡 *GIẢI PHÁP LỖI 302:*\n";
          statusMsg += "1. Mở URL webhook trong browser:\n";
          statusMsg += "   `" + webhookUrl + "`\n";
          statusMsg += "2. Click 'Advanced' → 'Go to [Project] (unsafe)' → 'Allow'\n";
          statusMsg += "3. Phải thấy 'Telegram Bot Webhook đang hoạt động!'\n";
          statusMsg += "4. Sau đó webhook sẽ hoạt động bình thường\n";
        }
        
        // Nếu là lỗi 500, đề xuất kiểm tra logs
        if (webhookInfo.last_error_message && webhookInfo.last_error_message.indexOf('500') >= 0) {
          statusMsg += "\n💡 *GIẢI PHÁP LỖI 500:*\n";
          statusMsg += "1. Kiểm tra Execution logs trong Apps Script Editor\n";
          statusMsg += "2. Xem có lỗi gì trong hàm doPost không\n";
          statusMsg += "3. Kiểm tra xem doPost có được gọi không\n";
        }
      } else {
        statusMsg += "\n✅ Không có lỗi\n";
      }
      
      if (webhookInfo.max_connections) {
        statusMsg += "Max connections: " + webhookInfo.max_connections + "\n";
      }
      
      // Thêm thông tin về execution logs
      statusMsg += "\n💡 *KIỂM TRA DEBUG:*\n";
      statusMsg += "1. Mở Apps Script Editor\n";
      statusMsg += "2. Xem Execution logs (biểu tượng đồng hồ)\n";
      statusMsg += "3. Tìm các log bắt đầu bằng '📥 doPost'\n";
      statusMsg += "4. Nếu không thấy log '📥 doPost', có nghĩa là Telegram không gửi được request\n";
      
      Logger.log("Webhook info: " + JSON.stringify(webhookInfo));
      
      if (chatId) {
        guiThongBaoTelegram(statusMsg, botToken, chatId);
      }
    } else {
      Logger.log("❌ Không thể lấy thông tin webhook: " + JSON.stringify(result));
      if (chatId) {
        guiThongBaoTelegram("❌ Không thể lấy thông tin webhook.\n\nLỗi: " + (result.description || "Unknown"), botToken, chatId);
      }
    }
  } catch (e) {
    Logger.log("🚨 Lỗi kiểm tra webhook: " + e.message);
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = settings['TELEGRAM_CHAT_ID'];
    if (botToken && chatId) {
      guiThongBaoTelegram("🚨 *LỖI KIỂM TRA WEBHOOK*\n\n" + e.message, botToken, chatId);
    }
  }
}

/**
 * Hàm debug: Kiểm tra xem doPost có được gọi không
 * Chạy hàm này và xem Execution logs
 */
function debugWebhook() {
  Logger.log("🔍 DEBUG WEBHOOK:");
  Logger.log("1. Kiểm tra Execution logs trong 5 phút gần nhất");
  Logger.log("2. Tìm các log bắt đầu bằng '📥 doPost'");
  Logger.log("3. Nếu không thấy log nào, có nghĩa là Telegram không gửi được request đến webhook");
  Logger.log("4. Kiểm tra webhook URL trong Telegram bằng lệnh /check_webhook");
  
  var settings = getSettingsSafe_();
  var botToken = settings['TELEGRAM_BOT_TOKEN'];
  var chatId = settings['TELEGRAM_CHAT_ID'];
  
  if (botToken && chatId) {
    var debugMsg = "🔍 *DEBUG WEBHOOK*\n\n";
    debugMsg += "Để kiểm tra webhook:\n\n";
    debugMsg += "1. *Xem Execution logs:*\n";
    debugMsg += "   • Apps Script Editor → Executions (đồng hồ)\n";
    debugMsg += "   • Tìm log '📥 doPost được gọi'\n";
    debugMsg += "   • Nếu KHÔNG thấy → Telegram không gửi được request\n\n";
    debugMsg += "2. *Kiểm tra webhook URL:*\n";
    debugMsg += "   • Gửi lệnh /check_webhook\n";
    debugMsg += "   • Đảm bảo URL đúng và không có lỗi\n\n";
    debugMsg += "3. *Test webhook thủ công:*\n";
    debugMsg += "   • Mở URL webhook trong browser\n";
    debugMsg += "   • Phải thấy 'Telegram Bot Webhook đang hoạt động!'\n\n";
    debugMsg += "4. *Nếu vẫn không hoạt động:*\n";
    debugMsg += "   • Xóa webhook cũ: /reset_webhook\n";
    debugMsg += "   • Set lại webhook với URL mới\n";
    
    guiThongBaoTelegram(debugMsg, botToken, chatId);
  }
}

/**
 * ==================================================================
 * WORKER FUNCTION: XỬ LÝ ASYNC CÁC TELEGRAM COMMANDS
 * ==================================================================
 * Hàm này được gọi bởi trigger để xử lý các payload đã được lưu trong queue
 * Đảm bảo doPost trả về 200 OK ngay lập tức, không block
 * ==================================================================
 */

/**
 * Worker function để xử lý các Telegram commands async
 * Được gọi bởi trigger sau khi doPost đã trả về 200 OK
 */
function _telegramWorker() {
  try {
    Logger.log("🔄 [_telegramWorker] Bắt đầu xử lý queue...");
    
    var props = PropertiesService.getScriptProperties();
    var allProps = props.getProperties();
    var pendingPayloads = [];
    
    // Tìm tất cả các payload trong queue (keys bắt đầu với PENDING_PAYLOAD_)
    for (var key in allProps) {
      if (key.startsWith('PENDING_PAYLOAD_')) {
        var updId = key.replace('PENDING_PAYLOAD_', '');
        pendingPayloads.push({
          key: key,
          updId: updId,
          payload: allProps[key]
        });
      }
    }
    
    Logger.log("📋 [_telegramWorker] Tìm thấy " + pendingPayloads.length + " payload trong queue");
    
    // Xử lý từng payload
    for (var i = 0; i < pendingPayloads.length; i++) {
      var item = pendingPayloads[i];
      var payloadKey = item.key;
      var updId = item.updId;
      var payloadStr = item.payload;
      
      try {
        Logger.log("🔄 [_telegramWorker] Xử lý Update ID: " + updId);
        
        // Tạo mock event object từ payload
        var mockEvent = {
          postData: {
            contents: payloadStr
          }
        };
        
        // Xử lý update
        var processResult = processWebhookUpdate_(mockEvent);
        
        if (processResult === true) {
          Logger.log("✅ [_telegramWorker] Xử lý Update ID " + updId + " thành công");
        } else {
          Logger.log("⚠️ [_telegramWorker] Xử lý Update ID " + updId + " thất bại. processResult: " + processResult);
        }
        
        // Xóa payload sau khi xử lý xong (dù thành công hay thất bại)
        try {
          props.deleteProperty(payloadKey);
          Logger.log("✅ [_telegramWorker] Đã xóa payload: " + payloadKey);
        } catch (deleteErr) {
          Logger.log("⚠️ [_telegramWorker] Lỗi khi xóa payload: " + deleteErr.message);
        }
      } catch (processErr) {
        Logger.log("🚨 [_telegramWorker] Lỗi xử lý payload " + updId + ": " + processErr.message);
        // Xóa payload ngay cả khi có lỗi để tránh queue bị đầy
        try {
          props.deleteProperty(payloadKey);
        } catch (deleteErr) {
          Logger.log("⚠️ [_telegramWorker] Lỗi khi xóa payload (sau lỗi): " + deleteErr.message);
        }
      }
    }
    
    // Xóa trigger của chính nó (chỉ xóa 1 trigger để tránh xóa nhầm)
    try {
      var triggers = ScriptApp.getProjectTriggers();
      for (var j = 0; j < triggers.length; j++) {
        if (triggers[j].getHandlerFunction() === '_telegramWorker') {
          ScriptApp.deleteTrigger(triggers[j]);
          Logger.log("✅ [_telegramWorker] Đã xóa trigger");
          break; // Chỉ xóa 1 trigger
        }
      }
    } catch (triggerErr) {
      Logger.log("⚠️ [_telegramWorker] Lỗi khi xóa trigger: " + triggerErr.message);
    }
    
    Logger.log("✅ [_telegramWorker] Hoàn thành xử lý queue");
  } catch (err) {
    Logger.log("🚨 [_telegramWorker] Lỗi ngoài cùng: " + err.message + " | Stack: " + (err.stack || "N/A"));
  }
}

/**
 * ==================================================================
 * TASK RUNNER FUNCTIONS: XỬ LÝ ASYNC CÁC COMMANDS NẶNG
 * ==================================================================
 * Mỗi command nặng có một task runner riêng để xử lý async
 * Đảm bảo doPost trả về 200 OK ngay lập tức, không block
 * ==================================================================
 */

/**
 * Task runner cho /report
 */
function _runTaskReport() {
  var props = PropertiesService.getScriptProperties();
  var messageJson = props.getProperty('PENDING_TASK_REPORT');
  if (!messageJson) return;
  
  try {
    props.deleteProperty('PENDING_TASK_REPORT');
    var message = JSON.parse(messageJson);
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = message.chat.id;
    var replyTo = message.message_id;
    
    if (!botToken || !chatId) {
      Logger.log("🚨 _runTaskReport: Không thể lấy botToken hoặc chatId");
      return;
    }
    
    Logger.log("🚀 Bắt đầu thực thi /report (async)");
    handleReportCommand(botToken, chatId, replyTo, false);
  } catch (e) {
    Logger.log("🚨 Lỗi nghiêm trọng khi chạy _runTaskReport (async): " + e.message);
    try {
      var settings = getSettingsSafe_();
      var botToken = settings['TELEGRAM_BOT_TOKEN'];
      var chatId = settings['TELEGRAM_CHAT_ID'];
      if (botToken && chatId) {
        guiThongBaoTelegram("🚨 Lỗi khi chạy tác vụ /report (async): " + e.message, botToken, chatId);
      }
    } catch (e2) {}
  }
  
  // Xóa trigger của chính nó
  try {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === '_runTaskReport') {
        ScriptApp.deleteTrigger(triggers[i]);
        Logger.log("✅ [_runTaskReport] Đã xóa trigger");
        break;
      }
    }
  } catch (triggerErr) {
    Logger.log("⚠️ [_runTaskReport] Lỗi khi xóa trigger: " + triggerErr.message);
  }
}

/**
 * Task runner cho /statusads
 */
function _runTaskStatusAds() {
  var props = PropertiesService.getScriptProperties();
  var messageJson = props.getProperty('PENDING_TASK_STATUSADS');
  if (!messageJson) return;
  
  try {
    props.deleteProperty('PENDING_TASK_STATUSADS');
    var message = JSON.parse(messageJson);
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = message.chat.id;
    var replyTo = message.message_id;
    
    if (!botToken || !chatId) {
      Logger.log("🚨 _runTaskStatusAds: Không thể lấy botToken hoặc chatId");
      return;
    }
    
    Logger.log("🚀 Bắt đầu thực thi /statusads (async)");
    handleStatusAdsCommand(botToken, chatId, replyTo, false);
  } catch (e) {
    Logger.log("🚨 Lỗi nghiêm trọng khi chạy _runTaskStatusAds (async): " + e.message);
    try {
      var settings = getSettingsSafe_();
      var botToken = settings['TELEGRAM_BOT_TOKEN'];
      var chatId = settings['TELEGRAM_CHAT_ID'];
      if (botToken && chatId) {
        guiThongBaoTelegram("🚨 Lỗi khi chạy tác vụ /statusads (async): " + e.message, botToken, chatId);
      }
    } catch (e2) {}
  }
  
  // Xóa trigger của chính nó
  try {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === '_runTaskStatusAds') {
        ScriptApp.deleteTrigger(triggers[i]);
        Logger.log("✅ [_runTaskStatusAds] Đã xóa trigger");
        break;
      }
    }
  } catch (triggerErr) {
    Logger.log("⚠️ [_runTaskStatusAds] Lỗi khi xóa trigger: " + triggerErr.message);
  }
}

/**
 * Task runner cho /status
 */
function _runTaskStatus() {
  var props = PropertiesService.getScriptProperties();
  var messageJson = props.getProperty('PENDING_TASK_STATUS');
  if (!messageJson) return;
  
  try {
    props.deleteProperty('PENDING_TASK_STATUS');
    var message = JSON.parse(messageJson);
    var settings = getSettingsSafe_();
    var botToken = settings['TELEGRAM_BOT_TOKEN'];
    var chatId = message.chat.id;
    var replyTo = message.message_id;
    
    if (!botToken || !chatId) {
      Logger.log("🚨 _runTaskStatus: Không thể lấy botToken hoặc chatId");
      return;
    }
    
    Logger.log("🚀 Bắt đầu thực thi /status (async)");
    handleStatusCommand(botToken, chatId, replyTo, false);
  } catch (e) {
    Logger.log("🚨 Lỗi nghiêm trọng khi chạy _runTaskStatus (async): " + e.message);
    try {
      var settings = getSettingsSafe_();
      var botToken = settings['TELEGRAM_BOT_TOKEN'];
      var chatId = settings['TELEGRAM_CHAT_ID'];
      if (botToken && chatId) {
        guiThongBaoTelegram("🚨 Lỗi khi chạy tác vụ /status (async): " + e.message, botToken, chatId);
      }
    } catch (e2) {}
  }
  
  // Xóa trigger của chính nó
  try {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === '_runTaskStatus') {
        ScriptApp.deleteTrigger(triggers[i]);
        Logger.log("✅ [_runTaskStatus] Đã xóa trigger");
        break;
      }
    }
  } catch (triggerErr) {
    Logger.log("⚠️ [_runTaskStatus] Lỗi khi xóa trigger: " + triggerErr.message);
  }
}

/**
 * ==================================================================
 * QUEUE SYSTEM: XỬ LÝ ASYNC CÁC TELEGRAM UPDATES
 * ==================================================================
 * doPost chỉ ACK và đẩy vào queue, worker sẽ xử lý sau
 * Đảm bảo không timeout và có thể xử lý nhiều lệnh cùng lúc
 * ==================================================================
 */

/**
 * Đẩy update vào hàng đợi (queue)
 * @param {string} rawJson - Raw JSON string của Telegram update
 */
function enqueueTelegramUpdate_(rawJson) {
  var props = PropertiesService.getScriptProperties();
  var lock = LockService.getScriptLock();
  
  // Thử lock trong 500ms, nếu không được thì bỏ qua (nhường lần sau)
  if (!lock.tryLock(500)) {
    Logger.log("⚠️ [enqueueTelegramUpdate_] Không thể lock, bỏ qua lần này");
    return;
  }
  
  try {
    var q = props.getProperty('TG_QUEUE') || '[]';
    var arr = JSON.parse(q);
    
    // Chặn tràn queue: giữ tối đa 100 phần tử (xóa phần tử cũ nhất)
    if (arr.length > 100) {
      arr = arr.slice(-100);
      Logger.log("⚠️ [enqueueTelegramUpdate_] Queue đầy, xóa phần tử cũ");
    }
    
    arr.push(rawJson);
    props.setProperty('TG_QUEUE', JSON.stringify(arr));
    
    Logger.log("✅ [enqueueTelegramUpdate_] Đã thêm update vào queue (tổng: " + arr.length + " items)");
  } catch (e) {
    Logger.log("🚨 [enqueueTelegramUpdate_] Lỗi: " + e.message);
  } finally {
    lock.releaseLock();
  }
}

/**
 * Tạo trigger chạy worker ngay (sau 0.5s) nếu chưa có worker đang chạy
 */
function ensureQueueWorker_() {
  var cache = CacheService.getScriptCache();
  
  // Kiểm tra xem đã có worker đang chạy chưa (trong 30 giây)
  if (cache.get('TG_WORKER_RUNNING')) {
    return; // Đã có worker, không tạo thêm
  }
  
  // Đánh dấu worker đang chạy (30 giây: khoảng bảo vệ bật trùng)
  cache.put('TG_WORKER_RUNNING', '1', 30);
  
  // Tạo trigger chạy sau 0.5 giây (nhanh hơn)
  try {
    ScriptApp.newTrigger('_processTelegramQueue_').timeBased().after(500).create();
    Logger.log("✅ [ensureQueueWorker_] Đã tạo trigger worker");
  } catch (e) {
    Logger.log("🚨 [ensureQueueWorker_] Lỗi tạo trigger: " + e.message);
  }
}

/**
 * Xử lý lệnh nhẹ trực tiếp (không qua queue)
 * Được gọi bởi time-based trigger sau 0.5 giây
 */
function _processDirectCommand_() {
  try {
    // Tìm và xóa trigger của chính nó
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === '_processDirectCommand_') {
        ScriptApp.deleteTrigger(triggers[i]);
        break;
      }
    }
    
    // Tìm update_id gần nhất trong PropertiesService
    var props = PropertiesService.getScriptProperties();
    var allProps = props.getProperties();
    var directKeys = [];
    for (var key in allProps) {
      if (key.startsWith('TG_DIRECT_')) {
        directKeys.push(key);
      }
    }
    
    if (directKeys.length === 0) {
      Logger.log("ℹ️ [_processDirectCommand_] Không có lệnh nhẹ để xử lý");
      return;
    }
    
    // Xử lý từng update (tối đa 10 để tránh quota)
    var processed = 0;
    for (var j = 0; j < Math.min(directKeys.length, 10); j++) {
      try {
        var key = directKeys[j];
        var raw = props.getProperty(key);
        if (!raw) {
          props.deleteProperty(key);
          continue;
        }
        
        var update = JSON.parse(raw);
        var message = update.message || update.edited_message || update.channel_post || update.edited_channel_post;
        if (!message) {
          props.deleteProperty(key);
          continue;
        }
        
        // Xử lý trực tiếp (không qua queue)
        Logger.log("✅ [_processDirectCommand_] Xử lý lệnh nhẹ: Message ID " + (message.message_id || 'N/A'));
        handleTelegramMessageSafe_(message);
        
        // Xóa key sau khi xử lý
        props.deleteProperty(key);
        processed++;
      } catch (itemErr) {
        Logger.log("🚨 [_processDirectCommand_] Lỗi xử lý item: " + itemErr.message);
        // Xóa key lỗi
        try {
          props.deleteProperty(directKeys[j]);
        } catch (delErr) {}
      }
    }
    
    Logger.log("✅ [_processDirectCommand_] Đã xử lý " + processed + " lệnh nhẹ");
    
    // Nếu còn lệnh, tạo trigger tiếp theo
    if (directKeys.length > processed) {
      ScriptApp.newTrigger('_processDirectCommand_').timeBased().after(500).create();
    }
    
  } catch (err) {
    Logger.log("🚨 [_processDirectCommand_] Lỗi ngoài cùng: " + (err.stack || err.message || err));
  }
}

/**
 * Worker: Rút queue & xử lý lần lượt
 * Được gọi bởi time-based trigger
 */
function _processTelegramQueue_() {
  var lock = LockService.getScriptLock();
  
  // Thử lock trong 2 giây, nếu không được thì có worker khác đang chạy
  if (!lock.tryLock(2000)) {
    Logger.log("⚠️ [_processTelegramQueue_] Có worker khác đang chạy, bỏ qua");
    return;
  }
  
  try {
    var props = PropertiesService.getScriptProperties();
    var q = props.getProperty('TG_QUEUE') || '[]';
    var arr = JSON.parse(q);
    
    if (arr.length === 0) {
      Logger.log("ℹ️ [_processTelegramQueue_] Queue rỗng, không có gì để xử lý");
      return;
    }
    
    // Rút từng item và xử lý, giới hạn 30 mục/lần để tránh quota
    var batch = arr.splice(0, 30);
    props.setProperty('TG_QUEUE', JSON.stringify(arr));
    
    Logger.log("🔄 [_processTelegramQueue_] Bắt đầu xử lý " + batch.length + " items (còn lại: " + arr.length + ")");
    
    for (var i = 0; i < batch.length; i++) {
      try {
        var update = JSON.parse(batch[i]);
        
        // Xử lý cả message và channel_post (nếu cần)
        var message = update.message || update.edited_message || update.channel_post || update.edited_channel_post;
        if (!message) {
          Logger.log("⚠️ [_processTelegramQueue_] Item " + i + ": Không có message");
          continue;
        }
        
        // DEDUPE PHỤ: message_id + chat_id để an toàn
        var mid = message.message_id ? String(message.message_id) : '';
        var cid = (message.chat && typeof message.chat.id !== 'undefined') ? String(message.chat.id) : '';
        if (mid && cid) {
          var cache = CacheService.getScriptCache();
          var k = "MSG_" + cid + "_" + mid;
          if (cache.get(k)) {
            Logger.log("⚠️ [_processTelegramQueue_] Item " + i + ": Message đã được xử lý (MSG_" + cid + "_" + mid + ")");
            continue; // Đã xử lý rồi, bỏ qua
          }
          cache.put(k, "1", 3600); // 1 giờ
        }
        
        // Gọi handler gốc (đã có rate-limit & phân quyền)
        Logger.log("✅ [_processTelegramQueue_] Xử lý item " + i + ": Message ID " + mid + ", Chat ID " + cid);
        handleTelegramMessageSafe_(message);
        
      } catch (itemErr) {
        try {
          Logger.log("🚨 [_processTelegramQueue_] Lỗi xử lý item " + i + ": " + (itemErr.stack || itemErr.message));
        } catch (logErr) {}
      }
    }
    
    Logger.log("✅ [_processTelegramQueue_] Đã xử lý xong " + batch.length + " items");
    
    // Nếu còn việc, tự bật thêm 1 worker nữa (để "chạy đến hết")
    if (arr.length > 0) {
      Logger.log("🔄 [_processTelegramQueue_] Còn " + arr.length + " items, tạo worker tiếp theo");
      try {
        ScriptApp.newTrigger('_processTelegramQueue_').timeBased().after(500).create();
      } catch (triggerErr) {
        Logger.log("⚠️ [_processTelegramQueue_] Lỗi tạo trigger tiếp theo: " + triggerErr.message);
      }
    } else {
      Logger.log("✅ [_processTelegramQueue_] Queue đã rỗng, hoàn thành");
    }
    
  } catch (err) {
    Logger.log("🚨 [_processTelegramQueue_] Lỗi ngoài cùng: " + (err.stack || err.message || err));
  } finally {
    lock.releaseLock();
    
    // Xóa trigger của chính nó
    try {
      var triggers = ScriptApp.getProjectTriggers();
      for (var i = 0; i < triggers.length; i++) {
        if (triggers[i].getHandlerFunction() === '_processTelegramQueue_') {
          ScriptApp.deleteTrigger(triggers[i]);
          Logger.log("✅ [_processTelegramQueue_] Đã xóa trigger của chính nó");
          break;
        }
      }
    } catch (triggerErr) {
      Logger.log("⚠️ [_processTelegramQueue_] Lỗi xóa trigger: " + triggerErr.message);
    }
    
    // Xóa flag "worker đang chạy" sau khi xong
    try {
      var cache = CacheService.getScriptCache();
      cache.remove('TG_WORKER_RUNNING');
    } catch (cacheErr) {
      Logger.log("⚠️ [_processTelegramQueue_] Lỗi xóa flag: " + cacheErr.message);
    }
  }
}
