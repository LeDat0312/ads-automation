/**
 * Save logic rules to LogicRules sheet
 * @param {Array} logicRules - Array of logic rule objects
 * @param {string} accountId - Facebook Ad Account ID
 * @param {string} prefix - Campaign prefix
 * @returns {number} - Number of rules saved
 */
function saveLogicRulesToSheet(logicRules, accountId, prefix) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("LogicRules");
    
    if (!sheet) {
      throw new Error("Không tìm thấy sheet LogicRules");
    }
    
    // Normalize account ID (thêm act_ nếu thiếu)
    var normalizedAccountId = String(accountId || '').trim();
    if (normalizedAccountId && !normalizedAccountId.startsWith("act_")) {
      normalizedAccountId = "act_" + normalizedAccountId;
    }
    if (!normalizedAccountId) {
      normalizedAccountId = "DEFAULT";
    }
    
    // Normalize prefix
    var normalizedPrefix = String(prefix || '').trim().toUpperCase();
    if (!normalizedPrefix) {
      normalizedPrefix = "DEFAULT";
    }
    
    // Column header: account_id|prefix
    var columnHeader = normalizedAccountId + "|" + normalizedPrefix;
    
    // Get all data
    var data = sheet.getDataRange().getValues();
    var headers = data[0] || [];
    
    // Find or create column for account_id|prefix
    var columnIndex = -1;
    for (var i = 0; i < headers.length; i++) {
      if (String(headers[i] || '').trim() === columnHeader) {
        columnIndex = i;
        break;
      }
    }
    
    // Create column if not found
    if (columnIndex === -1) {
      columnIndex = headers.length;
      sheet.getRange(1, columnIndex + 1).setValue(columnHeader);
      Logger.log("✅ Đã tạo cột mới: " + columnHeader);
    }
    
    // Map logic keys to row indices
    var keyToRowMap = {};
    for (var i = 1; i < data.length; i++) {
      var key = String(data[i][0] || '').trim();
      if (key) {
        keyToRowMap[key] = i + 1; // Row index (1-based)
      }
    }
    
    // Save each logic rule
    var savedCount = 0;
    logicRules.forEach(function(rule) {
      // Save condition_spend to SL_GIAI_DOAN_1_SPEND (GĐ1)
      if (rule.condition_spend !== undefined && rule.condition_spend !== null) {
        var spendKey = "SL_GIAI_DOAN_1_SPEND";
        var spendRowIndex = keyToRowMap[spendKey];
        if (spendRowIndex) {
          sheet.getRange(spendRowIndex, columnIndex + 1).setValue(rule.condition_spend);
          savedCount++;
        } else {
          Logger.log("⚠️ Không tìm thấy key: " + spendKey);
        }
      }
      
      // Save condition_results to SL_GIAI_DOAN_1_DATA (GĐ1)
      if (rule.condition_results !== undefined && rule.condition_results !== null) {
        var dataKey = "SL_GIAI_DOAN_1_DATA";
        var dataRowIndex = keyToRowMap[dataKey];
        if (dataRowIndex) {
          sheet.getRange(dataRowIndex, columnIndex + 1).setValue(rule.condition_results);
          savedCount++;
        } else {
          Logger.log("⚠️ Không tìm thấy key: " + dataKey);
        }
      }
      
      // Save condition_gia_data to SL_GIAI_DOAN_2_GIA_DATA (GĐ2)
      if (rule.condition_gia_data !== undefined && rule.condition_gia_data !== null) {
        var giaDataKey = "SL_GIAI_DOAN_2_GIA_DATA";
        var giaDataRowIndex = keyToRowMap[giaDataKey];
        if (giaDataRowIndex) {
          sheet.getRange(giaDataRowIndex, columnIndex + 1).setValue(rule.condition_gia_data);
          savedCount++;
        } else {
          Logger.log("⚠️ Không tìm thấy key: " + giaDataKey);
        }
      }
      
      // Save condition_roas (nếu có)
      if (rule.condition_roas !== undefined && rule.condition_roas !== null) {
        Logger.log("⚠️ ROAS condition chưa được map - cần thêm logic mapping");
      }
    });
    
    // Clear cache để đảm bảo đọc lại logic rules mới
    try {
      var cache = CacheService.getScriptCache();
      cache.remove('LOGIC_RULES_PREFIXES_EXTRACTED');
      cache.remove('LOGIC_RULES_ACCOUNT_IDS_EXTRACTED');
    } catch (cacheErr) {
      Logger.log("⚠️ Lỗi clear cache: " + cacheErr.message);
    }
    
    Logger.log("✅ Đã lưu " + savedCount + " giá trị vào LogicRules sheet cho " + columnHeader);
    return savedCount;
  } catch (error) {
    Logger.log("🚨 Lỗi trong saveLogicRulesToSheet: " + error.message);
    throw error;
  }
}


