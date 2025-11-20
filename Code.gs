// File: Mã.gs (Code.gs)
// === ĐÃ SỬA LỖI: Lỗi cú pháp (SyntaxError) 's' ===

// --- THÔNG SỐ CỐ ĐỊNH ---
var SHEET_NAME_DATA = "Data_FB"; 

/**
 * ==================================================================
 * HÀM "MASTER" (Đã đồng bộ)
 * ==================================================================
 */
function runAutomation() {
  var settings, logicMap, botToken, chatId, accessToken, adAccountIds, datePreset, delayMs;
  
  try {
    // 1. Tải 2 bộ cài đặt
    settings = getSettingsSafe_(); // Tải key, token từ "CaiDat" (an toàn)
    
    // KIỂM TRA TRẠNG THÁI DISABLE_ALL TRƯỚC
    // QUAN TRỌNG: Nếu disable_all = true, chỉ chạy những account|prefix được enable cụ thể
    // Nếu disable_all = false hoặc không có, chạy tất cả (trừ những cái bị disable cụ thể)
    try {
      var props = PropertiesService.getScriptProperties();
      var disableAll = props.getProperty('AUTOMATION_DISABLE_ALL');
      if (disableAll === 'true') {
        Logger.log("⚠️ Automation đã bị tắt tất cả (disable_all = true). Chỉ chạy những account|prefix được enable cụ thể.");
        // KHÔNG return ngay, vẫn tiếp tục nhưng sẽ kiểm tra enable cụ thể trong logic
      }
    } catch (eAuto) {
      Logger.log("⚠️ Lỗi kiểm tra trạng thái automation: " + eAuto.message);
    }
    
    // QUAN TRỌNG: LUÔN kiểm tra khung giờ cho phép (kể cả chạy thủ công)
    // Nếu muốn chạy ngoài giờ, dùng testRunAutomation()
    var isWithinWindow = isWithinWindow_(settings);
    if (!isWithinWindow) {
      var now = new Date();
      var tz = Session.getScriptTimeZone() || 'Asia/Ho_Chi_Minh';
      var hour = parseInt(Utilities.formatDate(now, tz, 'H'), 10);
      var minute = parseInt(Utilities.formatDate(now, tz, 'm'), 10);
      var startH = parseInt(settings['RUN_WINDOW_START_HOUR'] || '6', 10);
      var endH = parseInt(settings['RUN_WINDOW_END_HOUR'] || '23', 10);
      var currentTime = hour + ":" + (minute < 10 ? "0" + minute : minute);
      var errorMsg = "⚠️ KHÔNG ĐƯỢC PHÉP CHẠY NGOÀI KHUNG GIỜ: Hiện tại " + currentTime + " (Khung cho phép: " + startH + ":00 - " + endH + ":00).\n\nĐể chạy ngoài giờ, vui lòng dùng hàm testRunAutomation() thay vì runAutomation().";
      Logger.log(errorMsg);
      // Gửi cảnh báo qua Telegram nếu có
      botToken = settings["TELEGRAM_BOT_TOKEN"];
      chatId = settings["TELEGRAM_CHAT_ID"];
      if (botToken && chatId) {
        guiThongBaoTelegram(errorMsg, botToken, chatId);
      }
      return;
    }
    logicMap = buildLogicMap();   // Tải ma trận logic từ "LogicRules"
    
    // 2. Gán biến hệ thống
    botToken = settings["TELEGRAM_BOT_TOKEN"];
    chatId = settings["TELEGRAM_CHAT_ID"];
    accessToken = settings["ACCESS_TOKEN"];
    adAccountIds = settings["AD_ACCOUNT_IDS"]; 
    datePreset = settings["DATA_DATE_PRESET"];
    delayMs = settings["DELAY_KHI_TAT_BATCH"]; // <-- LẤY DELAY MỚI
    
    // 3. Kiểm tra cài đặt
    if (!accessToken || !adAccountIds || adAccountIds.length === 0 || !botToken || !chatId || !datePreset) {
      var msg = "⚠️ Lỗi cấu hình: Thiếu Token/Ad IDs/Bot/Chat ID/datePreset trong CaiDat";
      guiThongBaoTelegram(msg, botToken, chatId); 
      return;
    }

    // ----- BƯỚC 1: KÉO DỮ LIỆU MỚI -----
    pullFacebookData(accessToken, adAccountIds, datePreset); 
    
    // ----- BƯỚC 2: CHẠY LOGIC CẮT LỖ -----
    kiemTraVaTatQuangCao(logicMap, accessToken, botToken, chatId, delayMs); 
    
    resetTokenAlertCount_(); // chạy OK → reset cảnh báo token
    
  } catch (e) {
    var errorMsg = "LỖI SCRIPT NGHIÊM TRỌNG: " + e.message + "\n" + e.stack;
    if (!botToken || !chatId) { // Cố gắng gửi lỗi ngay cả khi cài đặt bị lỗi
       try { 
         if (!settings) settings = layCaiDatHeThong();
         botToken = settings["TELEGRAM_BOT_TOKEN"];
         chatId = settings["TELEGRAM_CHAT_ID"];
       } catch (e2) {} 
    }
    guiThongBaoTelegram(errorMsg, botToken, chatId);
    increaseTokenAlertCount_(0); // không tăng nhưng đảm bảo biến tồn tại
  }

  // Nếu cảnh báo token ≥ 3 → dừng triggers
  try {
    var c = getTokenAlertCount_();
    if (c >= 3) {
      stopAutomationTriggers_();
      if (botToken && chatId) guiThongBaoTelegram("⛔ Dừng tự động: Token lỗi quá 3 lần liên tiếp" , botToken, chatId);
    }
  } catch (_e) {}
}

/**
 * ==================================================================
 * HÀM TEST - CHẠY BẤT CỨ LÚC NÀO (Bỏ qua khung giờ)
 * 
 * LƯU Ý: Hàm này BỎ QUA kiểm tra khung giờ (6h-23h)
 * Sử dụng khi muốn test hoặc chạy ngoài giờ cho phép
 * 
 * Để chạy trong giờ cho phép, dùng runAutomation()
 * ==================================================================
 */
function testRunAutomation() {
  Logger.log("--- BẮT ĐẦU TEST CHẠY AUTOMATION (Bỏ qua khung giờ) ---");
  var settings, logicMap, botToken, chatId, accessToken, adAccountIds, datePreset, delayMs;
  
  try {
    // 1. Tải 2 bộ cài đặt
    settings = getSettingsSafe_();
    // LƯU Ý: testRunAutomation BỎ QUA kiểm tra khung giờ, có thể chạy bất kỳ lúc nào
    logicMap = buildLogicMap();
    
    // 2. Gán biến hệ thống
    botToken = settings["TELEGRAM_BOT_TOKEN"];
    chatId = settings["TELEGRAM_CHAT_ID"];
    accessToken = settings["ACCESS_TOKEN"];
    adAccountIds = settings["AD_ACCOUNT_IDS"]; 
    datePreset = settings["DATA_DATE_PRESET"];
    delayMs = settings["DELAY_KHI_TAT_BATCH"];
    
    // 3. Kiểm tra cài đặt
    if (!accessToken || !adAccountIds || adAccountIds.length === 0 || !datePreset) {
      Logger.log("LỖI: Không tìm thấy ACCESS_TOKEN, AD_ACCOUNT_IDS, hoặc DATA_DATE_PRESET trong tab CaiDat.");
      Logger.log("AD_ACCOUNT_IDS: " + (adAccountIds ? adAccountIds.length + " tài khoản" : "null"));
      return;
    }

    // ----- BƯỚC 1: KÉO DỮ LIỆU MỚI -----
    pullFacebookData(accessToken, adAccountIds, datePreset); 
    kiemTraVaTatQuangCao(logicMap, accessToken, botToken, chatId, delayMs); 
  } catch (e) {
    var errorMsg = "LỖI TEST: " + e.message;
    Logger.log(errorMsg);
    if (botToken && chatId) guiThongBaoTelegram(errorMsg, botToken, chatId);
  }
}

/**
 * ==================================================================
 * HÀM TEST (Đã đồng bộ)
 * ==================================================================
 */
function testPullData() {
  var settings, botToken, chatId, accessToken, adAccountIds, datePreset;
  try {
    settings = getSettingsSafe_();
    accessToken = settings["ACCESS_TOKEN"];
    adAccountIds = settings["AD_ACCOUNT_IDS"]; 
    datePreset = settings["DATA_DATE_PRESET"]; 
    botToken = settings["TELEGRAM_BOT_TOKEN"];
    chatId = settings["TELEGRAM_CHAT_ID"];
        
    if (!accessToken || !adAccountIds || adAccountIds.length === 0 || !datePreset) {
      Logger.log("LỖI: Thiếu cấu hình trong CaiDat");
      return;
    }
        
    pullFacebookData(accessToken, adAccountIds, datePreset); 

  } catch (e) {
    var errorMsg = "LỖI TEST PULL: " + e.message;
    Logger.log(errorMsg);
    if (botToken && chatId) guiThongBaoTelegram(errorMsg, botToken, chatId);
  }
}


/**
 * ==================================================================
 * HÀM CHÍNH: KIỂM TRA VÀ TẮT QUẢNG CÁO
 * === ĐÃ SỬA LỖI: Lỗi cú pháp 's' ===
 * ==================================================================
 */
