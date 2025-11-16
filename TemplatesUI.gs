/**
 * TEMPLATES UI - GOOGLE APPS SCRIPT
 * Giao diện chọn và apply rule templates tương tự Meta Ads/Birch
 * Không cần Python server, chạy 100% trên Google Apps Script
 */

/**
 * Serve Templates UI HTML page
 * Hàm này được gọi khi truy cập Web App URL
 */
function doGet(e) {
  try {
    // Test: Trả về HTML đơn giản trước để kiểm tra
    var testHtml = "<html><body><h1>Templates UI - Test</h1><p>Hàm doGet() đã chạy thành công!</p><p>Time: " + new Date() + "</p></body></html>";
    
    // Thử load file HTML
    try {
      var htmlTemplate = HtmlService.createTemplateFromFile('TemplatesUI_HTML');
      var htmlOutput = htmlTemplate.evaluate()
        .setTitle('Rule Templates - Meta Ads Style')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
      
      return htmlOutput;
    } catch (fileError) {
      // Nếu không load được file HTML, trả về error page với thông tin chi tiết
      return HtmlService.createHtmlOutput(
        "<html><body>" +
        "<h1>⚠️ Lỗi khi load TemplatesUI_HTML.html</h1>" +
        "<p><strong>Error:</strong> " + fileError.message + "</p>" +
        "<p><strong>Stack:</strong> " + (fileError.stack || "N/A") + "</p>" +
        "<p><strong>Time:</strong> " + new Date() + "</p>" +
        "<hr>" +
        "<h2>Test HTML (nếu thấy message này, hàm doGet() đã chạy):</h2>" +
        testHtml +
        "</body></html>"
      );
    }
  } catch (error) {
    // Lỗi tổng quát
    return HtmlService.createHtmlOutput(
      "<html><body>" +
      "<h1>🚨 LỖI NGHIÊM TRỌNG</h1>" +
      "<p><strong>Error:</strong> " + error.message + "</p>" +
      "<p><strong>Stack:</strong> " + (error.stack || "N/A") + "</p>" +
      "<p><strong>Time:</strong> " + new Date() + "</p>" +
      "</body></html>"
    );
  }
}

/**
 * Include HTML/CSS/JS files
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * Get templates data (grouped by category)
 */
