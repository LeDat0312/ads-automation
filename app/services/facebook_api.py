"""
Facebook API Service
Thay thế cho Facebook API.gs từ Google Apps Script
"""
import time
import requests
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Facebook Graph API version
FB_API_VERSION = "v24.0"
FB_GRAPH_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"


def chunk_list(arr: List, size: int) -> List[List]:
    """Chia list thành các chunk nhỏ hơn"""
    return [arr[i:i + size] for i in range(0, len(arr), size)]


def unique_list(arr: List) -> List:
    """Lấy danh sách unique từ list"""
    if not arr:
        return []
    seen = set()
    result = []
    for item in arr:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def fetch_adset_statuses(adset_ids: List[str], access_token: str) -> Dict[str, str]:
    """
    Lấy map { adset_id: effective_status } qua batch (?ids=)
    Thay thế cho hàm fetchAdsetStatuses() từ Facebook API.gs
    """
    if not adset_ids:
        return {}
    
    status_map = {}
    batches = chunk_list(unique_list(adset_ids), 50)
    
    for batch in batches:
        try:
            ids = ','.join(batch)
            url = f"{FB_GRAPH_API_BASE}/?ids={ids}&fields=effective_status&access_token={access_token}"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            json_data = response.json()
            if json_data and isinstance(json_data, dict):
                for adset_id, node in json_data.items():
                    if node and node.get('effective_status'):
                        status_map[adset_id] = node['effective_status']
        except Exception as e:
            logger.error(f"🚨 Lỗi lấy trạng thái AdSet (batch ids): {e}")
    
    return status_map


def pause_adsets(
    adset_id_list: List[str],
    access_token: str,
    delay_ms: int = 1000
) -> Dict[str, Any]:
    """
    Tắt NHIỀU Adset bằng 1 LỆNH BATCH
    Thay thế cho hàm goiFacebookAPIDeTatNhieuAdset() từ Facebook API.gs
    
    Returns:
        Dict với keys: success, errors, errorDetails
    """
    if not adset_id_list:
        return {"success": 0, "errors": 0, "errorDetails": []}
    
    batches = chunk_list(adset_id_list, 50)
    success_count = 0
    error_count = 0
    error_details = []
    
    for batch_idx, batch_ids in enumerate(batches):
        try:
            if batch_idx > 0 and delay_ms > 0:
                logger.info(f"Đang chờ {delay_ms / 1000} giây trước khi gửi batch tiếp theo...")
                time.sleep(delay_ms / 1000)
            
            # Tạo batch payload
            batch_payload = []
            for adset_id in batch_ids:
                batch_payload.append({
                    "method": "POST",
                    "relative_url": f"{FB_API_VERSION}/{adset_id}",
                    "body": "status=PAUSED"
                })
            
            # Gửi batch request
            form_data = {
                'access_token': access_token,
                'batch': str(batch_payload).replace("'", '"')  # Convert to JSON string
            }
            
            url = f"{FB_GRAPH_API_BASE}/"
            response = requests.post(url, data=form_data, timeout=60)
            response.raise_for_status()
            
            json_response = response.json()
            if isinstance(json_response, list):
                for i, item in enumerate(json_response):
                    adset_id = batch_ids[i] if i < len(batch_ids) else ""
                    if item.get('code') == 200:
                        success_count += 1
                    else:
                        error_count += 1
                        error_msg = "Unknown error"
                        try:
                            if 'body' in item:
                                body = item['body']
                                if isinstance(body, str):
                                    import json
                                    body_json = json.loads(body)
                                    if 'error' in body_json:
                                        error_msg = body_json['error'].get('message', error_msg)
                                else:
                                    error_msg = str(body)
                        except Exception:
                            error_msg = item.get('body', 'Failed to parse error')
                        
                        error_details.append({"adsetId": adset_id, "error": error_msg})
            else:
                error_count += len(batch_ids)
                for adset_id in batch_ids:
                    error_details.append({
                        "adsetId": adset_id,
                        "error": "Batch API error: Invalid response format"
                    })
        except Exception as e:
            error_count += len(batch_ids)
            for adset_id in batch_ids:
                error_details.append({
                    "adsetId": adset_id,
                    "error": f"Exception: {str(e)}"
                })
    
    logger.info(f"Thực thi Batch TẮT hoàn tất. Thành công: {success_count}, Thất bại: {error_count}")
    return {
        "success": success_count,
        "errors": error_count,
        "errorDetails": error_details
    }


