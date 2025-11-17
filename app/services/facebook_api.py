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


def pause_campaign(
    campaign_id: str,
    access_token: str
) -> Dict[str, Any]:
    """
    Tắt một Campaign
    """
    try:
        url = f"{FB_GRAPH_API_BASE}/{campaign_id}"
        params = {
            'access_token': access_token
        }
        data = {
            'status': 'PAUSED'
        }
        
        response = requests.post(url, params=params, data=data, timeout=30)
        response.raise_for_status()
        
        return {"success": True, "campaign_id": campaign_id}
    except Exception as e:
        logger.error(f"🚨 Lỗi tắt Campaign {campaign_id}: {e}")
        return {"success": False, "campaign_id": campaign_id, "error": str(e)}


def get_campaign_adsets_count(
    campaign_id: str,
    access_token: str
) -> int:
    """
    Lấy số lượng adsets trong một campaign
    """
    try:
        url = f"{FB_GRAPH_API_BASE}/{campaign_id}/adsets"
        params = {
            'access_token': access_token,
            'fields': 'id',
            'limit': 1
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        json_data = response.json()
        # Lấy total count từ paging nếu có
        if 'paging' in json_data and 'cursors' in json_data['paging']:
            # Nếu có paging, cần đếm tất cả
            count = 0
            url_with_count = f"{FB_GRAPH_API_BASE}/{campaign_id}/adsets"
            params_count = {
                'access_token': access_token,
                'fields': 'id',
                'limit': 100
            }
            
            while url_with_count:
                response = requests.get(url_with_count, params=params_count, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data:
                    count += len(data['data'])
                
                # Check for next page
                if 'paging' in data and 'next' in data['paging']:
                    url_with_count = data['paging']['next']
                else:
                    url_with_count = None
            
            return count
        else:
            # Không có paging, trả về số lượng trong data
            return len(json_data.get('data', []))
    except Exception as e:
        logger.error(f"🚨 Lỗi lấy số adsets của Campaign {campaign_id}: {e}")
        return 0


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


def update_adset_budget(
    adset_id: str,
    access_token: str,
    action_type: str = "increase",  # "increase", "decrease", "set"
    amount: Optional[float] = None,  # Amount to increase/decrease, or absolute value if action_type="set"
    percent: Optional[float] = None  # Percentage to increase/decrease (e.g., 10 for 10%)
) -> Dict[str, Any]:
    """
    Cập nhật ngân sách của adset
    
    Args:
        adset_id: ID của adset
        access_token: Facebook access token
        action_type: "increase", "decrease", hoặc "set"
        amount: Số tiền tăng/giảm hoặc giá trị tuyệt đối (nếu action_type="set")
        percent: Phần trăm tăng/giảm (ưu tiên hơn amount nếu có)
    
    Returns:
        Dict với keys: success, adset_id, old_budget, new_budget, error
    """
    try:
        # Lấy budget hiện tại
        url = f"{FB_GRAPH_API_BASE}/{adset_id}"
        params = {
            'fields': 'daily_budget,lifetime_budget',
            'access_token': access_token
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        adset_data = response.json()
        
        if 'error' in adset_data:
            return {
                "success": False,
                "adset_id": adset_id,
                "error": adset_data['error'].get('message', 'Unknown error')
            }
        
        # Xác định budget hiện tại (daily_budget hoặc lifetime_budget)
        current_budget = float(adset_data.get('daily_budget') or adset_data.get('lifetime_budget') or 0)
        budget_type = 'daily_budget' if adset_data.get('daily_budget') else 'lifetime_budget'
        
        # Tính toán budget mới
        if percent is not None:
            # Tính theo phần trăm
            if action_type == "increase":
                new_budget = current_budget * (1 + percent / 100)
            elif action_type == "decrease":
                new_budget = current_budget * (1 - percent / 100)
            else:
                return {
                    "success": False,
                    "adset_id": adset_id,
                    "error": "percent chỉ hỗ trợ với action_type='increase' hoặc 'decrease'"
                }
        elif amount is not None:
            # Tính theo số tiền
            if action_type == "increase":
                new_budget = current_budget + abs(amount)
            elif action_type == "decrease":
                new_budget = max(0, current_budget - abs(amount))
            elif action_type == "set":
                new_budget = abs(amount)
            else:
                return {
                    "success": False,
                    "adset_id": adset_id,
                    "error": "Invalid action_type. Use 'increase', 'decrease', or 'set'"
                }
        else:
            # Mặc định tăng 10% nếu không có amount hoặc percent
            if action_type == "increase":
                new_budget = current_budget * 1.1
            elif action_type == "decrease":
                new_budget = current_budget * 0.9
            else:
                return {
                    "success": False,
                    "adset_id": adset_id,
                    "error": "Cần cung cấp amount hoặc percent"
                }
        
        # Round to 2 decimals (Facebook yêu cầu)
        new_budget = round(new_budget * 100) / 100
        
        # Update budget
        update_url = f"{FB_GRAPH_API_BASE}/{adset_id}"
        update_params = {
            'access_token': access_token
        }
        update_data = {
            budget_type: new_budget
        }
        
        update_response = requests.post(update_url, params=update_params, data=update_data, timeout=30)
        update_response.raise_for_status()
        
        result = update_response.json()
        
        if 'error' in result:
            return {
                "success": False,
                "adset_id": adset_id,
                "old_budget": current_budget,
                "error": result['error'].get('message', 'Unknown error')
            }
        
        logger.info(f"✅ Đã cập nhật budget adset {adset_id}: {current_budget} → {new_budget}")
        
        return {
            "success": True,
            "adset_id": adset_id,
            "old_budget": current_budget,
            "new_budget": new_budget,
            "budget_type": budget_type
        }
        
    except Exception as e:
        logger.error(f"🚨 Lỗi cập nhật budget adset {adset_id}: {e}")
        return {
            "success": False,
            "adset_id": adset_id,
            "error": str(e)
        }


def pull_facebook_data(
    access_token: str,
    ad_account_ids: List[str],
    date_preset: Optional[str] = "yesterday",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
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
    
    # Cache để lưu campaign objectives (tránh gọi API nhiều lần)
    campaign_objectives_cache = {}
    
    def fetch_campaign_objectives_batch(campaign_ids: List[str], access_token: str) -> Dict[str, str]:
        """Lấy campaign objectives từ campaign objects (batch request)"""
        if not campaign_ids:
            return {}
        
        objectives_map = {}
        # Chia thành batches 50 campaigns mỗi batch
        campaign_batches = chunk_list(campaign_ids, 50)
        
        for batch in campaign_batches:
            try:
                # Tạo batch request
                batch_payload = []
                for campaign_id in batch:
                    batch_payload.append({
                        "method": "GET",
                        "relative_url": f"{FB_API_VERSION}/{campaign_id}?fields=objective"
                    })
                
                import json
                url = f"{FB_GRAPH_API_BASE}/"
                form_data = {
                    'access_token': access_token,
                    'batch': json.dumps(batch_payload)
                }
                
                response = requests.post(url, data=form_data, timeout=60)
                response.raise_for_status()
                
                json_response = response.json()
                if isinstance(json_response, list):
                    for i, item in enumerate(json_response):
                        if i < len(batch):
                            campaign_id = batch[i]
                            if item.get('code') == 200:
                                try:
                                    body = item.get('body', '{}')
                                    if isinstance(body, str):
                                        body_json = json.loads(body)
                                    else:
                                        body_json = body
                                    objective = body_json.get('objective', '')
                                    if objective:
                                        objectives_map[campaign_id] = objective
                                except Exception:
                                    pass
            except Exception as e:
                logger.warning(f"Lỗi khi lấy campaign objectives batch: {e}")
                continue
        
        return objectives_map
    
    for account_id in ad_account_ids:
        try:
            logger.info(f"Đang kéo dữ liệu cho tài khoản: {account_id} (Phạm vi: {date_preset})")
            
            # Xử lý pagination: Lấy TẤT CẢ pages (không chỉ page đầu tiên)
            next_url = None
            page_count = 0
            
            while True:
                page_count += 1
                
                if next_url:
                    # Lấy page tiếp theo từ next_url
                    url = next_url
                else:
                    # Tạo URL cho page đầu tiên
                    # QUAN TRỌNG: Với date_preset=yesterday, có thể dùng time_range để chính xác hơn
                    # Nhưng để đơn giản, dùng date_preset trực tiếp (Facebook API tự xử lý múi giờ)
                    url = (
                        f"{FB_GRAPH_API_BASE}/{account_id}/insights"
                        f"?level=ad"
                        f"&fields={fields_string}"
                        f"&limit=1000"
                        f"&access_token={access_token}"
                    )
                    
                    # Xử lý date_preset hoặc custom date range
                    import json
                    from urllib.parse import quote
                    
                    if date_from and date_to:
                        # Dùng custom date range với time_range
                        # Facebook API until là EXCLUSIVE, nên phải +1 ngày
                        from datetime import datetime as dt
                        try:
                            date_to_obj = dt.strptime(date_to, '%Y-%m-%d')
                            date_to_obj = date_to_obj + timedelta(days=1)  # +1 vì until là exclusive
                            date_to_str = date_to_obj.strftime('%Y-%m-%d')
                            
                            time_range_json = json.dumps({"since": date_from, "until": date_to_str})
                            url += f'&time_range={quote(time_range_json)}'
                        except ValueError:
                            # Fallback to date_preset nếu parse lỗi
                            if date_preset:
                                url += f'&date_preset={date_preset}'
                            else:
                                url += '&date_preset=last_7_days'
                    elif date_preset == 'yesterday':
                        # Convert yesterday sang time_range để chính xác hơn (giống Google Script)
                        from datetime import timezone, timedelta
                        # Dùng timezone Asia/Ho_Chi_Minh (UTC+7)
                        tz = timezone(timedelta(hours=7))
                        now = datetime.now(tz)
                        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                        yesterday = today - timedelta(days=1)
                        
                        # QUAN TRỌNG: Facebook API until là EXCLUSIVE, nên phải +1 ngày
                        since = yesterday.strftime('%Y-%m-%d')
                        until = today.strftime('%Y-%m-%d')  # until = today (exclusive, nên lấy hết yesterday)
                        time_range_json = json.dumps({"since": since, "until": until})
                        url += f'&time_range={quote(time_range_json)}'
                    else:
                        if date_preset:
                            url += f'&date_preset={date_preset}'
                        else:
                            url += '&date_preset=last_7_days'
                    
                    # Thêm action_report_time và attribution settings (giống Google Script)
                    url += (
                        '&action_report_time=conversion'
                        '&use_unified_attribution_setting=true'
                        '&action_attribution_windows=1d_click,7d_click,1d_view,7d_view'
                    )
                
                # Fetch data
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                json_data = response.json()
                if 'error' in json_data:
                    error_code = json_data['error'].get('code', 0)
                    error_msg = json_data['error'].get('message', 'Unknown error')
                    if error_code in [190, 100]:
                        raise Exception(f"Lỗi Token hoặc Quyền (Code {error_code}). Chi tiết: {error_msg}")
                    elif error_code == 200:
                        raise Exception(f"Mất quyền truy cập TK (Code 200). Chi tiết: {error_msg}")
                    raise Exception(f"LỖI API: {error_msg}")
                
                data = json_data.get('data', [])
                
                if not data or not isinstance(data, list) or len(data) == 0:
                    if page_count == 1:
                        logger.warning(f"⚠️ Tài khoản {account_id} không có dữ liệu insights cho {date_preset}.")
                        logger.warning("   (Có thể do: không có ads chạy trong khoảng thời gian này, hoặc không có quyền truy cập)")
                    break  # Không có dữ liệu, thoát khỏi vòng lặp
                
                logger.info(f"   📊 Page {page_count}: Nhận được {len(data)} ads từ API...")
                
                # Collect unique campaign IDs để fetch objectives
                campaign_ids_to_fetch = []
                for item in data:
                    campaign_id = item.get('campaign_id', '')
                    if campaign_id and campaign_id not in campaign_objectives_cache:
                        campaign_ids_to_fetch.append(campaign_id)
                
                # Fetch campaign objectives nếu có campaigns mới
                if campaign_ids_to_fetch:
                    logger.info(f"   🔍 Đang lấy objectives cho {len(campaign_ids_to_fetch)} campaigns...")
                    new_objectives = fetch_campaign_objectives_batch(campaign_ids_to_fetch, access_token)
                    campaign_objectives_cache.update(new_objectives)
                
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
                    
                    # Parse actions với nhiều variants (giống Google Script)
                    # Tạo map từ actions array để lookup nhanh
                    def build_action_map(actions_list):
                        """Tạo map { action_type: value } từ actions array"""
                        action_map = {}
                        if not actions_list or not isinstance(actions_list, list):
                            return action_map
                        for action_item in actions_list:
                            if not action_item:
                                continue
                            # Giữ nguyên case để match với bases (không lowercase)
                            action_type = str(action_item.get('action_type', ''))
                            value = float(action_item.get('value', 0) or 0)
                            if action_type:
                                # Nếu đã có, cộng dồn
                                if action_type in action_map:
                                    action_map[action_type] += value
                                else:
                                    action_map[action_type] = value
                        return action_map
                    
                    def pick_first_variant(action_map, bases, suffixes=None):
                        """
                        Tìm giá trị đầu tiên từ action_map với các variants
                        Giống hàm _pickFirstVariant_() từ Google Script
                        Case-insensitive matching
                        """
                        if suffixes is None:
                            suffixes = ["", "_unique", "_1d_click", "_7d_click", "_28d_click", 
                                       "_1d_view", "_7d_view", "_28d_view"]
                        
                        # Tạo lowercase map để lookup nhanh
                        action_map_lower = {k.lower(): v for k, v in action_map.items()}
                        
                        for base in bases:
                            for suffix in suffixes:
                                key = base + suffix
                                key_lower = key.lower()
                                if key_lower in action_map_lower:
                                    return float(action_map_lower[key_lower]) or 0
                        return 0
                    
                    # Build action map
                    act_map = build_action_map(actions)
                    
                    # Danh sách các action type variants - ĐẦY ĐỦ để bắt được tất cả cách Facebook trả về
                    # Giống Google Script (dòng 728-742)
                    bases_ic = ['initiate_checkout', 'offsite_conversion.fb_pixel_initiate_checkout', 
                               'omni_initiated_checkout', 'onsite_conversion.initiated_checkout']
                    bases_pur = ['purchase', 'offsite_conversion.fb_pixel_purchase', 
                                'omni_purchase', 'onsite_conversion.purchase']
                    bases_cmt = ['comment', 'post_comment', 'onsite_conversion.post_comment']
                    bases_msg = ['onsite_conversion.messaging_conversation_started', 
                                'messaging_conversation_started',
                                'messaging_conversation_started_1d_click',
                                'messaging_conversation_started_7d_click']
                    
                    # Lấy giá trị từ các variants
                    initiate_checkout = pick_first_variant(act_map, bases_ic)
                    purchases = pick_first_variant(act_map, bases_pur)
                    post_comments = pick_first_variant(act_map, bases_cmt)
                    msg_started = pick_first_variant(act_map, bases_msg)
                    
                    # Fallback THÔNG MINH: Nếu không tìm thấy, tìm trong act_map với tất cả variants
                    # (giống Google Script dòng 754-819)
                    if msg_started == 0 and spend > 0:
                        # Tìm tất cả keys có chứa messaging_conversation_started (case-insensitive)
                        all_msg_keys = [k for k in act_map.keys() 
                                       if 'messaging_conversation_started' in k.lower() 
                                       and '_unique' not in k.lower()]
                        if all_msg_keys:
                            # Ưu tiên base (không có suffix)
                            base_keys = [k for k in all_msg_keys 
                                        if '_1d_' not in k.lower() 
                                        and '_7d_' not in k.lower() 
                                        and '_28d_' not in k.lower()]
                            target_keys = base_keys if base_keys else all_msg_keys
                            msg_started = max([float(act_map.get(k, 0) or 0) for k in target_keys], default=0)
                    
                    if post_comments == 0 and spend > 0:
                        # Tìm tất cả keys có chứa comment (case-insensitive)
                        all_comment_keys = [k for k in act_map.keys() 
                                           if ('comment' in k.lower() or k.lower() == 'comment' 
                                               or k.lower() == 'post_comment')
                                           and '_unique' not in k.lower()]
                        if all_comment_keys:
                            # Ưu tiên base (không có suffix)
                            base_comment_keys = [k for k in all_comment_keys 
                                                if '_1d_' not in k.lower() 
                                                and '_7d_' not in k.lower() 
                                                and '_28d_' not in k.lower()]
                            target_comment_keys = base_comment_keys if base_comment_keys else all_comment_keys
                            post_comments = max([float(act_map.get(k, 0) or 0) for k in target_comment_keys], default=0)
                    
                    # Tính kết quả (comments + messages)
                    comments = int(post_comments)
                    messages = int(msg_started)
                    results = comments + messages
                    checkouts = int(initiate_checkout)
                    
                    # Tính giá DATA
                    gia_data = (spend / results) if results > 0 else 0
                    
                    # Tính purchase value (giống Google Script - dùng pick_first_variant)
                    def build_value_map(values_list):
                        """Tạo map { action_type: value } từ action_values array"""
                        value_map = {}
                        if not values_list or not isinstance(values_list, list):
                            return value_map
                        for value_item in values_list:
                            if not value_item:
                                continue
                            action_type = str(value_item.get('action_type', ''))
                            value = float(value_item.get('value', 0) or 0)
                            if action_type:
                                if action_type in value_map:
                                    value_map[action_type] += value
                                else:
                                    value_map[action_type] = value
                        return value_map
                    
                    val_map = build_value_map(action_values)
                    purchase_value = pick_first_variant(val_map, bases_pur)
                    
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
                    # Lấy campaign_objective từ cache (đã fetch từ campaign objects)
                    campaign_id = item.get('campaign_id', '')
                    campaign_objective = campaign_objectives_cache.get(campaign_id, '')
                    from app.services.campaign_detector import (
                        detect_campaign_type_from_objective,
                        detect_campaign_type_from_metrics,
                        detect_campaign_type_hybrid
                    )
                    
                    # Tạo metrics dict để detect
                    metrics_dict = {
                        'purchases': purchases,
                        'gia_tri_chuyen_doi_tu_luot_mua': purchase_value,
                        'messaging_conversations_started': messages,
                        'post_comments': comments,
                        'checkouts_initiated': checkouts
                    }
                    
                    # Dùng hybrid detection (ưu tiên objective, fallback metrics)
                    campaign_type = detect_campaign_type_hybrid(
                        objective=campaign_objective,
                        metrics=metrics_dict
                    )
                    
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
                        'checkouts_initiated': checkouts,  # Đã parse từ actions
                        'cost_per_purchase': cost_per_purchase,
                        'purchases': purchases,  # Đã parse từ actions
                        'sdt': checkouts,  # SĐT = checkouts (alias)
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
                next_url = paging.get('next', '')
                
                if not next_url:
                    # Không còn page nào, thoát khỏi vòng lặp
                    break
                
                logger.info(f"   📄 Page {page_count}: Nhận được {len(data)} ads, có page tiếp theo...")
            # Kết thúc while True loop
            
            logger.info(f"   ✅ Hoàn tất tài khoản {account_id}: Tổng {page_count} page(s)")
                
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

