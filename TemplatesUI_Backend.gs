/**
 * ==================================================================
 * BACKEND FUNCTIONS FOR TEMPLATES UI
 * ==================================================================
 */

/**
 * Get list of ad accounts (from CaiDat or LogicRules)
 */
function getAdAccounts() {
  try {
    var accounts = [];
    
    // Try to get from CaiDat first
    try {
      if (typeof layCaiDatHeThong === 'function') {
        var settings = layCaiDatHeThong();
        if (settings["AD_ACCOUNT_IDS"] && settings["AD_ACCOUNT_IDS"].length > 0) {
          accounts = settings["AD_ACCOUNT_IDS"].map(function(id) {
            return {
              id: id,
              name: id.replace('act_', ''),
              display: id
            };
          });
        }
      }
    } catch (e) {
      Logger.log("⚠️ Lỗi đọc từ CaiDat: " + e.message);
    }
    
    // Fallback: Get from LogicRules headers
    if (accounts.length === 0) {
      try {
        if (typeof extractAccountIdsFromLogicRules_ === 'function') {
          var accountIds = extractAccountIdsFromLogicRules_();
          accounts = accountIds.map(function(id) {
            return {
              id: id,
              name: id.replace('act_', ''),
              display: id
            };
          });
        }
      } catch (e) {
        Logger.log("⚠️ Lỗi đọc từ LogicRules: " + e.message);
      }
    }
    
    return {
      success: true,
      accounts: accounts
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      accounts: []
    };
  }
}

/**
 * Get list of rules (from LogicRules sheet or Properties)
 */
function getRulesList() {
  try {
    var rules = [];
    var props = PropertiesService.getScriptProperties();
    
    // Get all rule properties (format: RULE_<id>)
    var allProps = props.getProperties();
    var ruleIds = [];
    
    for (var key in allProps) {
      if (key.startsWith('RULE_')) {
        var ruleId = key.replace('RULE_', '');
        try {
          var ruleData = JSON.parse(allProps[key]);
          ruleData.id = ruleId;
          rules.push(ruleData);
        } catch (e) {
          Logger.log("⚠️ Lỗi parse rule " + ruleId + ": " + e.message);
        }
      }
    }
    
    // Group by folder
    var folders = {};
    rules.forEach(function(rule) {
      var folderName = rule.folder || 'General';
      if (!folders[folderName]) {
        folders[folderName] = [];
      }
      folders[folderName].push(rule);
    });
    
    return {
      success: true,
      rules: rules,
      folders: folders
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      rules: [],
      folders: {}
    };
  }
}

/**
 * Save rule with full configuration
 */
