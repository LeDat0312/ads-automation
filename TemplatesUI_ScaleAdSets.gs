/**
 * SCALE AD SETS - CUSTOMIZATION UI
 * Giao diện tùy chỉnh sâu cho Scale Ad Sets như Birch
 */

/**
 * Serve Scale Ad Sets customization page
 */
function doGetScaleAdSets(e) {
  try {
    var htmlTemplate = HtmlService.createTemplateFromFile('TemplatesUI_ScaleAdSets_HTML');
    htmlTemplate.ruleData = e.parameter.ruleId ? getRuleData(e.parameter.ruleId) : null;
    var htmlOutput = htmlTemplate.evaluate()
      .setTitle('Scale Ad Sets - Customize')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
    return htmlOutput;
  } catch (error) {
    return HtmlService.createHtmlOutput(
      "<html><body><h1>Error</h1><p>" + error.message + "</p></body></html>"
    );
  }
}

/**
 * Get list of connected Facebook ad accounts
 * @returns {Array} Array of account objects {id, name}
 */
function getConnectedAccounts() {
  try {
    var settings = getSettingsSafe_();
    var accountIds = settings['AD_ACCOUNT_IDS'] || [];
    
    // Get account names from Facebook API
    var accounts = [];
    var accessToken = settings['ACCESS_TOKEN'];
    
    if (!accessToken) {
      return accounts;
    }
    
    // For each account ID, get account name
    for (var i = 0; i < accountIds.length; i++) {
      try {
        var accountId = accountIds[i];
        var url = 'https://graph.facebook.com/v24.0/' + accountId +
                  '?fields=id,name,account_id' +
                  '&access_token=' + encodeURIComponent(accessToken);
        
        var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
        var json = JSON.parse(response.getContentText());
        
        if (json.id && json.name) {
          accounts.push({
            id: json.id,
            name: json.name || json.account_id || accountId
          });
        }
      } catch (e) {
        Logger.log("⚠️ Lỗi khi lấy thông tin account " + accountIds[i] + ": " + e.message);
        // Add account với ID nếu không lấy được name
        accounts.push({
          id: accountIds[i],
          name: accountIds[i]
        });
      }
    }
    
    return accounts;
  } catch (error) {
    Logger.log("🚨 Lỗi trong getConnectedAccounts: " + error.message);
    return [];
  }
}

/**
 * Get available metrics from Meta Ads or custom metrics
 * @param {string} type - 'meta', 'custom', or 'integrations'
 * @returns {Array} Array of metric objects
 */
function getAvailableMetrics(type) {
  try {
    var metrics = [];
    
    if (type === 'meta' || !type) {
      // Meta Ads standard metrics
      metrics = [
        { id: 'spend', name: 'Spend', category: 'Most common', level: 'adset' },
        { id: 'impressions', name: 'Impressions', category: 'Most common', level: 'adset' },
        { id: 'clicks', name: 'Clicks', category: 'Most common', level: 'adset' },
        { id: 'ctr', name: 'Click-through rate (CTR)', category: 'Most common', level: 'adset' },
        { id: 'cpc', name: 'Cost per click (CPC)', category: 'Most common', level: 'adset' },
        { id: 'cpm', name: 'Cost per mille (CPM)', category: 'High-level metrics', level: 'adset' },
        { id: 'roas', name: 'Return on ad spend (ROAS)', category: 'High-level metrics', level: 'adset' },
        { id: 'cpa', name: 'Cost per action (CPA)', category: 'High-level metrics', level: 'adset' },
        { id: 'cost_per_lead', name: 'Cost per lead (CPL)', category: 'High-level metrics', level: 'adset' },
        { id: 'leads', name: 'Leads', category: 'Website standard events', level: 'adset' },
        { id: 'purchases', name: 'Purchases', category: 'Website standard events', level: 'adset' },
        { id: 'revenue', name: 'Revenue', category: 'Website standard events', level: 'adset' }
      ];
    } else if (type === 'custom') {
      // Custom metrics (from LogicRules or custom definitions)
      metrics = [
        { id: 'cpl', name: 'CPL', category: 'Custom', level: 'adset' },
        { id: 'data', name: 'DATA', category: 'Custom', level: 'adset' },
        { id: 'gia_data', name: 'Giá DATA', category: 'Custom', level: 'adset' }
      ];
    }
    
    return metrics;
  } catch (error) {
    Logger.log("🚨 Lỗi trong getAvailableMetrics: " + error.message);
    return [];
  }
}

/**
 * Save rule draft
 * @param {Object} ruleData - Rule data object
 * @returns {Object} Result object
 */
