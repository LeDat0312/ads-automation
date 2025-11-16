// File: Logic.gs
// Đã cập nhật để đọc đúng `CaiDat` (cho hệ thống) và `LogicRules` (cho logic)

// ===== Cấu hình sheet =====
var SHEET_NAME_SYSTEM = "CaiDat"; // Trang chứa Token, Chat ID
var SHEET_NAME_LOGIC = "LogicRules"; // Trang chứa ma trận logic
var COLUMN_START_LOGIC_RULES = 3; // Cột bắt đầu của logic (Cột C = DEFAULT|DEFAULT)

// ===== Hàm Helper (Không đổi) =====
function getPrefixTuTen(campaignName) {
  if (!campaignName) return "DEFAULT";
  var ten = String(campaignName).toUpperCase().trim(); 
  var parts = ten.split(/[\s-_]+/); 
  var prefix = parts[0] || ""; 
  
  // QUAN TRỌNG: Nếu prefix quá dài (ví dụ: "LAKVDHNT80"), thử tìm prefix ngắn hơn
  // Bằng cách loại bỏ phần số ở cuối hoặc tìm prefix phù hợp nhất
  // Ví dụ: "LAKVDHNT80" → thử "LAKVDHNT", "LAKVDH"
  if (prefix.length > 6) {
    // Thử loại bỏ phần số ở cuối (nếu có)
    var prefixWithoutNumbers = prefix.replace(/\d+$/, '');
    if (prefixWithoutNumbers.length >= 3 && prefixWithoutNumbers.length < prefix.length) {
      // Nếu sau khi loại bỏ số vẫn còn ít nhất 3 ký tự, dùng prefix ngắn hơn
      prefix = prefixWithoutNumbers;
    }
  }
  
  return prefix || "DEFAULT"; // Trả về DEFAULT nếu tên rỗng
}


/**
 * Hàm 1: Đọc các cài đặt hệ thống (Token, Chat ID...)
 * Đọc từ trang `CaiDat` (Dạng Key-Value dọc)
 */