function saveRule(ruleData) {
  try {
    var props = PropertiesService.getScriptProperties();
    var ruleId = ruleData.id || 'rule_' + Date.now();
    
    // Prepare rule object
    var rule = {
      id: ruleId,
      name: ruleData.name || '',
      type: ruleData.type || 'custom',
      folder: ruleData.folder || 'General',
      enabled: ruleData.enabled !== undefined ? ruleData.enabled : false,
      status: ruleData.status || 'DRAFT',
      accounts: ruleData.accounts || [],
      filters: ruleData.filters || [],
      tasks: ruleData.tasks || [],
      schedule: ruleData.schedule || { type: 'interval', value: 60 },
      timezone: ruleData.timezone || 'GMT+07:00',
      created_at: ruleData.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    // Save to Properties
    props.setProperty('RULE_' + ruleId, JSON.stringify(rule));
    
    // If rule has conditions, also save to LogicRules sheet
    if (ruleData.tasks && ruleData.tasks.length > 0) {
      try {
        saveRuleToLogicRules(rule);
      } catch (e) {
        Logger.log("⚠️ Lỗi lưu vào LogicRules: " + e.message);
      }
    }
    
    return {
      success: true,
      rule_id: ruleId,
      rule: rule
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Save rule to LogicRules sheet
 */
function saveRuleToLogicRules(rule) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("LogicRules");
    if (!sheet) {
      Logger.log("⚠️ Không tìm thấy sheet LogicRules");
      return;
    }
    
    // Process each account
    rule.accounts.forEach(function(account) {
      var accountId = account.id || account;
      var prefix = account.prefix || 'DEFAULT';
      
      // Normalize account ID
      if (!accountId.startsWith("act_")) {
        accountId = "act_" + accountId;
      }
      
      var columnHeader = accountId + "|" + prefix.toUpperCase();
      
      // Get or create column
      var data = sheet.getDataRange().getValues();
      var headers = data[0] || [];
      var columnIndex = -1;
      
      for (var i = 0; i < headers.length; i++) {
        if (String(headers[i] || '').trim() === columnHeader) {
          columnIndex = i;
          break;
        }
      }
      
      if (columnIndex === -1) {
        columnIndex = headers.length;
        sheet.getRange(1, columnIndex + 1).setValue(columnHeader);
      }
      
      // Map logic keys
      var keyToRowMap = {};
      for (var i = 1; i < data.length; i++) {
        var key = String(data[i][0] || '').trim();
        if (key) {
          keyToRowMap[key] = i + 1;
        }
      }
      
      // Save task conditions
      rule.tasks.forEach(function(task) {
        if (task.conditions) {
          task.conditions.forEach(function(condition) {
            var logicKey = mapConditionToLogicKey(condition);
            if (logicKey && keyToRowMap[logicKey]) {
              var value = condition.value || condition.threshold;
              if (value !== undefined && value !== null) {
                sheet.getRange(keyToRowMap[logicKey], columnIndex + 1).setValue(value);
              }
            }
          });
        }
      });
    });
    
    // Clear cache
    try {
      var cache = CacheService.getScriptCache();
      cache.remove('LOGIC_RULES_PREFIXES_EXTRACTED');
      cache.remove('LOGIC_RULES_ACCOUNT_IDS_EXTRACTED');
    } catch (e) {}
    
  } catch (error) {
    Logger.log("🚨 Lỗi saveRuleToLogicRules: " + error.message);
    throw error;
  }
}

/**
 * Map condition to LogicRules key
 */
function mapConditionToLogicKey(condition) {
  var metric = condition.metric || '';
  var timeframe = condition.timeframe || '';
  
  // Map common metrics to LogicRules keys
  if (metric.toLowerCase().includes('spend')) {
    if (timeframe.toLowerCase().includes('today') || timeframe.toLowerCase().includes('1 day')) {
      return 'SL_GIAI_DOAN_1_SPEND';
    }
    return 'SL_GIAI_DOAN_2_SPEND';
  }
  
  if (metric.toLowerCase().includes('data') || metric.toLowerCase().includes('results')) {
    return 'SL_GIAI_DOAN_1_DATA';
  }
  
  if (metric.toLowerCase().includes('gia data') || metric.toLowerCase().includes('cost per data')) {
    return 'SL_GIAI_DOAN_2_GIA_DATA';
  }
  
  if (metric.toLowerCase().includes('cpl') || metric.toLowerCase().includes('cost per lead')) {
    return 'SL_GIAI_DOAN_3_MAX_CPL';
  }
  
  if (metric.toLowerCase().includes('cpa') || metric.toLowerCase().includes('cost per purchase')) {
    return 'SL_GIAI_DOAN_4_MAX_CPA';
  }
  
  return null;
}

/**
 * Toggle rule on/off
 */
function toggleRule(ruleId, enabled) {
  try {
    var props = PropertiesService.getScriptProperties();
    var ruleKey = 'RULE_' + ruleId;
    var ruleData = props.getProperty(ruleKey);
    
    if (!ruleData) {
      return {
        success: false,
        error: "Rule not found"
      };
    }
    
    var rule = JSON.parse(ruleData);
    rule.enabled = enabled;
    rule.updated_at = new Date().toISOString();
    
    props.setProperty(ruleKey, JSON.stringify(rule));
    
    return {
      success: true,
      rule: rule
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Delete rule
 */
function deleteRule(ruleId) {
  try {
    var props = PropertiesService.getScriptProperties();
    props.deleteProperty('RULE_' + ruleId);
    
    return {
      success: true
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Duplicate rule
 */
function duplicateRule(ruleId) {
  try {
    var props = PropertiesService.getScriptProperties();
    var ruleKey = 'RULE_' + ruleId;
    var ruleData = props.getProperty(ruleKey);
    
    if (!ruleData) {
      return {
        success: false,
        error: "Rule not found"
      };
    }
    
    var rule = JSON.parse(ruleData);
    var newRuleId = 'rule_' + Date.now();
    rule.id = newRuleId;
    rule.name = rule.name + ' (Copy)';
    rule.status = 'DRAFT';
    rule.enabled = false;
    rule.created_at = new Date().toISOString();
    rule.updated_at = new Date().toISOString();
    
    props.setProperty('RULE_' + newRuleId, JSON.stringify(rule));
    
    return {
      success: true,
      rule_id: newRuleId,
      rule: rule
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get metrics list (Meta Ads standard metrics)
 */
function getMetricsList(category) {
  try {
    var metrics = {
      'most_common': [
        { id: 'spend', name: 'Spend', type: 'currency' },
        { id: 'impressions', name: 'Impressions', type: 'number' },
        { id: 'clicks', name: 'Clicks', type: 'number' },
        { id: 'ctr', name: 'Click Through Rate (CTR)', type: 'percentage' },
        { id: 'cpc', name: 'Cost per Click (CPC)', type: 'currency' },
        { id: 'cpm', name: 'Cost per Mille (CPM)', type: 'currency' }
      ],
      'conversions': [
        { id: 'purchases', name: 'Purchases', type: 'number' },
        { id: 'purchase_value', name: 'Purchase Value', type: 'currency' },
        { id: 'cpa', name: 'Cost per Purchase (CPA)', type: 'currency' },
        { id: 'roas', name: 'Return on Ad Spend (ROAS)', type: 'number' },
        { id: 'leads', name: 'Leads', type: 'number' },
        { id: 'cpl', name: 'Cost per Lead (CPL)', type: 'currency' }
      ],
      'engagement': [
        { id: 'post_engagements', name: 'Post Engagements', type: 'number' },
        { id: 'post_reactions', name: 'Post Reactions', type: 'number' },
        { id: 'post_comments', name: 'Post Comments', type: 'number' },
        { id: 'post_shares', name: 'Post Shares', type: 'number' }
      ],
      'messaging': [
        { id: 'messaging_conversations_started', name: 'Messaging Conversations Started', type: 'number' },
        { id: 'messaging_replies', name: 'Messaging Replies', type: 'number' }
      ],
      'custom': [
        { id: 'cpl', name: 'CPL', type: 'currency' },
        { id: 'data', name: 'DATA', type: 'number' },
        { id: 'gia_data', name: 'Giá DATA', type: 'currency' }
      ]
    };
    
    if (category && metrics[category]) {
      return {
        success: true,
        metrics: metrics[category]
      };
    }
    
    // Return all metrics
    var allMetrics = [];
    for (var cat in metrics) {
      allMetrics = allMetrics.concat(metrics[cat]);
    }
    
    return {
      success: true,
      metrics: allMetrics,
      categories: Object.keys(metrics)
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      metrics: []
    };
  }
}

/**
 * Get rule templates for sidebar
 */
function getRuleTemplates(filter) {
  try {
    var templates = [
      {
        id: 'pause_no_conversions',
        category: 'Pause',
        icon: '💰',
        title: 'Spend',
        description: 'Pause Ad set with no conversions today'
      },
      {
        id: 'pause_high_cpm',
        category: 'Pause',
        icon: '📊',
        title: 'High-level metrics',
        description: 'Pause Ad set with high Cost per mille (CPM)'
      },
      {
        id: 'pause_high_cpc',
        category: 'Pause',
        icon: '📊',
        title: 'High-level metrics',
        description: 'Pause Ad set with high Cost per conversion (CPC)'
      },
      {
        id: 'pause_low_ctr',
        category: 'Pause',
        icon: '👁️',
        title: 'Impressions',
        description: 'Pause Ad set with low Click Through Rate (CTR)'
      },
      {
        id: 'pause_high_cpa',
        category: 'Pause',
        icon: '👥',
        title: 'CPA',
        description: 'Pause Ad set with high CPA'
      },
      {
        id: 'pause_low_roas',
        category: 'Pause',
        icon: '⭐',
        title: 'ROAS',
        description: 'Pause Ad set with low ROAS'
      },
      {
        id: 'pause_time_based',
        category: 'Pause',
        icon: '🕐',
        title: 'Time-based',
        description: 'Pause Ad set at a certain time of the day'
      }
    ];
    
    if (filter && filter !== 'all') {
      templates = templates.filter(function(t) {
        return t.category.toLowerCase() === filter.toLowerCase();
      });
    }
    
    return {
      success: true,
      templates: templates
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      templates: []
    };
  }
}

/**
 * Create folder
 */
function createFolder(folderName) {
  try {
    var props = PropertiesService.getScriptProperties();
    var folderId = 'folder_' + Date.now();
    
    var folder = {
      id: folderId,
      name: folderName,
      created_at: new Date().toISOString()
    };
    
    props.setProperty('FOLDER_' + folderId, JSON.stringify(folder));
    
    return {
      success: true,
      folder_id: folderId,
      folder: folder
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get folders list
 */
function getFolders() {
  try {
    var folders = [];
    var props = PropertiesService.getScriptProperties();
    var allProps = props.getProperties();
    
    for (var key in allProps) {
      if (key.startsWith('FOLDER_')) {
        try {
          var folder = JSON.parse(allProps[key]);
          folders.push(folder);
        } catch (e) {
          Logger.log("⚠️ Lỗi parse folder: " + e.message);
        }
      }
    }
    
    return {
      success: true,
      folders: folders
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      folders: []
    };
  }
}

/**
 * Get rule by ID
 */
function getRule(ruleId) {
  try {
    var props = PropertiesService.getScriptProperties();
    var ruleKey = 'RULE_' + ruleId;
    var ruleData = props.getProperty(ruleKey);
    
    if (!ruleData) {
      return {
        success: false,
        error: "Rule not found"
      };
    }
    
    var rule = JSON.parse(ruleData);
    
    return {
      success: true,
      rule: rule
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