def resume_adsets(
    adset_id_list: List[str],
    access_token: str,
    delay_ms: int = 1000
) -> Dict[str, Any]:
    """
    Bật lại NHIỀU Adset bằng 1 LỆNH BATCH
    Thay thế cho hàm goiFacebookAPIDeBatNhieuAdset() từ Facebook API.gs
    
    Returns:
        Dict với keys: success, errors, errorDetails
    """
    if not adset_id_list:
        return {"success": 0, "errors": 0, "errorDetails": []}
    
    batches = chunk_list(adset_id_list, 50)
    success_count = 0
    error_count = 0
    error_details = []
    
    for batch_idx, batch_ids in enumerate(batches):
        try:
            if batch_idx > 0 and delay_ms > 0:
                logger.info(f"Đang chờ {delay_ms / 1000} giây trước khi gửi batch tiếp theo...")
                time.sleep(delay_ms / 1000)
            
            # Tạo batch payload
            batch_payload = []
            for adset_id in batch_ids:
                batch_payload.append({
                    "method": "POST",
                    "relative_url": f"{FB_API_VERSION}/{adset_id}",
                    "body": "status=ACTIVE"
                })
            
            # Gửi batch request
            form_data = {
                'access_token': access_token,
                'batch': str(batch_payload).replace("'", '"')  # Convert to JSON string
            }
            
            url = f"{FB_GRAPH_API_BASE}/"
            response = requests.post(url, data=form_data, timeout=60)
            response.raise_for_status()
            
            json_response = response.json()
            if isinstance(json_response, list):
                for i, item in enumerate(json_response):
                    adset_id = batch_ids[i] if i < len(batch_ids) else ""
                    if item.get('code') == 200:
                        success_count += 1
                    else:
                        error_count += 1
                        error_msg = "Unknown error"
                        try:
                            if 'body' in item:
                                body = item['body']
                                if isinstance(body, str):
                                    import json
                                    body_json = json.loads(body)
                                    if 'error' in body_json:
                                        error_msg = body_json['error'].get('message', error_msg)
                                else:
                                    error_msg = str(body)
                        except Exception:
                            error_msg = item.get('body', 'Failed to parse error')
                        
                        error_details.append({"adsetId": adset_id, "error": error_msg})
            else:
                error_count += len(batch_ids)
                for adset_id in batch_ids:
                    error_details.append({
                        "adsetId": adset_id,
                        "error": "Batch API error: Invalid response format"
                    })
        except Exception as e:
            error_count += len(batch_ids)
            for adset_id in batch_ids:
                error_details.append({
                    "adsetId": adset_id,
                    "error": f"Exception: {str(e)}"
                })
    
    logger.info(f"Thực thi Batch BẬT LẠI hoàn tất. Thành công: {success_count}, Thất bại: {error_count}")
    return {
        "success": success_count,
        "errors": error_count,
        "errorDetails": error_details
    }