function saveRuleDraft(ruleData) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('RuleDrafts') || ss.insertSheet('RuleDrafts');
    
    // Set headers if new sheet
    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, 10).setValues([[
        'ID', 'Name', 'Folder', 'Accounts', 'Filters', 'Conditions', 'Schedule', 'Timezone', 'Status', 'Created'
      ]]);
    }
    
    // Generate ID if new
    if (!ruleData.id) {
      ruleData.id = 'rule_' + new Date().getTime();
      ruleData.created = new Date();
    }
    
    // Find existing row or append new
    var data = sheet.getDataRange().getValues();
    var rowIndex = -1;
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] === ruleData.id) {
        rowIndex = i + 1;
        break;
      }
    }
    
    if (rowIndex === -1) {
      rowIndex = sheet.getLastRow() + 1;
    }
    
    // Save data
    sheet.getRange(rowIndex, 1, 1, 10).setValues([[
      ruleData.id,
      ruleData.name || 'Untitled Rule',
      ruleData.folder || '',
      JSON.stringify(ruleData.accounts || []),
      JSON.stringify(ruleData.filters || []),
      JSON.stringify(ruleData.conditions || []),
      JSON.stringify(ruleData.schedule || {}),
      ruleData.timezone || 'GMT+07:00',
      'DRAFT',
      ruleData.created || new Date()
    ]]);
    
    return {
      success: true,
      id: ruleData.id,
      message: 'Draft saved successfully'
    };
  } catch (error) {
    Logger.log("🚨 Lỗi trong saveRuleDraft: " + error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Set rule live
 * @param {Object} ruleData - Rule data object
 * @returns {Object} Result object
 */
function setRuleLive(ruleData) {
  try {
    // Save to RuleDrafts with status LIVE
    var result = saveRuleDraft(ruleData);
    if (!result.success) {
      return result;
    }
    
    // Update status to LIVE
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('RuleDrafts');
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var i = 1; i < data.length; i++) {
        if (data[i][0] === result.id) {
          sheet.getRange(i + 1, 9).setValue('LIVE');
          break;
        }
      }
    }
    
    // Convert conditions to LogicRules format and save
    convertRuleToLogicRules(ruleData);
    
    return {
      success: true,
      id: result.id,
      message: 'Rule set live successfully'
    };
  } catch (error) {
    Logger.log("🚨 Lỗi trong setRuleLive: " + error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Convert rule conditions to LogicRules format and save
 * @param {Object} ruleData - Rule data object
 */
function convertRuleToLogicRules(ruleData) {
  try {
    // This function converts the complex rule conditions to LogicRules sheet format
    // For now, it's a placeholder - needs to be implemented based on your LogicRules structure
    
    Logger.log("✅ Converting rule to LogicRules format: " + ruleData.name);
    
    // TODO: Implement conversion logic
    // - Map conditions to LogicRules keys
    // - Save to LogicRules sheet for each account|prefix
    // - Handle multiple conditions, timeframes, comparisons
    
  } catch (error) {
    Logger.log("🚨 Lỗi trong convertRuleToLogicRules: " + error.message);
    throw error;
  }
}

/**
 * Get rule data by ID
 * @param {string} ruleId - Rule ID
 * @returns {Object} Rule data object
 */
function getRuleData(ruleId) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('RuleDrafts');
    
    if (!sheet) {
      return null;
    }
    
    var data = sheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] === ruleId) {
        return {
          id: data[i][0],
          name: data[i][1],
          folder: data[i][2],
          accounts: JSON.parse(data[i][3] || '[]'),
          filters: JSON.parse(data[i][4] || '[]'),
          conditions: JSON.parse(data[i][5] || '[]'),
          schedule: JSON.parse(data[i][6] || '{}'),
          timezone: data[i][7],
          status: data[i][8],
          created: data[i][9]
        };
      }
    }
    
    return null;
  } catch (error) {
    Logger.log("🚨 Lỗi trong getRuleData: " + error.message);
    return null;
  }
}

/**
 * Create Scale Ad Sets rules (2 rules: Increase and Decrease)
 * @param {string} folderName - Folder name (if new folder)
 * @param {string} existingFolder - Existing folder ID (if adding to existing)
 * @returns {Object} Result object
 */
function createScaleAdSetsRules(folderName, existingFolder) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var foldersSheet = ss.getSheetByName('RuleFolders') || ss.insertSheet('RuleFolders');
    
    // Set headers if new sheet
    if (foldersSheet.getLastRow() === 0) {
      foldersSheet.getRange(1, 1, 1, 3).setValues([['ID', 'Name', 'Rules']]);
    }
    
    var folderId = existingFolder || 'folder_' + new Date().getTime();
    
    // Create or update folder
    if (!existingFolder) {
      foldersSheet.appendRow([folderId, folderName || 'Scale Ad Sets', '[]']);
    }
    
    // Create 2 rules
    var rule1 = {
      id: 'rule_increase_' + new Date().getTime(),
      name: 'Increase ad sets budget',
      folder: folderId,
      accounts: [],
      filters: ['Ad sets', 'Ad set status is active'],
      conditions: [],
      schedule: { type: 'interval', minutes: 60 },
      timezone: 'GMT+07:00',
      status: 'DRAFT'
    };
    
    var rule2 = {
      id: 'rule_decrease_' + new Date().getTime(),
      name: 'Decrease budget for underperformers',
      folder: folderId,
      accounts: [],
      filters: ['Ad sets', 'Ad set status is active'],
      conditions: [],
      schedule: { type: 'interval', minutes: 60 },
      timezone: 'GMT+07:00',
      status: 'DRAFT'
    };
    
    // Save rules
    saveRuleDraft(rule1);
    saveRuleDraft(rule2);
    
    // Update folder rules list
    var data = foldersSheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] === folderId) {
        var rules = JSON.parse(data[i][2] || '[]');
        rules.push(rule1.id, rule2.id);
        foldersSheet.getRange(i + 1, 3).setValue(JSON.stringify(rules));
        break;
      }
    }
    
    return {
      success: true,
      folderId: folderId,
      rules: [rule1.id, rule2.id],
      message: 'Rules created successfully'
    };
  } catch (error) {
    Logger.log("🚨 Lỗi trong createScaleAdSetsRules: " + error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get all rule folders
 * @returns {Array} Array of folder objects
 */
function getAllRuleFolders() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('RuleFolders');
    
    if (!sheet || sheet.getLastRow() === 0) {
      return [];
    }
    
    var data = sheet.getDataRange().getValues();
    var folders = [];
    
    for (var i = 1; i < data.length; i++) {
      folders.push({
        id: data[i][0],
        name: data[i][1],
        rules: JSON.parse(data[i][2] || '[]')
      });
    }
    
    return folders;
  } catch (error) {
    Logger.log("🚨 Lỗi trong getAllRuleFolders: " + error.message);
    return [];
  }
}