function kiemTraVaTatQuangCao(logicMap, accessToken, botToken, chatId, delayMs) { 
  var thongBaoLoi = "";
  var canhBaoThieuDieuKien = []; // Lưu các cảnh báo về thiếu điều kiện trong LogicRules
  var adsetsToPause = {}; // { adsetId: {adId, adName, adsetName, campaignName, reason, prefix, accountId} }
  var adsetsToResume = {}; // { adsetId: {adId, adName, adsetName, campaignName, reason, prefix} } - cho logic bật lại
  var logMessages = []; 
  var adsetCount = 0;
  var resumeCount = 0;
  
  try {
    // 1. Kiểm tra an toàn (Nếu chạy trực tiếp)
    if (!logicMap || !accessToken || !botToken || !chatId) {
      var settings = layCaiDatHeThong();
      logicMap = buildLogicMap(); 
      accessToken = settings["ACCESS_TOKEN"]; 
      botToken = settings["TELEGRAM_BOT_TOKEN"];
      chatId = settings["TELEGRAM_CHAT_ID"];
      delayMs = settings["DELAY_KHI_TAT_BATCH"];
      if (!accessToken) throw new Error("Tự tải thất bại: Không tìm thấy ACCESS_TOKEN.");
    }

    // 1.5. Lấy dữ liệu breakdown theo ngày để kiểm tra tin nhắn và checkout cùng ngày
    var dailyBreakdownData = {}; // { adsetId: { msgDates: [], checkoutDates: [] } }
    try {
      var settings = layCaiDatHeThong();
      var adAccountIds = settings["AD_ACCOUNT_IDS"];
      var datePreset = settings["DATA_DATE_PRESET"] || "yesterday";
      if (adAccountIds && accessToken) {
        dailyBreakdownData = getDailyBreakdownData(accessToken, adAccountIds, datePreset);
      }
    } catch (eDaily) {
      Logger.log("⚠️ Lỗi khi lấy dữ liệu breakdown theo ngày: " + eDaily.message);
      // Tiếp tục chạy logic bình thường nếu không lấy được breakdown data
    }
    
    // Helper function: Kiểm tra xem tin nhắn và checkout có cùng ngày không
    // QUAN TRỌNG: Ngày được so sánh theo format YYYY-MM-DD từ Facebook API (theo múi giờ của tài khoản)
    function hasMatchingDates(adsetId, logDetails) {
      if (!dailyBreakdownData[adsetId]) {
        if (logDetails) {
          Logger.log("⚠️ hasMatchingDates: Không có dữ liệu breakdown cho adset " + adsetId);
        }
        return false;
      }
      var msgDates = dailyBreakdownData[adsetId].msgDates || [];
      var checkoutDates = dailyBreakdownData[adsetId].checkoutDates || [];
      
      if (logDetails && (msgDates.length > 0 || checkoutDates.length > 0)) {
        Logger.log("🔍 hasMatchingDates cho adset " + adsetId + ": msgDates=" + JSON.stringify(msgDates) + ", checkoutDates=" + JSON.stringify(checkoutDates));
      }
      
      // Tối ưu: dùng object lookup thay vì indexOf
      var checkoutSet = {};
      for (var cIdx = 0; cIdx < checkoutDates.length; cIdx++) {
        checkoutSet[checkoutDates[cIdx]] = true;
      }
      
      for (var i = 0; i < msgDates.length; i++) {
        if (checkoutSet[msgDates[i]]) {
          if (logDetails) {
            Logger.log("✅ hasMatchingDates: Tìm thấy ngày khớp " + msgDates[i] + " cho adset " + adsetId);
          }
          return true;
        }
      }
      
      return false;
    }

    // 2. Lấy dữ liệu
    var dataSheet = getSpreadsheet_().getSheetByName(SHEET_NAME_DATA);
    var data = dataSheet.getDataRange().getValues();
    
    data.shift(); // Bỏ qua hàng 1 (Status)
    var headers = data.shift(); // Hàng 2 (Headers)
    
    var colMap = {};
    headers.forEach(function(h, i) { if (h) { colMap[h.trim()] = i; } });
    
    // (Đồng bộ hóa thứ tự cột (colMap) với file "BẢN VÁ" của bạn)
    var accountIdCol = colMap['Account ID'];             // B
    var adIdCol = colMap['Ad Id'];                       // F
    var adsetIdCol = colMap['Adset Id'];                 // D
    var adNameCol = colMap['Ad name'];                   // G
    var adsetNameCol = colMap['Adset name'];             // E
    var adsetStatusCol = colMap['Adset Effective Status'];// H
    var campaignNameCol = colMap['Campaign name'];       // C
    var spendCol = colMap['Amount spent'];               // I
    var msgCol = colMap['Messaging conversations started'];// W
    var commentCol = colMap['Post comments'];            // V
    var leadsCol = colMap['Checkouts Initiated'];        // T
    var cplCol = colMap['Cost per checkout initiated'];  // P
    var purchaseCol = colMap['Purchases'];               // U
    var cpaCol = colMap['Cost per purchase'];            // Q
    var freqCol = colMap['Frequency'];                   // L
    var ketQuaCol = colMap['Kết Quả']; // New column for Kết Quả

    if (adsetIdCol === undefined || adNameCol === undefined || adsetStatusCol === undefined || accountIdCol === undefined) { 
      throw new Error("Thiếu cột bắt buộc (Adset Id, Ad name, Adset status, Account ID...) trong trang " + SHEET_NAME_DATA);
    }
    
    // Tham số áp dụng cho GĐ1
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
    Logger.log("📋 Prefix được sử dụng cho logic kiểm tra: " + ALLOWED_PREFIXES.join(", "));
    var TARGET_STATUS = 'ACTIVE';
    
    // TỐI ƯU: Cache prefix và logic lookup để tránh gọi hàm lặp lại
    var prefixCache = {}; // { campaignName: prefix }
    var logicCache = {}; // { accountId|campaignName: logic }
    var matchingDatesCache = {}; // { adsetId: boolean }
    var enabledCache = {}; // { accountId|prefix: boolean } - Cache trạng thái enable/disable
    
    // Pre-cache matching dates cho tất cả adsets
    Object.keys(dailyBreakdownData).forEach(function(adsetId) {
      matchingDatesCache[adsetId] = hasMatchingDates(adsetId, false);
    });
    
    // TỐI ƯU: Batch load PropertiesService cho cooldown checks
    var props = PropertiesService.getScriptProperties();
    var cooldownCache = {}; // { adsetId: { shouldSkip: boolean, lastToggle: number } }
    var adsetIdsForCooldown = []; // Thu thập tất cả adsetIds cần check cooldown
    
    // 3. Lặp qua từng hàng - TỐI ƯU: dùng for thay vì forEach để nhanh hơn
    var rowCount = data.length;
    for (var rowIdx = 0; rowIdx < rowCount; rowIdx++) {
      var row = data[rowIdx];
      var accountId = row[accountIdCol];
      var campaignName = row[campaignNameCol];
      var adId = row[adIdCol];
      var adsetId = row[adsetIdCol]; 
      var adName = row[adNameCol];
      var adsetName = row[adsetNameCol];
      var adsetStatus = row[adsetStatusCol]; 
      
      if (!adId || !campaignName || !adsetId || !accountId) continue; 

      // TỐI ƯU: Cache prefix lookup
      var prefix = prefixCache[campaignName];
      if (!prefix) {
        prefix = getPrefixTuTen(campaignName);
        prefixCache[campaignName] = prefix;
      }

      // TỐI ƯU: Cache logic lookup
      var cacheKey = accountId + "|" + campaignName;
      var logic = logicCache[cacheKey];
      if (!logic) {
        logic = getLogicForRow(logicMap, accountId, campaignName);
        if (logic) {
          logicCache[cacheKey] = logic;
        }
      }
      if (!logic) {
        // Debug log cho các trường hợp không tìm thấy logic (đặc biệt với prefix LAKVDH)
        if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0)) {
          Logger.log("⚠️ DEBUG: Không tìm thấy logic cho Account: " + accountId + ", Prefix: " + prefix + ", Campaign: " + campaignName);
          Logger.log("   Đã thử: act_" + accountId + "|" + prefix + ", " + accountId + "|" + prefix + ", DEFAULT|" + prefix + ", DEFAULT|DEFAULT");
        }
        thongBaoLoi += "\nLỖI LOGIC: Không tìm thấy quy tắc (kể cả DEFAULT) cho TK " + accountId + ", Prefix " + prefix;
        continue;
      }
      
      // Debug log khi tìm thấy logic (đặc biệt với prefix LAKVDH)
      if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0)) {
        Logger.log("✅ DEBUG: Tìm thấy logic cho Account: " + accountId + ", Prefix: " + prefix + ", Campaign: " + campaignName);
        // Log thêm thông tin về logic được tìm thấy
        if (logic) {
          var logicKeys = Object.keys(logic);
          Logger.log("   Logic keys: " + logicKeys.slice(0, 10).join(", ") + (logicKeys.length > 10 ? "..." : ""));
          Logger.log("   SL_GIAI_DOAN_1_SPEND: " + (logic["SL_GIAI_DOAN_1_SPEND"] || logic["SL_1_SPEND"] || "N/A"));
          Logger.log("   SL_GIAI_DOAN_1_DATA: " + (logic["SL_GIAI_DOAN_1_DATA"] || logic["SL_1_DATA"] || "N/A"));
        }
      }
      
      // QUAN TRỌNG: Kiểm tra trạng thái enable/disable cho account|prefix
      // Logic:
      // 1. Nếu DISABLE_ALL = true: CHỈ chạy những account|prefix được enable cụ thể (có flag "true")
      // 2. Nếu DISABLE_ALL = false hoặc không có: Chạy tất cả TRỪ những cái bị disable cụ thể (có flag "false")
      // TỐI ƯU: Cache trạng thái enable/disable để tránh gọi PropertiesService nhiều lần
      var enabledCacheKey = accountId + "|" + prefix;
      var isEnabled = enabledCache[enabledCacheKey];
      if (isEnabled === undefined) {
        // Chưa có trong cache, kiểm tra từ PropertiesService
        try {
          var props = PropertiesService.getScriptProperties();
          var disableAll = props.getProperty('AUTOMATION_DISABLE_ALL');
          var isDisableAll = (disableAll === 'true');
          
          if (isDisableAll) {
            // Chế độ disable_all: CHỈ chạy những cái được enable cụ thể
            // Kiểm tra xem có flag "true" cho account|prefix này không
            var normalizedAccountId = String(accountId).trim();
            if (normalizedAccountId.indexOf('act_') === 0) {
              normalizedAccountId = normalizedAccountId.substring(4);
            }
            var normalizedPrefix = String(prefix).trim().toUpperCase();
            var allProps = props.getProperties();
            var prefixKey = "AUTOMATION_ENABLED_" + normalizedAccountId + "|";
            
            // Tìm tất cả keys có cùng accountId và match prefix
            var matchingKeys = [];
            for (var key in allProps) {
              if (key.indexOf(prefixKey) === 0) {
                var keyPrefix = key.substring(prefixKey.length);
                // Kiểm tra match linh hoạt
                if (normalizedPrefix.indexOf(keyPrefix) === 0 || keyPrefix.indexOf(normalizedPrefix) === 0) {
                  matchingKeys.push({ key: key, keyPrefix: keyPrefix, value: allProps[key] });
                }
              }
            }
            
            // Ưu tiên prefix dài nhất
            if (matchingKeys.length > 0) {
              matchingKeys.sort(function(a, b) {
                return b.keyPrefix.length - a.keyPrefix.length;
              });
              var firstMatch = matchingKeys[0];
              isEnabled = (firstMatch.value === "true"); // CHỈ enabled nếu value = "true"
            } else {
              isEnabled = false; // Không có flag → disabled
            }
          } else {
            // Chế độ bình thường: Chạy tất cả TRỪ những cái bị disable cụ thể
            if (typeof isAutomationEnabled === 'function') {
              isEnabled = isAutomationEnabled(accountId, prefix);
            } else {
              isEnabled = true; // Mặc định enabled nếu hàm không tồn tại
            }
          }
          enabledCache[enabledCacheKey] = isEnabled;
        } catch (eEnable) {
          Logger.log("⚠️ Lỗi kiểm tra enable/disable: " + eEnable.message);
          // Mặc định: nếu disable_all thì disabled, nếu không thì enabled
          var props = PropertiesService.getScriptProperties();
          var disableAll = props.getProperty('AUTOMATION_DISABLE_ALL');
          isEnabled = (disableAll !== 'true'); // Nếu disable_all thì disabled, ngược lại enabled
          enabledCache[enabledCacheKey] = isEnabled;
        }
      }
      
      if (!isEnabled) {
        // Debug log khi bị disable
        Logger.log("⛔ SKIP: Automation đã bị tắt cho Account: " + accountId + ", Prefix: " + prefix + ", Campaign: " + campaignName);
        continue; // Bỏ qua logic cho account|prefix này
      }
      
      // Đọc các chỉ số (dùng Kết Quả nếu có, fallback = V+W)
      var spend     = chuyenDoiTienTe(row[spendCol]);
      var ketQua    = (ketQuaCol !== undefined) ? chuyenDoiThapPhan(row[ketQuaCol]) :
                      (chuyenDoiThapPhan(row[msgCol]) + chuyenDoiThapPhan(row[commentCol]));
      var leads     = chuyenDoiThapPhan(row[leadsCol]);
      var cpl       = chuyenDoiThapPhan(row[cplCol]);
      var purchases = chuyenDoiThapPhan(row[purchaseCol]);
      var cpa       = chuyenDoiThapPhan(row[cpaCol]);
      var frequency = chuyenDoiThapPhan(row[freqCol]);
      
      // Tính Giá DATA (nếu có Kết Quả > 0)
      var giaData = (ketQua > 0) ? (spend / ketQua) : 0;
      var giaDataCol = colMap['Giá DATA'];
      if (giaDataCol !== undefined && row[giaDataCol] != null && row[giaDataCol] !== "") {
        giaData = chuyenDoiThapPhan(row[giaDataCol]);
      }
      
      // Kiểm tra dữ liệu có hợp lệ không
      var impressions = chuyenDoiThapPhan(row[colMap['Impressions']] || 0);
      var hasValidData = impressions > 0 || spend > 0; // Có dữ liệu từ Facebook
     
      var lyDoTat = ""; 

      // 4.1) Giai đoạn 1 theo yêu cầu: dùng rule theo account+prefix (từ getLogicForRow)
      if (adsetStatus === TARGET_STATUS && hasValidData) {
        try {
          // Helper: lấy số với các biến thể key và fallback DEFAULT|DEFAULT
          function pickKey(obj, keys) {
            for (var i = 0; i < keys.length; i++) {
              if (obj && obj[keys[i]] != null && obj[keys[i]] !== "") return obj[keys[i]];
            }
            return undefined;
          }
          var defaultLogic = (logicMap && logicMap["DEFAULT|DEFAULT"]) || {};
          var rawSpend = pickKey(logic, ["SL_GIAI_DOAN_1_SPEND", "SL_1_SPEND"]); if (rawSpend === undefined) rawSpend = pickKey(defaultLogic, ["SL_GIAI_DOAN_1_SPEND", "SL_1_SPEND"]);
          var rawData  = pickKey(logic, ["SL_GIAI_DOAN_1_DATA", "SL_1_DATA"]);   if (rawData === undefined)  rawData  = pickKey(defaultLogic, ["SL_GIAI_DOAN_1_DATA", "SL_1_DATA"]);
          // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
          var SL_1_SPEND = chuyenDoiTienTe(rawSpend);
          var SL_1_DATA  = chuyenDoiThapPhan(rawData);
          
          // QUAN TRỌNG: Không dùng fallback mặc định, cảnh báo nếu thiếu điều kiện
          // TỐI ƯU: Dùng cache prefix
          var prefix = prefixCache[campaignName] || getPrefixTuTen(campaignName);
          if (!prefixCache[campaignName]) prefixCache[campaignName] = prefix;
          if (rawSpend === undefined || rawSpend === null || rawSpend === "" || !SL_1_SPEND || isNaN(SL_1_SPEND)) {
            var warningKey = accountId + "|GĐ1|SL_1_SPEND|" + prefix;
            if (canhBaoThieuDieuKien.indexOf(warningKey) === -1) {
              canhBaoThieuDieuKien.push(warningKey);
              Logger.log("⚠️ CẢNH BÁO: Tài khoản " + accountId + "|Prefix " + prefix + " ở GĐ1 không có điều kiện SL_GIAI_DOAN_1_SPEND");
            }
            return; // Không chạy logic nếu thiếu điều kiện
          }
          if (rawData === undefined || rawData === null || rawData === "" || SL_1_DATA === undefined || SL_1_DATA === null || isNaN(SL_1_DATA)) {
            var warningKey = accountId + "|GĐ1|SL_1_DATA|" + prefix;
            if (canhBaoThieuDieuKien.indexOf(warningKey) === -1) {
              canhBaoThieuDieuKien.push(warningKey);
              Logger.log("⚠️ CẢNH BÁO: Tài khoản " + accountId + "|Prefix " + prefix + " ở GĐ1 không có điều kiện SL_GIAI_DOAN_1_DATA");
            }
            return; // Không chạy logic nếu thiếu điều kiện
          }
          
          // Kiểm tra điều kiện tắt: Spend >= ngưỡng VÀ Kết Quả <= ngưỡng
          // NGOẠI LỆ: Nếu có checkout tốt VÀ tin nhắn và checkout cùng ngày → GIỮ LẠI
          // QUAN TRỌNG: Sử dụng > thay vì >= cho spend để tránh tắt khi spend = ngưỡng chính xác
          // Logic 1: spend > SL_1_SPEND VÀ ketQua <= SL_1_DATA (ketQua = 0 khi không có kết quả)
          var shouldPause = (spend > SL_1_SPEND && ketQua <= SL_1_DATA);
          
          // Debug log cho các trường hợp đặc biệt
          if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0)) {
            Logger.log("🔍 DEBUG GĐ1 - Account: " + accountId + ", Prefix: " + prefix + ", Campaign: " + campaignName);
            Logger.log("   AdsetId: " + adsetId + ", AdId: " + adId);
            Logger.log("   spend: " + spend + " (type: " + typeof spend + "), SL_1_SPEND: " + SL_1_SPEND + " (type: " + typeof SL_1_SPEND + ")");
            Logger.log("   ketQua: " + ketQua + " (type: " + typeof ketQua + "), SL_1_DATA: " + SL_1_DATA + " (type: " + typeof SL_1_DATA + ")");
            Logger.log("   Comparison: spend > SL_1_SPEND = " + (spend > SL_1_SPEND) + " (" + spend + " > " + SL_1_SPEND + ")");
            Logger.log("   Comparison: ketQua <= SL_1_DATA = " + (ketQua <= SL_1_DATA) + " (" + ketQua + " <= " + SL_1_DATA + ")");
            Logger.log("   shouldPause: " + shouldPause);
            Logger.log("   rawSpend từ logic: " + rawSpend + ", rawData từ logic: " + rawData);
          }
          
          if (shouldPause) {
            // Kiểm tra ngoại lệ: Có checkout tốt và cùng ngày với tin nhắn
            var checkouts = leads || 0;
            var cpCheckout = cpl || 0;
            if (checkouts > 0 && cpCheckout === 0) {
              cpCheckout = spend / checkouts;
            }
            
            // Logic ngoại lệ: CHỈ áp dụng khi checkout và tin nhắn CÙNG NGÀY
            // Điều kiện: 1) Cùng ngày VÀ 2) Có checkout > 0 VÀ 3) CP Checkout <= MAX_CP_CHECKOUT
            var rawMaxCpCheckout = pickKey(logic, ["MAX_CP_CHECKOUT", "MAX_CPL"]); 
            if (rawMaxCpCheckout === undefined || rawMaxCpCheckout === null || rawMaxCpCheckout === "") {
              rawMaxCpCheckout = pickKey(defaultLogic, ["MAX_CP_CHECKOUT", "MAX_CPL"]);
            }
            var MAX_CP_CHECKOUT = chuyenDoiTienTe(rawMaxCpCheckout);
            
            var coCheckoutTot = false;
            // TỐI ƯU: Dùng cache thay vì gọi hàm
            var coCungNgay = matchingDatesCache[adsetId] || false;
            
            // QUAN TRỌNG: Kiểm tra cùng ngày TRƯỚC - nếu không cùng ngày → KHÔNG áp dụng ngoại lệ
            if (coCungNgay && checkouts > 0) {
              // CHỈ áp dụng ngoại lệ khi: cùng ngày VÀ có MAX_CP_CHECKOUT được cấu hình VÀ CP Checkout <= ngưỡng
              if (rawMaxCpCheckout !== undefined && rawMaxCpCheckout !== null && rawMaxCpCheckout !== "" && MAX_CP_CHECKOUT > 0 && MAX_CP_CHECKOUT < 999999) {
                if (cpCheckout <= MAX_CP_CHECKOUT && cpCheckout > 0) {
                  coCheckoutTot = true;
                  shouldPause = false;
                  
                  // Debug log cho ngoại lệ
                  if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0)) {
                    Logger.log("   ⚠️ NGOẠI LỆ: Có checkout tốt và cùng ngày, KHÔNG TẮT. checkouts: " + checkouts + ", cpCheckout: " + cpCheckout + ", MAX_CP_CHECKOUT: " + MAX_CP_CHECKOUT + ", coCungNgay: " + coCungNgay);
                  }
                }
              }
            } else {
              // Debug log khi không có ngoại lệ
              if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0) && shouldPause) {
                Logger.log("   🔍 Kiểm tra ngoại lệ: coCungNgay=" + (coCungNgay || false) + ", checkouts=" + (checkouts || 0) + ", cpCheckout=" + (cpCheckout || 0));
              }
            }
          }
          
          if (shouldPause) {
            lyDoTat = "GĐ1: Spend > " + SL_1_SPEND + " & Kết Quả ≤ " + SL_1_DATA;
            
            // Debug log khi quyết định tắt
            if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0)) {
              Logger.log("   ✅ QUYẾT ĐỊNH TẮT: " + lyDoTat + " (AdsetId: " + adsetId + ")");
            }
          } else {
            // Debug log khi KHÔNG tắt (chỉ log nếu đã có shouldPause ban đầu là true)
            if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0)) {
              var originalShouldPause = (spend > SL_1_SPEND && ketQua <= SL_1_DATA);
              if (originalShouldPause) {
                Logger.log("   ❌ KHÔNG TẮT (sau khi kiểm tra ngoại lệ): shouldPause=" + shouldPause + ", coCheckoutTot=" + (coCheckoutTot || false));
              } else {
                Logger.log("   ❌ KHÔNG TẮT: Không đủ điều kiện. spend=" + spend + " > " + SL_1_SPEND + " = " + (spend > SL_1_SPEND) + ", ketQua=" + ketQua + " <= " + SL_1_DATA + " = " + (ketQua <= SL_1_DATA));
              }
            }
          }
        } catch (eCfg) {
          thongBaoLoi += "\nLỖI LOGIC (GĐ1): Không thể đọc SL_1 cho rule của TK '" + accountId + "' với campaign '" + campaignName + "'.";
        }
      }

      // 4.2) Giai đoạn 2 (Cắt lỗ 2): Nếu số tiền chi tiêu > ngưỡng VÀ giá DATA > ngưỡng thì tắt
      // NGOẠI LỆ: Nếu có Checkouts Initiated tốt (>= MIN_CHECKOUTS) VÀ Cost per checkout initiated tốt (<= MAX_CP_CHECKOUT) thì GIỮ LẠI
      if (!lyDoTat && adsetStatus === TARGET_STATUS && hasValidData) {
        try {
          function pickKey(obj, keys) {
            for (var i = 0; i < keys.length; i++) {
              if (obj && obj[keys[i]] != null && obj[keys[i]] !== "") return obj[keys[i]];
            }
            return undefined;
          }
          var defaultLogic = (logicMap && logicMap["DEFAULT|DEFAULT"]) || {};
          var rawSpend2 = pickKey(logic, ["SL_GIAI_DOAN_2_SPEND", "SL_2_SPEND"]); if (rawSpend2 === undefined) rawSpend2 = pickKey(defaultLogic, ["SL_GIAI_DOAN_2_SPEND", "SL_2_SPEND"]);
          var rawGiaData2 = pickKey(logic, ["SL_GIAI_DOAN_2_GIA_DATA", "SL_2_GIA_DATA"]); if (rawGiaData2 === undefined) rawGiaData2 = pickKey(defaultLogic, ["SL_GIAI_DOAN_2_GIA_DATA", "SL_2_GIA_DATA"]);
          var rawMaxCpCheckout = pickKey(logic, ["MAX_CP_CHECKOUT", "MAX_CPL"]); 
          if (rawMaxCpCheckout === undefined || rawMaxCpCheckout === null || rawMaxCpCheckout === "") {
            rawMaxCpCheckout = pickKey(defaultLogic, ["MAX_CP_CHECKOUT", "MAX_CPL"]);
          }
          var SL_2_SPEND = chuyenDoiTienTe(rawSpend2);
          var SL_2_GIA_DATA = chuyenDoiTienTe(rawGiaData2);
          var MAX_CP_CHECKOUT = chuyenDoiTienTe(rawMaxCpCheckout);
          
          // QUAN TRỌNG: Không dùng fallback mặc định, cảnh báo nếu thiếu điều kiện
          // TỐI ƯU: Dùng cache prefix
          var prefix = prefixCache[campaignName] || getPrefixTuTen(campaignName);
          if (!prefixCache[campaignName]) prefixCache[campaignName] = prefix;
          if (rawSpend2 === undefined || rawSpend2 === null || rawSpend2 === "" || !SL_2_SPEND || isNaN(SL_2_SPEND)) {
            var warningKey = accountId + "|GĐ2|SL_2_SPEND|" + prefix;
            if (canhBaoThieuDieuKien.indexOf(warningKey) === -1) {
              canhBaoThieuDieuKien.push(warningKey);
              Logger.log("⚠️ CẢNH BÁO: Tài khoản " + accountId + "|Prefix " + prefix + " ở GĐ2 không có điều kiện SL_GIAI_DOAN_2_SPEND");
            }
            return; // Không chạy logic nếu thiếu điều kiện
          }
          if (rawGiaData2 === undefined || rawGiaData2 === null || rawGiaData2 === "" || !SL_2_GIA_DATA || isNaN(SL_2_GIA_DATA)) {
            var warningKey = accountId + "|GĐ2|SL_2_GIA_DATA|" + prefix;
            if (canhBaoThieuDieuKien.indexOf(warningKey) === -1) {
              canhBaoThieuDieuKien.push(warningKey);
              Logger.log("⚠️ CẢNH BÁO: Tài khoản " + accountId + "|Prefix " + prefix + " ở GĐ2 không có điều kiện SL_GIAI_DOAN_2_GIA_DATA");
            }
            return; // Không chạy logic nếu thiếu điều kiện
          }
          
          // Đọc dữ liệu checkout từ row
          var checkouts = leads || 0; // Checkouts Initiated
          var cpCheckout = cpl || 0; // Cost per checkout initiated
          if (checkouts > 0 && cpCheckout === 0) {
            // Tính lại nếu chưa có
            cpCheckout = spend / checkouts;
          }
          
          // Kiểm tra điều kiện tắt: Spend > ngưỡng VÀ Giá DATA > ngưỡng
          // QUAN TRỌNG: Logic 2: spend > SL_2_SPEND VÀ giaData > SL_2_GIA_DATA
          var shouldPauseG2 = (spend > SL_2_SPEND && giaData > SL_2_GIA_DATA);
          
          // Debug log cho các trường hợp đặc biệt
          if (prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0)) {
            Logger.log("🔍 DEBUG GĐ2 - Account: " + accountId + ", Prefix: " + prefix + ", Campaign: " + campaignName);
            Logger.log("   spend: " + spend + ", SL_2_SPEND: " + SL_2_SPEND + ", giaData: " + giaData + ", SL_2_GIA_DATA: " + SL_2_GIA_DATA);
            Logger.log("   shouldPauseG2: " + shouldPauseG2 + " (spend > SL_2_SPEND: " + (spend > SL_2_SPEND) + ", giaData > SL_2_GIA_DATA: " + (giaData > SL_2_GIA_DATA) + ")");
          }
          
          if (shouldPauseG2) {
            // NGOẠI LỆ: Kiểm tra nếu có checkout tốt VÀ cùng ngày với tin nhắn thì GIỮ LẠI
            // QUAN TRỌNG: Nếu CP Checkout tốt (≤ MAX_CP_CHECKOUT) và cùng ngày, thì BỎ QUA điều kiện Giá DATA
            // Ví dụ: Giá DATA = 90,000 (vượt ngưỡng 40,000) nhưng CP Checkout = 90,000 (≤ 150,000) → GIỮ LẠI
            var coCheckoutTot = false;
            // TỐI ƯU: Dùng cache thay vì gọi hàm
            var coCungNgay = matchingDatesCache[adsetId] || false;
            
            // QUAN TRỌNG: Kiểm tra cùng ngày TRƯỚC - nếu không cùng ngày → KHÔNG áp dụng ngoại lệ
            if (coCungNgay && checkouts > 0) {
              // CHỈ áp dụng ngoại lệ khi: cùng ngày VÀ có MAX_CP_CHECKOUT được cấu hình VÀ CP Checkout <= ngưỡng
              if (rawMaxCpCheckout !== undefined && rawMaxCpCheckout !== null && rawMaxCpCheckout !== "" && MAX_CP_CHECKOUT > 0 && MAX_CP_CHECKOUT < 999999) {
                if (cpCheckout <= MAX_CP_CHECKOUT && cpCheckout > 0) {
                  // KIỂM TRA BỔ SUNG: Nếu Giá DATA quá cao so với mốc cho phép (ví dụ > 2x), thì KHÔNG áp dụng ngoại lệ
                  // Lý do: Không hợp lý khi Giá DATA quá cao (ví dụ 90k vs mốc 35k), dù CP Checkout tốt
                  // Vì không có quảng cáo nào ra 1 tin nhắn chốt 1 đơn, 2 tin nhắn chốt 2 đơn
                  var GIA_DATA_MULTIPLIER_THRESHOLD = 2.0; // Hệ số nhân tối đa (2x = gấp đôi mốc cho phép)
                  var giaDataMultiplier = SL_2_GIA_DATA > 0 ? (giaData / SL_2_GIA_DATA) : 999;
                  
                  if (giaDataMultiplier <= GIA_DATA_MULTIPLIER_THRESHOLD) {
                    coCheckoutTot = true;
                  }
                }
              }
            }
            
            if (!coCheckoutTot) {
              lyDoTat = "GĐ2: Spend > " + SL_2_SPEND + " & Giá DATA > " + SL_2_GIA_DATA;
            }
          }
        } catch (eCfg) {
          thongBaoLoi += "\nLỖI LOGIC (GĐ2): Không thể đọc SL_2 cho rule của TK '" + accountId + "' với campaign '" + campaignName + "'.";
        }
      }

      // 4.3) Gom adset đủ điều kiện TẮT (chỉ khi ACTIVE)
      // KIỂM TRA COOLDOWN THÔNG MINH: Đếm số lần bật/tắt và tăng cooldown nếu lặp lại nhiều lần
      if (lyDoTat && adsetStatus === TARGET_STATUS) {
        // TỐI ƯU: Thu thập adsetIds để batch check cooldown sau
        adsetIdsForCooldown.push(adsetId);
        
        // TỐI ƯU: Check cooldown từ cache (sẽ được tính sau)
        var shouldSkipDueToCooldown = cooldownCache[adsetId] ? cooldownCache[adsetId].shouldSkip : false;
        
        if (!shouldSkipDueToCooldown && !adsetsToPause[adsetId]) { 
          adsetsToPause[adsetId] = {
            adId: adId,
            adName: adName || "(Không có tên Ad)",
            adsetName: adsetName || "(Không có tên Adset)",
            campaignName: campaignName || "(Không có tên Campaign)",
            reason: lyDoTat,
            prefix: prefixCache[campaignName] || getPrefixTuTen(campaignName)
          };
        }
      }
      
      // 4.4) LOGIC BẬT LẠI: Kiểm tra adsets đang PAUSED và bật lại nếu đủ điều kiện
      // Điều kiện: Spend > RESUME_SPEND VÀ Kết Quả > RESUME_DATA VÀ Giá DATA < RESUME_GIA_DATA
      // NGOẠI LỆ: Nếu có Checkouts Initiated tốt (>= MIN_CHECKOUTS) VÀ Cost per checkout initiated tốt (<= MAX_CP_CHECKOUT) thì BẬT LẠI ngay cả khi Giá DATA >= RESUME_GIA_DATA
      // QUAN TRỌNG: Thêm điều kiện Giá DATA để tránh bật lại adsets có Giá DATA quá đắt
      // (Nếu không có điều kiện này, adset có Spend cao và Kết Quả cao nhưng Giá DATA đắt sẽ bị bật lại,
      // rồi ngay lập tức bị tắt lại bởi GĐ2, gây lặp vô hạn)
      if (adsetStatus === 'PAUSED' && hasValidData && ketQua > 0) {
        try {
          function pickKey(obj, keys) {
            for (var i = 0; i < keys.length; i++) {
              if (obj && obj[keys[i]] != null && obj[keys[i]] !== "") return obj[keys[i]];
            }
            return undefined;
          }
          var defaultLogic = (logicMap && logicMap["DEFAULT|DEFAULT"]) || {};
          
          // Đọc các ngưỡng RESUME
          var rawResumeSpend = pickKey(logic, ["RESUME_SPEND", "BAT_LAI_SPEND"]); 
          if (rawResumeSpend === undefined) rawResumeSpend = pickKey(defaultLogic, ["RESUME_SPEND", "BAT_LAI_SPEND"]);
          
          var rawResumeData = pickKey(logic, ["RESUME_DATA", "RESUME_KET_QUA", "BAT_LAI_DATA"]); 
          if (rawResumeData === undefined) rawResumeData = pickKey(defaultLogic, ["RESUME_DATA", "RESUME_KET_QUA", "BAT_LAI_DATA"]);
          
          // Đọc ngưỡng Giá DATA tối đa để bật lại
          var rawResumeGiaData = pickKey(logic, ["RESUME_GIA_DATA", "BAT_LAI_GIA_DATA"]); 
          if (rawResumeGiaData === undefined) rawResumeGiaData = pickKey(defaultLogic, ["RESUME_GIA_DATA", "BAT_LAI_GIA_DATA"]);
          
          // Nếu không có RESUME_GIA_DATA, fallback về SL_GIAI_DOAN_2_GIA_DATA (ngưỡng GĐ2)
          // Để đảm bảo không bật lại adsets sẽ bị tắt ngay bởi GĐ2
          if (rawResumeGiaData === undefined || rawResumeGiaData === null || rawResumeGiaData === "") {
            var rawGiaData2 = pickKey(logic, ["SL_GIAI_DOAN_2_GIA_DATA", "SL_2_GIA_DATA"]);
            if (rawGiaData2 === undefined) rawGiaData2 = pickKey(defaultLogic, ["SL_GIAI_DOAN_2_GIA_DATA", "SL_2_GIA_DATA"]);
            rawResumeGiaData = rawGiaData2;
          }
          
          var rawMaxCpCheckout = pickKey(logic, ["MAX_CP_CHECKOUT", "MAX_CPL"]); 
          if (rawMaxCpCheckout === undefined || rawMaxCpCheckout === null || rawMaxCpCheckout === "") {
            rawMaxCpCheckout = pickKey(defaultLogic, ["MAX_CP_CHECKOUT", "MAX_CPL"]);
          }
          
          var RESUME_SPEND = chuyenDoiTienTe(rawResumeSpend);
          var RESUME_DATA = chuyenDoiThapPhan(rawResumeData);
          var RESUME_GIA_DATA = chuyenDoiTienTe(rawResumeGiaData);
          var MAX_CP_CHECKOUT = chuyenDoiTienTe(rawMaxCpCheckout);
          
          // QUAN TRỌNG: Không dùng fallback mặc định, cảnh báo nếu thiếu điều kiện
          // TỐI ƯU: Dùng cache prefix
          var prefix = prefixCache[campaignName] || getPrefixTuTen(campaignName);
          if (!prefixCache[campaignName]) prefixCache[campaignName] = prefix;
          if (rawResumeSpend === undefined || rawResumeSpend === null || rawResumeSpend === "" || !RESUME_SPEND || isNaN(RESUME_SPEND)) {
            var warningKey = accountId + "|BẬT LẠI|RESUME_SPEND|" + prefix;
            if (canhBaoThieuDieuKien.indexOf(warningKey) === -1) {
              canhBaoThieuDieuKien.push(warningKey);
              Logger.log("⚠️ CẢNH BÁO: Tài khoản " + accountId + "|Prefix " + prefix + " ở Logic Bật lại không có điều kiện RESUME_SPEND");
            }
            return; // Không chạy logic nếu thiếu điều kiện
          }
          // RESUME_DATA có thể là 0 hoặc undefined (cho phép ketQua > 0)
          if (RESUME_DATA === undefined || RESUME_DATA === null || isNaN(RESUME_DATA)) {
            RESUME_DATA = 0; // Cho phép ketQua > 0 (tức là ketQua >= 1)
          }
          // RESUME_GIA_DATA có thể không có (sẽ dùng SL_2_GIA_DATA hoặc bỏ qua điều kiện này)
          if (!RESUME_GIA_DATA || isNaN(RESUME_GIA_DATA)) {
            // Nếu không có RESUME_GIA_DATA và không có SL_2_GIA_DATA, cảnh báo nhưng vẫn chạy (bỏ qua điều kiện Giá DATA)
            if (rawResumeGiaData === undefined || rawResumeGiaData === null || rawResumeGiaData === "") {
              var prefix = getPrefixTuTen(campaignName);
              var warningKey = accountId + "|BẬT LẠI|RESUME_GIA_DATA|" + prefix;
              if (canhBaoThieuDieuKien.indexOf(warningKey) === -1) {
                canhBaoThieuDieuKien.push(warningKey);
                Logger.log("⚠️ CẢNH BÁO: Tài khoản " + accountId + "|Prefix " + prefix + " ở Logic Bật lại không có điều kiện RESUME_GIA_DATA");
              }
              RESUME_GIA_DATA = 999999; // Bỏ qua điều kiện Giá DATA
            }
          }
          
          // Đọc dữ liệu checkout từ row
          var checkouts = leads || 0; // Checkouts Initiated
          var cpCheckout = cpl || 0; // Cost per checkout initiated
          if (checkouts > 0 && cpCheckout === 0) {
            // Tính lại nếu chưa có
            cpCheckout = spend / checkouts;
          }
          
          // Kiểm tra điều kiện bật lại: 
          // 1. Spend > ngưỡng VÀ 
          // 2. Kết Quả > ngưỡng (nếu RESUME_DATA = 0, thì kiểm tra ketQua > 0, tức là ketQua >= 1) VÀ 
          // 3. Giá DATA < ngưỡng (để tránh bật lại adsets có Giá DATA quá đắt)
          // NGOẠI LỆ: Nếu có checkout tốt thì bỏ qua điều kiện Giá DATA
          var ketQuaCheck = (RESUME_DATA === 0) ? (ketQua > 0) : (ketQua > RESUME_DATA);
          var giaDataCheck = (giaData < RESUME_GIA_DATA);
          
          // Kiểm tra ngoại lệ với checkout - CHỈ áp dụng khi checkout và tin nhắn CÙNG NGÀY
          // QUAN TRỌNG: Kiểm tra cùng ngày TRƯỚC - nếu không cùng ngày → KHÔNG áp dụng ngoại lệ
          var coCheckoutTot = false;
          // TỐI ƯU: Dùng cache thay vì gọi hàm
          var coCungNgay = matchingDatesCache[adsetId] || false;
          
          if (coCungNgay && checkouts > 0) {
            // CHỈ áp dụng ngoại lệ khi: cùng ngày VÀ có MAX_CP_CHECKOUT được cấu hình VÀ CP Checkout <= ngưỡng
            if (rawMaxCpCheckout !== undefined && rawMaxCpCheckout !== null && rawMaxCpCheckout !== "" && MAX_CP_CHECKOUT > 0 && MAX_CP_CHECKOUT < 999999) {
              if (cpCheckout <= MAX_CP_CHECKOUT && cpCheckout > 0) {
                // KIỂM TRA BỔ SUNG: Nếu Giá DATA quá cao so với mốc cho phép (ví dụ > 2x), thì KHÔNG áp dụng ngoại lệ
                var GIA_DATA_MULTIPLIER_THRESHOLD = 2.0; // Hệ số nhân tối đa (2x = gấp đôi mốc cho phép)
                var giaDataMultiplier = RESUME_GIA_DATA > 0 && RESUME_GIA_DATA < 999999 ? (giaData / RESUME_GIA_DATA) : 999;
                
                if (giaDataMultiplier <= GIA_DATA_MULTIPLIER_THRESHOLD) {
                  coCheckoutTot = true;
                  giaDataCheck = true;
                }
              }
            }
          }
          // CHỈ log khi có checkout > 0, không log khi checkouts = 0
          
          if (spend > RESUME_SPEND && ketQuaCheck && giaDataCheck) {
            // TỐI ƯU: Thu thập adsetIds để batch check cooldown sau
            adsetIdsForCooldown.push(adsetId);
            
            // TỐI ƯU: Check cooldown từ cache (sẽ được tính sau)
            var shouldSkipDueToCooldown = cooldownCache[adsetId] ? cooldownCache[adsetId].shouldSkip : false;
            
            // Thêm vào danh sách bật lại
            if (!shouldSkipDueToCooldown && !adsetsToResume[adsetId]) {
              var reasonResume = "Bật lại: Spend > " + RESUME_SPEND + " & Kết Quả > " + (RESUME_DATA === 0 ? "0" : RESUME_DATA);
              if (coCheckoutTot) {
                reasonResume += " & Checkout tốt (bỏ qua Giá DATA)";
              } else {
                reasonResume += " & Giá DATA < " + RESUME_GIA_DATA;
              }
              adsetsToResume[adsetId] = {
                adId: adId,
                adName: adName || "(Không có tên Ad)",
                adsetName: adsetName || "(Không có tên Adset)",
                campaignName: campaignName || "(Không có tên Campaign)",
                reason: reasonResume,
                prefix: prefixCache[campaignName] || getPrefixTuTen(campaignName)
              };
              var kqMsg = (RESUME_DATA === 0) ? "KQ=" + ketQua + " (>0)" : "KQ=" + ketQua + " (>" + RESUME_DATA + ")";
              var giaDataMsg = coCheckoutTot ? "Giá DATA=" + giaData + " (bỏ qua do checkout tốt)" : "Giá DATA=" + giaData + " (<" + RESUME_GIA_DATA + ")";
            }
          } else {
            var reasonSkip = [];
            if (spend <= RESUME_SPEND) reasonSkip.push("Spend=" + spend + " (≤" + RESUME_SPEND + ")");
            if (RESUME_DATA === 0) {
              if (ketQua <= 0) reasonSkip.push("KQ=" + ketQua + " (≤0)");
            } else {
              if (ketQua <= RESUME_DATA) reasonSkip.push("KQ=" + ketQua + " (≤" + RESUME_DATA + ")");
            }
            if (!coCheckoutTot && giaData >= RESUME_GIA_DATA) reasonSkip.push("Giá DATA=" + giaData + " (≥" + RESUME_GIA_DATA + ")");
            // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
          }
        } catch (eCfg) {
          thongBaoLoi += "\nLỖI LOGIC (BẬT LẠI): Không thể đọc RESUME cho rule của TK '" + accountId + "' với campaign '" + campaignName + "'.";
        }
      } 
    }

    // TỐI ƯU: Batch check cooldown cho tất cả adsets cần check
    if (adsetIdsForCooldown.length > 0) {
      try {
        var now = Date.now();
        var windowHours = 2;
        var windowMs = windowHours * 60 * 60 * 1000;
        
        // Batch load tất cả properties một lần
        // TỐI ƯU: Tạo set các keys cần tìm để filter nhanh
        var keysToFind = {};
        for (var i = 0; i < adsetIdsForCooldown.length; i++) {
          var aid = adsetIdsForCooldown[i];
          keysToFind["ADSET_TOGGLE_COUNT_" + aid] = true;
          keysToFind["ADSET_TOGGLE_HISTORY_" + aid] = true;
        }
        
        // Load tất cả properties (getProperties() không nhận tham số)
        var allPropsRaw = props.getProperties();
        // Filter chỉ lấy các properties cần thiết
        var allProps = {};
        var allKeys = Object.keys(allPropsRaw);
        for (var kIdx = 0; kIdx < allKeys.length; kIdx++) {
          var key = allKeys[kIdx];
          if (keysToFind[key]) {
            allProps[key] = allPropsRaw[key];
          }
        }
        
        // Tính cooldown cho từng adset
        for (var i = 0; i < adsetIdsForCooldown.length; i++) {
          var aid = adsetIdsForCooldown[i];
          var toggleHistoryKey = "ADSET_TOGGLE_HISTORY_" + aid;
          var toggleHistory = allProps[toggleHistoryKey] || '';
          
          var historyTimestamps = [];
          if (toggleHistory) {
            var parts = toggleHistory.split(',');
            for (var j = 0; j < parts.length; j++) {
              var ts = parseInt(parts[j].trim(), 10);
              if (!isNaN(ts) && ts > 0) {
                historyTimestamps.push(ts);
              }
            }
          }
          
          // Lọc các lần toggle trong cửa sổ thời gian
          var recentToggles = [];
          for (var j = 0; j < historyTimestamps.length; j++) {
            if ((now - historyTimestamps[j]) <= windowMs) {
              recentToggles.push(historyTimestamps[j]);
            }
          }
          
          var recentToggleCount = recentToggles.length;
          var cooldownMinutes = 30;
          if (recentToggleCount >= 3) {
            cooldownMinutes = 120;
          } else if (recentToggleCount >= 2) {
            cooldownMinutes = 60;
          }
          var cooldownMs = cooldownMinutes * 60 * 1000;
          
          var shouldSkip = false;
          if (recentToggles.length > 0) {
            var lastToggle = recentToggles[0];
            for (var j = 1; j < recentToggles.length; j++) {
              if (recentToggles[j] > lastToggle) {
                lastToggle = recentToggles[j];
              }
            }
            if ((now - lastToggle) < cooldownMs) {
              shouldSkip = true;
            }
          }
          
          cooldownCache[aid] = { shouldSkip: shouldSkip, lastToggle: recentToggles.length > 0 ? lastToggle : 0 };
        }
        
        // Áp dụng cooldown check vào adsetsToPause và adsetsToResume
        for (var aid in adsetsToPause) {
          if (cooldownCache[aid] && cooldownCache[aid].shouldSkip) {
            delete adsetsToPause[aid];
          }
        }
        for (var aid in adsetsToResume) {
          if (cooldownCache[aid] && cooldownCache[aid].shouldSkip) {
            delete adsetsToResume[aid];
          }
        }
      } catch (eCooldown) {
        Logger.log("⚠️ Lỗi batch check cooldown: " + eCooldown.message);
      }
    }

    var adsetIdList = Object.keys(adsetsToPause); 
    adsetCount = adsetIdList.length;

    var resumeIdList = Object.keys(adsetsToResume);
    resumeCount = resumeIdList.length;
      
    // ----- THỰC THI LỆNH TẮT (AUTO) -----
    var actualPausedCount = 0;
    var pauseErrorDetails = [];
    if (adsetIdList.length > 0) {
      var batchResult = goiFacebookAPIDeTatNhieuAdset(adsetIdList, accessToken, delayMs); 
      actualPausedCount = batchResult.success;
      pauseErrorDetails = batchResult.errorDetails || [];
      
      // CHỈ hiển thị số lượng thành công, thất bại sẽ được báo riêng
      if (batchResult.success > 0) {
        logMessages.push("\n*Đã gửi lệnh TẮT HÀNG LOẠT: " + batchResult.success + " thành công" + (batchResult.errors > 0 ? ", " + batchResult.errors + " thất bại" : "") + ".*");
      }
      
      // Gửi thông báo lỗi riêng nếu có
      if (batchResult.errors > 0 && pauseErrorDetails.length > 0) {
        var errorMsg = "🚨 *LỖI KHI TẮT ADSET*\n\n";
        errorMsg += "Có " + batchResult.errors + " adset KHÔNG THỂ TẮT:\n\n";
        pauseErrorDetails.slice(0, 10).forEach(function(err) {
          var adsetInfo = adsetsToPause[err.adsetId];
          if (adsetInfo) {
            errorMsg += "▪️ *" + adsetInfo.adsetName + "* (" + adsetInfo.prefix + ")\n";
            errorMsg += "   Adset ID: `" + err.adsetId + "`\n";
            errorMsg += "   Lỗi: " + err.error + "\n\n";
          } else {
            errorMsg += "▪️ Adset ID: `" + err.adsetId + "`\n";
            errorMsg += "   Lỗi: " + err.error + "\n\n";
          }
        });
        if (pauseErrorDetails.length > 10) {
          errorMsg += "... và " + (pauseErrorDetails.length - 10) + " lỗi khác.\n";
        }
        errorMsg += "\n👉 Vui lòng kiểm tra và khắc phục.";
        try {
          if (botToken && chatId) {
            guiThongBaoTelegram(errorMsg, botToken, chatId);
          }
        } catch (eErr) {
          Logger.log("🚨 Lỗi gửi thông báo lỗi: " + eErr.message);
        }
      }
    }
    
    // ----- THỰC THI LỆNH BẬT LẠI (AUTO) -----
    var actualResumedCount = 0;
    var resumeErrorDetails = [];
    if (resumeIdList.length > 0) {
      var batchResumeResult = goiFacebookAPIDeBatNhieuAdset(resumeIdList, accessToken, delayMs);
      actualResumedCount = batchResumeResult.success;
      resumeErrorDetails = batchResumeResult.errorDetails || [];
      
      // CHỈ hiển thị số lượng thành công
      if (batchResumeResult.success > 0) {
        logMessages.push("\n*Đã gửi lệnh BẬT LẠI HÀNG LOẠT: " + batchResumeResult.success + " thành công" + (batchResumeResult.errors > 0 ? ", " + batchResumeResult.errors + " thất bại" : "") + ".*");
      }
      
      // Gửi thông báo lỗi riêng nếu có
      if (batchResumeResult.errors > 0 && resumeErrorDetails.length > 0) {
        var errorMsg = "🚨 *LỖI KHI BẬT LẠI ADSET*\n\n";
        errorMsg += "Có " + batchResumeResult.errors + " adset KHÔNG THỂ BẬT LẠI:\n\n";
        resumeErrorDetails.slice(0, 10).forEach(function(err) {
          var adsetInfo = adsetsToResume[err.adsetId];
          if (adsetInfo) {
            errorMsg += "▪️ *" + adsetInfo.adsetName + "* (" + adsetInfo.prefix + ")\n";
            errorMsg += "   Adset ID: `" + err.adsetId + "`\n";
            errorMsg += "   Lỗi: " + err.error + "\n\n";
          } else {
            errorMsg += "▪️ Adset ID: `" + err.adsetId + "`\n";
            errorMsg += "   Lỗi: " + err.error + "\n\n";
          }
        });
        if (resumeErrorDetails.length > 10) {
          errorMsg += "... và " + (resumeErrorDetails.length - 10) + " lỗi khác.\n";
        }
        errorMsg += "\n👉 Vui lòng kiểm tra và khắc phục.";
        try {
          if (botToken && chatId) {
            guiThongBaoTelegram(errorMsg, botToken, chatId);
          }
        } catch (eErr) {
          Logger.log("🚨 Lỗi gửi thông báo lỗi: " + eErr.message);
        }
      }
    }
    
  } catch (e) {
    thongBaoLoi += "\nLỖI SCRIPT TẮT QC: " + e.message;
  } 
  
  finally {
    // Lấy thời gian hiện tại
    var now = new Date();
    var timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "HH:mm");
    var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "dd/MM/yyyy");
    
    var finalLog = ""; 
    
    // CHỈ hiển thị số lượng THÀNH CÔNG (không phải số lượng gửi lệnh)
    if (actualPausedCount > 0 || actualResumedCount > 0) {
    if (actualPausedCount > 0) {
        finalLog += '🛑 *ĐÃ TẮT ' + actualPausedCount + " adset*\n";
        finalLog += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
        finalLog += "⏰ *Thời gian:* " + timeStr + " ngày " + dateStr + "\n\n";

      // CHỈ hiển thị các adset đã tắt THÀNH CÔNG
      var shownPauseCount = 0;
      for (var adsetId in adsetsToPause) {
        // Chỉ hiển thị nếu không có trong danh sách lỗi (tức là thành công)
        var isError = false;
        for (var e = 0; e < pauseErrorDetails.length; e++) {
          if (pauseErrorDetails[e].adsetId === adsetId) {
            isError = true;
            break;
          }
        }
        if (!isError && shownPauseCount < actualPausedCount) {
         var info = adsetsToPause[adsetId];
         finalLog += "▪️ *Adset:* " + info.adsetName + " (" + info.prefix + ")\n";
          finalLog += "   *Lý do:* " + info.reason + "\n";
          finalLog += "   *Ad vi phạm:* " + info.adName + "\n";
          finalLog += "   *Campaign:* " + info.campaignName + "\n";
          finalLog += "\n";
          shownPauseCount++;
        }
      }
      }
      
      if (actualResumedCount > 0) {
        if (actualPausedCount > 0) {
          finalLog += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
        }
        finalLog += '✅ *ĐÃ BẬT LẠI ' + actualResumedCount + " adset*\n";
        finalLog += "⏰ *Thời gian:* " + timeStr + " ngày " + dateStr + "\n\n";

        // CHỈ hiển thị các adset đã bật lại THÀNH CÔNG
        var shownResumeCount = 0;
        for (var adsetId in adsetsToResume) {
          // Chỉ hiển thị nếu không có trong danh sách lỗi (tức là thành công)
          var isError = false;
          for (var e = 0; e < resumeErrorDetails.length; e++) {
            if (resumeErrorDetails[e].adsetId === adsetId) {
              isError = true;
              break;
            }
          }
          if (!isError && shownResumeCount < actualResumedCount) {
            var info = adsetsToResume[adsetId];
            finalLog += "▪️ *Adset:* " + info.adsetName + " (" + info.prefix + ")\n";
            finalLog += "   *Lý do:* " + info.reason + "\n";
            finalLog += "   *Ad:* " + info.adName + "\n";
            finalLog += "   *Campaign:* " + info.campaignName + "\n";
            finalLog += "\n";
            shownResumeCount++;
          }
        }
      }
      
      if (logMessages.length > 0) {
        finalLog += "\n" + logMessages.join("\n");
      }
      
      // BÁO CÁO TỔNG KẾT: KHÔNG tự động gửi, chỉ gửi khi user yêu cầu qua command /report
      // (Đã tách ra thành command riêng trong Telegram Bot)
      
      // GỬI THÔNG BÁO NGAY LẬP TỨC khi có adset vi phạm hoặc bật lại (không check điều kiện)
      try {
        if (botToken && chatId) {
          var actionSummary = "";
          if (actualPausedCount > 0) actionSummary += actualPausedCount + " adset tắt";
          if (actualPausedCount > 0 && actualResumedCount > 0) actionSummary += ", ";
          if (actualResumedCount > 0) actionSummary += actualResumedCount + " adset bật lại";
          guiThongBaoTelegram(finalLog, botToken, chatId);
    } else {
          Logger.log("⚠️ Không có Bot Token hoặc Chat ID để gửi thông báo");
    }
      } catch (eNotify) {
        Logger.log("🚨 LỖI GỬI THÔNG BÁO TELEGRAM: " + eNotify.message);
    }
    
        } else {
      finalLog = "✅ *Không có adset vi phạm hoặc cần bật lại trong lượt kiểm tra này.*\n";
      finalLog += "⏰ *Thời gian:* " + timeStr + " ngày " + dateStr;
      
      // Chỉ gửi thông báo "không vi phạm" theo khoảng thời gian cấu hình
      try {
        var notifyGapMin = parseInt((getSettingsSafe_() || {})['NOTIFY_NO_VIOLATION_MINUTES'] || '30', 10);
        if (shouldSendNoViolation_(notifyGapMin)) {
          if (botToken && chatId) {
           guiThongBaoTelegram(finalLog, botToken, chatId); 
            markNoViolationSent_();
          }
        }
      } catch (_e) {}
    }
    
    // Gửi cảnh báo về thiếu điều kiện trong LogicRules
    if (canhBaoThieuDieuKien.length > 0) {
      var warningMsg = "*⚠️ CẢNH BÁO: THIẾU ĐIỀU KIỆN TRONG LOGICRULES*\n\n";
      var warningMap = {}; // Gom theo tài khoản và giai đoạn
      canhBaoThieuDieuKien.forEach(function(key) {
        var parts = key.split("|");
        if (parts.length >= 3) {
          var accountId = parts[0];
          var giaiDoan = parts[1];
          var dieuKien = parts[2];
          var prefix = parts.length >= 4 ? parts[3] : "";
          var mapKey = accountId + "|" + (prefix || "");
          if (!warningMap[mapKey]) warningMap[mapKey] = { accountId: accountId, prefix: prefix, giaiDoan: {} };
          if (!warningMap[mapKey].giaiDoan[giaiDoan]) warningMap[mapKey].giaiDoan[giaiDoan] = [];
          warningMap[mapKey].giaiDoan[giaiDoan].push(dieuKien);
        }
      });
      
      Object.keys(warningMap).forEach(function(mapKey) {
        var item = warningMap[mapKey];
        var displayName = item.accountId + (item.prefix ? "|Prefix " + item.prefix : "");
        warningMsg += "📌 *Tài khoản " + displayName + "*:\n";
        Object.keys(item.giaiDoan).forEach(function(giaiDoan) {
          warningMsg += "  • " + giaiDoan + ": Thiếu " + item.giaiDoan[giaiDoan].join(", ") + "\n";
        });
        warningMsg += "\n";
      });
      warningMsg += "Vui lòng kiểm tra và điền đầy đủ điều kiện trong sheet LogicRules.";
      
      try {
        if (botToken && chatId) {
          guiThongBaoTelegram(warningMsg, botToken, chatId);
        }
      } catch (_e) {
        Logger.log("🚨 LỖI GỬI CẢNH BÁO TELEGRAM: " + _e.message);
      }
    }
    
    if (thongBaoLoi) {
      var errorMsg = "\n*⚠️ CÁC LỖI ĐÃ XẢY RA:*\n" + thongBaoLoi;
      try {
        if (botToken && chatId) {
          guiThongBaoTelegram(errorMsg, botToken, chatId);
        }
      } catch (_e) {}
    } 
  }
}