function layCaiDatHeThong() {
  var sheet = getSpreadsheet_().getSheetByName(SHEET_NAME_SYSTEM);
  if (!sheet) {
    throw new Error("LỖI: Không tìm thấy trang cài đặt hệ thống '" + SHEET_NAME_SYSTEM + "'");
  }
  
  var data = sheet.getDataRange().getValues(); // Lấy tất cả
  var settings = {}; 

  // Lặp qua các hàng (bỏ qua hàng tiêu đề A1, B1, C1)
  for (var i = 1; i < data.length; i++) {
    var key = data[i][0]; // Cột A (Tên Cài Đặt)
    var value = data[i][2]; // Cột C (Giá Trị)
    
    if (key && key.trim() !== "") {
      // Chuẩn hóa value: trim và chuyển về string (tránh số được parse thành number)
      var normalizedKey = key.trim();
      var normalizedValue = value !== null && value !== undefined ? String(value).trim() : "";
      
      settings[normalizedKey] = normalizedValue;
      
      // Log các giá trị quan trọng để debug
      if (normalizedKey === 'TELEGRAM_AUTHORIZED_CHAT_ID' || normalizedKey === 'TELEGRAM_CHAT_ID' || normalizedKey === 'TELEGRAM_BOT_TOKEN') {
        var logValue = normalizedKey === 'TELEGRAM_BOT_TOKEN' ? 
          (normalizedValue ? normalizedValue.substring(0, 10) + "..." + normalizedValue.substring(normalizedValue.length - 5) : "null") :
          normalizedValue;
        Logger.log("📋 Đọc " + normalizedKey + " từ sheet: '" + logValue + "' (type: " + typeof normalizedValue + ", length: " + (normalizedValue ? normalizedValue.length : 0) + ")");
      }
    }
  }
  
  // Xử lý chuỗi Ad Account IDs - Tự động thêm "act_" nếu thiếu
  // Hỗ trợ nhiều format: dấu phẩy, chấm phẩy, xuống dòng, khoảng trắng
  // QUAN TRỌNG: CHỈ đọc từ CaiDat, KHÔNG tự động lấy từ LogicRules
  if (settings["AD_ACCOUNT_IDS"]) {
    var idsStr = String(settings["AD_ACCOUNT_IDS"]).trim();
    // Thay thế các ký tự phân cách khác nhau thành dấu phẩy
    idsStr = idsStr.replace(/[;\n\r\t]+/g, ','); // Chấm phẩy, xuống dòng, tab → phẩy
    idsStr = idsStr.replace(/\s*,\s*/g, ','); // Chuẩn hóa dấu phẩy
    idsStr = idsStr.replace(/,+/g, ','); // Loại bỏ dấu phẩy trùng lặp
    
    var rawIds = idsStr.split(',');
    Logger.log("📋 Raw AD_ACCOUNT_IDS từ CaiDat: '" + idsStr + "' (" + rawIds.length + " phần tử)");
    
    settings["AD_ACCOUNT_IDS"] = rawIds
      .map(function(id) { 
        id = id.trim();
        // Bỏ qua rỗng
        if (!id) return null;
        // Nếu không có "act_" prefix, tự động thêm vào
        if (!id.startsWith("act_")) {
          id = "act_" + id;
        }
        return id;
      })
      .filter(function(id) { return id && id.length > 4; }); // Lọc bỏ rỗng hoặc quá ngắn
    
    Logger.log("✅ Đã đọc " + settings["AD_ACCOUNT_IDS"].length + " tài khoản quảng cáo từ CaiDat: " + 
               settings["AD_ACCOUNT_IDS"].join(", "));
    
    if (settings["AD_ACCOUNT_IDS"].length === 0) {
      Logger.log("⚠️ CẢNH BÁO: AD_ACCOUNT_IDS trong CaiDat không hợp lệ (rỗng hoặc format sai)!");
    }
  } else {
    // Nếu CaiDat không có AD_ACCOUNT_IDS → để mảng rỗng và log cảnh báo
    settings["AD_ACCOUNT_IDS"] = [];
    Logger.log("⚠️ KHÔNG TÌM THẤY AD_ACCOUNT_IDS trong CaiDat. Vui lòng cấu hình AD_ACCOUNT_IDS trong sheet CaiDat để chạy automation.");
  }
  
  // Lấy delay
  settings["DELAY_KHI_TAT_BATCH"] = parseInt(settings["DELAY_KHI_TAT_BATCH"] || "1000", 10);
  
  Logger.log("Đã tải Cài đặt Hệ thống thành công.");
  return settings;
}

/**
 * Hàm Helper: Tự động trích xuất Prefix từ LogicRules headers (hàng 1)
 * Format: "act_123456|PX" → trích xuất "PX"
 * Trả về array các prefix duy nhất (không trùng lặp)
 */
function extractPrefixesFromLogicRules_() {
  // ⚠️ TỐI ƯU: Cache kết quả trong 60 giây để tránh đọc sheet nhiều lần
  try {
    var cache = CacheService.getScriptCache();
    var cacheKey = 'LOGIC_RULES_PREFIXES_EXTRACTED';
    var cached = cache.get(cacheKey);
    
    if (cached !== null && cached !== '') {
      try {
        var prefixes = JSON.parse(cached);
        Logger.log("✅ Đã lấy prefixes từ cache (" + prefixes.length + " prefixes)");
        return prefixes;
      } catch (parseErr) {
        Logger.log("⚠️ Lỗi parse cache, đọc lại từ sheet");
      }
    }
  } catch (cacheErr) {
    Logger.log("⚠️ Lỗi khi kiểm tra cache: " + cacheErr.message);
  }
  
  var prefixes = [];
  try {
    var ss = getSpreadsheet_ ? getSpreadsheet_() : SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME_LOGIC);
    if (!sheet) {
      Logger.log("⚠️ Không tìm thấy sheet LogicRules để trích xuất Prefixes");
      return prefixes;
    }
    
    var data = sheet.getDataRange().getValues();
    if (data.length === 0) return prefixes;
    
    var headers = data[0]; // Hàng 1
    // Bỏ qua cột A (KEY) và cột B (Ghi chú), bắt đầu từ cột C (index 2)
    for (var j = (COLUMN_START_LOGIC_RULES - 1); j < headers.length; j++) {
      var header = String(headers[j] || '').trim();
      if (!header || header === '') continue;
      
      // Format header: "act_123456|PX" hoặc "DEFAULT|DEFAULT"
      // Trích xuất phần prefix (sau dấu |)
      var parts = header.split('|');
      if (parts.length >= 2) {
        var prefixPart = parts[1].trim();
        // Bỏ qua DEFAULT và các giá trị rỗng
        if (prefixPart && prefixPart !== 'DEFAULT' && prefixPart.length > 0) {
          // Thêm vào mảng nếu chưa có
          var upperPrefix = prefixPart.toUpperCase();
          if (prefixes.indexOf(upperPrefix) < 0) {
            prefixes.push(upperPrefix);
          }
        }
      }
    }
    
    // Cache kết quả trong 60 giây
    try {
      var cache = CacheService.getScriptCache();
      cache.put('LOGIC_RULES_PREFIXES_EXTRACTED', JSON.stringify(prefixes), 60);
    } catch (cacheErr) {
      Logger.log("⚠️ Lỗi cache prefixes: " + cacheErr.message);
    }
    
    Logger.log("📋 Đã trích xuất " + prefixes.length + " prefix từ LogicRules headers: " + prefixes.join(", "));
  } catch (e) {
    Logger.log("⚠️ Lỗi khi trích xuất Prefixes từ LogicRules: " + e.message);
  }
  
  return prefixes;
}