function getTemplatesData(campaignType, category) {
  try {
    var templates = getAllTemplates();
    
    // Filter by campaign type
    if (campaignType && campaignType !== 'BOTH') {
      templates = templates.filter(function(t) {
        return t.campaign_type === campaignType || t.campaign_type === 'BOTH';
      });
    }
    
    // Filter by category
    if (category) {
      templates = templates.filter(function(t) {
        return t.category === category;
      });
    }
    
    // Group by category
    var grouped = {
      essential: [],
      pause: [],
      scale: [],
      optimise: [],
      time: []
    };
    
    templates.forEach(function(template) {
      var cat = template.category || 'essential';
      if (grouped[cat]) {
        grouped[cat].push(template);
      }
    });
    
    return {
      success: true,
      templates: grouped,
      total: templates.length
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get all templates definitions
 */
function getAllTemplates() {
  return [
    // ========== ESSENTIAL ==========
    {
      name: "Quick Start ROAS",
      description: "Three essential automations for pausing, starting, and scaling budgets",
      campaign_type: "ECOMMERCE",
      category: "essential",
      labels: ["ROAS-based", "Quick Start"],
      icon: "play",
      template_config: {
        rules: [
          {
            name: "Pause Low ROAS",
            logic_type: "logic1",
            conditions: {
              spend: { operator: ">", value: 20000 },
              roas: { operator: "<", value: 2.0 }
            },
            action: "PAUSE"
          },
          {
            name: "Resume High ROAS",
            logic_type: "logic3",
            conditions: {
              spend: { operator: ">", value: 15000 },
              roas: { operator: ">=", value: 2.0 },
              results: { operator: ">", value: 0 }
            },
            action: "RESUME"
          }
        ]
      }
    },
    {
      name: "Quick Start CPA",
      description: "Three essential automations for pausing, starting, and scaling budgets",
      campaign_type: "LEAD",
      category: "essential",
      labels: ["CPA-based", "Quick Start"],
      icon: "play",
      template_config: {
        rules: [
          {
            name: "Pause High CPA",
            logic_type: "logic1",
            conditions: {
              spend: { operator: ">", value: 20000 },
              cost_per_lead: { operator: ">", value: 15000 }
            },
            action: "PAUSE"
          },
          {
            name: "Resume Low CPA",
            logic_type: "logic3",
            conditions: {
              spend: { operator: ">", value: 15000 },
              cost_per_lead: { operator: "<", value: 10000 },
              leads: { operator: ">", value: 0 }
            },
            action: "RESUME"
          }
        ]
      }
    },
    
    // ========== PAUSE ==========
    {
      name: "Forfeit the game",
      description: "Pause underperforming ad sets that spent over half of its budget",
      campaign_type: "ECOMMERCE",
      category: "pause",
      labels: ["ROAS-based"],
      icon: "pause",
      template_config: {
        rules: [
          {
            name: "Forfeit the game",
            logic_type: "logic1",
            conditions: {
              spend_percent_of_budget: { operator: ">", value: 50 },
              roas: { operator: "<", value: 2.0 }
            },
            action: "PAUSE"
          }
        ]
      }
    },
    {
      name: "Down and out (ROAS)",
      description: "Pause ads with a below average ROAS",
      campaign_type: "ECOMMERCE",
      category: "pause",
      labels: ["ROAS-based"],
      icon: "pause",
      template_config: {
        rules: [
          {
            name: "Down and out",
            logic_type: "logic1",
            conditions: {
              spend: { operator: ">", value: 15000 },
              roas: { operator: "<", value: "average_roas" }
            },
            action: "PAUSE"
          }
        ]
      }
    },
    {
      name: "Down and out (CPA)",
      description: "Pause ads with an above average CPA",
      campaign_type: "LEAD",
      category: "pause",
      labels: ["CPA-based"],
      icon: "pause",
      template_config: {
        rules: [
          {
            name: "Down and out",
            logic_type: "logic1",
            conditions: {
              spend: { operator: ">", value: 15000 },
              cost_per_lead: { operator: ">", value: "average_cpa" }
            },
            action: "PAUSE"
          }
        ]
      }
    },
    {
      name: "On the safe side",
      description: "Pause ads with zero conversions after a certain amount of time",
      campaign_type: "LEAD",
      category: "pause",
      labels: ["CPA-based"],
      icon: "pause",
      template_config: {
        rules: [
          {
            name: "On the safe side",
            logic_type: "logic1",
            conditions: {
              spend: { operator: ">", value: 20000 },
              leads: { operator: "==", value: 0 },
              days_running: { operator: ">=", value: 3 }
            },
            action: "PAUSE"
          }
        ]
      }
    },
    {
      name: "Stop Loss",
      description: "Pause ads that spent the limit in the last 3 days including today but there were no conversions attributed",
      campaign_type: "BOTH",
      category: "pause",
      labels: [],
      icon: "pause",
      template_config: {
        rules: [
          {
            name: "Stop Loss",
            logic_type: "logic1",
            conditions: {
              spend_3days: { operator: ">", value: 50000 },
              conversions_3days: { operator: "==", value: 0 }
            },
            action: "PAUSE"
          }
        ]
      }
    },
    
    // ========== SCALE ==========
    {
      name: "Scale Ad Sets",
      description: "Gradually increase the budget for high-performing ad sets and decrease the budget for underperformers",
      campaign_type: "BOTH",
      category: "scale",
      labels: ["New"],
      icon: "scale",
      template_config: {
        rules: [
          {
            name: "Scale Up High Performers",
            logic_type: "scale",
            conditions: {
              roas: { operator: ">=", value: 3.0 },
              spend: { operator: ">", value: 10000 }
            },
            action: "INCREASE_BUDGET",
            amount_percent: 20
          },
          {
            name: "Scale Down Underperformers",
            logic_type: "scale",
            conditions: {
              roas: { operator: "<", value: 1.5 },
              spend: { operator: ">", value: 15000 }
            },
            action: "DECREASE_BUDGET",
            amount_percent: 20
          }
        ]
      }
    },
    {
      name: "Scale Slow and Fast",
      description: "Scale Ad set budget based on ROAS on the Ad set and Ad account levels",
      campaign_type: "ECOMMERCE",
      category: "scale",
      labels: ["New", "ROAS-based"],
      icon: "scale",
      template_config: {
        rules: [
          {
            name: "Scale Slow and Fast",
            logic_type: "scale",
            conditions: {
              adset_roas: { operator: ">=", value: 2.5 },
              account_roas: { operator: ">=", value: 2.0 }
            },
            action: "INCREASE_BUDGET",
            amount_percent: 25
          }
        ]
      }
    },
    {
      name: "Daily scaling",
      description: "Scale the budget if half the budget is spent with high ROAS",
      campaign_type: "ECOMMERCE",
      category: "scale",
      labels: ["ROAS-based"],
      icon: "scale",
      template_config: {
        rules: [
          {
            name: "Daily scaling",
            logic_type: "scale",
            conditions: {
              spend_percent_of_budget: { operator: ">=", value: 50 },
              roas: { operator: ">=", value: 2.5 }
            },
            action: "INCREASE_BUDGET",
            amount_percent: 30
          }
        ]
      }
    },
    {
      name: "Double down",
      description: "Duplicate a well performing campaign with double the budget",
      campaign_type: "ECOMMERCE",
      category: "scale",
      labels: ["ROAS-based"],
      icon: "scale",
      template_config: {
        rules: [
          {
            name: "Double down",
            logic_type: "duplicate",
            conditions: {
              roas: { operator: ">=", value: 3.0 },
              spend: { operator: ">", value: 20000 }
            },
            action: "DUPLICATE_CAMPAIGN",
            budget_multiplier: 2
          }
        ]
      }
    },
    {
      name: "Profit marching (CBO)",
      description: "Scale the budget if a campaign performed well the previous day",
      campaign_type: "ECOMMERCE",
      category: "scale",
      labels: ["ROAS-based"],
      icon: "scale",
      template_config: {
        rules: [
          {
            name: "Profit marching",
            logic_type: "scale",
            conditions: {
              yesterday_roas: { operator: ">=", value: 2.5 },
              yesterday_spend: { operator: ">", value: 10000 }
            },
            action: "INCREASE_BUDGET",
            amount_percent: 20
          }
        ]
      }
    },
    {
      name: "To the moon",
      description: "Scale the budget if a campaign has a below average CPA",
      campaign_type: "LEAD",
      category: "scale",
      labels: ["CPA-based"],
      icon: "scale",
      template_config: {
        rules: [
          {
            name: "To the moon",
            logic_type: "scale",
            conditions: {
              cost_per_lead: { operator: "<", value: "average_cpa" },
              spend: { operator: ">", value: 10000 }
            },
            action: "INCREASE_BUDGET",
            amount_percent: 25
          }
        ]
      }
    },
    
    // ========== OPTIMISE ==========
    {
      name: "Power of threes (ROAS)",
      description: "Pause ads at midnight and only turn back on the top three performers",
      campaign_type: "ECOMMERCE",
      category: "optimise",
      labels: ["ROAS-based"],
      icon: "optimise",
      template_config: {
        rules: [
          {
            name: "Power of threes",
            logic_type: "midnight_reset",
            conditions: {
              time: { operator: "==", value: "00:00" },
              top_n: { operator: "==", value: 3 },
              metric: { operator: "==", value: "roas" }
            },
            action: "PAUSE_ALL_EXCEPT_TOP_N"
          }
        ]
      }
    },
    {
      name: "Power of threes (CPA)",
      description: "Pause ads at midnight and only turn back on the top three performers",
      campaign_type: "LEAD",
      category: "optimise",
      labels: ["CPA-based"],
      icon: "optimise",
      template_config: {
        rules: [
          {
            name: "Power of threes",
            logic_type: "midnight_reset",
            conditions: {
              time: { operator: "==", value: "00:00" },
              top_n: { operator: "==", value: 3 },
              metric: { operator: "==", value: "cpa" }
            },
            action: "PAUSE_ALL_EXCEPT_TOP_N"
          }
        ]
      }
    },
    {
      name: "Roundtable Ad Sets",
      description: "Launches 3 new ad sets at a specific hour of the day (between 11 am and 12 pm) if Ad account ROAS is over 3",
      campaign_type: "ECOMMERCE",
      category: "optimise",
      labels: ["New", "ROAS-based"],
      icon: "optimise",
      template_config: {
        rules: [
          {
            name: "Roundtable Ad Sets",
            logic_type: "scheduled_launch",
            conditions: {
              time: { operator: ">=", value: "11:00" },
              time_end: { operator: "<=", value: "12:00" },
              account_roas: { operator: ">", value: 3.0 }
            },
            action: "LAUNCH_NEW_ADSETS",
            count: 3
          }
        ]
      }
    },
    {
      name: "Budget Ladder",
      description: "Reset and adjust campaigns budgets with CBO (advantage campaign budget) setting based on yesterday's campaign performance",
      campaign_type: "ECOMMERCE",
      category: "optimise",
      labels: ["New", "ROAS-based"],
      icon: "optimise",
      template_config: {
        rules: [
          {
            name: "Budget Ladder",
            logic_type: "budget_reset",
            conditions: {
              yesterday_roas: { operator: ">=", value: 2.0 }
            },
            action: "RESET_BUDGET",
            adjust_percent: 10
          }
        ]
      }
    },
    {
      name: "Fire and Ice",
      description: "Set a visual indicator of which ad sets are performing above or below expectations",
      campaign_type: "ECOMMERCE",
      category: "optimise",
      labels: ["New", "ROAS-based"],
      icon: "optimise",
      template_config: {
        rules: [
          {
            name: "Fire and Ice",
            logic_type: "visual_indicator",
            conditions: {
              roas: { operator: ">=", value: 2.5 }
            },
            action: "MARK_PERFORMING",
            indicator: "fire"
          },
          {
            name: "Fire and Ice (Below)",
            logic_type: "visual_indicator",
            conditions: {
              roas: { operator: "<", value: 1.5 }
            },
            action: "MARK_UNDERPERFORMING",
            indicator: "ice"
          }
        ]
      }
    },
    {
      name: "Burnouts",
      description: "Notify if CTR metric declines over the time",
      campaign_type: "LEAD",
      category: "optimise",
      labels: ["New", "CPA-based"],
      icon: "notify",
      template_config: {
        rules: [
          {
            name: "Burnouts",
            logic_type: "notification",
            conditions: {
              ctr_decline_percent: { operator: ">", value: 20 }
            },
            action: "NOTIFY",
            metric: "CTR"
          }
        ]
      }
    },
    {
      name: "Notify about Key Metrics Drops",
      description: "Notify if conversion metrics shift (Leads, CPL, CPM)",
      campaign_type: "BOTH",
      category: "optimise",
      labels: ["New"],
      icon: "notify",
      template_config: {
        rules: [
          {
            name: "Notify about Key Metrics Drops",
            logic_type: "notification",
            conditions: {
              leads_drop_percent: { operator: ">", value: 30 },
              cpl_increase_percent: { operator: ">", value: 30 },
              cpm_increase_percent: { operator: ">", value: 30 }
            },
            action: "NOTIFY",
            metrics: ["Leads", "CPL", "CPM"]
          }
        ]
      }
    },
    
    // ========== TIME ==========
    {
      name: "Day parting",
      description: "Pause ads during specific times of the day",
      campaign_type: "BOTH",
      category: "time",
      labels: [],
      icon: "time",
      template_config: {
        rules: [
          {
            name: "Day parting",
            logic_type: "time_based",
            conditions: {
              time_start: { operator: ">=", value: "22:00" },
              time_end: { operator: "<=", value: "06:00" }
            },
            action: "PAUSE_DURING_TIME"
          }
        ]
      }
    },
    {
      name: "Midnight reset",
      description: "Restart ad sets at midnight with their original budgets",
      campaign_type: "BOTH",
      category: "time",
      labels: [],
      icon: "time",
      template_config: {
        rules: [
          {
            name: "Midnight reset",
            logic_type: "midnight_reset",
            conditions: {
              time: { operator: "==", value: "00:00" }
            },
            action: "RESTART_WITH_ORIGINAL_BUDGET"
          }
        ]
      }
    }
  ];
}

/**
 * Apply template to account/prefix
 */
function applyTemplate(templateName, accountId, prefix, customValues) {
  try {
    var template = getAllTemplates().find(function(t) {
      return t.name === templateName;
    });
    
    if (!template) {
      return {
        success: false,
        error: "Template not found"
      };
    }
    
    // Convert template to LogicRules format
    var rules = template.template_config.rules;
    var logicRules = [];
    
    rules.forEach(function(rule) {
      var logicRule = {
        account_id: accountId,
        prefix: prefix || "",
        giai_doan: "GĐ1",
        logic_type: rule.logic_type,
        enabled: true
      };
      
      // Set conditions based on rule
      if (rule.conditions.spend) {
        logicRule.condition_spend = rule.conditions.spend.value;
      }
      if (rule.conditions.results) {
        logicRule.condition_results = rule.conditions.results.value;
      }
      if (rule.conditions.gia_data) {
        logicRule.condition_gia_data = rule.conditions.gia_data.value;
      }
      if (rule.conditions.roas) {
        logicRule.condition_roas = rule.conditions.roas.value;
      }
      
      logicRules.push(logicRule);
    });
    
    // Save to LogicRules sheet
    try {
      var savedCount = saveLogicRulesToSheet(logicRules, accountId, prefix);
      Logger.log("✅ Đã lưu " + savedCount + " rules vào LogicRules sheet");
    } catch (saveError) {
      Logger.log("🚨 Lỗi khi lưu vào LogicRules sheet: " + saveError.message);
      return {
        success: false,
        error: "Lỗi khi lưu vào LogicRules sheet: " + saveError.message
      };
    }
    
    return {
      success: true,
      message: "Template applied successfully",
      template_name: templateName,
      account_id: accountId,
      prefix: prefix,
      rules_created: logicRules.length,
      saved_count: savedCount || 0
    };
    
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