/* CÁC HÀM XỬ LÝ SỐ LIỆU (Không thay đổi) */
function chuyenDoiTienTe(giaTri) {
  if (!giaTri || giaTri === "") return 0;
  var str = String(giaTri);
  str = str.replace(/[₫đ$€]/g, '').trim(); 
  str = str.replace(/\./g, '');             
  str = str.replace(',', '.');             
  return parseFloat(str) || 0;
}
function chuyenDoiThapPhan(giaTri) {
  if (!giaTri || giaTri === "") return 0;
  var str = String(giaTri);
  str = str.replace(',', '.'); 
  return parseFloat(str) || 0;
}

/**
 * Cài đặt Trigger thời gian để chạy gần real-time
 * Ví dụ: chạy 5 phút/lần
 */
function caiDatTriggerTuDong() {
  // Xóa các trigger cũ của hàm này để tránh trùng lặp
  xoaTriggerCuaHam_('runAutomation');
  // Tạo trigger mới mỗi 5 phút
  ScriptApp.newTrigger('runAutomation')
    .timeBased()
    .everyMinutes(5)
    .create();
  Logger.log('Đã cài đặt trigger chạy runAutomation mỗi 5 phút.');
}

/**
 * Xóa tất cả trigger của một hàm theo tên
 */
function xoaTriggerCuaHam_(functionName) {
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(tr) {
    if (tr.getHandlerFunction && tr.getHandlerFunction() === functionName) {
      ScriptApp.deleteTrigger(tr);
    }
  });
}