/**
 * Hàm Helper: Tự động trích xuất Account IDs từ LogicRules headers (hàng 1)
 * Format: "act_123456|PX" → trích xuất "act_123456"
 */
function extractAccountIdsFromLogicRules_() {
  // ⚠️ TỐI ƯU: Cache kết quả trong 60 giây để tránh đọc sheet nhiều lần
  try {
    var cache = CacheService.getScriptCache();
    var cacheKey = 'LOGIC_RULES_ACCOUNT_IDS_EXTRACTED';
    var cached = cache.get(cacheKey);
    
    if (cached !== null && cached !== '') {
      try {
        var accountIds = JSON.parse(cached);
        Logger.log("✅ Đã lấy account IDs từ cache (" + accountIds.length + " accounts)");
        return accountIds;
      } catch (parseErr) {
        Logger.log("⚠️ Lỗi parse cache, đọc lại từ sheet");
      }
    }
  } catch (cacheErr) {
    Logger.log("⚠️ Lỗi khi kiểm tra cache: " + cacheErr.message);
  }
  
  var accountIds = [];
  try {
    var ss = getSpreadsheet_ ? getSpreadsheet_() : SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME_LOGIC);
    if (!sheet) {
      Logger.log("⚠️ Không tìm thấy sheet LogicRules để trích xuất Account IDs");
      return accountIds;
    }
    
    var data = sheet.getDataRange().getValues();
    if (data.length === 0) return accountIds;
    
    var headers = data[0]; // Hàng 1
    // Bỏ qua cột A (KEY) và cột B (Ghi chú), bắt đầu từ cột C (index 2)
    for (var j = (COLUMN_START_LOGIC_RULES - 1); j < headers.length; j++) {
      var header = String(headers[j] || '').trim();
      if (!header || header === '') continue;
      
      // Format header: "act_123456|PX" hoặc "DEFAULT|DEFAULT"
      // Trích xuất phần account ID (trước dấu |)
      var parts = header.split('|');
      if (parts.length >= 1) {
        var accountPart = parts[0].trim();
        // Bỏ qua DEFAULT và các giá trị không phải account ID
        if (accountPart && accountPart !== 'DEFAULT' && accountPart.startsWith('act_')) {
          // Đảm bảo có prefix act_
          if (accountIds.indexOf(accountPart) < 0) {
            accountIds.push(accountPart);
          }
        }
      }
    }
    
    // Cache kết quả trong 60 giây
    try {
      var cache = CacheService.getScriptCache();
      cache.put('LOGIC_RULES_ACCOUNT_IDS_EXTRACTED', JSON.stringify(accountIds), 60);
    } catch (cacheErr) {
      Logger.log("⚠️ Lỗi cache account IDs: " + cacheErr.message);
    }
    
    Logger.log("📋 Đã trích xuất " + accountIds.length + " account IDs từ LogicRules headers");
  } catch (e) {
    Logger.log("⚠️ Lỗi khi trích xuất Account IDs từ LogicRules: " + e.message);
  }
  
  return accountIds;
}

