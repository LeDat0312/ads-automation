/******************************************************
 * FacebookAPI.gs  —  BẢN HOÀN CHỈNH (v4.1)
 * - Đã SỬA LỖI: Lỗi cú pháp (SyntaxError) do gõ nhầm 'g'
 * - Giữ nguyên logic Batch API, CTR/100, Cột tùy chỉnh
 ******************************************************/

// ==== Cấu hình chung ====
var SHEET_NAME_DATA = "Data_FB"; // Trang tính đổ dữ liệu
var INCLUDE_WIDE_AD_STATUSES = true; // <-- Sửa lỗi 'is not defined'

// ==== Utilities dùng chung ====
// TỐI ƯU: Tối ưu hàm unique
function unique(arr){ 
  if (!arr || arr.length === 0) return [];
  var seen = {};
  var out = [];
  for (var i = 0; i < arr.length; i++) {
    var val = arr[i];
    if (val && !seen[val]) {
      seen[val] = true;
      out.push(val);
    }
  }
  return out;
}

function chunk(arr, size){
  var out = [];
  for (var i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

// Lấy map { adset_id: effective_status } qua batch (?ids=)
function fetchAdsetStatuses(adsetIds, accessToken){
  var map = {};
  try {
    if (!adsetIds || adsetIds.length === 0) return map;
    var batches = chunk(unique(adsetIds), 50);
    // TỐI ƯU: Dùng for thay vì forEach
    for (var bIdx = 0; bIdx < batches.length; bIdx++) {
      var batch = batches[bIdx];
      var ids = batch.join(',');
      var url = 'https://graph.facebook.com/v24.0' +
                '/?ids=' + encodeURIComponent(ids) +
                '&fields=effective_status' +
                '&access_token=' + encodeURIComponent(accessToken);
      var resp = UrlFetchApp.fetch(url, { 'muteHttpExceptions': true });
      var json = JSON.parse(resp.getContentText());
      if (json && typeof json === 'object') {
        // TỐI ƯU: Dùng for thay vì Object.keys().forEach
        var jsonKeys = Object.keys(json);
        for (var kIdx = 0; kIdx < jsonKeys.length; kIdx++) {
          var id = jsonKeys[kIdx];
          var node = json[id];
          if (node && node.effective_status) map[id] = node.effective_status;
      }
      }
      }
  } catch (e) {
    try {
      var settings = layCaiDatHeThong && layCaiDatHeThong();
      var bot = settings && settings["TELEGRAM_BOT_TOKEN"];
      var chat = settings && settings["TELEGRAM_CHAT_ID"];
      if (bot && chat) {
        guiThongBaoTelegram(
          "🔴 *LỖI lấy trạng thái AdSet (batch ids)*\n" +
          "*Chi tiết:* " + e.message,
          bot, chat
        );
      }
    } catch (_e) {}
  }
  return map;
}

/**
 * ==================================================================
 * HÀM API TẮT QUẢNG CÁO (NÂNG CẤP)
 * === Tắt NHIỀU Adset bằng 1 LỆNH BATCH (Đa luồng) ===
 * ==================================================================
 */
function goiFacebookAPIDeTatNhieuAdset(adsetIdList, accessToken, delayMs) {
  if (!adsetIdList || adsetIdList.length === 0) {
    return { success: 0, errors: 0, errorDetails: [] };
  }
  var batches = chunk(adsetIdList, 50);
  var successCount = 0;
  var errorCount = 0;
  var errorDetails = [];

  // TỐI ƯU: Dùng for thay vì forEach
  for (var batchIdx = 0; batchIdx < batches.length; batchIdx++) {
    var batchIds = batches[batchIdx];
    var index = batchIdx;
    
    var batchPayload = [];
    // TỐI ƯU: Dùng for thay vì forEach
    for (var idIdx = 0; idIdx < batchIds.length; idIdx++) {
      var id = batchIds[idIdx];
      batchPayload.push({
        "method": "POST",
        "relative_url": "v24.0/" + id,
        "body": "status=PAUSED" // Lệnh tắt
      });
    }

    var formData = {
      'access_token': accessToken,
      'batch': JSON.stringify(batchPayload)
    };
    var options = {
      'method' : 'post',
      'payload' : formData,
      'muteHttpExceptions': true
    };

    try {
      if (index > 0 && delayMs > 0) {
         Logger.log("Đang chờ " + (delayMs / 1000) + " giây trước khi gửi batch tiếp theo...");
         Utilities.sleep(delayMs);
      }
      
      var response = UrlFetchApp.fetch("https://graph.facebook.com/v24.0/", options);
      var jsonResponse = JSON.parse(response.getContentText());

      if (Array.isArray(jsonResponse)) {
        // TỐI ƯU: Dùng for thay vì forEach
        for (var i = 0; i < jsonResponse.length; i++) {
          var item = jsonResponse[i];
          var adsetId = batchIds[i];
          if (item.code === 200) {
            successCount++;
            // Lưu lịch sử toggle thành công (để cooldown thông minh)
            try {
              var props = PropertiesService.getScriptProperties();
              var now = Date.now();
              var toggleHistoryKey = "ADSET_TOGGLE_HISTORY_" + adsetId;
              var toggleCountKey = "ADSET_TOGGLE_COUNT_" + adsetId;
              
              // Lấy lịch sử hiện tại
              var currentHistory = props.getProperty(toggleHistoryKey) || '';
              var historyTimestamps = [];
              if (currentHistory) {
                // TỐI ƯU: Dùng for thay vì map + filter
                var parts = currentHistory.split(',');
                for (var pIdx = 0; pIdx < parts.length; pIdx++) {
                  var ts = parseInt(parts[pIdx].trim(), 10);
                  if (!isNaN(ts) && ts > 0) {
                    historyTimestamps.push(ts);
                  }
                }
              }
              
              // Thêm timestamp mới
              historyTimestamps.push(now);
              
              // Chỉ giữ lại các timestamp trong 24 giờ gần nhất (để tránh lưu quá nhiều)
              var dayMs = 24 * 60 * 60 * 1000;
              // TỐI ƯU: Dùng for thay vì filter
              var filteredTimestamps = [];
              for (var tsIdx = 0; tsIdx < historyTimestamps.length; tsIdx++) {
                if ((now - historyTimestamps[tsIdx]) <= dayMs) {
                  filteredTimestamps.push(historyTimestamps[tsIdx]);
                }
              }
              historyTimestamps = filteredTimestamps;
              
              // Sắp xếp và lưu lại (giữ tối đa 20 lần gần nhất)
              historyTimestamps.sort(function(a, b) { return b - a; }); // Sắp xếp giảm dần
              historyTimestamps = historyTimestamps.slice(0, 20); // Chỉ giữ 20 lần gần nhất
              
              // Lưu lại
              props.setProperty(toggleHistoryKey, historyTimestamps.join(','));
              props.setProperty(toggleCountKey, String(historyTimestamps.length));
            } catch (eSave) {
              // Ignore
            }
          } else {
            errorCount++;
            var errorMsg = "Unknown error";
            try {
            var errorBody = JSON.parse(item.body);
              errorMsg = errorBody.error ? errorBody.error.message : item.body;
            } catch (e) {
              errorMsg = item.body || "Failed to parse error";
            }
            errorDetails.push({ adsetId: adsetId, error: errorMsg });
          }
        }
      } else {
        errorCount += batchIds.length;
        // TỐI ƯU: Dùng for thay vì forEach
        for (var errIdx = 0; errIdx < batchIds.length; errIdx++) {
          errorDetails.push({ adsetId: batchIds[errIdx], error: "Batch API error: Invalid response format" });
        }
      }
    } catch (e) {
      errorCount += batchIds.length; 
      // TỐI ƯU: Dùng for thay vì forEach
      for (var errIdx2 = 0; errIdx2 < batchIds.length; errIdx2++) {
        errorDetails.push({ adsetId: batchIds[errIdx2], error: "Exception: " + e.message });
    }
    }
    }
  
  Logger.log("Thực thi Batch TẮT hoàn tất. Thành công: " + successCount + ", Thất bại: " + errorCount);
  return { success: successCount, errors: errorCount, errorDetails: errorDetails };
}

/**
 * ==================================================================
 * HÀM API BẬT LẠI QUẢNG CÁO (NÂNG CẤP)
 * === Bật lại NHIỀU Adset bằng 1 LỆNH BATCH (Đa luồng) ===
 * ==================================================================
 */
function goiFacebookAPIDeBatNhieuAdset(adsetIdList, accessToken, delayMs) {
  if (!adsetIdList || adsetIdList.length === 0) {
    return { success: 0, errors: 0, errorDetails: [] };
  }
  var batches = chunk(adsetIdList, 50);
  var successCount = 0;
  var errorCount = 0;
  var errorDetails = [];

  // TỐI ƯU: Dùng for thay vì forEach
  for (var batchIdx = 0; batchIdx < batches.length; batchIdx++) {
    var batchIds = batches[batchIdx];
    var index = batchIdx;
    
    var batchPayload = [];
    // TỐI ƯU: Dùng for thay vì forEach
    for (var idIdx = 0; idIdx < batchIds.length; idIdx++) {
      var id = batchIds[idIdx];
      batchPayload.push({
        "method": "POST",
        "relative_url": "v24.0/" + id,
        "body": "status=ACTIVE" // Lệnh bật lại
      });
    }

    var formData = {
      'access_token': accessToken,
      'batch': JSON.stringify(batchPayload)
    };
    var options = {
      'method' : 'post',
      'payload' : formData,
      'muteHttpExceptions': true
    };

    try {
      if (index > 0 && delayMs > 0) {
         Logger.log("Đang chờ " + (delayMs / 1000) + " giây trước khi gửi batch tiếp theo...");
         Utilities.sleep(delayMs);
      }
      
      var response = UrlFetchApp.fetch("https://graph.facebook.com/v24.0/", options);
      var jsonResponse = JSON.parse(response.getContentText());

      if (Array.isArray(jsonResponse)) {
        // TỐI ƯU: Dùng for thay vì forEach
        for (var i = 0; i < jsonResponse.length; i++) {
          var item = jsonResponse[i];
          var adsetId = batchIds[i];
          if (item.code === 200) {
            successCount++;
            // Lưu lịch sử toggle thành công (để cooldown thông minh)
            try {
              var props = PropertiesService.getScriptProperties();
              var now = Date.now();
              var toggleHistoryKey = "ADSET_TOGGLE_HISTORY_" + adsetId;
              var toggleCountKey = "ADSET_TOGGLE_COUNT_" + adsetId;
              
              // Lấy lịch sử hiện tại
              var currentHistory = props.getProperty(toggleHistoryKey) || '';
              var historyTimestamps = [];
              if (currentHistory) {
                // TỐI ƯU: Dùng for thay vì map + filter
                var parts = currentHistory.split(',');
                for (var pIdx = 0; pIdx < parts.length; pIdx++) {
                  var ts = parseInt(parts[pIdx].trim(), 10);
                  if (!isNaN(ts) && ts > 0) {
                    historyTimestamps.push(ts);
                  }
                }
              }
              
              // Thêm timestamp mới
              historyTimestamps.push(now);
              
              // Chỉ giữ lại các timestamp trong 24 giờ gần nhất (để tránh lưu quá nhiều)
              var dayMs = 24 * 60 * 60 * 1000;
              // TỐI ƯU: Dùng for thay vì filter
              var filteredTimestamps = [];
              for (var tsIdx = 0; tsIdx < historyTimestamps.length; tsIdx++) {
                if ((now - historyTimestamps[tsIdx]) <= dayMs) {
                  filteredTimestamps.push(historyTimestamps[tsIdx]);
                }
              }
              historyTimestamps = filteredTimestamps;
              
              // Sắp xếp và lưu lại (giữ tối đa 20 lần gần nhất)
              historyTimestamps.sort(function(a, b) { return b - a; }); // Sắp xếp giảm dần
              historyTimestamps = historyTimestamps.slice(0, 20); // Chỉ giữ 20 lần gần nhất
              
              // Lưu lại
              props.setProperty(toggleHistoryKey, historyTimestamps.join(','));
              props.setProperty(toggleCountKey, String(historyTimestamps.length));
            } catch (eSave) {
              // Ignore
            }
          } else {
            errorCount++;
            var errorMsg = "Unknown error";
            try {
              var errorBody = JSON.parse(item.body);
              errorMsg = errorBody.error ? errorBody.error.message : item.body;
            } catch (e) {
              errorMsg = item.body || "Failed to parse error";
            }
            errorDetails.push({ adsetId: adsetId, error: errorMsg });
          }
        }
      } else {
        errorCount += batchIds.length;
        // TỐI ƯU: Dùng for thay vì forEach
        for (var errIdx = 0; errIdx < batchIds.length; errIdx++) {
          errorDetails.push({ adsetId: batchIds[errIdx], error: "Batch API error: Invalid response format" });
        }
      }
    } catch (e) {
      errorCount += batchIds.length;
      // TỐI ƯU: Dùng for thay vì forEach
      for (var errIdx2 = 0; errIdx2 < batchIds.length; errIdx2++) {
        errorDetails.push({ adsetId: batchIds[errIdx2], error: "Exception: " + e.message });
      }
    }
  }
  
  Logger.log("Thực thi Batch BẬT LẠI hoàn tất. Thành công: " + successCount + ", Thất bại: " + errorCount);
  return { success: successCount, errors: errorCount, errorDetails: errorDetails };
}


/**
 * Kéo dữ liệu Insights level=ad
 */
function pullFacebookData(accessToken, adAccountIds, datePreset) {
  // ===== Safety check & Auto-load logic =====
  try {
    if (!adAccountIds || !accessToken || !datePreset) {
      Logger.log("CẢNH BÁO: 'pullFacebookData' đang được chạy trực tiếp. Đang tự tải logic...");
      var settings = layCaiDatHeThong();
      accessToken = accessToken || settings["ACCESS_TOKEN"];
      adAccountIds = adAccountIds || settings["AD_ACCOUNT_IDS"];
      datePreset = datePreset || settings["DATA_DATE_PRESET"];
      if (!accessToken || !adAccountIds || adAccountIds.length === 0 || !datePreset) {
        throw new Error("Tự tải thất bại: Không tìm thấy ACCESS_TOKEN, AD_ACCOUNT_IDS, hoặc DATA_DATE_PRESET.");
      }
    }
  } catch (e) {
    Logger.log("LỖI NGHIÊM TRỌNG (Safety Check): " + e.message);
    throw e;
  }

  // ===== Chuẩn bị sheet =====
  var ss = getSpreadsheet_();
  var sheet = ss.getSheetByName(SHEET_NAME_DATA) || ss.insertSheet(SHEET_NAME_DATA);
  
  // Lưu trạng thái filter hiện tại (nếu có)
  var filter = sheet.getFilter();
  var wasFiltered = filter !== null;
  
  // Nếu có filter, tạm thời tắt để đảm bảo ghi dữ liệu đúng
  if (wasFiltered) {
    try {
      // Lưu filter range để khôi phục sau
      var filterRange = filter.getRange();
      Logger.log("📋 Đã phát hiện filter đang hoạt động, tạm thời tắt để ghi dữ liệu đúng");
      // Không thể "tắt" filter trực tiếp, nhưng sẽ ghi dữ liệu vào tất cả hàng
    } catch (e) {
      Logger.log("⚠️ Không thể xử lý filter: " + e.message);
    }
  }
  
  // KHÔNG dùng clearContents() vì sẽ xóa filter views
  // Thay vào đó, chỉ xóa phần dữ liệu từ hàng 3 trở đi (giữ lại hàng 1 và 2)
  var lastRow = sheet.getLastRow();
  var lastCol = sheet.getLastColumn();
  
  // Nếu có dữ liệu từ hàng 3 trở đi, xóa nó (nhưng giữ lại filter views)
  if (lastRow >= 3) {
    // Xóa dữ liệu từ hàng 3 đến cuối, nhưng giữ lại filter views
    // Dùng clearContent() thay vì clear() để không xóa định dạng và filter
    var rangeToClear = sheet.getRange(3, 1, lastRow - 2, lastCol > 0 ? lastCol : 30);
    rangeToClear.clearContent();
    
    // Đảm bảo không còn dữ liệu thừa ở các hàng sau (nếu dữ liệu mới ít hơn)
    // Nhưng không xóa toàn bộ để tránh ảnh hưởng đến filter
    Logger.log("Đã xóa dữ liệu cũ từ hàng 3 đến hàng " + lastRow + " (giữ lại filter views)");
  }
  
  // Ghi lại header row 1 (metadata)
  sheet.getRange("A1").setValue("Dữ liệu từ API Facebook (Custom Script)");

  var newHeaders = [
    'Account name','Account ID','Campaign name',
    'Adset Id','Adset name',
    'Ad Id','Ad name',
    'Adset Effective Status',   // H
    'Amount spent',             // I
    'Kết Quả',                  // J (sum of comments + messages)
    'Giá DATA',                 // K (I / J)
    '% ADS',                    // L (I / Purchase value)
    'Cost per checkout initiated', // M
    'Checkouts Initiated',      // N
    'Cost per purchase',        // O
    'Purchases',                // P
    'Giá trị chuyển đổi từ lượt mua', // Q (purchase value)
    'CPM',                      // R (I / Impressions * 1000)
    'Impressions',              // S
    'Reach',                    // T
    'Frequency',                // U
    'Clicks (all)',             // V
    'CTR (all)',                // W
    'CPC (all)',                // X
    'Cost per comment',         // Y
    'Cost per messaging conversation', // Z
    'Post comments',            // AA
    'Messaging conversations started'  // AB
  ];
  sheet.getRange(2, 1, 1, newHeaders.length).setValues([newHeaders]);

  // ===== Danh sách fields HỢP LỆ cho insights
  var fields = [
    'account_name','account_id','campaign_name','campaign_id',
    'adset_id','adset_name',
    'ad_id','ad_name',
    'spend','impressions','reach','frequency','clicks','ctr','cpc',
    'cost_per_initiate_checkout','cost_per_purchase',
    'cost_per_action_type','actions','action_values'
  ];
  var fieldsString = fields.join(',');

  var allRows = [];
  var collectedAdsetIds = [];
  var purchaseValues = []; // giá trị chuyển đổi từ lượt mua
  var totalAdsFromAPI = 0; // Tổng số ads từ API
  var filteredAdsCount = 0; // Số ads sau khi filter prefix
  
  // Tự động đọc prefix từ LogicRules hàng 1 (format: act_xxx|PREFIX)
  // Nếu không đọc được, dùng danh sách mặc định
  var ALLOWED_PREFIXES = [];
  try {
    ALLOWED_PREFIXES = extractPrefixesFromLogicRules_();
    if (ALLOWED_PREFIXES.length === 0) {
      Logger.log("⚠️ Không đọc được prefix từ LogicRules, dùng danh sách mặc định");
      ALLOWED_PREFIXES = ['PX','TL','FL','NM','CCHL','DHHL','HSHL','CCB'];
    }
  } catch (e) {
    Logger.log("⚠️ Lỗi khi đọc prefix từ LogicRules: " + e.message + ". Dùng danh sách mặc định");
    ALLOWED_PREFIXES = ['PX','TL','FL','NM','CCHL','DHHL','HSHL','CCB'];
  }
  
  // Helper: Lấy prefix từ campaign name (lấy phần đầu tiên, có thể có số)
  function getPrefixFromCampaign_(campaignName) {
    if (!campaignName) return '';
    var upperName = String(campaignName).toUpperCase();
    var parts = upperName.split(/[\s-_]+/);
    return parts[0] || '';
  }
  
  // Helper: Kiểm tra campaign name có prefix hợp lệ không
  // Hỗ trợ: "CCB1" match với "CCB", "PX1" match với "PX", v.v.
  // TỐI ƯU: Cache ALLOWED_PREFIXES thành Set để lookup nhanh hơn
  var allowedPrefixesSet = {};
  for (var apIdx = 0; apIdx < ALLOWED_PREFIXES.length; apIdx++) {
    allowedPrefixesSet[ALLOWED_PREFIXES[apIdx]] = true;
  }
  
  function hasAllowedPrefix(campaignName) {
    if (!campaignName) return false;
    var extractedPrefix = getPrefixFromCampaign_(campaignName);
    
    // 1. Thử exact match trước - TỐI ƯU: dùng object lookup
    if (allowedPrefixesSet[extractedPrefix]) {
      return true;
    }
    
    // 2. Thử match prefix là substring (ví dụ: "CCB1" bắt đầu bằng "CCB")
    for (var i = 0; i < ALLOWED_PREFIXES.length; i++) {
      var allowedPrefix = ALLOWED_PREFIXES[i];
      if (extractedPrefix.indexOf(allowedPrefix) === 0) {
        return true; // "CCB1" bắt đầu bằng "CCB" → match
      }
      // Hoặc ngược lại: "CCB" match với "CCB1"
      if (allowedPrefix.indexOf(extractedPrefix) === 0 && extractedPrefix.length >= 2) {
        return true;
      }
    }
    
    return false;
  }

  Logger.log("Đang thử kéo dữ liệu với " + adAccountIds.length + " tài khoản (Phạm vi: " + datePreset + ")...");
  Logger.log("📋 Lọc theo campaign prefix (tự động đọc từ LogicRules): " + ALLOWED_PREFIXES.join(", "));
  Logger.log("📋 Lấy cả adsets PAUSED để có thể bật lại sau");

  // ===== Kéo theo từng ad account =====
  // TỐI ƯU: Dùng for thay vì forEach
  for (var accIdx = 0; accIdx < adAccountIds.length; accIdx++) {
    var adAccountId = adAccountIds[accIdx];
    Logger.log("Đang kéo dữ liệu cho tài khoản: " + adAccountId + " (Phạm vi: " + datePreset + ")");
    try {
      // Xử lý pagination: Lấy TẤT CẢ pages (không chỉ page đầu tiên)
      var nextUrl = null;
      var pageCount = 0;
      
      do {
        pageCount++;
        var baseUrl;
        if (nextUrl) {
          // Lấy page tiếp theo từ nextUrl
          baseUrl = nextUrl;
        } else {
          // Tạo URL cho page đầu tiên
          // QUAN TRỌNG: Với date_preset=yesterday, API có thể không trả về PAUSED ads có data
          // Nên dùng time_range để lấy chính xác yesterday
          var baseUrlPart = 'https://graph.facebook.com/v24.0/' + adAccountId + '/insights' +
                    '?level=ad' +
                    '&fields=' + fieldsString +
                    '&limit=1000' +
                    '&access_token=' + encodeURIComponent(accessToken);
          
          // Xử lý date_preset: Nếu là yesterday, convert sang time_range
          // QUAN TRỌNG: Dùng script timezone (không phải UTC) để tính yesterday chính xác
          if (datePreset === 'yesterday') {
            // Tính toán yesterday theo script timezone (thường là Asia/Ho_Chi_Minh)
            var tz = Session.getScriptTimeZone() || 'Asia/Ho_Chi_Minh';
            var now = new Date();
            var today = new Date(now);
            today.setHours(0, 0, 0, 0); // Reset về 00:00:00 theo script timezone
            var yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            
            // Format: YYYY-MM-DD (dùng script timezone, không phải UTC)
            // Facebook API time_range: since là ngày bắt đầu, until là ngày kết thúc (exclusive)
            // Để lấy yesterday: since = yesterday, until = today
            var since = Utilities.formatDate(yesterday, tz, 'yyyy-MM-dd');
            var until = Utilities.formatDate(today, tz, 'yyyy-MM-dd');
            baseUrlPart += '&time_range=' + encodeURIComponent('{"since":"' + since + '","until":"' + until + '"}');
          } else {
            baseUrlPart += '&date_preset=' + datePreset;
          }

      if (INCLUDE_WIDE_AD_STATUSES) {
            baseUrlPart += '&action_report_time=conversion' +
                       '&use_unified_attribution_setting=true' +
                       '&action_attribution_windows=1d_click,7d_click,1d_view,7d_view';
          }
          
          baseUrl = baseUrlPart;
      }

      var response = UrlFetchApp.fetch(baseUrl, { 'muteHttpExceptions': true });
      var jsonText = response.getContentText();
      var json = JSON.parse(jsonText);

      // (Phần xử lý lỗi API giữ nguyên)
      if (json.error) {
        var code = json.error.code;
          if (code === 190 || code === 100) { try{ increaseTokenAlertCount_(1); }catch(_e){} throw new Error("Lỗi Token hoặc Quyền (Code " + code + "). Chi tiết: " + json.error.message); }
          if (code === 200) { try{ increaseTokenAlertCount_(1); }catch(_e){} throw new Error("Mất quyền truy cập TK (Code 200). Chi tiết: " + json.error.message); }
        throw new Error("LỖI API: " + json.error.message);
      }
        
      if (!json.data || !Array.isArray(json.data) || json.data.length === 0) {
          if (pageCount === 1) {
            Logger.log("⚠️ Tài khoản " + adAccountId + " không có dữ liệu insights cho " + datePreset + ".");
            Logger.log("   (Đã dùng time_range thay vì date_preset để lấy được cả PAUSED ads)");
            Logger.log("   (Có thể do: không có ads chạy trong khoảng thời gian này, hoặc không có quyền truy cập)");
            Logger.log("   💡 Gợi ý: Kiểm tra trong Ads Manager xem có dữ liệu không. Nếu có nhưng API không trả về, có thể do quyền token)");
            
            // Gửi cảnh báo qua Telegram nếu có thể (đặc biệt khi nghi ngờ mất quyền)
            try {
              var settings = layCaiDatHeThong && layCaiDatHeThong();
              var botToken = settings && settings["TELEGRAM_BOT_TOKEN"];
              var chatId = settings && settings["TELEGRAM_CHAT_ID"];
              if (botToken && chatId) {
                // Sử dụng plain text để tránh lỗi HTML entities
                var warningMsg = "⚠️ CẢNH BÁO: KHÔNG CÓ DỮ LIỆU INSIGHTS\n\n";
                warningMsg += "📛 Tài khoản: " + adAccountId + "\n";
                warningMsg += "📅 Khoảng thời gian: " + datePreset + "\n\n";
                warningMsg += "🔍 NGUYÊN NHÂN CÓ THỂ:\n";
                warningMsg += "• Không có ads chạy trong khoảng thời gian này\n";
                warningMsg += "• Mất quyền truy cập (token thiếu quyền ads_read)\n";
                warningMsg += "• Tài khoản bị vô hiệu hóa hoặc bị hạn chế\n\n";
                warningMsg += "💡 HÀNH ĐỘNG CẦN THỰC HIỆN:\n";
                warningMsg += "1. Kiểm tra trong Ads Manager xem có dữ liệu không\n";
                warningMsg += "2. Nếu có dữ liệu nhưng API không trả về:\n";
                warningMsg += "   → Kiểm tra quyền token (cần ads_read hoặc ads_management)\n";
                warningMsg += "   → Kiểm tra token còn hiệu lực không\n";
                warningMsg += "3. Nếu không có dữ liệu:\n";
                warningMsg += "   → Kiểm tra xem có ads đang chạy không\n";
                warningMsg += "   → Kiểm tra tài khoản có bị hạn chế không";
                guiThongBaoTelegram(warningMsg, botToken, chatId);
              }
            } catch (eWarn) {
              Logger.log("⚠️ Lỗi gửi cảnh báo Telegram: " + eWarn.message);
            }
          }
          break; // Không có dữ liệu, thoát khỏi vòng lặp pagination
        }
        
        // Log số ads có prefix hợp lệ trong page này (để debug)
        var prefixMatchCount = 0;
        var prefixMatchDetails = {};
        var sampleCampaigns = [];
        var sampleCampaignsSet = {}; // TỐI ƯU: Cache để tránh indexOf
        // TỐI ƯU: Dùng for thay vì forEach
        for (var adIdx3 = 0; adIdx3 < json.data.length; adIdx3++) {
          var ad = json.data[adIdx3];
          if (ad && ad.campaign_name) {
            var prefix = getPrefixFromCampaign_(ad.campaign_name);
            if (hasAllowedPrefix(ad.campaign_name)) {
              prefixMatchCount++;
              prefixMatchDetails[prefix] = (prefixMatchDetails[prefix] || 0) + 1;
            } else {
              // Thu thập sample campaigns không match để debug
              var campName = ad.campaign_name;
              if (sampleCampaigns.length < 3 && !sampleCampaignsSet[campName]) {
                sampleCampaignsSet[campName] = true;
                sampleCampaigns.push(campName + " (prefix: " + prefix + ")");
              }
            }
          }
        }
        if (prefixMatchCount > 0) {
          Logger.log("   📋 Trong page " + pageCount + ": " + prefixMatchCount + "/" + json.data.length + " ads có prefix hợp lệ");
          // TỐI ƯU: Dùng for thay vì map
          var detailParts = [];
          var prefixKeys = Object.keys(prefixMatchDetails);
          for (var pkIdx2 = 0; pkIdx2 < prefixKeys.length; pkIdx2++) {
            var p = prefixKeys[pkIdx2];
            detailParts.push(p + ":" + prefixMatchDetails[p]);
          }
          var detailStr = detailParts.join(", ");
          if (detailStr) Logger.log("      Chi tiết prefix: " + detailStr);
        } else if (json.data.length > 0 && pageCount === 1) {
          // Chỉ log ở page đầu tiên để tránh spam
          Logger.log("   ⚠️ Trong page " + pageCount + ": " + json.data.length + " ads nhưng KHÔNG CÓ ads nào có prefix hợp lệ");
          if (sampleCampaigns.length > 0) {
            Logger.log("      Ví dụ campaign names: " + sampleCampaigns.join(", "));
          }
          Logger.log("      Prefix cần tìm: " + ALLOWED_PREFIXES.join(", "));
        }
        
        totalAdsFromAPI += json.data.length;
        Logger.log("   📊 Page " + pageCount + ": Nhận được " + json.data.length + " ads từ API (sẽ lọc theo prefix + impressions>0 hoặc spend>0)...");

      var parseApiNumber = function(v){ return parseFloat(v) || 0; };
      var _SUFFIXES = ["", "_unique", "_1d_click", "_7d_click", "_28d_click", "_1d_view", "_7d_view", "_28d_view"];
      function _buildMap_(arr) { var map = {}; if (!arr || !Array.isArray(arr)) return map; for (var i=0;i<arr.length;i++){ var it=arr[i]; if (!it) continue; var k=String(it.action_type||""); var v=parseFloat(it.value); if (!isNaN(v)) map[k]=v; } return map; }
      function _pickFirstVariant_(map, bases) { for (var b=0;b<(bases||[]).length;b++){ var base=bases[b]; for (var s=0;s<_SUFFIXES.length;s++){ var key=base+_SUFFIXES[s]; if (map[key]!=null) return parseFloat(map[key])||0; } } return 0; }
      function _pickCost_(costMap, bases){ for (var b=0;b<(bases||[]).length;b++){ var base=bases[b]; if (costMap[base]!=null) return parseFloat(costMap[base]); for (var s=0;s<_SUFFIXES.length;s++){ var key=base+_SUFFIXES[s]; if (costMap[key]!=null) return parseFloat(costMap[key]); } } return NaN; }

      // ===== Duyệt từng ad row =====
      // Tracking để phát hiện duplicate hoặc nhiều ads trong cùng adset
      var adsetSpendMap = {}; // { adsetId: totalSpend }
      var campaignSpendMap = {}; // { campaignName: totalSpend }
      
      // TỐI ƯU: Dùng for thay vì forEach - đây là vòng lặp lớn nhất, cần tối ưu
      for (var adIdx2 = 0; adIdx2 < json.data.length; adIdx2++) {
        var ad = json.data[adIdx2];
        if (!ad) continue; // TỐI ƯU: Dùng continue thay vì return trong for loop
        try {
          // Bước 1: Lọc theo campaign prefix: CHỈ lấy các campaign có prefix hợp lệ
          var campaignName = ad.campaign_name || '';
          if (!hasAllowedPrefix(campaignName)) {
            // Bỏ qua campaign không có prefix hợp lệ
            continue; // TỐI ƯU: Dùng continue thay vì return trong for loop
          }
          
          // Track spend cho campaign (để debug dữ liệu bị cộng dồn)
          if (!campaignSpendMap[campaignName]) {
            campaignSpendMap[campaignName] = { count: 0, totalSpend: 0, adsetIds: [] };
          }
          
          // Bước 2: Kiểm tra impressions > 0 HOẶC spend > 0 (lấy adsets có dữ liệu)
          var impressionsNum = parseInt(ad.impressions || 0, 10);
          var spendV = parseApiNumber(ad.spend);
          
          // Track spend cho adset và campaign
          var adsetId = ad.adset_id || 'UNKNOWN';
          if (!adsetSpendMap[adsetId]) {
            adsetSpendMap[adsetId] = { count: 0, totalSpend: 0, campaignName: campaignName };
          }
          adsetSpendMap[adsetId].count++;
          adsetSpendMap[adsetId].totalSpend += spendV;
          
          campaignSpendMap[campaignName].count++;
          campaignSpendMap[campaignName].totalSpend += spendV;
          if (campaignSpendMap[campaignName].adsetIds.indexOf(adsetId) < 0) {
            campaignSpendMap[campaignName].adsetIds.push(adsetId);
          }
          
          // Lấy nếu: impressions > 0 HOẶC spend > 0 (có thể adset đã tắt nhưng vẫn có dữ liệu chi tiêu)
          if (impressionsNum <= 0 && spendV <= 0) {
            // Bỏ qua adset không có impressions và không có spend (không có dữ liệu gì)
            Logger.log("   ⏭️ Bỏ qua ad " + (ad.ad_id || 'UNKNOWN') + " (Adset: " + adsetId + ") - Campaign: " + campaignName + " (Impressions = 0, Spend = 0)");
            continue; // TỐI ƯU: Dùng continue thay vì return trong for loop
          }
          
          // Log nếu có spend nhưng không có impressions (để debug)
          if (spendV > 0 && impressionsNum === 0) {
            Logger.log("   ℹ️ Ad " + (ad.ad_id || 'UNKNOWN') + " (Adset: " + adsetId + ") có Spend=" + spendV + " nhưng Impressions=0 (vẫn lấy)");
          }
          
          filteredAdsCount++; // Đếm ads sau khi filter prefix + (impressions>0 hoặc spend>0)
          
          if (ad.adset_id) collectedAdsetIds.push(ad.adset_id);

          var actMap = _buildMap_(ad.actions);
          var costMap = _buildMap_(ad.cost_per_action_type);
          var valMap  = _buildMap_(ad.action_values || []);

          // Danh sách các action type variants - ĐẦY ĐỦ để bắt được tất cả cách Facebook trả về
          var basesIC  = ['initiate_checkout','offsite_conversion.fb_pixel_initiate_checkout','omni_initiated_checkout','onsite_conversion.initiated_checkout'];
          var basesPUR = ['purchase','offsite_conversion.fb_pixel_purchase','omni_purchase','onsite_conversion.purchase'];
          // Comments: Thử nhiều variants vì Facebook có thể trả về khác nhau
          var basesCMT = [
            'comment',                    // Base variant
            'post_comment',               // Variant có prefix post_
            'onsite_conversion.post_comment' // Variant có prefix onsite_conversion
          ];
          // Messaging: Thử tất cả variants có thể
          var basesMSG = [
            'onsite_conversion.messaging_conversation_started',  // Ưu tiên variant có prefix onsite_conversion
            'messaging_conversation_started',                     // Base variant
            'messaging_conversation_started_1d_click',           // Variant với attribution window
            'messaging_conversation_started_7d_click'             // Variant với attribution window
          ];

          var initiateCheckout = _pickFirstVariant_(actMap, basesIC);
          var purchases        = _pickFirstVariant_(actMap, basesPUR);
          var postComments     = _pickFirstVariant_(actMap, basesCMT);
          var msgStarted       = _pickFirstVariant_(actMap, basesMSG);
          var purchaseValue    = _pickFirstVariant_(valMap, basesPUR);
          
          // spendV đã được tính ở trên (bước 2 filter)
          
          // Fallback THÔNG MINH: Nếu không tìm thấy, tìm trong actMap với tất cả variants
          // Nhưng ưu tiên base variant (không có suffix), sau đó mới lấy variants có suffix
          if (msgStarted === 0 && spendV > 0 && ad.actions && Array.isArray(ad.actions)) {
            // TỐI ƯU: Dùng for thay vì filter
            var allMsgKeys = [];
            var actMapKeys = Object.keys(actMap);
            for (var mkIdx = 0; mkIdx < actMapKeys.length; mkIdx++) {
              var k = actMapKeys[mkIdx];
              var kLower = k.toLowerCase();
              // Tìm tất cả keys có chứa messaging_conversation_started (kể cả với suffix)
              if ((kLower.indexOf('messaging_conversation_started') >= 0) && k.indexOf('_unique') < 0) {
                allMsgKeys.push(k);
              }
            }
            if (allMsgKeys.length > 0) {
              // Ưu tiên base (không có suffix), nếu không có thì lấy variant có suffix
              // TỐI ƯU: Dùng for thay vì filter
              var baseKeys = [];
              for (var bkIdx = 0; bkIdx < allMsgKeys.length; bkIdx++) {
                var k2 = allMsgKeys[bkIdx];
                if (k2.indexOf('_1d_') < 0 && k2.indexOf('_7d_') < 0 && k2.indexOf('_28d_') < 0) {
                  baseKeys.push(k2);
                }
              }
              var targetKeys = baseKeys.length > 0 ? baseKeys : allMsgKeys;
              // TỐI ƯU: Dùng for thay vì map
              var maxVal = 0;
              for (var tkIdx = 0; tkIdx < targetKeys.length; tkIdx++) {
                var val = parseFloat(actMap[targetKeys[tkIdx]]) || 0;
                if (val > maxVal) maxVal = val;
              }
              msgStarted = maxVal;
            }
          }
          
          // Fallback cho comments: Tìm tất cả variants của comment/post_comment
          if (postComments === 0 && spendV > 0 && ad.actions && Array.isArray(ad.actions)) {
            // TỐI ƯU: Dùng for thay vì filter
            var allCommentKeys = [];
            var actMapKeys2 = Object.keys(actMap);
            for (var ckIdx = 0; ckIdx < actMapKeys2.length; ckIdx++) {
              var k = actMapKeys2[ckIdx];
              var kLower = k.toLowerCase();
              // Tìm comment hoặc post_comment (kể cả với suffix)
              if ((kLower === 'comment' || kLower === 'post_comment' || kLower.indexOf('comment') >= 0) && k.indexOf('_unique') < 0) {
                allCommentKeys.push(k);
              }
            }
            if (allCommentKeys.length > 0) {
              // Ưu tiên base (không có suffix)
              // TỐI ƯU: Dùng for thay vì filter
              var baseCommentKeys = [];
              for (var bckIdx = 0; bckIdx < allCommentKeys.length; bckIdx++) {
                var k2 = allCommentKeys[bckIdx];
                if (k2.indexOf('_1d_') < 0 && k2.indexOf('_7d_') < 0 && k2.indexOf('_28d_') < 0) {
                  baseCommentKeys.push(k2);
                }
              }
              var targetCommentKeys = baseCommentKeys.length > 0 ? baseCommentKeys : allCommentKeys;
              // TỐI ƯU: Dùng for thay vì map
              var maxCommentVal = 0;
              for (var tckIdx = 0; tckIdx < targetCommentKeys.length; tckIdx++) {
                var val = parseFloat(actMap[targetCommentKeys[tckIdx]]) || 0;
                if (val > maxCommentVal) maxCommentVal = val;
              }
              postComments = maxCommentVal;
            }
          }
          
          // Debug logging cho TẤT CẢ ads có spend > 0 nhưng ketQua = 0 (để tìm pattern)
          var ketQuaCalc = (postComments || 0) + (msgStarted || 0);
          if (spendV > 1000 && ketQuaCalc === 0) {
            Logger.log("🔍 DEBUG Ad " + (ad.ad_id || 'UNKNOWN') + " (Adset: " + (ad.adset_id || 'UNKNOWN') + "):");
            Logger.log("  - Spend: " + spendV);
            Logger.log("  - actMap keys: " + Object.keys(actMap).join(", "));
            Logger.log("  - postComments (từ _pickFirstVariant_): " + _pickFirstVariant_(actMap, basesCMT));
            Logger.log("  - msgStarted (từ _pickFirstVariant_): " + _pickFirstVariant_(actMap, basesMSG));
            Logger.log("  - postComments (sau fallback): " + postComments);
            Logger.log("  - msgStarted (sau fallback): " + msgStarted);
            Logger.log("  - ketQua tính được: " + ketQuaCalc);
          }

          var cpiCheckout = _pickCost_(costMap, basesIC);
          if (isNaN(cpiCheckout)) cpiCheckout = initiateCheckout > 0 ? spendV / initiateCheckout : 0;
          var cpPurchase = _pickCost_(costMap, basesPUR);
          if (isNaN(cpPurchase)) cpPurchase = purchases > 0 ? spendV / purchases : 0;
          var cpComment = _pickCost_(costMap, basesCMT);
          if (isNaN(cpComment)) cpComment = postComments > 0 ? spendV / postComments : 0;
          var cpMsg = _pickCost_(costMap, basesMSG);
          if (isNaN(cpMsg)) cpMsg = msgStarted > 0 ? spendV / msgStarted : 0;

          var ketQua  = (postComments || 0) + (msgStarted || 0);
          // Tính Giá DATA: nếu ketQua > 0 thì spendV / ketQua, nếu không thì 0 (hoặc có thể để là spendV để báo hiệu)
          var giaData = ketQua > 0 ? (spendV / ketQua) : 0;
          // Đảm bảo giaData là số hợp lệ (không phải NaN hoặc Infinity)
          if (isNaN(giaData) || !isFinite(giaData)) {
            giaData = 0;
          }
          var pctAds  = purchaseValue > 0 ? (spendV / purchaseValue) : 0;
          // Đảm bảo pctAds là số hợp lệ
          if (isNaN(pctAds) || !isFinite(pctAds)) {
            pctAds = 0;
          }
          // impressionsNum đã được tính ở trên (bước 2 filter)
          var cpm = impressionsNum > 0 ? (spendV / impressionsNum) * 1000 : 0;
          // Đảm bảo cpm là số hợp lệ
          if (isNaN(cpm) || !isFinite(cpm)) {
            cpm = 0;
          }
          
          // Debug logging cho trường hợp có spend và ketQua nhưng giaData không hợp lệ
          if (spendV > 0 && ketQua > 0 && (isNaN(giaData) || giaData === 0)) {
            Logger.log("⚠️ DEBUG: Ad " + (ad.ad_id || 'UNKNOWN') + " - Spend: " + spendV + ", Kết Quả: " + ketQua + ", Giá DATA tính được: " + giaData);
          }
          
          // Đảm bảo giaData là số (không phải string hoặc undefined)
          if (typeof giaData !== 'number') {
            Logger.log("⚠️ WARNING: giaData không phải số cho Ad " + (ad.ad_id || 'UNKNOWN') + ", giá trị: " + giaData + ", type: " + typeof giaData);
            giaData = parseFloat(giaData) || 0;
          }
          
          // Log chi tiết cho một số ads để debug (chỉ log 5 ads đầu tiên để tránh spam)
          if (allRows.length < 5) {
            Logger.log("📊 DEBUG Ad " + (ad.ad_id || 'UNKNOWN') + ": Spend=" + spendV + ", Kết Quả=" + ketQua + ", Giá DATA=" + giaData + 
                      ", postComments=" + postComments + ", msgStarted=" + msgStarted);
          }

          var row = [
            ad.account_name || '',            // A
            ad.account_id || '',              // B
            ad.campaign_name || '',           // C
            ad.adset_id || '',                // D
            ad.adset_name || '',              // E
            ad.ad_id || '',                   // F
            ad.ad_name || '',                 // G
            'PENDING',                        // H
            spendV,                           // I Amount spent
            ketQua,                           // J Kết Quả
            giaData,                          // K Giá DATA (đảm bảo là số)
            pctAds,                           // L % ADS
            cpiCheckout,                      // M CPL (checkout initiated)
            initiateCheckout,                 // N Checkouts Initiated
            cpPurchase,                       // O CPA (purchase)
            purchases,                        // P Purchases
            purchaseValue,                    // Q Purchase value
            cpm,                              // R CPM
            impressionsNum,                   // S Impressions
            parseInt(ad.reach || 0, 10),      // T Reach
            parseApiNumber(ad.frequency),     // U Frequency
            parseInt(ad.clicks || 0, 10),     // V Clicks
            (function(){ var ctrRaw = parseApiNumber(ad.ctr); return (ctrRaw > 1) ? ctrRaw/100 : ctrRaw; })(), // W CTR fraction
            parseApiNumber(ad.cpc),           // X CPC
            cpComment,                        // Y Cost per comment
            cpMsg,                            // Z Cost per messaging conversation
            postComments,                     // AA Post comments
            msgStarted                        // AB Messaging conversations started
          ];
          allRows.push(row);
          purchaseValues.push(purchaseValue);
        } catch (eRow) {
          Logger.log("LỖI: Bỏ qua 1 ad (ID: " + (ad.ad_id || 'UNKNOWN') + ") do lỗi xử lý hàng: " + eRow.message);
        }
      } // Kết thúc for loop
      
        // Log thống kê spend cho các campaign (để debug dữ liệu bị cộng dồn)
        // Chỉ log ở page đầu tiên để tránh spam và có cái nhìn tổng quan
        if (Object.keys(campaignSpendMap).length > 0 && pageCount === 1) {
          Logger.log("   📊 Thống kê spend theo campaign (page " + pageCount + "):");
          var topCampaigns = Object.keys(campaignSpendMap).slice(0, 10); // Chỉ log top 10 để tránh spam
          // TỐI ƯU: Dùng for thay vì forEach
          for (var tcIdx = 0; tcIdx < topCampaigns.length; tcIdx++) {
            var campName = topCampaigns[tcIdx];
            var stats = campaignSpendMap[campName];
            Logger.log("      - " + campName + ": " + stats.count + " ads, Tổng spend: " + Math.round(stats.totalSpend) + " ₫, " + stats.adsetIds.length + " adsets");
            // Cảnh báo nếu có nhiều ads trong cùng campaign (có thể bị cộng dồn)
            if (stats.count > 3) {
              Logger.log("         ⚠️ Campaign này có " + stats.count + " ads → spend có thể bị cộng dồn (trên Manager thường hiển thị theo adset/campaign level)");
            }
          }
          if (Object.keys(campaignSpendMap).length > 10) {
            Logger.log("      ... và " + (Object.keys(campaignSpendMap).length - 10) + " campaigns khác");
          }
        }
        
        // Kiểm tra xem có page tiếp theo không
        if (json.paging && json.paging.next) {
          nextUrl = json.paging.next;
          Logger.log("   📄 Có page tiếp theo, đang lấy...");
          // Reset tracking cho page tiếp theo (chỉ log page đầu để tránh spam)
          campaignSpendMap = {};
          adsetSpendMap = {};
        } else {
          nextUrl = null;
        }
        
      } while (nextUrl); // Lặp cho đến khi không còn page nào
      
      Logger.log("   ✅ Hoàn tất tài khoản " + adAccountId + ": Tổng " + pageCount + " page(s)");

    } catch (e) {
      // (Phần thông báo lỗi Telegram giữ nguyên)
      Logger.log("LỖI NGHIÊM TRỌNG khi kéo TK " + adAccountId + ": " + e.message);
      try {
        var logic = layCaiDatHeThong(); // Dùng hàm mới
        var botToken = logic["TELEGRAM_BOT_TOKEN"];
        var chatId = logic["TELEGRAM_CHAT_ID"];
        if (botToken && chatId) {
          var code200 = e.message.includes("(Code 200)");
          var msg;
          if (code200) { msg = "🚨 *LỖI KÉO DỮ LIỆU FACEBOOK*\n" + "📛 *Tài khoản:* `" + adAccountId + "`\n" + "🔒 *Nguyên nhân:* Mất quyền truy cập (Code 200)\n" + "👉 Vui lòng cấp lại quyền `ads_read` hoặc `ads_management`."; } 
          else { msg = "🚨 *LỖI KÉO DỮ LIỆU FACEBOOK*\n" + "📛 *Tài khoản:* `" + adAccountId + "`\n" + "⚠️ *Chi tiết:* " + e.message.split(".")[0]; }
          guiThongBaoTelegram(msg, botToken, chatId);
          try{ increaseTokenAlertCount_(1);}catch(__e){}
        }
      } catch (_e) {}
    }
  } // Kết thúc for loop adAccountIds

  // (Phần batch status và ghi đè Cột H giữ nguyên)
  if (allRows.length > 0) {
    // TỐI ƯU: Dùng for thay vì map để lấy adsetIds
    var adsetIdsForStatus = [];
    for (var sIdx = 0; sIdx < allRows.length; sIdx++) {
      adsetIdsForStatus.push(allRows[sIdx][3]);
    }
    var statusMap = fetchAdsetStatuses(adsetIdsForStatus, accessToken);
    // TỐI ƯU: Dùng for thay vì map
    for (var rIdx = 0; rIdx < allRows.length; rIdx++) {
      var r = allRows[rIdx];
      var adsetId = r[3];
      r[7] = statusMap[adsetId] || r[7] || 'UNKNOWN'; // H
      // Đảm bảo giaData (cột K, index 10) là số hợp lệ
      if (r.length > 10 && (isNaN(r[10]) || !isFinite(r[10]))) {
        Logger.log("⚠️ WARNING: Sửa giaData không hợp lệ cho Adset " + adsetId + ": " + r[10]);
        r[10] = 0;
      }
      // Đảm bảo giaData là number type (không phải string)
      if (r.length > 10 && typeof r[10] !== 'number') {
        r[10] = parseFloat(r[10]) || 0;
      }
    }
  }

  // ===== Thống kê và ghi dữ liệu =====
  Logger.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Logger.log("📊 THỐNG KÊ KÉO DỮ LIỆU:");
  Logger.log("   - Tổng ads từ API: " + totalAdsFromAPI);
  Logger.log("   - Ads sau filter prefix + (impressions>0 hoặc spend>0): " + filteredAdsCount);
  Logger.log("   - Ads ghi vào sheet: " + allRows.length);
  Logger.log("   - Prefix được lọc: " + ALLOWED_PREFIXES.join(", "));
  Logger.log("   - Tiêu chí: Campaign có prefix hợp lệ VÀ (Impressions > 0 HOẶC Spend > 0)");
  if (filteredAdsCount !== allRows.length) {
    Logger.log("   ⚠️ Cảnh báo: filteredAdsCount (" + filteredAdsCount + ") khác allRows.length (" + allRows.length + ")");
  }
  Logger.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  if (allRows.length > 0) {
    // Đảm bảo tất cả rows đều có đủ số cột (bằng với số headers)
    var expectedCols = newHeaders.length;
    // TỐI ƯU: Dùng for thay vì map
    for (var rowIdx = 0; rowIdx < allRows.length; rowIdx++) {
      var row = allRows[rowIdx];
      // Nếu row thiếu cột, thêm các cột rỗng
      while (row.length < expectedCols) {
        row.push('');
      }
      // Nếu row thừa cột, cắt bớt
      if (row.length > expectedCols) {
        allRows[rowIdx] = row.slice(0, expectedCols);
      }
    }
    
    // Đảm bảo giaData (cột K, index 10) trong mỗi row là số hợp lệ TRƯỚC KHI GHI
    // TỐI ƯU: Dùng for thay vì forEach
    for (var idx = 0; idx < allRows.length; idx++) {
      var row = allRows[idx];
      if (row.length > 10) {
        var giaDataVal = row[10];
        var spend = typeof row[8] === 'number' ? row[8] : parseFloat(row[8]) || 0;
        var ketQua = typeof row[9] === 'number' ? row[9] : parseFloat(row[9]) || 0;
        
        // LUÔN tính lại giaData từ spend và ketQua để đảm bảo chính xác
        // Đây là giá trị TĨNH, không phải công thức
        if (ketQua > 0 && spend > 0) {
          row[10] = spend / ketQua;
        } else {
          row[10] = 0;
        }
        
        // Validation cuối cùng: đảm bảo giaData là số hợp lệ
        if (typeof row[10] !== 'number' || isNaN(row[10]) || !isFinite(row[10])) {
          Logger.log("⚠️ WARNING Row " + (idx + 3) + ": giaData không hợp lệ sau khi tính lại: " + row[10]);
          row[10] = 0;
        }
        
        // Log một số rows để debug
        if (idx < 5 && ketQua > 0) {
          Logger.log("✅ Row " + (idx + 3) + ": Spend=" + spend + ", Kết Quả=" + ketQua + ", Giá DATA=" + row[10]);
        }
      }
    } // Kết thúc for loop
    
    // Ghi dữ liệu vào sheet (hàng 3 trở đi)
    // QUAN TRỌNG: Ghi dưới dạng giá trị số tĩnh, không phải công thức
    // setValues() sẽ ghi vào TẤT CẢ các hàng, kể cả hàng bị ẩn bởi filter
    var targetRange = sheet.getRange(3, 1, allRows.length, expectedCols);
    targetRange.setValues(allRows);
    
    // Đảm bảo cột "Giá DATA" (cột K, index 11) được format là số, không phải công thức
    // Sau khi ghi, kiểm tra lại một số giá trị để đảm bảo không bị mất
    try {
      var giaDataCol = 11; // Cột K (index 11, vì cột A = 1)
      var sampleRange = sheet.getRange(3, giaDataCol, Math.min(5, allRows.length), 1);
      var sampleValues = sampleRange.getValues();
      var hasZeroIssue = false;
      for (var i = 0; i < sampleValues.length; i++) {
        var val = sampleValues[i][0];
        var expectedKetQua = allRows[i][9]; // Kết Quả
        var expectedSpend = allRows[i][8]; // Amount spent
        if (expectedKetQua > 0 && expectedSpend > 0 && (val === 0 || val === '' || val === null)) {
          hasZeroIssue = true;
          Logger.log("⚠️ PHÁT HIỆN VẤN ĐỀ: Row " + (i + 3) + " có Kết Quả=" + expectedKetQua + ", Spend=" + expectedSpend + " nhưng Giá DATA=" + val);
          // Sửa lại giá trị
          var correctGiaData = expectedSpend / expectedKetQua;
          sheet.getRange(i + 3, giaDataCol).setValue(correctGiaData);
          Logger.log("   ✅ Đã sửa lại Giá DATA=" + correctGiaData);
        }
      }
      if (!hasZeroIssue) {
        Logger.log("✅ Đã kiểm tra: Tất cả giá trị Giá DATA đều hợp lệ");
      }
    } catch (e) {
      Logger.log("⚠️ Không thể kiểm tra giá trị sau khi ghi: " + e.message);
    }

    Logger.log("Đang áp dụng định dạng cho 'dễ nhìn'...");
    var currencyFormat = '#,##0 ₫';
    var decimalFormat  = '0.00';
    var percentFormat  = '0.00%'; 
    var integerFormat  = '#,##0';

    // Helper: format by header name
    function colOf(name){ var idx = newHeaders.indexOf(name); return idx >= 0 ? (idx+1) : -1; }
    function fmtCol(name, fmt){ var c = colOf(name); if (c > 0) sheet.getRange(3, c, sheet.getLastRow()-2, 1).setNumberFormat(fmt); }

    // Currency columns - TỐI ƯU: Dùng for thay vì forEach
    var currencyCols = ['Amount spent','CPC (all)','Cost per checkout initiated','Cost per purchase','Cost per comment','Cost per messaging conversation','Giá DATA','Giá trị chuyển đổi từ lượt mua','CPM'];
    for (var ccIdx = 0; ccIdx < currencyCols.length; ccIdx++) {
      fmtCol(currencyCols[ccIdx], currencyFormat);
    }

    // Percent columns
    var percentCols = ['CTR (all)','% ADS'];
    for (var pcIdx = 0; pcIdx < percentCols.length; pcIdx++) {
      fmtCol(percentCols[pcIdx], percentFormat);
    }

    // Decimal columns
    fmtCol('Frequency', decimalFormat);

    // Integer columns
    var integerCols = ['Impressions','Reach','Clicks (all)','Checkouts Initiated','Purchases','Post comments','Messaging conversations started','Kết Quả'];
    for (var icIdx = 0; icIdx < integerCols.length; icIdx++) {
      fmtCol(integerCols[icIdx], integerFormat);
    }
    
    // SAU KHI FORMAT: Kiểm tra lại TẤT CẢ các giá trị "Giá DATA" để đảm bảo không bị mất
    // Đặc biệt quan trọng khi có filter
    try {
      var giaDataCol = 11; // Cột K
      var spendCol = 9;    // Cột I (Amount spent)
      var ketQuaCol = 10;   // Cột J (Kết Quả)
      
      var allDataRange = sheet.getRange(3, 1, allRows.length, expectedCols);
      var allDataValues = allDataRange.getValues();
      var fixedCount = 0;
      
      for (var i = 0; i < allDataValues.length; i++) {
        var row = allDataValues[i];
        var spend = parseFloat(row[spendCol - 1]) || 0; // -1 vì array index
        var ketQua = parseFloat(row[ketQuaCol - 1]) || 0;
        var giaData = parseFloat(row[giaDataCol - 1]) || 0;
        
        // Nếu có Kết Quả > 0 và Spend > 0 nhưng Giá DATA = 0 hoặc không hợp lệ
        if (ketQua > 0 && spend > 0 && (giaData === 0 || isNaN(giaData) || !isFinite(giaData))) {
          var correctGiaData = spend / ketQua;
          // Ghi lại giá trị đúng vào sheet
          sheet.getRange(i + 3, giaDataCol).setValue(correctGiaData);
          fixedCount++;
          if (fixedCount <= 5) {
            Logger.log("🔧 Sửa Row " + (i + 3) + ": Spend=" + spend + ", Kết Quả=" + ketQua + ", Giá DATA (sửa từ " + giaData + " → " + correctGiaData + ")");
          }
        }
      }
      
      if (fixedCount > 0) {
        Logger.log("✅ Đã sửa " + fixedCount + " giá trị Giá DATA bị mất sau khi format");
      } else {
        Logger.log("✅ Tất cả giá trị Giá DATA đều hợp lệ sau khi format");
      }
    } catch (e) {
      Logger.log("⚠️ Lỗi khi kiểm tra giá trị sau format: " + e.message);
    }
  }

  // Sắp xếp cột Giá DATA từ cao xuống thấp (chỉ sắp xếp phần dữ liệu, giữ nguyên header)
  try {
    if (allRows.length > 0) {
      var giaDataCol = 11; // Cột K (Giá DATA)
      var dataStartRow = 3; // Hàng bắt đầu dữ liệu (sau header)
      var dataEndRow = dataStartRow + allRows.length - 1;
      
      // Tạo range để sắp xếp (tất cả các cột từ hàng 3 đến cuối)
      var sortRange = sheet.getRange(dataStartRow, 1, allRows.length, expectedCols);
      
      // Sắp xếp theo cột Giá DATA (cột K, index 11) từ cao xuống thấp
      sortRange.sort([{column: giaDataCol, ascending: false}]);
      
      Logger.log("✅ Đã sắp xếp dữ liệu theo cột Giá DATA từ cao xuống thấp");
    }
  } catch (e) {
    Logger.log("⚠️ Lỗi khi sắp xếp cột Giá DATA: " + e.message);
  }

  sheet.getRange("B1").setValue("Last updated " + new Date().toLocaleString("vi-VN") + " (" + allRows.length + " ads từ " + (adAccountIds ? adAccountIds.length : 0) + " tài khoản)");
  Logger.log("Hoàn tất kéo dữ liệu. Đã lấy " + allRows.length + " hàng từ " + (adAccountIds ? adAccountIds.length : 0) + " tài khoản.");
}

/**
 * ==================================================================
 * HÀM PULL DỮ LIỆU 7 NGÀY QUA (Level Adset)
 * Hàm riêng để lấy dữ liệu 7 ngày, không phụ thuộc vào CaiDat
 * Trả về: { adsetId: {spend, ketQua, giaData, pctAds, cpCheckout, checkouts, cpPurchase, purchases, accountId, campaignName, adsetName} }
 * ==================================================================
 */
function pullFacebookData7Ngay(accessToken, adAccountIds) {
  if (!accessToken || !adAccountIds || adAccountIds.length === 0) {
    throw new Error("Thiếu ACCESS_TOKEN hoặc AD_ACCOUNT_IDS");
  }
  
  var adsetsData = {}; // { adsetId: {spend, ketQua, giaData, pctAds, cpCheckout, checkouts, cpPurchase, purchases, accountId, campaignName, adsetName} }
  
  Logger.log("Đang kéo dữ liệu 7 ngày qua cho " + adAccountIds.length + " tài khoản...");
  
  // TỐI ƯU: Dùng for thay vì forEach
  for (var accIdx7 = 0; accIdx7 < adAccountIds.length; accIdx7++) {
    var adAccountId = adAccountIds[accIdx7];
    var url = 'https://graph.facebook.com/v24.0/' + adAccountId + '/insights' +
              '?level=adset' +
              '&date_preset=last_7d' +
              '&fields=adset_id,adset_name,account_id,campaign_name,spend,actions,action_values,cost_per_action_type' +
              '&limit=1000' +
              '&access_token=' + encodeURIComponent(accessToken);
    
    var resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var json = JSON.parse(resp.getContentText());
    
    if (json.error) {
      Logger.log("Lỗi kéo dữ liệu 7d cho " + adAccountId + ": " + json.error.message);
      continue; // TỐI ƯU: Dùng continue thay vì return
    }
    
    var data = Array.isArray(json.data) ? json.data : [];
    // TỐI ƯU: Dùng for thay vì forEach
    for (var adsetIdx = 0; adsetIdx < data.length; adsetIdx++) {
      var adset = data[adsetIdx];
      var adsetId = adset.adset_id;
      if (!adsetId) continue; // TỐI ƯU: Dùng continue thay vì return
      
      if (!adsetsData[adsetId]) {
        adsetsData[adsetId] = {
          spend: 0,
          ketQua: 0,
          giaData: 0,
          pctAds: 0,
          cpCheckout: 0,
          checkouts: 0,
          cpPurchase: 0,
          purchases: 0,
          purchaseValue: 0,
          accountId: adset.account_id || adAccountId,
          campaignName: adset.campaign_name || '',
          adsetName: adset.adset_name || ''
        };
      }
      
      var spend = parseFloat(adset.spend) || 0;
      var actions = adset.actions || [];
      var actionValues = adset.action_values || [];
      var costPerAction = adset.cost_per_action_type || [];
      
      function getActionValue(actions, type) {
        if (!actions || !Array.isArray(actions)) return 0;
        var a = actions.find(function(x) { return x.action_type === type; });
        return a ? (parseFloat(a.value) || 0) : 0;
      }
      function getActionValueMoney(values, type) {
        if (!values || !Array.isArray(values)) return 0;
        var v = values.find(function(x) { return x.action_type === type; });
        return v ? (parseFloat(v.value) || 0) : 0;
      }
      function getCostPerAction(costs, type) {
        if (!costs || !Array.isArray(costs)) return 0;
        var c = costs.find(function(x) { return x.action_type === type; });
        return c ? (parseFloat(c.value) || 0) : 0;
      }
      
      var comments = getActionValue(actions, 'comment');
      var messages = getActionValue(actions, 'onsite_conversion.messaging_conversation_started');
      var checkouts = getActionValue(actions, 'initiate_checkout');
      var purchases = getActionValue(actions, 'purchase');
      var purchaseValue = getActionValueMoney(actionValues, 'purchase');
      var cpCheckout = getCostPerAction(costPerAction, 'initiate_checkout');
      var cpPurchase = getCostPerAction(costPerAction, 'purchase');
      
      var ketQua = comments + messages;
      var giaData = ketQua > 0 ? (spend / ketQua) : 0;
      var pctAds = purchaseValue > 0 ? (spend / purchaseValue) : 0;
      
      if (!cpCheckout && checkouts > 0) cpCheckout = spend / checkouts;
      if (!cpPurchase && purchases > 0) cpPurchase = spend / purchases;
      
      adsetsData[adsetId].spend += spend;
      adsetsData[adsetId].ketQua += ketQua;
      adsetsData[adsetId].checkouts += checkouts;
      adsetsData[adsetId].purchases += purchases;
      adsetsData[adsetId].purchaseValue += purchaseValue;
    } // Kết thúc for loop data
  } // Kết thúc for loop adAccountIds
  
  // Tính lại các chỉ số tổng hợp sau khi gom
  // TỐI ƯU: Dùng for thay vì forEach
  var adsetIds = Object.keys(adsetsData);
  for (var calcIdx = 0; calcIdx < adsetIds.length; calcIdx++) {
    var adsetId = adsetIds[calcIdx];
    var d = adsetsData[adsetId];
    d.giaData = d.ketQua > 0 ? (d.spend / d.ketQua) : 0;
    d.pctAds = d.purchaseValue > 0 ? (d.spend / d.purchaseValue) : 0;
    d.cpCheckout = d.checkouts > 0 ? (d.spend / d.checkouts) : 0;
    d.cpPurchase = d.purchases > 0 ? (d.spend / d.purchases) : 0;
  }
  
  Logger.log("Đã kéo dữ liệu 7 ngày cho " + Object.keys(adsetsData).length + " adset");
  return adsetsData;
}

/**
 * Lấy dữ liệu breakdown theo ngày cho tin nhắn và checkout
 * Trả về: { adsetId: { msgDates: ['2024-11-06', ...], checkoutDates: ['2024-11-06', ...] } }
 * @param {string} accessToken - Facebook Access Token
 * @param {Array<string>} adAccountIds - Danh sách Account IDs
 * @param {string} datePreset - Date preset (yesterday, today, etc.)
 * @returns {Object} Map adsetId -> { msgDates: [], checkoutDates: [] }
 */
function getDailyBreakdownData(accessToken, adAccountIds, datePreset) {
  var dailyData = {}; // { adsetId: { msgDates: [], checkoutDates: [] } }
  
  if (!accessToken || !adAccountIds || adAccountIds.length === 0) {
    Logger.log("⚠️ getDailyBreakdownData: Thiếu accessToken hoặc adAccountIds");
    return dailyData;
  }
  
  // QUAN TRỌNG: Sử dụng date_preset trực tiếp thay vì convert sang time_range
  // Facebook API sẽ tự động xử lý múi giờ của từng tài khoản quảng cáo
  // Điều này đảm bảo ngày trả về khớp với múi giờ của account (ví dụ: HongKong +8)
  var timeRangeStr = '&date_preset=' + datePreset;
  
  Logger.log("📅 Đang lấy dữ liệu breakdown theo ngày cho " + adAccountIds.length + " tài khoản (date_preset: " + datePreset + ")...");
  Logger.log("💡 Lưu ý: Facebook API sẽ trả về ngày theo múi giờ của từng tài khoản quảng cáo");
  
  // TỐI ƯU: Dùng for thay vì forEach
  for (var accIdxBD = 0; accIdxBD < adAccountIds.length; accIdxBD++) {
    var adAccountId = adAccountIds[accIdxBD];
    try {
      // Lấy dữ liệu breakdown theo ngày với các fields cần thiết
      // QUAN TRỌNG: Dùng date_preset trực tiếp để Facebook tự xử lý múi giờ
      var url = 'https://graph.facebook.com/v24.0/' + adAccountId + '/insights' +
                '?level=adset' +
                '&breakdown=day' +
                timeRangeStr +
                '&fields=adset_id,actions,date_start' +
                '&limit=1000' +
                '&access_token=' + encodeURIComponent(accessToken);
      
      var resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
      var json = JSON.parse(resp.getContentText());
      
      if (json.error) {
        Logger.log("⚠️ Lỗi lấy breakdown data cho " + adAccountId + ": " + json.error.message);
        continue; // TỐI ƯU: Dùng continue thay vì return
      }
      
      var data = Array.isArray(json.data) ? json.data : [];
      Logger.log("📊 Tài khoản " + adAccountId + ": Lấy được " + data.length + " ngày dữ liệu breakdown");
      
      // Debug: Log một vài ngày đầu tiên để kiểm tra format
      if (data.length > 0) {
        var sampleDate = data[0].date_start;
        Logger.log("📅 Mẫu ngày đầu tiên từ API: " + sampleDate + " (theo múi giờ của tài khoản)");
      }
      
      // TỐI ƯU: Dùng for thay vì forEach
      for (var dayIdx = 0; dayIdx < data.length; dayIdx++) {
        var dayData = data[dayIdx];
        var adsetId = dayData.adset_id;
        var dateStart = dayData.date_start; // Format: YYYY-MM-DD (theo múi giờ của tài khoản quảng cáo)
        
        if (!adsetId || !dateStart) continue; // TỐI ƯU: Dùng continue thay vì return
        
        if (!dailyData[adsetId]) {
          dailyData[adsetId] = { msgDates: [], checkoutDates: [], msgCounts: {}, checkoutCounts: {} };
        }
        
        // Lấy actions
        var actions = dayData.actions || [];
        
        // Tìm tin nhắn (messaging_conversation_started)
        var msgCount = 0;
        var checkoutCount = 0;
        
        if (Array.isArray(actions)) {
          // TỐI ƯU: Dùng for thay vì forEach
          for (var actIdx = 0; actIdx < actions.length; actIdx++) {
            var action = actions[actIdx];
            if (!action || !action.action_type) continue; // TỐI ƯU: Dùng continue thay vì return
            
            var actionType = String(action.action_type).toLowerCase();
            var value = parseFloat(action.value) || 0;
            
            // Kiểm tra tin nhắn (các variants) - tìm tất cả variants có thể
            var isMsg = actionType.indexOf('messaging_conversation_started') >= 0 || 
                       actionType === 'onsite_conversion.messaging_conversation_started' ||
                       actionType.indexOf('messaging_conversation') >= 0;
            
            if (isMsg && value > 0) {
              // TỐI ƯU: Dùng object lookup thay vì indexOf
              if (!dailyData[adsetId].msgDatesSet) {
                dailyData[adsetId].msgDatesSet = {};
              }
              if (!dailyData[adsetId].msgDatesSet[dateStart]) {
                dailyData[adsetId].msgDatesSet[dateStart] = true;
                dailyData[adsetId].msgDates.push(dateStart);
              }
              dailyData[adsetId].msgCounts[dateStart] = (dailyData[adsetId].msgCounts[dateStart] || 0) + value;
              msgCount += value;
            }
            
            // Kiểm tra checkout (các variants) - tìm tất cả variants có thể
            var isCheckout = actionType.indexOf('initiate_checkout') >= 0 || 
                            actionType === 'initiate_checkout' ||
                            actionType === 'offsite_conversion.fb_pixel_initiate_checkout' ||
                            actionType.indexOf('checkout') >= 0;
            
            if (isCheckout && value > 0) {
              // TỐI ƯU: Dùng object lookup thay vì indexOf
              if (!dailyData[adsetId].checkoutDatesSet) {
                dailyData[adsetId].checkoutDatesSet = {};
              }
              if (!dailyData[adsetId].checkoutDatesSet[dateStart]) {
                dailyData[adsetId].checkoutDatesSet[dateStart] = true;
                dailyData[adsetId].checkoutDates.push(dateStart);
              }
              dailyData[adsetId].checkoutCounts[dateStart] = (dailyData[adsetId].checkoutCounts[dateStart] || 0) + value;
              checkoutCount += value;
            }
          } // Kết thúc for loop actions
        } // Kết thúc if (Array.isArray(actions))
      } // Kết thúc for loop data
      
    } catch (e) {
      Logger.log("⚠️ Lỗi breakdown data cho " + adAccountId + ": " + e.message);
    }
  } // Kết thúc for loop adAccountIds
  
  // Log tổng kết
  var totalAdsets = Object.keys(dailyData).length;
  Logger.log("✅ Hoàn tất lấy breakdown data: " + totalAdsets + " adsets có dữ liệu");
  if (totalAdsets > 0) {
    var sampleAdsetId = Object.keys(dailyData)[0];
    var sampleData = dailyData[sampleAdsetId];
    Logger.log("📊 Mẫu dữ liệu adset " + sampleAdsetId + ": " + 
               sampleData.msgDates.length + " ngày có tin nhắn, " + 
               sampleData.checkoutDates.length + " ngày có checkout");
  }
  
  return dailyData;
}