/**
 * Safe loader: trả về settings, fallback đọc trực tiếp từ sheet CaiDat
 */
function getSettingsSafe_() {
  var settings = {};
  try {
    if (typeof layCaiDatHeThong === 'function') {
      settings = layCaiDatHeThong();
    }
  } catch (e) {
    Logger.log("⚠️ Lỗi gọi layCaiDatHeThong: " + e.message);
  }
  
  // Nếu không lấy được từ layCaiDatHeThong, fallback đọc trực tiếp
  if (!settings || Object.keys(settings).length === 0) {
    try {
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      var sheet = ss.getSheetByName('CaiDat');
      if (!sheet) {
        throw new Error("LỖI: Không tìm thấy trang cài đặt hệ thống 'CaiDat'");
      }
      var data = sheet.getDataRange().getValues();
      settings = {};
      for (var i = 1; i < data.length; i++) {
        var key = data[i][0]; // cột A
        var value = data[i][2]; // cột C
        if (key && String(key).trim() !== '') {
          settings[String(key).trim()] = value;
        }
      }
    } catch (e2) {
      Logger.log("⚠️ Lỗi đọc trực tiếp từ CaiDat: " + e2.message);
      settings = {};
    }
  }
  
  // QUAN TRỌNG: Luôn parse các giá trị số, kể cả khi lấy từ layCaiDatHeThong (vì nó trả về string)
  if (settings['AD_ACCOUNT_IDS']) {
    if (typeof settings['AD_ACCOUNT_IDS'] === 'string') {
      settings['AD_ACCOUNT_IDS'] = String(settings['AD_ACCOUNT_IDS']).split(',')
        .map(function(id){ return String(id).trim(); })
        .filter(function(id){ return id.indexOf('act_') === 0; });
    }
    // Nếu đã là array rồi thì giữ nguyên
  } else {
    settings['AD_ACCOUNT_IDS'] = [];
  }
  settings['DELAY_KHI_TAT_BATCH'] = parseInt(settings['DELAY_KHI_TAT_BATCH'] || '1000', 10);
  // Cấu hình lịch và thông báo - QUAN TRỌNG: Parse lại các giá trị số
  settings['RUN_EVERY_MINUTES'] = parseInt(settings['RUN_EVERY_MINUTES'] || '30', 10);
  settings['RUN_WINDOW_START_HOUR'] = parseInt(settings['RUN_WINDOW_START_HOUR'] || '6', 10);
  settings['RUN_WINDOW_END_HOUR'] = parseInt(settings['RUN_WINDOW_END_HOUR'] || '23', 10);
  settings['NOTIFY_NO_VIOLATION_MINUTES'] = parseInt(settings['NOTIFY_NO_VIOLATION_MINUTES'] || '30', 10);
  return settings;
}