/**
 * Hàm 2: Xây dựng một Map tra cứu logic
 * Đọc từ trang `LogicRules` (Dạng Ma trận)
 */
function buildLogicMap() {
  var ss = getSpreadsheet_ ? getSpreadsheet_() : SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME_LOGIC) || ss.getSheetByName(SHEET_NAME_SYSTEM);
  if (!sheet) {
    throw new Error("LỖI: Không tìm thấy trang logic '" + SHEET_NAME_LOGIC + "' hoặc '" + SHEET_NAME_SYSTEM + "'");
  }
  
  var data = sheet.getDataRange().getValues();
  var headers = data.shift(); // Lấy hàng 1 (Key, Ghi chú, DEFAULT|DEFAULT, act_123|PX, ...)
  
  var logicMap = {}; // { "act_123|PX": { SL_1_SPEND: 50000, ... }, "DEFAULT|DEFAULT": {...} }

  // 1. Lặp qua các CỘT quy tắc (từ Cột C trở đi)
  for (var j = (COLUMN_START_LOGIC_RULES - 1); j < headers.length; j++) {
    var ruleKey = headers[j]; // (ví dụ: "act_121...|PX" hoặc "DEFAULT|DEFAULT")
    if (!ruleKey || ruleKey.trim() === "") continue;

    logicMap[ruleKey.trim()] = {}; // Tạo 1 object cho quy tắc này

    // 2. Lặp qua các HÀNG Key (Cột A)
    for (var i = 0; i < data.length; i++) { // Bắt đầu từ hàng 2 (index 0 trong mảng 'data')
       var logicName = data[i][0]; // (ví dụ: "SL_1_SPEND")
       if (logicName && logicName.trim() !== "" && !logicName.startsWith("LOGIC")) {
          var logicValue = data[i][j]; // Lấy giá trị ở ô (i, j)
          // Xử lý giá trị rỗng/null - chỉ lưu nếu có giá trị hợp lệ
          // QUAN TRỌNG: Kiểm tra cả số 0 (0 là giá trị hợp lệ cho một số trường)
          if (logicValue !== null && logicValue !== undefined) {
            // Chuyển đổi sang string để kiểm tra rỗng (tránh trường hợp "   " là rỗng)
            var strValue = String(logicValue).trim();
            // Lưu nếu không rỗng hoặc là số 0
            if (strValue !== "" || logicValue === 0 || logicValue === "0") {
              // Nếu là số, lưu dạng số; nếu không, lưu dạng string
              var numValue = parseFloat(strValue.replace(/[^\d,\.\-]/g, '').replace(',', '.'));
              logicMap[ruleKey.trim()][logicName.trim()] = (!isNaN(numValue) && strValue !== "") ? numValue : logicValue;
            }
          }
          // Nếu giá trị rỗng, không lưu vào map (sẽ là undefined khi pickKey)
       }
    }
  }
  
  // TỐI ƯU: Loại bỏ Logger.log không cần thiết để tăng hiệu suất
  // var keys = Object.keys(logicMap);
  // Logger.log("Đã xây dựng Logic Map thành công (" + keys.length + " quy tắc). Ví dụ: " + (keys[0] || 'n/a'));
  
  return logicMap;
}


/**
 * Hàm 3: Tra cứu logic cho một Ad cụ thể
 */
