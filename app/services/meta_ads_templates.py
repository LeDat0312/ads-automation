"""
Meta Ads Style Templates
Tạo templates tương tự Meta Ads automation rules
"""
from typing import List, Dict, Any

# Template definitions tương tự Meta Ads
META_ADS_TEMPLATES = [
    # ========== ESSENTIAL ==========
    {
        "name": "Quick Start ROAS",
        "description": "Three essential automations for pausing, starting, and scaling budgets",
        "campaign_type": "ECOMMERCE",
        "category": "essential",
        "labels": ["ROAS-based", "Quick Start"],
        "icon": "play",
        "template_config": {
            "rules": [
                {
                    "name": "Pause Low ROAS",
                    "logic_type": "logic1",
                    "conditions": {
                        "spend": {"operator": ">", "value": 20000},
                        "roas": {"operator": "<", "value": 2.0}
                    },
                    "action": "PAUSE"
                },
                {
                    "name": "Resume High ROAS",
                    "logic_type": "logic3",
                    "conditions": {
                        "spend": {"operator": ">", "value": 15000},
                        "roas": {"operator": ">=", "value": 2.0},
                        "results": {"operator": ">", "value": 0}
                    },
                    "action": "RESUME"
                }
            ]
        }
    },
    {
        "name": "Quick Start CPA",
        "description": "Three essential automations for pausing, starting, and scaling budgets",
        "campaign_type": "LEAD",
        "category": "essential",
        "labels": ["CPA-based", "Quick Start"],
        "icon": "play",
        "template_config": {
            "rules": [
                {
                    "name": "Pause High CPA",
                    "logic_type": "logic1",
                    "conditions": {
                        "spend": {"operator": ">", "value": 20000},
                        "cost_per_lead": {"operator": ">", "value": 15000}
                    },
                    "action": "PAUSE"
                },
                {
                    "name": "Resume Low CPA",
                    "logic_type": "logic3",
                    "conditions": {
                        "spend": {"operator": ">", "value": 15000},
                        "cost_per_lead": {"operator": "<", "value": 10000},
                        "leads": {"operator": ">", "value": 0}
                    },
                    "action": "RESUME"
                }
            ]
        }
    },
    
    # ========== PAUSE ==========
    {
        "name": "Forfeit the game",
        "description": "Pause underperforming ad sets that spent over half of its budget",
        "campaign_type": "ECOMMERCE",
        "category": "pause",
        "labels": ["ROAS-based"],
        "icon": "pause",
        "template_config": {
            "rules": [
                {
                    "name": "Forfeit the game",
                    "logic_type": "logic1",
                    "conditions": {
                        "spend_percent_of_budget": {"operator": ">", "value": 50},
                        "roas": {"operator": "<", "value": 2.0}
                    },
                    "action": "PAUSE"
                }
            ]
        }
    },
    {
        "name": "Down and out (ROAS)",
        "description": "Pause ads with a below average ROAS",
        "campaign_type": "ECOMMERCE",
        "category": "pause",
        "labels": ["ROAS-based"],
        "icon": "pause",
        "template_config": {
            "rules": [
                {
                    "name": "Down and out",
                    "logic_type": "logic1",
                    "conditions": {
                        "spend": {"operator": ">", "value": 15000},
                        "roas": {"operator": "<", "value": "average_roas"}
                    },
                    "action": "PAUSE"
                }
            ]
        }
    },
    {
        "name": "Down and out (CPA)",
        "description": "Pause ads with an above average CPA",
        "campaign_type": "LEAD",
        "category": "pause",
        "labels": ["CPA-based"],
        "icon": "pause",
        "template_config": {
            "rules": [
                {
                    "name": "Down and out",
                    "logic_type": "logic1",
                    "conditions": {
                        "spend": {"operator": ">", "value": 15000},
                        "cost_per_lead": {"operator": ">", "value": "average_cpa"}
                    },
                    "action": "PAUSE"
                }
            ]
        }
    },
    {
        "name": "No leads",
        "description": "Pause adsets with high spend but no leads",
        "campaign_type": "LEAD",
        "category": "pause",
        "labels": ["CPA-based"],
        "icon": "pause",
        "template_config": {
            "rules": [
                {
                    "name": "No leads",
                    "logic_type": "logic1",
                    "conditions": {
                        "spend": {"operator": ">", "value": 20000},
                        "leads": {"operator": "==", "value": 0}
                    },
                    "action": "PAUSE"
                }
            ]
        }
    },
    
    # ========== SCALE ==========
    {
        "name": "Scale Ad Sets",
        "description": "Gradually increase the budget for high-performing ad sets and decrease the budget for underperformers",
        "campaign_type": "BOTH",
        "category": "scale",
        "labels": ["New"],
        "icon": "scale",
        "template_config": {
            "rules": [
                {
                    "name": "Scale Up High Performers",
                    "logic_type": "scale",
                    "conditions": {
                        "roas": {"operator": ">=", "value": 3.0},
                        "spend": {"operator": ">", "value": 10000}
                    },
                    "action": "INCREASE_BUDGET",
                    "amount_percent": 20
                },
                {
                    "name": "Scale Down Underperformers",
                    "logic_type": "scale",
                    "conditions": {
                        "roas": {"operator": "<", "value": 1.5},
                        "spend": {"operator": ">", "value": 15000}
                    },
                    "action": "DECREASE_BUDGET",
                    "amount_percent": 20
                }
            ]
        }
    },
    {
        "name": "Daily scaling",
        "description": "Scale the budget if half the budget is spent with high ROAS",
        "campaign_type": "ECOMMERCE",
        "category": "scale",
        "labels": ["ROAS-based"],
        "icon": "scale",
        "template_config": {
            "rules": [
                {
                    "name": "Daily scaling",
                    "logic_type": "scale",
                    "conditions": {
                        "spend_percent_of_budget": {"operator": ">=", "value": 50},
                        "roas": {"operator": ">=", "value": 2.5}
                    },
                    "action": "INCREASE_BUDGET",
                    "amount_percent": 30
                }
            ]
        }
    },
    {
        "name": "To the moon",
        "description": "Scale the budget if a campaign has a below average CPA",
        "campaign_type": "LEAD",
        "category": "scale",
        "labels": ["CPA-based"],
        "icon": "scale",
        "template_config": {
            "rules": [
                {
                    "name": "To the moon",
                    "logic_type": "scale",
                    "conditions": {
                        "cost_per_lead": {"operator": "<", "value": "average_cpa"},
                        "spend": {"operator": ">", "value": 10000}
                    },
                    "action": "INCREASE_BUDGET",
                    "amount_percent": 25
                }
            ]
        }
    },
    
    # ========== OPTIMISE ==========
    {
        "name": "Power of threes (ROAS)",
        "description": "Pause ads at midnight and only turn back on the top three performers",
        "campaign_type": "ECOMMERCE",
        "category": "optimise",
        "labels": ["ROAS-based"],
        "icon": "optimise",
        "template_config": {
            "rules": [
                {
                    "name": "Power of threes",
                    "logic_type": "midnight_reset",
                    "conditions": {
                        "time": {"operator": "==", "value": "00:00"},
                        "top_n": {"operator": "==", "value": 3},
                        "metric": {"operator": "==", "value": "roas"}
                    },
                    "action": "PAUSE_ALL_EXCEPT_TOP_N"
                }
            ]
        }
    },
    {
        "name": "Power of threes (CPA)",
        "description": "Pause ads at midnight and only turn back on the top three performers",
        "campaign_type": "LEAD",
        "category": "optimise",
        "labels": ["CPA-based"],
        "icon": "optimise",
        "template_config": {
            "rules": [
                {
                    "name": "Power of threes",
                    "logic_type": "midnight_reset",
                    "conditions": {
                        "time": {"operator": "==", "value": "00:00"},
                        "top_n": {"operator": "==", "value": 3},
                        "metric": {"operator": "==", "value": "cpa"}
                    },
                    "action": "PAUSE_ALL_EXCEPT_TOP_N"
                }
            ]
        }
    },
    {
        "name": "Roundtable Ad Sets",
        "description": "Launches 3 new ad sets at a specific hour of the day (between 11 am and 12 pm) if Ad account ROAS is over 3",
        "campaign_type": "ECOMMERCE",
        "category": "optimise",
        "labels": ["New", "ROAS-based"],
        "icon": "optimise",
        "template_config": {
            "rules": [
                {
                    "name": "Roundtable Ad Sets",
                    "logic_type": "scheduled_launch",
                    "conditions": {
                        "time": {"operator": ">=", "value": "11:00"},
                        "time": {"operator": "<=", "value": "12:00"},
                        "account_roas": {"operator": ">", "value": 3.0}
                    },
                    "action": "LAUNCH_NEW_ADSETS",
                    "count": 3
                }
            ]
        }
    },
    {
        "name": "Burnouts",
        "description": "Notify if CTR metric declines over the time",
        "campaign_type": "LEAD",
        "category": "optimise",
        "labels": ["New", "CPA-based"],
        "icon": "notify",
        "template_config": {
            "rules": [
                {
                    "name": "Burnouts",
                    "logic_type": "notification",
                    "conditions": {
                        "ctr_decline_percent": {"operator": ">", "value": 20}
                    },
                    "action": "NOTIFY",
                    "metric": "CTR"
                }
            ]
        }
    },
    {
        "name": "Notify about Key Metrics Drops",
        "description": "Notify if conversion metrics shift (Leads, CPL, CPM)",
        "campaign_type": "BOTH",
        "category": "optimise",
        "labels": ["New"],
        "icon": "notify",
        "template_config": {
            "rules": [
                {
                    "name": "Notify about Key Metrics Drops",
                    "logic_type": "notification",
                    "conditions": {
                        "leads_drop_percent": {"operator": ">", "value": 30},
                        "cpl_increase_percent": {"operator": ">", "value": 30},
                        "cpm_increase_percent": {"operator": ">", "value": 30}
                    },
                    "action": "NOTIFY",
                    "metrics": ["Leads", "CPL", "CPM"]
                }
            ]
        }
    }
]


def get_templates_by_category(
    campaign_type: str = None,
    category: str = None
) -> List[Dict[str, Any]]:
    """
    Get templates filtered by campaign_type and category
    """
    filtered = META_ADS_TEMPLATES
    
    if campaign_type:
        filtered = [
            t for t in filtered
            if t['campaign_type'] == campaign_type or t['campaign_type'] == 'BOTH'
        ]
    
    if category:
        filtered = [
            t for t in filtered
            if t['category'] == category
        ]
    
    return filtered


def get_template_by_name(name: str) -> Dict[str, Any]:
    """
    Get template by name
    """
    for template in META_ADS_TEMPLATES:
        if template['name'] == name:
            return template
    return None