/**
 * Lấy Spreadsheet theo SPREADSHEET_ID nếu có, ngược lại dùng Active.
 */
function getSpreadsheet_() {
  // 1) Ưu tiên lấy từ Script Properties (không phụ thuộc vào bất kỳ loader nào)
  try {
    var props = PropertiesService.getScriptProperties();
    var idFromProps = props && props.getProperty('SPREADSHEET_ID');
    if (idFromProps && String(idFromProps).trim() !== '') {
      return SpreadsheetApp.openById(String(idFromProps).trim());
    }
  } catch (e1) {}

  // 2) Thử đọc trực tiếp từ file đang mở (tab CaiDat) mà không gọi loader
  try {
    var active = SpreadsheetApp.getActiveSpreadsheet();
    var caiDat = active && active.getSheetByName('CaiDat');
    if (caiDat) {
      var values = caiDat.getDataRange().getValues();
      for (var i = 1; i < values.length; i++) {
        var key = values[i][0]; // cột A
        var val = values[i][2]; // cột C
        if (key && String(key).trim() === 'SPREADSHEET_ID' && val && String(val).trim() !== '') {
          var id = String(val).trim();
          try { return SpreadsheetApp.openById(id); } catch (_e) { break; }
        }
      }
      // Không có SPREADSHEET_ID → dùng luôn Active
      return active;
    }
  } catch (e2) {}

  // 3) Fallback cuối cùng
  return SpreadsheetApp.getActiveSpreadsheet();
}

