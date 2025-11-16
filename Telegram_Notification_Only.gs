/**
 * ==================================================================
 * Telegram.gs - QUẢN LÝ THÔNG BÁO TELEGRAM (CHỈ THÔNG BÁO)
 * ==================================================================
 * Hàm gửi thông báo đến Telegram Bot
 * Hỗ trợ Markdown formatting và error handling
 * 
 * ⚠️ ĐÃ LOẠI BỎ: Tất cả phần webhook, nghe, gọi, xử lý commands
 * ✅ CHỈ GIỮ LẠI: Phần gửi thông báo
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
 * Gửi một tin nhắn đến kênh/chat Telegram
 * @param {string} message - Tin nhắn cần gửi (hỗ trợ Markdown)
 * @param {string} botToken - Mã Token của Bot Telegram (từ BotFather)
 * @param {string} chatId - ID của nhóm/kênh/người nhận
 * @param {number} replyToMessageId - (Optional) ID của message cần reply
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
 * @returns {boolean} - true nếu gửi thành công
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
 * @returns {boolean} - true nếu gửi thành công
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
 * @returns {boolean} - true nếu gửi thành công
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
  if (!accountId || !prefix) return true; // Mặc định enabled nếu thiếu thông tin
  
  try {
    var props = PropertiesService.getScriptProperties();
    var normalizedAccountId = String(accountId).replace(/^act_/, ''); // Bỏ "act_" prefix nếu có
    var key = "AUTOMATION_ENABLED_" + normalizedAccountId + "|" + String(prefix).toUpperCase();
    var value = props.getProperty(key);
    return value === "true"; // Chỉ enabled nếu value = "true"
  } catch (e) {
    Logger.log("⚠️ Lỗi kiểm tra automation enabled: " + e.message);
    return true; // Mặc định enabled nếu có lỗi
  }
}

/**
 * Bật automation cho account|prefix
 * @param {string} accountId - Account ID
 * @param {string} prefix - Prefix
 * @returns {boolean} - true nếu thành công
 */
function enableAutomation(accountId, prefix) {
  if (!accountId || !prefix) return false;
  
  try {
    var props = PropertiesService.getScriptProperties();
    var normalizedAccountId = String(accountId).replace(/^act_/, '');
    var key = "AUTOMATION_ENABLED_" + normalizedAccountId + "|" + String(prefix).toUpperCase();
    props.setProperty(key, "true");
    Logger.log("✅ Đã bật automation cho " + accountId + "|" + prefix);
    return true;
  } catch (e) {
    Logger.log("🚨 Lỗi khi bật automation: " + e.message);
    return false;
  }
}

/**
 * Tắt automation cho account|prefix
 * @param {string} accountId - Account ID
 * @param {string} prefix - Prefix
 * @returns {boolean} - true nếu thành công
 */
function disableAutomation(accountId, prefix) {
  if (!accountId || !prefix) return false;
  
  try {
    var props = PropertiesService.getScriptProperties();
    var normalizedAccountId = String(accountId).replace(/^act_/, '');
    var key = "AUTOMATION_ENABLED_" + normalizedAccountId + "|" + String(prefix).toUpperCase();
    props.setProperty(key, "false");
    Logger.log("✅ Đã tắt automation cho " + accountId + "|" + prefix);
    return true;
  } catch (e) {
    Logger.log("🚨 Lỗi khi tắt automation: " + e.message);
    return false;
  }
}

/**
 * Lấy tất cả trạng thái automation
 * @returns {Object} - Object chứa tất cả trạng thái enable/disable
 */
function getAllAutomationStatus() {
  try {
    var props = PropertiesService.getScriptProperties();
    var allProps = props.getProperties();
    var status = {};
    
    // Filter các key bắt đầu bằng "AUTOMATION_ENABLED_"
    for (var key in allProps) {
      if (key.indexOf("AUTOMATION_ENABLED_") === 0) {
        var value = allProps[key];
        var accountPrefix = key.replace("AUTOMATION_ENABLED_", "");
        status[accountPrefix] = value === "true";
      }
    }
    
    return status;
  } catch (e) {
    Logger.log("🚨 Lỗi khi lấy trạng thái automation: " + e.message);
    return {};
  }
}

