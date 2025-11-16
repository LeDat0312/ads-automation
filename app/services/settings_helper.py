# -*- coding: utf-8 -*-
"""
Helper functions cho Settings Enhancement
Utility functions cho pattern matching, formatting, etc.
"""

import re
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import pytz


# ===== PATTERN MATCHING =====

def match_campaign_prefix(campaign_name: str, pattern: str, pattern_type: str) -> bool:
    """
    Match campaign name với prefix pattern
    
    Args:
        campaign_name: Tên campaign
        pattern: Pattern string
        pattern_type: "EXACT" | "CONTAINS" | "STARTS_WITH" | "ENDS_WITH" | "REGEX"
    
    Returns:
        True nếu match, False nếu không
    """
    if not campaign_name or not pattern:
        return False
    
    campaign_name = campaign_name.strip()
    pattern = pattern.strip()
    
    try:
        if pattern_type == "EXACT":
            return campaign_name == pattern
        elif pattern_type == "CONTAINS":
            return pattern in campaign_name
        elif pattern_type == "STARTS_WITH":
            return campaign_name.startswith(pattern)
        elif pattern_type == "ENDS_WITH":
            return campaign_name.endswith(pattern)
        elif pattern_type == "REGEX":
            return bool(re.match(pattern, campaign_name))
        else:
            return False
    except re.error:
        # Regex error
        return False


def validate_regex_pattern(pattern: str) -> Tuple[bool, Optional[str]]:
    """
    Validate regex pattern
    
    Returns:
        (is_valid, error_message)
    """
    try:
        re.compile(pattern)
        return True, None
    except re.error as e:
        return False, str(e)


def test_pattern_matching(pattern: str, pattern_type: str, test_strings: List[str]) -> List[dict]:
    """
    Test pattern matching với list of strings
    
    Returns:
        List[{"test_string": str, "matched": bool}]
    """
    results = []
    for test_str in test_strings:
        matched = match_campaign_prefix(test_str, pattern, pattern_type)
        results.append({
            "test_string": test_str,
            "matched": matched
        })
    return results


# ===== TIME FORMATTING =====

def format_datetime_ago(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime thành "X minutes ago" format
    """
    if not dt:
        return None
    
    # Convert to HCM timezone
    hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    dt_hcm = dt.astimezone(hcm_tz)
    
    now = datetime.now(hcm_tz)
    diff = now - dt_hcm
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"


def format_datetime_hcm(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime thành "HH:MM:SS DD/MM/YYYY" (HCM timezone)
    """
    if not dt:
        return None
    
    hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    dt_hcm = dt.astimezone(hcm_tz)
    
    return dt_hcm.strftime("%H:%M:%S %d/%m/%Y")


def format_datetime_full(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime full info
    Ví dụ: "17/11/2025 15:30:45 (2 hours ago)"
    """
    if not dt:
        return None
    
    formatted = format_datetime_hcm(dt)
    ago = format_datetime_ago(dt)
    
    if formatted and ago:
        return f"{formatted} ({ago})"
    return formatted


# ===== SPEND FORMATTING =====

def format_spend(spend: float, currency: str = "VND") -> str:
    """
    Format spend amount thành readable format
    """
    if currency == "VND":
        if spend >= 1_000_000:
            return f"{spend / 1_000_000:.1f}M đ"
        elif spend >= 1_000:
            return f"{spend / 1_000:.1f}K đ"
        else:
            return f"{int(spend)} đ"
    else:
        # USD or others
        if spend >= 1_000_000:
            return f"${spend / 1_000_000:.1f}M"
        elif spend >= 1_000:
            return f"${spend / 1_000:.1f}K"
        else:
            return f"${spend:.2f}"


# ===== PERMISSION CHECKING =====

def check_required_permissions(token_permissions: List[str]) -> Tuple[bool, List[str]]:
    """
    Check nếu token có đủ permissions
    
    Returns:
        (has_all, missing_permissions)
    """
    required = [
        "ads_management",
        "pages_manage_ads",
        "business_management"
    ]
    
    missing = [p for p in required if p not in token_permissions]
    has_all = len(missing) == 0
    
    return has_all, missing


def format_permissions_display(permissions: List[str]) -> str:
    """
    Format permissions thành readable string
    """
    permission_names = {
        "ads_management": "Quản lý Ads",
        "pages_manage_ads": "Quản lý Ads trên Pages",
        "business_management": "Quản lý Business",
        "pages_read_engagement": "Xem Engagement",
        "pages_read_user_content": "Xem nội dung người dùng",
    }
    
    readable = []
    for perm in permissions:
        readable.append(permission_names.get(perm, perm))
    
    return " • ".join(readable)


# ===== ACCOUNT STATS =====

def calculate_campaign_percentage(active: int, paused: int) -> dict:
    """
    Calculate percentage of campaigns
    """
    total = active + paused
    if total == 0:
        return {"active_pct": 0, "paused_pct": 0}
    
    return {
        "active_pct": round((active / total) * 100, 1),
        "paused_pct": round((paused / total) * 100, 1)
    }


# ===== NOTIFICATION TEMPLATES =====

TELEGRAM_TEMPLATES = {
    "CAMPAIGN_PAUSED": """
🚨 Campaign Paused

📊 Rule: {rule_name}
🎯 Campaign: {campaign_name}
💰 Spend (7d): {spend}
📈 ROAS: {roas}
🎬 Action: ⏸️ PAUSED

📱 Account: {account_name}
🏷 Prefix: {prefix_name}
⏰ Time: {time}
""",
    
    "CAMPAIGN_RESUMED": """
✅ Campaign Resumed

🎯 Campaign: {campaign_name}
💰 Spend (7d): {spend}
📈 ROAS: {roas}
🎬 Action: ▶️ RESUMED

📱 Account: {account_name}
⏰ Time: {time}
""",
    
    "BUDGET_ADJUSTED": """
💵 Budget Adjusted

🎯 Campaign: {campaign_name}
💰 Old Budget: {old_budget}
💰 New Budget: {new_budget}

📱 Account: {account_name}
⏰ Time: {time}
""",
    
    "LOW_ROAS_ALERT": """
⚠️ Low ROAS Alert

🎯 Campaign: {campaign_name}
📈 Current ROAS: {roas} ❌
📈 Target ROAS: {target_roas} ✅
💰 Spend (7d): {spend}

📱 Account: {account_name}
🏷 Prefix: {prefix_name}
⏰ Time: {time}
""",
    
    "DAILY_SUMMARY": """
📊 Daily Summary

📈 Total Spend (24h): {total_spend}
📈 Avg ROAS: {avg_roas}
🎯 Campaigns Active: {active_campaigns}
⏸️ Campaigns Paused: {paused_campaigns}
🎬 Actions Triggered: {actions_triggered}

📱 Account: {account_name}
⏰ Date: {date}
"""
}


def format_telegram_message(template_key: str, **kwargs) -> str:
    """
    Format telegram notification message
    """
    template = TELEGRAM_TEMPLATES.get(template_key, "")
    try:
        return template.format(**kwargs).strip()
    except KeyError as e:
        return f"Error formatting message: missing {e}"


# ===== VALIDATION =====

def validate_timezone(tz: str) -> bool:
    """
    Validate timezone string
    """
    try:
        pytz.timezone(tz)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False


def validate_currency(currency: str) -> bool:
    """
    Validate currency code
    """
    valid_currencies = {
        "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF",
        "VND", "THB", "SGD", "HKD", "MYR", "PHP", "IDR",
        "INR", "CNY", "KRW", "MXN", "BRL", "ZAR"
    }
    return currency.upper() in valid_currencies