// ====== Lập lịch theo CaiDat và khung giờ cấu hình ======
function isWithinWindow_(settings) {
  var s = settings || getSettingsSafe_() || {};
  var startH = parseInt(s['RUN_WINDOW_START_HOUR'] || '6', 10);
  var endH   = parseInt(s['RUN_WINDOW_END_HOUR']   || '23', 10);
  var tz = Session.getScriptTimeZone() || 'Asia/Ho_Chi_Minh';
  var now = new Date();
  var hour = parseInt(Utilities.formatDate(now, tz, 'H'), 10);
  var minute = parseInt(Utilities.formatDate(now, tz, 'm'), 10);
  
  // Kiểm tra: hour phải >= startH
  if (hour < startH) return false;
  
  // Kiểm tra: nếu hour > endH thì không cho phép
  if (hour > endH) return false;
  
  // Kiểm tra: nếu hour = endH, chỉ cho phép nếu phút = 0 (tức là chỉ cho phép đến endH:00, không bao gồm sau đó)
  if (hour === endH && minute > 0) return false;
  
  return true;
}

function caiDatTriggerTheoCaiDat() {
  var s = getSettingsSafe_() || {};
  var every = parseInt(s['RUN_EVERY_MINUTES'] || '30', 10);
  if (every < 1) every = 30;
  xoaTriggerCuaHam_('runAutomation');
  ScriptApp.newTrigger('runAutomation').timeBased().everyMinutes(every).create();
}