function getLogicForRow(logicMap, accountId, campaignName) {
  var prefix = getPrefixTuTen(campaignName);
  var acct = String(accountId || '').trim();
  var actId = acct.indexOf('act_') === 0 ? acct : ('act_' + acct);
  
  // Debug log cho prefix matching (đặc biệt với LAKVDH)
  var shouldDebug = prefix && (prefix.indexOf('LAKVDH') >= 0 || prefix.indexOf('LAK') >= 0);
  if (shouldDebug) {
    Logger.log("🔍 getLogicForRow - Account: " + accountId + ", Campaign: " + campaignName + ", Extracted Prefix: " + prefix);
  }

  // Helper: Tìm prefix match linh hoạt (ví dụ: "DHHL1" match với "DHHL", "LAKVDHNT80" match với "LAKVDH")
  function findMatchingPrefixKey(baseKey, prefixToMatch) {
    // 1. Thử exact match trước
    var exactKey = baseKey + "|" + prefixToMatch;
    if (logicMap[exactKey]) {
      return exactKey;
    }
    
    // 2. Thử match prefix là substring (ưu tiên prefix trong logicMap ngắn hơn và là phần đầu của prefixToMatch)
    // Ví dụ: "LAKVDHNT80" (prefixToMatch) sẽ match với "LAKVDH" (keyPrefix trong logicMap)
    var allKeys = Object.keys(logicMap);
    var bestMatch = null;
    var bestMatchLength = 0;
    
    for (var i = 0; i < allKeys.length; i++) {
      var key = allKeys[i];
      if (key.indexOf(baseKey + "|") === 0) {
        var keyPrefix = key.split("|")[1];
        if (!keyPrefix) continue;
        
        // Case 1: prefixToMatch bắt đầu bằng keyPrefix (ưu tiên cao nhất)
        // Ví dụ: "LAKVDHNT80" bắt đầu bằng "LAKVDH"
        if (prefixToMatch.indexOf(keyPrefix) === 0) {
          // Ưu tiên prefix dài hơn (ví dụ: "LAKVDH" tốt hơn "LAK")
          if (keyPrefix.length > bestMatchLength) {
            bestMatch = key;
            bestMatchLength = keyPrefix.length;
          }
        }
        
        // Case 2: keyPrefix bắt đầu bằng prefixToMatch (ít phổ biến hơn)
        // Ví dụ: "DHHL1" bắt đầu bằng "DHHL"
        if (keyPrefix.indexOf(prefixToMatch) === 0 && prefixToMatch.length > bestMatchLength) {
          bestMatch = key;
          bestMatchLength = prefixToMatch.length;
        }
      }
    }
    
    return bestMatch;
  }

  // 1. Thử tìm chính xác: "act_123|PX"
  var key = actId + "|" + prefix;
  if (logicMap[key]) {
    if (shouldDebug) {
      Logger.log("   ✅ Tìm thấy logic exact match: " + key);
    }
    return logicMap[key];
  }
  if (shouldDebug) {
    Logger.log("   ❌ Không tìm thấy exact match: " + key);
  }

  // 1b. Thử match prefix linh hoạt cho account+prefix
  var flexibleKey = findMatchingPrefixKey(actId, prefix);
  if (flexibleKey && logicMap[flexibleKey]) {
    if (shouldDebug) {
      Logger.log("   ✅ Tìm thấy logic flexible match: " + flexibleKey + " (từ prefix: " + prefix + ")");
    }
    return logicMap[flexibleKey];
  }
  if (shouldDebug && flexibleKey) {
    Logger.log("   ⚠️ Tìm thấy flexibleKey nhưng không có trong logicMap: " + flexibleKey);
  }

  // 2. Thử theo Account có act_: "act_123|DEFAULT"
  key = actId + "|DEFAULT";
  if (logicMap[key]) {
    // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
    return logicMap[key];
  }

  // 3. Thử theo Account numeric-only (phòng khi sheet dùng số trần): "123|PX" rồi "123|DEFAULT"
  if (logicMap[acct + '|' + prefix]) {
    // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
    return logicMap[acct + '|' + prefix];
  }
  
  // 3b. Thử match prefix linh hoạt cho numeric account
  flexibleKey = findMatchingPrefixKey(acct, prefix);
  if (flexibleKey && logicMap[flexibleKey]) {
    // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
    return logicMap[flexibleKey];
  }
  
  if (logicMap[acct + '|DEFAULT']) {
    // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
    return logicMap[acct + '|DEFAULT'];
  }

  // 4. Thử theo Prefix: "DEFAULT|PX"
  key = "DEFAULT|" + prefix;
  if (logicMap[key]) {
    // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
    return logicMap[key];
  }
  
  // 4b. Thử match prefix linh hoạt cho DEFAULT|prefix
  flexibleKey = findMatchingPrefixKey("DEFAULT", prefix);
  if (flexibleKey && logicMap[flexibleKey]) {
    // TỐI ƯU: Loại bỏ Logger.log trong vòng lặp để tăng hiệu suất
    return logicMap[flexibleKey];
  }
  
  // 5. Dùng mặc định: "DEFAULT|DEFAULT"
  key = "DEFAULT|DEFAULT";
  if (logicMap[key]) {
    if (shouldDebug) {
      Logger.log("   ⚠️ Dùng DEFAULT|DEFAULT logic");
    }
    return logicMap[key];
  }

  // 6. Không tìm thấy logic - Log chi tiết cho debugging
  if (shouldDebug) {
    Logger.log("   ❌ KHÔNG TÌM THẤY LOGIC cho account=" + actId + " prefix=" + prefix);
    Logger.log("   Đã thử: " + actId + "|" + prefix + ", " + acct + "|" + prefix + ", DEFAULT|" + prefix + ", DEFAULT|DEFAULT");
    var sampleKeys = Object.keys(logicMap).slice(0, 10);
    Logger.log("   Sample logic keys: " + sampleKeys.join(", "));
  }
  return null;
}