def pull_facebook_data(
    access_token: str,
    ad_account_ids: List[str],
    date_preset: str = "yesterday"
) -> List[Dict[str, Any]]:
    """
    Kéo dữ liệu Insights level=ad từ Facebook API
    Thay thế cho hàm pullFacebookData() từ Facebook API.gs
    
    Returns:
        List of ad metrics dictionaries
    """
    # Fields hợp lệ cho insights
    fields = [
        'account_name', 'account_id', 'campaign_name', 'campaign_id',
        'adset_id', 'adset_name',
        'ad_id', 'ad_name',
        'spend', 'impressions', 'reach', 'frequency', 'clicks', 'ctr', 'cpc',
        'cost_per_initiate_checkout', 'cost_per_purchase',
        'cost_per_action_type', 'actions', 'action_values'
    ]
    fields_string = ','.join(fields)
    
    all_rows = []
    
    for account_id in ad_account_ids:
        try:
            # Lấy insights từ account
            url = (
                f"{FB_GRAPH_API_BASE}/{account_id}/insights"
                f"?level=ad"
                f"&fields={fields_string}"
                f"&date_preset={date_preset}"
                f"&limit=1000"
                f"&access_token={access_token}"
            )
            
            while url:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                json_data = response.json()
                if 'error' in json_data:
                    raise Exception(f"Facebook API error: {json_data['error']['message']}")
                
                data = json_data.get('data', [])
                for item in data:
                    # Parse actions và action_values
                    actions = item.get('actions', [])
                    action_values = item.get('action_values', [])
                    
                    # Tính toán các metrics
                    spend = float(item.get('spend', 0) or 0)
                    impressions = int(item.get('impressions', 0) or 0)
                    clicks = int(item.get('clicks', 0) or 0)
                    ctr = float(item.get('ctr', 0) or 0)
                    cpc = float(item.get('cpc', 0) or 0)
                    
                    # Tính kết quả (comments + messages)
                    results = 0
                    comments = 0
                    messages = 0
                    
                    for action in actions:
                        action_type = action.get('action_type', '')
                        value = int(action.get('value', 0) or 0)
                        if action_type == 'comment':
                            comments += value
                        elif action_type == 'onsite_conversion.messaging_conversation_started_7d':
                            messages += value
                    
                    results = comments + messages
                    
                    # Tính giá DATA
                    gia_data = (spend / results) if results > 0 else 0
                    
                    # Tính purchase value
                    purchase_value = 0
                    for action_value in action_values:
                        action_type = action_value.get('action_type', '')
                        value = float(action_value.get('value', 0) or 0)
                        if 'purchase' in action_type:
                            purchase_value += value
                    
                    # Tính % ADS và các metrics khác
                    percent_ads = (spend / purchase_value * 100) if purchase_value > 0 else 0
                    cost_per_checkout = float(item.get('cost_per_initiate_checkout', 0) or 0)
                    cost_per_purchase = float(item.get('cost_per_purchase', 0) or 0)
                    
                    # Tính CPM
                    cpm = (spend / impressions * 1000) if impressions > 0 else 0
                    
                    # Lấy prefix từ campaign name
                    campaign_name = item.get('campaign_name', '')
                    from app.services.logics import get_prefix_from_name
                    prefix = get_prefix_from_name(campaign_name)
                    
                    # Detect campaign type
                    campaign_objective = item.get('campaign_objective', '')
                    from app.services.campaign_detector import detect_campaign_type_from_objective
                    campaign_type = detect_campaign_type_from_objective(campaign_objective)
                    
                    # Tạo row data
                    row = {
                        'account_name': item.get('account_name', ''),
                        'account_id': item.get('account_id', ''),
                        'campaign_name': campaign_name,
                        'campaign_id': item.get('campaign_id', ''),
                        'adset_id': item.get('adset_id', ''),
                        'adset_name': item.get('adset_name', ''),
                        'ad_id': item.get('ad_id', ''),
                        'ad_name': item.get('ad_name', ''),
                        'prefix': prefix,
                        'campaign_type': campaign_type,
                        'campaign_objective': campaign_objective,
                        'adset_status': 'ACTIVE',  # Mặc định, sẽ được cập nhật sau
                        'effective_status': '',  # Sẽ được cập nhật sau
                        'spend': spend,
                        'amount_spent': spend,
                        'results': results,
                        'ket_qua': results,
                        'gia_data': gia_data,
                        'percent_ads': percent_ads,
                        'cost_per_checkout_initiated': cost_per_checkout,
                        'checkouts_initiated': 0,  # Cần parse từ actions
                        'cost_per_purchase': cost_per_purchase,
                        'purchases': 0,  # Cần parse từ actions
                        'gia_tri_chuyen_doi_tu_luot_mua': purchase_value,
                        'cpm': cpm,
                        'impressions': impressions,
                        'reach': int(item.get('reach', 0) or 0),
                        'frequency': float(item.get('frequency', 0) or 0),
                        'clicks': clicks,
                        'clicks_all': clicks,
                        'ctr': ctr,
                        'ctr_all': ctr,
                        'cpc': cpc,
                        'cpc_all': cpc,
                        'cost_per_comment': (spend / comments) if comments > 0 else 0,
                        'cost_per_messaging_conversation': (spend / messages) if messages > 0 else 0,
                        'post_comments': comments,
                        'messaging_conversations_started': messages,
                        'date': datetime.now(),
                        'date_preset': date_preset,
                    }
                    
                    all_rows.append(row)
                
                # Check for next page
                paging = json_data.get('paging', {})
                url = paging.get('next', '')
                
        except Exception as e:
            logger.error(f"🚨 Lỗi khi lấy dữ liệu từ account {account_id}: {e}")
            continue
    
    logger.info(f"✅ Đã lấy {len(all_rows)} ads từ Facebook API")
    return all_rows


def get_daily_breakdown_data(
    access_token: str,
    ad_account_ids: List[str],
    date_preset: str = "yesterday"
) -> Dict[str, Dict[str, List[str]]]:
    """
    Lấy dữ liệu breakdown theo ngày để kiểm tra tin nhắn và checkout cùng ngày
    Thay thế cho hàm getDailyBreakdownData() từ Facebook API.gs
    
    Returns:
        Dict { adset_id: { msgDates: [], checkoutDates: [] } }
    """
    result = {}
    
    for account_id in ad_account_ids:
        try:
            url = (
                f"{FB_GRAPH_API_BASE}/{account_id}/insights"
                f"?level=adset"
                f"&fields=adset_id,actions,action_values"
                f"&date_preset={date_preset}"
                f"&time_increment=1"
                f"&limit=1000"
                f"&access_token={access_token}"
            )
            
            while url:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                json_data = response.json()
                if 'error' in json_data:
                    raise Exception(f"Facebook API error: {json_data['error']['message']}")
                
                data = json_data.get('data', [])
                for item in data:
                    adset_id = item.get('adset_id', '')
                    if not adset_id:
                        continue
                    
                    if adset_id not in result:
                        result[adset_id] = {
                            'msgDates': [],
                            'checkoutDates': []
                        }
                    
                    # Parse date từ date_start
                    date_start = item.get('date_start', '')
                    if date_start:
                        actions = item.get('actions', [])
                        for action in actions:
                            action_type = action.get('action_type', '')
                            if 'messaging_conversation' in action_type:
                                result[adset_id]['msgDates'].append(date_start)
                            elif 'initiate_checkout' in action_type:
                                result[adset_id]['checkoutDates'].append(date_start)
                
                # Check for next page
                paging = json_data.get('paging', {})
                url = paging.get('next', '')
                
        except Exception as e:
            logger.error(f"🚨 Lỗi khi lấy daily breakdown từ account {account_id}: {e}")
            continue
    
    return result

