/**
 * MAKE.COM + GOOGLE APPS SCRIPT INTEGRATION
 * 
 * Thêm file này vào Google Apps Script project
 * Deploy as Web App để Make.com có thể gọi
 */

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
        var amount = params.amount; // Số tiền tăng/giảm
        var action_type = params.action_type; // 'increase', 'decrease', hoặc 'set'
        result = adjustAdsetBudget(accountId, adsetId, amount, action_type);
        break;
        
      case 'get_status':
        // Lấy trạng thái
        result = getAutomationStatus();
        break;
        
      case 'get_ad_performance':
        // Lấy performance data (cho AI analysis)
        var accountId = params.account_id;
        var datePreset = params.date_preset || 'yesterday';
        result = getAdPerformanceData(accountId, datePreset);
        break;
        
      default:
        result = { success: false, message: "Unknown action: " + action };
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
 * ⚠️ ĐÃ ĐỔI TÊN: doGet() → doGetMakeCom() để tránh conflict với TemplatesUI.gs
 */
function doGetMakeCom(e) {
  var action = e.parameter.action || 'status';
  
  if (action === 'status') {
    var status = getAutomationStatus();
    return ContentService.createTextOutput(JSON.stringify(status))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput("OK");
}

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
    
    if (!adsetIds || adsetIds.length === 0) {
      return { success: false, message: "No adset IDs provided" };
    }
    
    var successCount = 0;
    var errorCount = 0;
    var errors = [];
    var delayMs = parseInt(settings['DELAY_KHI_TAT_BATCH'] || 1000);
    
    for (var i = 0; i < adsetIds.length; i++) {
      var adsetId = adsetIds[i];
      try {
        var url = 'https://graph.facebook.com/v18.0/' + adsetId;
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
        
        if (result.success !== false) {
          successCount++;
        } else {
          errorCount++;
          errors.push({ adset_id: adsetId, error: result.error || 'Unknown error' });
        }
        
        // Delay giữa các requests
        if (i < adsetIds.length - 1) {
          Utilities.sleep(delayMs);
        }
        
      } catch (e) {
        errorCount++;
        errors.push({ adset_id: adsetId, error: e.message });
      }
    }
    
    // Gửi thông báo Telegram
    var message = '⏸️ ĐÃ TẮT ADSETS\n\n';
    message += '✅ Thành công: ' + successCount + ' adsets\n';
    if (errorCount > 0) {
      message += '⚠️ Lỗi: ' + errorCount + ' adsets\n';
    }
    if (accountId) {
      message += '📛 Account: ' + accountId + '\n';
    }
    
    guiThongBaoTelegram(message, settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID']);
    
    return {
      success: true,
      success_count: successCount,
      error_count: errorCount,
      errors: errors
    };
    
  } catch (error) {
    Logger.log("🚨 Error in pauseAdsetsBatch: " + error.message);
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
    
    if (!adsetIds || adsetIds.length === 0) {
      return { success: false, message: "No adset IDs provided" };
    }
    
    var successCount = 0;
    var errorCount = 0;
    var errors = [];
    var delayMs = parseInt(settings['DELAY_KHI_TAT_BATCH'] || 1000);
    
    for (var i = 0; i < adsetIds.length; i++) {
      var adsetId = adsetIds[i];
      try {
        var url = 'https://graph.facebook.com/v18.0/' + adsetId;
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
        
        if (result.success !== false) {
          successCount++;
        } else {
          errorCount++;
          errors.push({ adset_id: adsetId, error: result.error || 'Unknown error' });
        }
        
        // Delay giữa các requests
        if (i < adsetIds.length - 1) {
          Utilities.sleep(delayMs);
        }
        
      } catch (e) {
        errorCount++;
        errors.push({ adset_id: adsetId, error: e.message });
      }
    }
    
    // Gửi thông báo Telegram
    var message = '▶️ ĐÃ BẬT ADSETS\n\n';
    message += '✅ Thành công: ' + successCount + ' adsets\n';
    if (errorCount > 0) {
      message += '⚠️ Lỗi: ' + errorCount + ' adsets\n';
    }
    if (accountId) {
      message += '📛 Account: ' + accountId + '\n';
    }
    
    guiThongBaoTelegram(message, settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID']);
    
    return {
      success: true,
      success_count: successCount,
      error_count: errorCount,
      errors: errors
    };
    
  } catch (error) {
    Logger.log("🚨 Error in resumeAdsetsBatch: " + error.message);
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
    
    if (!adsetId) {
      return { success: false, message: "No adset ID provided" };
    }
    
    // Lấy budget hiện tại
    var url = 'https://graph.facebook.com/v18.0/' + adsetId + '?fields=daily_budget,lifetime_budget&access_token=' + accessToken;
    var response = UrlFetchApp.fetch(url);
    var adsetData = JSON.parse(response.getContentText());
    
    if (adsetData.error) {
      return { success: false, error: adsetData.error.message };
    }
    
    var currentBudget = parseFloat(adsetData.daily_budget || adsetData.lifetime_budget || 0);
    var newBudget = currentBudget;
    
    if (actionType === 'increase') {
      newBudget = currentBudget + Math.abs(amount);
    } else if (actionType === 'decrease') {
      newBudget = Math.max(0, currentBudget - Math.abs(amount));
    } else if (actionType === 'set') {
      newBudget = amount;
    } else {
      return { success: false, message: "Invalid action_type. Use 'increase', 'decrease', or 'set'" };
    }
    
    // Round to 2 decimals
    newBudget = Math.round(newBudget * 100) / 100;
    
    // Update budget
    var updateUrl = 'https://graph.facebook.com/v18.0/' + adsetId;
    var payload = {
      daily_budget: newBudget
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
    
    if (result.error) {
      return { success: false, error: result.error.message };
    }
    
    // Gửi thông báo Telegram
    var message = '💰 ĐIỀU CHỈNH NGÂN SÁCH\n\n';
    message += '📛 Adset ID: ' + adsetId + '\n';
    message += '📊 Từ: ' + currentBudget.toLocaleString('vi-VN') + ' ₫\n';
    message += '📊 Thành: ' + newBudget.toLocaleString('vi-VN') + ' ₫\n';
    message += '📈 Thay đổi: ' + (newBudget - currentBudget).toLocaleString('vi-VN') + ' ₫\n';
    if (accountId) {
      message += '📛 Account: ' + accountId + '\n';
    }
    
    guiThongBaoTelegram(message, settings['TELEGRAM_BOT_TOKEN'], settings['TELEGRAM_CHAT_ID']);
    
    return {
      success: true,
      adset_id: adsetId,
      old_budget: currentBudget,
      new_budget: newBudget,
      change: newBudget - currentBudget,
      action_type: actionType
    };
    
  } catch (error) {
    Logger.log("🚨 Error in adjustAdsetBudget: " + error.message);
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
    Logger.log("🚨 Error in getAutomationStatus: " + error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Get ad performance data (cho AI analysis)
 */
function getAdPerformanceData(accountId, datePreset) {
  try {
    // Gọi hàm pullFacebookData() hiện có
    // Hoặc tạo hàm riêng để lấy data
    
    var settings = layCaiDatHeThong();
    var accessToken = settings['FACEBOOK_ACCESS_TOKEN'];
    
    if (!accessToken) {
      return { success: false, message: "No access token" };
    }
    
    // Lấy insights từ Facebook API
    var url = 'https://graph.facebook.com/v18.0/' + accountId + '/insights';
    url += '?level=ad';
    url += '&fields=ad_id,adset_id,adset_name,campaign_name,spend,impressions,clicks,results,ctr,cpc';
    url += '&date_preset=' + (datePreset || 'yesterday');
    url += '&access_token=' + accessToken;
    
    var response = UrlFetchApp.fetch(url);
    var data = JSON.parse(response.getContentText());
    
    if (data.error) {
      return { success: false, error: data.error.message };
    }
    
    return {
      success: true,
      account_id: accountId,
      date_preset: datePreset,
      data: data.data || [],
      total: data.data ? data.data.length : 0
    };
    
  } catch (error) {
    Logger.log("🚨 Error in getAdPerformanceData: " + error.message);
    return { success: false, error: error.message };
  }
}

