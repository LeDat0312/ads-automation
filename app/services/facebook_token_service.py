# -*- coding: utf-8 -*-
"""
Facebook Token Service - Test token và sync accounts từ Facebook API
"""
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

FB_API_VERSION = "v24.0"
FB_GRAPH_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"


def test_facebook_token(access_token: str) -> Dict[str, Any]:
    """
    Test Facebook token xem có hợp lệ và đủ quyền không
    
    Returns:
        {
            "valid": bool,
            "status": str,  # "VALID", "INVALID", "EXPIRED", "INSUFFICIENT_PERMISSIONS"
            "message": str,
            "permissions": List[str],  # Danh sách permissions
            "user_info": Dict  # Thông tin user/account
        }
    """
    try:
        # Test 1: Lấy thông tin user/me
        me_url = f"{FB_GRAPH_API_BASE}/me?access_token={access_token}"
        me_response = requests.get(me_url, timeout=10)
        
        if me_response.status_code != 200:
            error_data = me_response.json() if me_response.text else {}
            error = error_data.get('error', {})
            error_code = error.get('code', 0)
            error_message = error.get('message', 'Unknown error')
            
            if error_code == 190:  # Invalid OAuth 2.0 Access Token
                return {
                    "valid": False,
                    "status": "EXPIRED",
                    "message": "Token đã hết hạn hoặc không hợp lệ",
                    "permissions": [],
                    "user_info": {}
                }
            elif error_code == 200:  # Permissions error
                return {
                    "valid": False,
                    "status": "INSUFFICIENT_PERMISSIONS",
                    "message": f"Token thiếu quyền: {error_message}",
                    "permissions": [],
                    "user_info": {}
                }
            else:
                return {
                    "valid": False,
                    "status": "INVALID",
                    "message": f"Lỗi: {error_message} (Code: {error_code})",
                    "permissions": [],
                    "user_info": {}
                }
        
        me_data = me_response.json()
        user_id = me_data.get('id')
        user_name = me_data.get('name', '')
        
        # Test 2: Lấy permissions
        permissions_url = f"{FB_GRAPH_API_BASE}/me/permissions?access_token={access_token}"
        permissions_response = requests.get(permissions_url, timeout=10)
        
        permissions = []
        if permissions_response.status_code == 200:
            permissions_data = permissions_response.json()
            perms_list = permissions_data.get('data', [])
            # Chỉ lấy permissions có status = "granted"
            permissions = [p.get('permission') for p in perms_list if p.get('status') == 'granted']
        
        # Test 3: Kiểm tra quyền ads_management (quan trọng cho automation)
        required_permissions = ['ads_management', 'ads_read', 'business_management']
        has_ads_permission = any(perm in permissions for perm in required_permissions)
        
        if not has_ads_permission:
            return {
                "valid": False,
                "status": "INSUFFICIENT_PERMISSIONS",
                "message": "Token thiếu quyền quản lý quảng cáo (ads_management, ads_read, hoặc business_management)",
                "permissions": permissions,
                "user_info": {
                    "id": user_id,
                    "name": user_name
                }
            }
        
        # Test 4: Thử lấy danh sách ad accounts (test quyền thực tế)
        accounts_url = f"{FB_GRAPH_API_BASE}/me/adaccounts?fields=id,name,account_id&limit=1&access_token={access_token}"
        accounts_response = requests.get(accounts_url, timeout=10)
        
        if accounts_response.status_code != 200:
            return {
                "valid": False,
                "status": "INSUFFICIENT_PERMISSIONS",
                "message": "Token không thể truy cập ad accounts. Kiểm tra quyền ads_management.",
                "permissions": permissions,
                "user_info": {
                    "id": user_id,
                    "name": user_name
                }
            }
        
        return {
            "valid": True,
            "status": "VALID",
            "message": "Token hợp lệ và có đủ quyền để sử dụng automation Facebook Ads",
            "permissions": permissions,
            "user_info": {
                "id": user_id,
                "name": user_name
            }
        }
        
    except requests.exceptions.Timeout:
        return {
            "valid": False,
            "status": "INVALID",
            "message": "Timeout khi kiểm tra token. Vui lòng thử lại.",
            "permissions": [],
            "user_info": {}
        }
    except Exception as e:
        logger.error(f"Error testing Facebook token: {e}")
        return {
            "valid": False,
            "status": "INVALID",
            "message": f"Lỗi khi kiểm tra token: {str(e)}",
            "permissions": [],
            "user_info": {}
        }


def fetch_facebook_ad_accounts(access_token: str) -> List[Dict[str, Any]]:
    """
    Lấy danh sách ad accounts từ Facebook API
    
    Returns:
        List of {
            "account_id": str,  # act_123456789
            "id": str,  # ID của account
            "name": str,  # Tên account
            "account_status": int,  # 1 = ACTIVE, 2 = DISABLED, etc.
            "currency": str,  # USD, VND, etc.
            "timezone_name": str,  # Asia/Ho_Chi_Minh
            "spend_cap": Optional[float],  # Giới hạn chi tiêu
            "amount_spent": Optional[float]  # Đã chi tiêu
        }
    """
    accounts = []
    url = f"{FB_GRAPH_API_BASE}/me/adaccounts"
    
    params = {
        "fields": "id,name,account_id,account_status,currency,timezone_name,spend_cap,amount_spent",
        "limit": 100,
        "access_token": access_token
    }
    
    try:
        while url:
            response = requests.get(url, params=params if '?' not in url else None, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                raise Exception(f"Facebook API error: {data['error']['message']}")
            
            accounts_data = data.get('data', [])
            for acc in accounts_data:
                accounts.append({
                    "account_id": acc.get('account_id') or acc.get('id', ''),  # act_xxx
                    "id": acc.get('id', ''),
                    "name": acc.get('name', acc.get('account_id', 'Unknown')),
                    "account_status": acc.get('account_status', 1),
                    "currency": acc.get('currency', 'USD'),
                    "timezone_name": acc.get('timezone_name', 'Asia/Ho_Chi_Minh'),
                    "spend_cap": acc.get('spend_cap'),
                    "amount_spent": acc.get('amount_spent', 0.0)
                })
            
            # Check for next page
            paging = data.get('paging', {})
            url = paging.get('next')
            params = None  # Next URL đã có params
            
    except Exception as e:
        logger.error(f"Error fetching Facebook ad accounts: {e}")
        raise
    
    return accounts


def fetch_account_30_days_spend(access_token: str, account_id: str) -> float:
    """
    Lấy chi tiêu 30 ngày qua của một account
    
    Returns:
        float: Số tiền chi tiêu (USD)
    """
    try:
        # Normalize account_id: đảm bảo có prefix "act_"
        account_id_for_api = account_id
        if not account_id_for_api.startswith("act_"):
            account_id_for_api = f"act_{account_id_for_api}"
        
        # Lấy insights 30 ngày qua
        url = f"{FB_GRAPH_API_BASE}/{account_id_for_api}/insights"
        params = {
            "fields": "spend",
            "time_range": '{"since":"' + (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d') + '","until":"' + datetime.now().strftime('%Y-%m-%d') + '"}',
            "access_token": access_token
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if 'error' in data:
            return 0.0
        
        insights = data.get('data', [])
        if not insights:
            return 0.0
        
        # Sum tất cả spend
        total_spend = 0.0
        for insight in insights:
            spend_str = insight.get('spend', '0')
            try:
                total_spend += float(spend_str)
            except (ValueError, TypeError):
                pass
        
        return total_spend
        
    except Exception as e:
        logger.error(f"Error fetching 30 days spend for {account_id}: {e}")
        return 0.0