function stopAutomationTriggers_() {
  xoaTriggerCuaHam_('runAutomation');
}

// ====== Đếm cảnh báo token và tự dừng sau 3 lần ======
function increaseTokenAlertCount_(inc) {
  try {
    var props = PropertiesService.getScriptProperties();
    var cur = parseInt(props.getProperty('TOKEN_ALERT_COUNT') || '0', 10);
    if (isNaN(inc)) inc = 1;
    props.setProperty('TOKEN_ALERT_COUNT', String(cur + inc));
  } catch (_e) {}
}

function resetTokenAlertCount_() {
  try { PropertiesService.getScriptProperties().setProperty('TOKEN_ALERT_COUNT', '0'); } catch (_e) {}
}

function getTokenAlertCount_() {
  try { return parseInt(PropertiesService.getScriptProperties().getProperty('TOKEN_ALERT_COUNT') || '0', 10); } catch (_e) { return 0; }
}

// ====== Kiểm soát gửi tin 'không vi phạm' theo phút ======
function shouldSendNoViolation_(gapMin) {
  try {
    if (!gapMin || gapMin <= 0) return false;
    var props = PropertiesService.getScriptProperties();
    var last = parseInt(props.getProperty('NO_VIOLATION_LAST_TS') || '0', 10);
    var now = Date.now();
    return (now - last) >= gapMin * 60 * 1000;
  } catch (_e) { return true; }
}

function markNoViolationSent_() {
  try { PropertiesService.getScriptProperties().setProperty('NO_VIOLATION_LAST_TS', String(Date.now())); } catch (_e) {}
}

/**
 * Tạo báo cáo tổng kết: tổng ads được bật hôm nay, tổng adsets đã tắt, tổng adsets đang bật
 * @param {Sheet} dataSheet - Sheet Data_FB
 * @param {Object} colMap - Map cột
 * @param {number} totalPausedToday - Tổng số adsets đã tắt hôm nay
 * @returns {string} - Báo cáo dạng text
 */
function generateSummaryReport(dataSheet, colMap, totalPausedToday) {
  try {
    // Kiểm tra tham số đầu vào
    if (!dataSheet) {
      var stack = new Error().stack;
      Logger.log("⚠️ Lỗi: dataSheet không được truyền vào generateSummaryReport");
      Logger.log("⚠️ Stack trace: " + stack);
      return null;
    }
    if (!colMap || typeof colMap !== 'object') {
      var stack = new Error().stack;
      Logger.log("⚠️ Lỗi: colMap không hợp lệ trong generateSummaryReport");
      Logger.log("⚠️ colMap type: " + typeof colMap + ", value: " + colMap);
      Logger.log("⚠️ Stack trace: " + stack);
      return null;
    }
    
    // Nếu dataSheet là string (tên sheet), lấy sheet object
    var sheetNameForLog = '';
    if (typeof dataSheet === 'string') {
      sheetNameForLog = dataSheet;
      var ss = getSpreadsheet_();
      dataSheet = ss.getSheetByName(dataSheet);
      if (!dataSheet) {
        Logger.log("⚠️ Lỗi: Không tìm thấy sheet '" + sheetNameForLog + "'");
        return null;
      }
    }
    
    var data = dataSheet.getDataRange().getValues();
    if (data.length < 3) return null;
    
    // Bỏ qua hàng 1, 2 (header)
    data.shift();
    data.shift();
    
    var accountIdCol = colMap['Account ID'];
    var adsetIdCol = colMap['Adset Id'];
    var campaignNameCol = colMap['Campaign name'];
    var adsetStatusCol = colMap['Adset Effective Status'];
    var impressionsCol = colMap['Impressions'];
    
    if (accountIdCol === undefined || adsetIdCol === undefined || campaignNameCol === undefined || 
        adsetStatusCol === undefined || impressionsCol === undefined) {
      Logger.log("⚠️ Không đủ cột để tạo báo cáo tổng kết");
      return null;
    }
    
    // Đọc tất cả prefix từ LogicRules (không hardcode)
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
    Logger.log("📋 Prefix được sử dụng cho báo cáo tổng kết: " + ALLOWED_PREFIXES.join(", "));
    
    // Tạo set để lookup nhanh
    var allowedPrefixesSet = {};
    for (var apIdx = 0; apIdx < ALLOWED_PREFIXES.length; apIdx++) {
      allowedPrefixesSet[ALLOWED_PREFIXES[apIdx]] = true;
    }
    
    // Helper: Kiểm tra campaign name có prefix hợp lệ không
    function hasAllowedPrefix(campaignName) {
      if (!campaignName) return false;
      var extractedPrefix = getPrefixTuTen(campaignName);
      
      // Thử exact match trước
      if (allowedPrefixesSet[extractedPrefix]) {
        return extractedPrefix;
      }
      
      // Thử match prefix là substring (ví dụ: "CCB1" bắt đầu bằng "CCB")
      for (var i = 0; i < ALLOWED_PREFIXES.length; i++) {
        var allowedPrefix = ALLOWED_PREFIXES[i];
        if (extractedPrefix.indexOf(allowedPrefix) === 0) {
          return allowedPrefix; // "CCB1" bắt đầu bằng "CCB" → match
        }
        // Hoặc ngược lại: "CCB" match với "CCB1"
        if (allowedPrefix.indexOf(extractedPrefix) === 0 && extractedPrefix.length >= 2) {
          return allowedPrefix;
        }
      }
      
      return null; // Không match
    }
    
    // Thống kê theo account và prefix
    var statsByAccount = {}; // { accountId: { prefix: { enabled: 0, active: 0, paused: 0, total: 0 } } }
    var adsetIdsSeen = {}; // Để đếm unique adsets
    
    // TỐI ƯU: Dùng for thay vì forEach
    for (var rowIdx = 0; rowIdx < data.length; rowIdx++) {
      var row = data[rowIdx];
      var accountId = row[accountIdCol];
      var campaignName = row[campaignNameCol] || '';
      var adsetId = row[adsetIdCol];
      var status = row[adsetStatusCol];
      var impressions = chuyenDoiThapPhan(row[impressionsCol] || 0);
      
      if (!accountId || !adsetId || !campaignName) continue;
      
      // CHỈ tổng kết prefix có trong LogicRules
      var prefix = hasAllowedPrefix(campaignName);
      if (!prefix) continue; // Bỏ qua prefix không có trong LogicRules
      
      if (!statsByAccount[accountId]) {
        statsByAccount[accountId] = {};
      }
      if (!statsByAccount[accountId][prefix]) {
        statsByAccount[accountId][prefix] = { enabled: 0, active: 0, paused: 0, total: 0 };
      }
      
      // Đếm unique adset (không đếm trùng)
      var adsetKey = accountId + "|" + adsetId;
      if (!adsetIdsSeen[adsetKey]) {
        adsetIdsSeen[adsetKey] = true;
        statsByAccount[accountId][prefix].total++;
        
        // Đếm ads enabled hôm nay (impressions > 0 và status = ACTIVE)
        if (status === 'ACTIVE' && impressions > 0) {
          statsByAccount[accountId][prefix].enabled++;
          statsByAccount[accountId][prefix].active++;
        } else if (status === 'ACTIVE') {
          statsByAccount[accountId][prefix].active++;
        } else if (status === 'PAUSED') {
          statsByAccount[accountId][prefix].paused++;
        }
      }
    }
    
    // Tạo báo cáo
    var report = "*📊 BÁO CÁO TỔNG KẾT*\n\n";
    
    var totalEnabledAll = 0;
    var totalActiveAll = 0;
    var totalPausedAll = 0;
    var totalAdsetsAll = 0;
    
    // Báo cáo theo từng account
    Object.keys(statsByAccount).sort().forEach(function(accountId) {
      var accountStats = statsByAccount[accountId];
      report += "📌 *Tài khoản:* `" + accountId + "`\n";
      
      var accountEnabled = 0;
      var accountActive = 0;
      var accountPaused = 0;
      var accountTotal = 0;
      
      Object.keys(accountStats).sort().forEach(function(prefix) {
        var prefixStats = accountStats[prefix];
        report += "  • *" + prefix + "*:\n";
        report += "    - Ads bật hôm nay (impressions > 0): " + prefixStats.enabled + "\n";
        report += "    - Adsets đang bật: " + prefixStats.active + "\n";
        report += "    - Adsets đã tắt: " + prefixStats.paused + "\n";
        report += "    - Tổng adsets: " + prefixStats.total + "\n";
        
        accountEnabled += prefixStats.enabled;
        accountActive += prefixStats.active;
        accountPaused += prefixStats.paused;
        accountTotal += prefixStats.total;
      });
      
      report += "  *Tổng Account:* Bật=" + accountEnabled + ", Đang bật=" + accountActive + ", Đã tắt=" + accountPaused + ", Tổng=" + accountTotal + "\n\n";
      
      totalEnabledAll += accountEnabled;
      totalActiveAll += accountActive;
      totalPausedAll += accountPaused;
      totalAdsetsAll += accountTotal;
    });
    
    // Tổng kết tất cả
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
    report += "*TỔNG TẤT CẢ:*\n";
    report += "  • Ads bật hôm nay (impressions > 0): " + totalEnabledAll + "\n";
    report += "  • Adsets đang bật: " + totalActiveAll + "\n";
    report += "  • Adsets đã tắt: " + totalPausedAll + "\n";
    if (totalPausedToday > 0) {
      report += "  • Adsets đã tắt trong lượt kiểm tra gần nhất: " + totalPausedToday + "\n";
    }
    report += "  • Tổng adsets: " + totalAdsetsAll + "\n";
    
    // Thêm thời gian báo cáo
    var now = new Date();
    var timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "HH:mm");
    var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "dd/MM/yyyy");
    report += "\n⏰ *Thời gian:* " + timeStr + " ngày " + dateStr + "\n";
    
    return report;
  } catch (e) {
    Logger.log("⚠️ Lỗi tạo báo cáo tổng kết: " + e.message);
    return null;
  }
}
 
/**
 * TỔNG KẾT CUỐI NGÀY (23:30): Tất cả tài khoản và prefix
 * - Tổng chi tiêu
 * - Tổng tương tác (Post comments + Messaging conversations started)
 * - Giá DATA = Spend / Tương tác
 * - Số điện thoại = Checkouts Initiated
 * - Giá SĐT = Spend / Số điện thoại (nếu >0)
 * - Tỉ lệ SĐT/Tương tác
 */