/**
 * Tạo sheet LogicRules mẫu, với cột cho 2 tài khoản bạn cung cấp:
 *  - act_2827767517395636|FL, act_2827767517395636|NM
 *  - act_723686686812438|PX, act_723686686812438|TL
 * Gồm các hàng khóa cho GĐ1..GĐ4 và Frequency. Véctơ DEFAULT|DEFAULT cũng có.
 */
function taoLogicRulesMau() {
  var ss = getSpreadsheet_ ? getSpreadsheet_() : SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME_LOGIC);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME_LOGIC);
  } else {
    sheet.clearContents();
  }

  var headers = [
    'KEY','Ghi chú',
    'DEFAULT|DEFAULT',
    'act_2827767517395636|FL',
    'act_2827767517395636|NM',
    'act_723686686812438|PX',
    'act_723686686812438|TL'
  ];

  var rows = [
    // ===== PHẦN 1: GIAI ĐOẠN 1-4 VÀ FREQUENCY =====
    ['', '', '', '', '', '', ''], // Hàng trống
    ['GIAI ĐOẠN 1 - LỌC DATA (Stop Loss)', '', '', '', '', '', ''],
    ['SL_GIAI_DOAN_1_SPEND', 'Ngưỡng chi tiêu GĐ1 (lọc Data)', '', '', '', '', ''],
    ['SL_GIAI_DOAN_1_DATA',  'Kết Quả tối thiểu (Mess+Cmt) ở GĐ1', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['GIAI ĐOẠN 2 - CẮT LỖ 2 (Spend & Giá DATA)', '', '', '', '', '', ''],
    ['SL_GIAI_DOAN_2_SPEND', 'Ngưỡng chi tiêu GĐ2 (nếu > ngưỡng này thì kiểm tra)', '', '', '', '', ''],
    ['SL_GIAI_DOAN_2_GIA_DATA', 'Ngưỡng Giá DATA tối đa GĐ2 (nếu > ngưỡng này thì tắt)', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['GIAI ĐOẠN 3 - ĐÁNH GIÁ CPL', '', '', '', '', '', ''],
    ['SL_GIAI_DOAN_3_MIN_LEADS', 'Leads tối thiểu để đánh giá CPL (GĐ3)', '', '', '', '', ''],
    ['SL_GIAI_DOAN_3_MAX_CPL',   'CPL tối đa (GĐ3)', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['GIAI ĐOẠN 4 - ĐÁNH GIÁ CPA', '', '', '', '', '', ''],
    ['SL_GIAI_DOAN_4_MIN_PURCHASE', 'Purchase tối thiểu để đánh giá CPA (GĐ4)', '', '', '', '', ''],
    ['SL_GIAI_DOAN_4_MAX_CPA',     'CPA tối đa (GĐ4)', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['CHỐNG MỎI - FREQUENCY', '', '', '', '', '', ''],
    ['SL_MAX_FREQUENCY', 'Frequency tối đa (chống mỏi)', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['BẬT LẠI QUẢNG CÁO (Resume)', '', '', '', '', '', ''],
    ['RESUME_SPEND', 'Ngưỡng chi tiêu tối thiểu để bật lại (Spend > ngưỡng này)', '', '', '', '', ''],
    ['RESUME_DATA', 'Kết Quả tối thiểu để bật lại (Kết Quả > ngưỡng này). Để 0 = cho phép Kết Quả > 0', '', '', '', '', ''],
    ['RESUME_GIA_DATA', 'Ngưỡng Giá DATA tối đa để bật lại (Giá DATA < ngưỡng này). Nếu để trống, dùng SL_GIAI_DOAN_2_GIA_DATA', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['', '', '', '', '', '', ''], // Hàng trống
    // ===== PHẦN 2: LOGIC NGOẠI LỆ - CHECKOUT CÙNG NGÀY VỚI TIN NHẮN =====
    ['LOGIC NGOẠI LỆ - CHECKOUT CÙNG NGÀY (Áp dụng cho GĐ1, GĐ2, Bật lại)', '', '', '', '', '', ''],
    ['MAX_CP_CHECKOUT', 'Chi phí trên mỗi lượt bắt đầu thanh toán tối đa (dùng cho logic ngoại lệ). Điều kiện: 1) Checkout và tin nhắn CÙNG NGÀY (BẮT BUỘC) VÀ 2) CP Checkout <= ngưỡng này → GIỮ LẠI/BẬT LẠI', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['LƯU Ý QUAN TRỌNG:', 'Logic ngoại lệ CHỈ áp dụng khi: 1) Ngày có checkout TRÙNG với ngày có tin nhắn (BẮT BUỘC - kiểm tra TRƯỚC) VÀ 2) Có checkout > 0 VÀ 3) CP Checkout <= MAX_CP_CHECKOUT. Nếu không cùng ngày → KHÔNG áp dụng ngoại lệ (tránh nhóm quảng cáo ảo)', '', '', '', '', ''],
    ['', '', '', '', '', '', ''], // Hàng trống
    ['', '', '', '', '', '', ''], // Hàng trống
    // ===== PHẦN 3: LOGIC LỌC 7 NGÀY =====
    ['LOGIC LỌC 7 NGÀY (Đánh giá tổng hợp 7 ngày qua)', '', '', '', '', '', ''],
    ['MAX_GIÁ_DATA', 'Giá DATA tối đa cho phép (7 ngày)', '', '', '', '', ''],
    ['MIN_KET_QUA', 'Kết Quả tối thiểu (Mess+Cmt) cho phép (7 ngày)', '', '', '', '', ''],
    ['MAX_CP_PURCHASE', 'Chi phí trên mỗi lượt mua tối đa (7 ngày)', '', '', '', '', ''],
    ['MIN_PURCHASES', 'Tổng số lượt mua tối thiểu (7 ngày)', '', '', '', '', '']
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);

  // Định dạng: In đậm hàng tiêu đề và các hàng ghi chú logic
  sheet.getRange('A1:' + sheet.getRange(1, headers.length).getA1Notation()).setFontWeight('bold');
  
  // In đậm các hàng ghi chú logic (tìm các hàng có KEY rỗng nhưng có text ở cột B)
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var key = row[0] || '';
    var note = row[1] || '';
    // Nếu là hàng tiêu đề logic (key rỗng nhưng có note)
    if (!key && note && (
      note.indexOf('GIAI ĐOẠN') >= 0 ||
      note.indexOf('CHỐNG MỎI') >= 0 ||
      note.indexOf('BẬT LẠI') >= 0 ||
      note.indexOf('LOGIC NGOẠI LỆ') >= 0 ||
      note.indexOf('LOGIC LỌC 7 NGÀY') >= 0 ||
      note.indexOf('LƯU Ý:') >= 0
    )) {
      sheet.getRange(i + 2, 1, 1, headers.length).setFontWeight('bold');
      sheet.getRange(i + 2, 1, 1, headers.length).setFontStyle('italic');
      sheet.getRange(i + 2, 1, 1, headers.length).setBackground('#E8F0FE');
    }
  }
  
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, headers.length);

  Logger.log('Đã tạo LogicRules mẫu. Vui lòng điền ngưỡng vào các cột tài khoản/prefix.');
}