function tongKetCuoiNgay(botTokenOverride, chatIdOverride) {
  var settings = getSettingsSafe_();
  var botToken = botTokenOverride || settings['TELEGRAM_BOT_TOKEN'];
  var chatId = chatIdOverride || settings['TELEGRAM_CHAT_ID'];

  var sheet = getSpreadsheet_().getSheetByName(SHEET_NAME_DATA);
  if (!sheet) {
    if (botToken && chatId) guiThongBaoTelegram('⚠️ Không tìm thấy sheet Data_FB để tổng kết', botToken, chatId);
    return;
  }

  var values = sheet.getDataRange().getValues();
  if (!values || values.length < 3) return;
  values.shift(); // row1
  var headers = values.shift();
  var col = {};
  headers.forEach(function(h,i){ if (h) col[h.trim()] = i; });

  function idx(name){ var i = col[name]; if (i === undefined) throw new Error('Thiếu cột '+name); return i; }

  var ACCOUNT_ID = idx('Account ID');
  var CAMPAIGN = idx('Campaign name');
  var SPEND = idx('Amount spent');
  var COMMENTS = idx('Post comments');
  var MSGS = idx('Messaging conversations started');
  var CHECKOUTS = col['Checkouts Initiated'] !== undefined ? col['Checkouts Initiated'] : col['Checkouts initiated'];
  if (CHECKOUTS === undefined) CHECKOUTS = idx('Checkouts Initiated');
  var IMP = idx('Impressions');

  // Đọc tất cả prefix từ LogicRules (không hardcode)
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
  Logger.log("📋 Prefix được sử dụng cho tổng kết: " + ALLOWED_PREFIXES.join(", "));

  // Tổng kết theo account và prefix: { accountId: { prefix: {spend, interactions, phones} } }
  var agg = {}; 
  var accountIds = {}; // Để lưu danh sách account IDs đã gặp

  // Helper: Lấy prefix từ campaign name
  function getPrefixFromCampaign(campaignName) {
    if (!campaignName) return '';
    var upperName = String(campaignName).toUpperCase();
    var parts = upperName.split(/[\s-_]+/);
    var extractedPrefix = parts[0] || '';
    
    // Kiểm tra exact match trước
    for (var i = 0; i < ALLOWED_PREFIXES.length; i++) {
      if (ALLOWED_PREFIXES[i] === extractedPrefix) {
        return extractedPrefix;
      }
      // Kiểm tra prefix là substring (ví dụ: "CCB1" bắt đầu bằng "CCB")
      if (extractedPrefix.indexOf(ALLOWED_PREFIXES[i]) === 0 || ALLOWED_PREFIXES[i].indexOf(extractedPrefix) === 0) {
        return ALLOWED_PREFIXES[i];
      }
    }
    return '';
  }

  // Duyệt qua tất cả rows
  for (var i = 0; i < values.length; i++) {
    var r = values[i];
    var accountId = String(r[ACCOUNT_ID] || '').trim();
    var name = String(r[CAMPAIGN] || '');
    var spend = parseNumber_(r[SPEND]);
    var inter = (parseNumber_(r[COMMENTS]) + parseNumber_(r[MSGS]));
    var phones = parseNumber_(r[CHECKOUTS]);
    var imp = parseNumber_(r[IMP]);
    
    if (imp <= 0 || !accountId) continue; // chỉ tổng kết các ad đã hiển thị > 0 và có account ID
    
    var prefix = getPrefixFromCampaign(name);
    if (!prefix) continue; // Bỏ qua nếu không match prefix nào
    
    // Khởi tạo cấu trúc nếu chưa có
    if (!agg[accountId]) {
      agg[accountId] = {};
      accountIds[accountId] = true;
    }
    if (!agg[accountId][prefix]) {
      agg[accountId][prefix] = {spend: 0, interactions: 0, phones: 0};
    }
    
    // Cộng dồn
    agg[accountId][prefix].spend += spend;
    agg[accountId][prefix].interactions += inter;
    agg[accountId][prefix].phones += phones;
  }

  var lines = [];
  lines.push('🧾 Tổng kết cuối ngày (23:30)');
  lines.push('━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  // Sắp xếp account IDs để hiển thị
  var sortedAccountIds = Object.keys(accountIds).sort();
  
  // Tổng kết theo từng account
  for (var accIdx = 0; accIdx < sortedAccountIds.length; accIdx++) {
    var accId = sortedAccountIds[accIdx];
    var accountData = agg[accId];
    var accountPrefixes = Object.keys(accountData).sort();
    
    lines.push('\n📛 Tài khoản: ' + accId);
    
    // Tổng kết theo từng prefix trong account
    for (var pIdx = 0; pIdx < accountPrefixes.length; pIdx++) {
      var p = accountPrefixes[pIdx];
      var a = accountData[p];
      var cpd = a.interactions > 0 ? a.spend / a.interactions : 0;
      var cpphone = a.phones > 0 ? a.spend / a.phones : 0;
      var phoneRate = a.interactions > 0 ? (a.phones / a.interactions) : 0;
      
      lines.push('  — ' + p + ':');
      lines.push('    • Chi tiêu: ' + formatCurrency_(a.spend));
      lines.push('    • Tương tác: ' + Math.round(a.interactions));
      lines.push('    • Giá DATA: ' + formatCurrency_(cpd));
      lines.push('    • SĐT (checkout): ' + Math.round(a.phones));
      lines.push('    • Giá SĐT: ' + formatCurrency_(cpphone));
      lines.push('    • Tỷ lệ SĐT/Tương tác: ' + (phoneRate*100).toFixed(1) + '%');
    }
  }

  if (botToken && chatId) guiThongBaoTelegram(lines.join('\n'), botToken, chatId);
}

function caiDatTriggerTongKet2330() {
  xoaTriggerCuaHam_('tongKetCuoiNgay');
  ScriptApp.newTrigger('tongKetCuoiNgay').timeBased().atHour(23).nearMinute(30).everyDays(1).create();
}

function parseNumber_(v) {
  if (typeof v === 'number') return v;
  if (v === null || v === '' || v === undefined) return 0;
  var s = String(v).trim().replace(/[^\d,\.\-]/g,'').replace(/\s+/g,'').replace(/\./g,'').replace(',', '.');
  var n = parseFloat(s); return isNaN(n) ? 0 : n;
}

function formatCurrency_(n) {
  try { return Utilities.formatString('%s ₫', Math.round(n).toLocaleString('vi-VN')); } catch (_e) { return String(Math.round(n)); }
}

// (Hàm lietKeFanpageQuanLy đã chuyển sang Pages.gs)

/**
 * ==================================================================
 * LỌC DỮ LIỆU 7 NGÀY QUA - ĐÁNH GIÁ VÀ TẮT ADSET KHÔNG ĐẠT CHUẨN
 * Chạy vào 0h hàng ngày, đánh giá theo các chỉ số tổng hợp 7 ngày
 * ==================================================================
 */
function locDuLieu7Ngay() {
  var settings = getSettingsSafe_();
  var logicMap = buildLogicMap();
  var accessToken = settings['ACCESS_TOKEN'];
  var adAccountIds = settings['AD_ACCOUNT_IDS'];
  var botToken = settings['TELEGRAM_BOT_TOKEN'];
  var chatId = settings['TELEGRAM_CHAT_ID'];
  var delayMs = settings['DELAY_KHI_TAT_BATCH'] || 1000;
  
  if (!accessToken || !adAccountIds || adAccountIds.length === 0) {
    if (botToken && chatId) guiThongBaoTelegram('⚠️ Thiếu ACCESS_TOKEN hoặc AD_ACCOUNT_IDS', botToken, chatId);
    return;
  }
  
  var adsetsToPause = {};
  
  try {
    // 1. Kéo dữ liệu 7 ngày qua bằng hàm riêng (không phụ thuộc CaiDat)
    var adsetsData = pullFacebookData7Ngay(accessToken, adAccountIds);
    
    if (!adsetsData || Object.keys(adsetsData).length === 0) {
      if (botToken && chatId) guiThongBaoTelegram('⚠️ Không có dữ liệu 7 ngày để đánh giá', botToken, chatId);
      return;
    }
    
    // 2. Đánh giá từng adset theo ngưỡng LogicRules
    Object.keys(adsetsData).forEach(function(adsetId) {
      var d = adsetsData[adsetId];
      var logic = getLogicForRow(logicMap, d.accountId, d.campaignName);
      if (!logic) return;
      
      var prefix = getPrefixTuTen(d.campaignName);
      var lyDoTat = '';
      
      // Lấy ngưỡng từ LogicRules (tập trung vào Checkout và Purchase)
      var MAX_GIÁ_DATA = chuyenDoiTienTe(logic['MAX_GIÁ_DATA'] || logic['MAX_GIA_DATA'] || 999999);
      var MIN_KET_QUA = parseFloat(logic['MIN_KET_QUA'] || 0);
      var MAX_CP_CHECKOUT = chuyenDoiTienTe(logic['MAX_CP_CHECKOUT'] || logic['MAX_CPL'] || 999999);
      var MIN_CHECKOUTS = parseFloat(logic['MIN_CHECKOUTS'] || logic['MIN_LEADS'] || 0);
      var MAX_CP_PURCHASE = chuyenDoiTienTe(logic['MAX_CP_PURCHASE'] || logic['MAX_CPA'] || 999999);
      var MIN_PURCHASES = parseFloat(logic['MIN_PURCHASES'] || 0);
      
      // Kiểm tra các điều kiện (theo thứ tự ưu tiên)
      if (d.giaData > MAX_GIÁ_DATA && MAX_GIÁ_DATA < 999999) {
        lyDoTat = '7d: Giá DATA (' + Math.round(d.giaData) + ') > ' + MAX_GIÁ_DATA;
      } else if (d.ketQua < MIN_KET_QUA && MIN_KET_QUA > 0) {
        lyDoTat = '7d: Kết Quả (' + Math.round(d.ketQua) + ') < ' + MIN_KET_QUA;
      } else if (d.cpCheckout > MAX_CP_CHECKOUT && d.checkouts > 0 && MAX_CP_CHECKOUT < 999999) {
        lyDoTat = '7d: CP Checkout (' + Math.round(d.cpCheckout) + ') > ' + MAX_CP_CHECKOUT;
      } else if (d.checkouts < MIN_CHECKOUTS && MIN_CHECKOUTS > 0) {
        lyDoTat = '7d: Checkouts (' + Math.round(d.checkouts) + ') < ' + MIN_CHECKOUTS;
      } else if (d.cpPurchase > MAX_CP_PURCHASE && d.purchases > 0 && MAX_CP_PURCHASE < 999999) {
        lyDoTat = '7d: CP Purchase (' + Math.round(d.cpPurchase) + ') > ' + MAX_CP_PURCHASE;
      } else if (d.purchases < MIN_PURCHASES && MIN_PURCHASES > 0 && d.purchases > 0) {
        lyDoTat = '7d: Purchases (' + Math.round(d.purchases) + ') < ' + MIN_PURCHASES;
      }
      
      if (lyDoTat) {
        adsetsToPause[adsetId] = {
          adsetName: d.adsetName,
          campaignName: d.campaignName,
          prefix: prefix,
          reason: lyDoTat
        };
      }
    });
    
    // 4. Tắt adset vi phạm
    var adsetIds = Object.keys(adsetsToPause);
    if (adsetIds.length > 0) {
      var batchResult = goiFacebookAPIDeTatNhieuAdset(adsetIds, accessToken, delayMs);
      var msg = '🛑 Lọc 7 ngày: Đã tắt ' + batchResult.success + '/' + adsetIds.length + ' adset vi phạm\n';
      Object.keys(adsetsToPause).forEach(function(id) {
        var info = adsetsToPause[id];
        msg += '▪️ ' + info.adsetName + ' (' + info.prefix + ')\n   ' + info.reason + '\n';
      });
      if (botToken && chatId) guiThongBaoTelegram(msg, botToken, chatId);
    } else {
      if (botToken && chatId) guiThongBaoTelegram('✅ Lọc 7 ngày: Tất cả adset đều đạt chuẩn.', botToken, chatId);
    }
  } catch (e) {
    if (botToken && chatId) guiThongBaoTelegram('🚨 Lỗi lọc 7 ngày: ' + e.message, botToken, chatId);
  }
}

/**
 * Cài trigger chạy lọc 7 ngày vào 0h hàng ngày
 */
function caiDatTriggerLoc7Ngay() {
  xoaTriggerCuaHam_('locDuLieu7Ngay');
  ScriptApp.newTrigger('locDuLieu7Ngay').timeBased().atHour(0).everyDays(1).create();
}