"""
Facebook API Service
Thay thế cho Facebook API.gs từ Google Apps Script
"""
import time
import requests
import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

# Facebook Graph API version
FB_API_VERSION = "v24.0"
FB_GRAPH_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"


def _normalize_budget(value) -> int:
    """
    Chuẩn hóa budget value thành integer để tránh lỗi:
    "Param daily_budget must be an integer. Instead, got float."
    
    Args:
        value: Có thể là str, float, int, Decimal
    
    Returns:
        int: Budget value đã chuẩn hóa (>= 0)
    """
    if value is None:
        return 0
    
    # Xử lý string
    if isinstance(value, str):
        # Loại bỏ dấu phân cách (99.999 hoặc 99,999)
        clean = value.replace(".", "").replace(",", "")
        value = clean or "0"
        value = int(value)
    
    # Xử lý Decimal
    if isinstance(value, Decimal):
        value = float(value)
    
    # Xử lý float
    if isinstance(value, float):
        # Round để tránh 99998.9999
        value = round(value)
    
    # Convert sang int và đảm bảo >= 0
    value_int = max(int(value), 0)
    
    return value_int


# Custom exceptions
class FacebookRateLimitError(Exception):
    """Raised when Facebook API rate limit is reached"""
    pass

# Global cache cho objectives và budgets (cache lâu hơn - 5 phút)
_objectives_cache: Dict[str, Dict[str, str]] = {}  # {access_token: {campaign_id: objective}}
_budgets_cache: Dict[str, Dict[str, float]] = {}  # {access_token: {adset_id: budget}}
_status_cache: Dict[str, Dict[str, str]] = {}  # {access_token: {adset_id: status}}
_cache_timestamps: Dict[str, datetime] = {}  # {cache_key: timestamp}
CACHE_TTL_OBJECTIVES_BUDGETS = 300  # 5 phút
CACHE_TTL_STATUS = 120  # 2 phút (status thay đổi thường xuyên hơn)


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


# Status normalization constants
ACTIVE_STATUSES = {
    "ACTIVE", "IN_PROCESS", "WITH_ISSUES",
    "PREAPPROVED", "PENDING_REVIEW"
}

PAUSED_STATUSES = {
    "PAUSED", "ADSET_PAUSED", "CAMPAIGN_PAUSED"
}

DELETED_STATUSES = {"DELETED", "ARCHIVED"}


def normalize_status(effective_status: str) -> str:
    """
    Chuẩn hóa effective_status từ Facebook thành 3 trạng thái chính:
    ACTIVE, PAUSED, DELETED
    """
    if not effective_status:
        return "UNKNOWN"
    
    status_upper = effective_status.upper()
    
    if status_upper in ACTIVE_STATUSES:
        return "ACTIVE"
    if status_upper in PAUSED_STATUSES:
        return "PAUSED"
    if status_upper in DELETED_STATUSES:
        return "DELETED"
    
    # Fallback
    return "OTHER"


def fetch_adset_statuses(adset_ids: List[str], access_token: str, use_cache: bool = True) -> Dict[str, Dict[str, str]]:
    """
    Lấy map { adset_id: { configured_status, effective_status, campaign_configured_status, ... } }
    - configured_status: Status do user gạt (ACTIVE/PAUSED) - dùng cho nút gạt UI
    - effective_status: Status thực tế (ACTIVE, CAMPAIGN_PAUSED, ...) - dùng để biết có đang phân phối
    - campaign_configured_status: Status campaign do user gạt
    - campaign_effective_status: Status campaign thực tế
    Có cache global để tránh fetch lại nhiều lần
    """
    if not adset_ids:
        return {}
    
    # Check cache
    cache_key = f"status_{access_token[:20]}"  # Dùng 20 ký tự đầu của token làm key
    cached_result: Dict[str, Dict[str, str]] = {}
    
    if use_cache:
        now = datetime.now()
        cached_timestamp = _cache_timestamps.get(cache_key)
        if cached_timestamp:
            age_seconds = (now - cached_timestamp).total_seconds()
            if age_seconds < CACHE_TTL_STATUS:
                # Lấy từ cache những adset_ids có sẵn
                cached_statuses = _status_cache.get(access_token, {})
                cached_result = {
                    adset_id: cached_statuses[adset_id]
                    for adset_id in adset_ids
                    if adset_id in cached_statuses and cached_statuses.get(adset_id)
                }
                if len(cached_result) == len(adset_ids):
                    logger.info(f"✅ Cache hit cho statuses ({len(adset_ids)} adsets)")
                    return cached_result
                # Nếu thiếu một số, chỉ fetch những cái thiếu
                missing_ids = [
                    adset_id for adset_id in adset_ids
                    if adset_id not in cached_statuses or not cached_statuses.get(adset_id)
                ]
                if missing_ids:
                    logger.info(f"⏰ Cache partial hit: {len(cached_result)} cached, fetch thêm {len(missing_ids)} statuses...")
                    adset_ids = missing_ids
            else:
                # Cache expired, clear và fetch lại
                logger.info(f"⏰ Cache expired cho statuses, fetch lại...")
                _status_cache.pop(access_token, None)
                _cache_timestamps.pop(cache_key, None)
    
    # Fetch từ API
    status_map = {}
    batches = chunk_list(unique_list(adset_ids), 50)
    
    # DEBUG: Target adset FL-13.11-B9
    TARGET_ADSET_ID = "120237687958500742"
    
    for batch in batches:
        try:
            ids = ','.join(batch)
            # Lấy cả configured_status (nút gạt) và effective_status (trạng thái thực tế)
            # Và cả campaign status để kiểm tra
            fields = "id,configured_status,effective_status,status,campaign{id,configured_status,effective_status}"
            url = f"{FB_GRAPH_API_BASE}/?ids={ids}&fields={fields}&access_token={access_token}"
            
            logger.warning(f"   🔍 DEBUG_STATUS_API_CALL | adset_ids_sample={batch[:3]} | use_cache={use_cache}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            json_data = response.json()
            
            # DEBUG: Log raw response cho vài adsets đầu
            for idx, (aid, node) in enumerate(list(json_data.items())[:3]):
                logger.warning(
                    f"   🔍 DEBUG_STATUS_RAW[{idx}] | id={aid} | "
                    f"conf={node.get('configured_status')} | eff={node.get('effective_status')} | "
                    f"status={node.get('status')} | campaign={node.get('campaign')}"
                )
            
            if json_data and isinstance(json_data, dict):
                for adset_id, node in json_data.items():
                    if node:
                        # Lấy tất cả status fields
                        configured_status = node.get('configured_status') or node.get('status') or 'UNKNOWN'
                        effective_status = node.get('effective_status') or 'UNKNOWN'
                        
                        # Lấy campaign status
                        campaign = node.get('campaign', {})
                        campaign_configured = campaign.get('configured_status') if isinstance(campaign, dict) else 'UNKNOWN'
                        campaign_effective = campaign.get('effective_status') if isinstance(campaign, dict) else 'UNKNOWN'
                        
                        # Lưu dict đầy đủ thông tin
                        status_map[adset_id] = {
                            'configured_status': configured_status,
                            'effective_status': effective_status,
                            'campaign_configured_status': campaign_configured,
                            'campaign_effective_status': campaign_effective,
                        }
                        
                        # DEBUG: Log chi tiết cho FL-13.11-B9
                        if adset_id == TARGET_ADSET_ID:
                            logger.warning(
                                f"   ⚠️ DEBUG_FL_B9_STATUS | raw_status_info={status_map[adset_id]}"
                            )
                        
                        logger.debug(
                            f"   🔍 Adset {adset_id}: "
                            f"configured={configured_status}, effective={effective_status}, "
                            f"campaign_conf={campaign_configured}, campaign_eff={campaign_effective}"
                        )
        except Exception as e:
            logger.error(f"🚨 Lỗi lấy trạng thái AdSet (batch ids): {e}")
    
    # Merge cached + newly fetched
    final_result = {**cached_result, **status_map}
    
    # Update cache
    if use_cache and status_map:
        if access_token not in _status_cache:
            _status_cache[access_token] = {}
        _status_cache[access_token].update(status_map)
        _cache_timestamps[cache_key] = datetime.now()
    
    logger.info(f"   📦 Returning statuses: {len(cached_result)} from cache + {len(status_map)} fetched = {len(final_result)} total")
    return final_result


def fetch_ad_statuses(ad_ids: List[str], access_token: str, use_cache: bool = True) -> Dict[str, str]:
    """
    Lấy map { ad_id: normalized_status } qua batch (?ids=)
    Trả về status đã được normalize: ACTIVE, PAUSED, DELETED, OTHER
    Có cache global để tránh fetch lại nhiều lần
    """
    if not ad_ids:
        return {}
    
    # Check cache
    cache_key = f"ad_status_{access_token[:20]}"
    if use_cache:
        now = datetime.now()
        cached_timestamp = _cache_timestamps.get(cache_key)
        if cached_timestamp:
            age_seconds = (now - cached_timestamp).total_seconds()
            if age_seconds < CACHE_TTL_STATUS:
                # Lấy từ cache những ad_ids có sẵn
                cached_statuses = _status_cache.get(f"ads_{access_token}", {})
                result = {ad_id: cached_statuses.get(ad_id) for ad_id in ad_ids if ad_id in cached_statuses and cached_statuses.get(ad_id)}
                if len(result) == len(ad_ids):
                    logger.info(f"✅ Cache hit cho ad statuses ({len(ad_ids)} ads)")
                    return result
                # Nếu thiếu một số, chỉ fetch những cái thiếu
                missing_ids = [ad_id for ad_id in ad_ids if ad_id not in cached_statuses or not cached_statuses.get(ad_id)]
                if missing_ids:
                    logger.info(f"⏰ Cache partial hit, fetch thêm {len(missing_ids)} ad statuses...")
                    ad_ids = missing_ids
            else:
                # Cache expired
                logger.info(f"⏰ Cache expired cho ad statuses, fetch lại...")
                _status_cache.pop(f"ads_{access_token}", None)
                _cache_timestamps.pop(cache_key, None)
    
    # Fetch từ API
    status_map = {}
    batches = chunk_list(unique_list(ad_ids), 50)
    
    for batch in batches:
        try:
            ids = ','.join(batch)
            url = f"{FB_GRAPH_API_BASE}/?ids={ids}&fields=effective_status,status&access_token={access_token}"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            json_data = response.json()
            logger.debug(f"   🔍 DEBUG - Facebook response for ad statuses: {json_data}")
            if json_data and isinstance(json_data, dict):
                for ad_id, node in json_data.items():
                    if node:
                        effective_status = node.get('effective_status')
                        ad_status = node.get('status')
                        
                        if effective_status:
                            normalized = normalize_status(effective_status)
                            status_map[ad_id] = normalized
                            logger.debug(f"   🔍 Ad {ad_id}: effective={effective_status}, status={ad_status} → {normalized}")
                        else:
                            if ad_status:
                                normalized = normalize_status(ad_status)
                                status_map[ad_id] = normalized
                                logger.debug(f"   🔍 Ad {ad_id}: status={ad_status} → {normalized}")
                            else:
                                status_map[ad_id] = 'UNKNOWN'
                                logger.warning(f"   ⚠️ No status found for ad {ad_id}")
        except Exception as e:
            logger.error(f"🚨 Lỗi lấy trạng thái Ad (batch ids): {e}")
    
    # Update cache
    if use_cache and status_map:
        cache_ads_key = f"ads_{access_token}"
        if cache_ads_key not in _status_cache:
            _status_cache[cache_ads_key] = {}
        _status_cache[cache_ads_key].update(status_map)
        _cache_timestamps[cache_key] = datetime.now()
    
    return status_map


def fetch_campaign_statuses(campaign_ids: List[str], access_token: str, use_cache: bool = True) -> Dict[str, str]:
    """
    Lấy map { campaign_id: normalized_status } qua batch (?ids=)
    Trả về status đã được normalize: ACTIVE, PAUSED, DELETED, OTHER
    Có cache global để tránh fetch lại nhiều lần
    """
    if not campaign_ids:
        return {}
    
    # Check cache
    cache_key = f"campaign_status_{access_token[:20]}"
    if use_cache:
        now = datetime.now()
        cached_timestamp = _cache_timestamps.get(cache_key)
        if cached_timestamp:
            age_seconds = (now - cached_timestamp).total_seconds()
            if age_seconds < CACHE_TTL_STATUS:
                # Lấy từ cache những campaign_ids có sẵn
                cached_statuses = _status_cache.get(f"campaigns_{access_token}", {})
                result = {cid: cached_statuses.get(cid) for cid in campaign_ids if cid in cached_statuses and cached_statuses.get(cid)}
                if len(result) == len(campaign_ids):
                    logger.info(f"✅ Cache hit cho campaign statuses ({len(campaign_ids)} campaigns)")
                    return result
                # Nếu thiếu một số, chỉ fetch những cái thiếu
                missing_ids = [cid for cid in campaign_ids if cid not in cached_statuses or not cached_statuses.get(cid)]
                if missing_ids:
                    logger.info(f"⏰ Cache partial hit, fetch thêm {len(missing_ids)} campaign statuses...")
                    campaign_ids = missing_ids
            else:
                # Cache expired
                logger.info(f"⏰ Cache expired cho campaign statuses, fetch lại...")
                _status_cache.pop(f"campaigns_{access_token}", None)
                _cache_timestamps.pop(cache_key, None)
    
    # Fetch từ API
    status_map = {}
    batches = chunk_list(unique_list(campaign_ids), 50)
    
    for batch in batches:
        try:
            ids = ','.join(batch)
            url = f"{FB_GRAPH_API_BASE}/?ids={ids}&fields=effective_status,status&access_token={access_token}"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            json_data = response.json()
            logger.debug(f"   🔍 DEBUG - Facebook response for campaign statuses: {json_data}")
            if json_data and isinstance(json_data, dict):
                for campaign_id, node in json_data.items():
                    if node:
                        effective_status = node.get('effective_status')
                        campaign_status = node.get('status')
                        
                        if effective_status:
                            normalized = normalize_status(effective_status)
                            status_map[campaign_id] = normalized
                            logger.debug(f"   🔍 Campaign {campaign_id}: effective={effective_status}, status={campaign_status} → {normalized}")
                        else:
                            if campaign_status:
                                normalized = normalize_status(campaign_status)
                                status_map[campaign_id] = normalized
                                logger.debug(f"   🔍 Campaign {campaign_id}: status={campaign_status} → {normalized}")
                            else:
                                status_map[campaign_id] = 'UNKNOWN'
                                logger.warning(f"   ⚠️ No status found for campaign {campaign_id}")
        except Exception as e:
            logger.error(f"🚨 Lỗi lấy trạng thái Campaign (batch ids): {e}")
    
    # Update cache
    if use_cache and status_map:
        cache_campaigns_key = f"campaigns_{access_token}"
        if cache_campaigns_key not in _status_cache:
            _status_cache[cache_campaigns_key] = {}
        _status_cache[cache_campaigns_key].update(status_map)
        _cache_timestamps[cache_key] = datetime.now()
    
    return status_map


def fetch_adset_budgets(adset_ids: List[str], access_token: str, use_cache: bool = True) -> Dict[str, float]:
    """
    Lấy map { adset_id: budget } qua batch (?ids=)
    Budget = daily_budget hoặc lifetime_budget (tùy loại)
    Có cache global để tránh fetch lại nhiều lần
    """
    if not adset_ids:
        return {}
    
    # Check cache
    cache_key = f"budgets_{access_token[:20]}"  # Dùng 20 ký tự đầu của token làm key
    if use_cache:
        now = datetime.now()
        cached_timestamp = _cache_timestamps.get(cache_key)
        if cached_timestamp:
            age_seconds = (now - cached_timestamp).total_seconds()
            if age_seconds < CACHE_TTL_OBJECTIVES_BUDGETS:
                # Lấy từ cache những adset_ids có sẵn
                cached_budgets = _budgets_cache.get(access_token, {})
                result = {adset_id: cached_budgets.get(adset_id, 0.0) for adset_id in adset_ids if adset_id in cached_budgets}
                if len(result) == len(adset_ids):
                    logger.info(f"✅ Cache hit cho budgets ({len(adset_ids)} adsets)")
                    return result
                # Nếu thiếu một số, chỉ fetch những cái thiếu
                missing_ids = [adset_id for adset_id in adset_ids if adset_id not in cached_budgets]
                if missing_ids:
                    logger.info(f"⏰ Cache partial hit, fetch thêm {len(missing_ids)} budgets...")
                    adset_ids = missing_ids
            else:
                # Cache expired, clear và fetch lại
                logger.info(f"⏰ Cache expired cho budgets, fetch lại...")
                _budgets_cache.pop(access_token, None)
                _cache_timestamps.pop(cache_key, None)
    
    # Fetch từ API
    budget_map = {}
    batches = chunk_list(unique_list(adset_ids), 50)
    
    for batch in batches:
        try:
            ids = ','.join(batch)
            url = f"{FB_GRAPH_API_BASE}/?ids={ids}&fields=daily_budget,lifetime_budget&access_token={access_token}"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            json_data = response.json()
            if json_data and isinstance(json_data, dict):
                for adset_id, node in json_data.items():
                    if node:
                        # Lưu CẢ daily và lifetime budget vào dict
                        daily = float(node.get('daily_budget', 0) or 0)
                        lifetime = float(node.get('lifetime_budget', 0) or 0)
                        budget_map[adset_id] = {
                            'daily_budget': daily,
                            'lifetime_budget': lifetime,
                            'budget': daily if daily > 0 else lifetime  # Fallback cho backward compat
                        }
        except Exception as e:
            logger.error(f"🚨 Lỗi lấy budget AdSet (batch ids): {e}")
    
    # Update cache
    if use_cache and budget_map:
        if access_token not in _budgets_cache:
            _budgets_cache[access_token] = {}
        _budgets_cache[access_token].update(budget_map)
        _cache_timestamps[cache_key] = datetime.now()
    
    return budget_map


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


def resume_campaign(
    campaign_id: str,
    access_token: str
) -> Dict[str, Any]:
    """
    Bật một Campaign
    """
    try:
        url = f"{FB_GRAPH_API_BASE}/{campaign_id}"
        params = {
            'access_token': access_token
        }
        data = {
            'status': 'ACTIVE'
        }
        
        response = requests.post(url, params=params, data=data, timeout=30)
        response.raise_for_status()
        
        return {"success": True, "campaign_id": campaign_id}
    except Exception as e:
        logger.error(f"🚨 Lỗi bật Campaign {campaign_id}: {e}")
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


def fetch_all_adsets_from_accounts(
    ad_account_ids: List[str],
    access_token: str,
    view_mode: str = "ecommerce",
    account_type_map: Optional[Dict[str, str]] = None,
    use_cache: bool = True
) -> Dict[str, Dict[str, str]]:
    """
    Fetch tất cả adsets từ accounts (không chỉ từ insights) để đếm đúng số lượng
    Returns: { adset_id: { effective_status, campaign_id, ... } }
    """
    if not ad_account_ids:
        return {}
    
    all_adsets_map = {}
    
    for account_id in ad_account_ids:
        try:
            # Đảm bảo account_id có prefix "act_"
            if not account_id.startswith("act_"):
                account_id_formatted = f"act_{account_id}"
            else:
                account_id_formatted = account_id
            
            # Filter theo account_type nếu có
            if account_type_map:
                clean_id = account_id.replace('act_', '')
                account_type = account_type_map.get(clean_id)
                if view_mode == "ecommerce" and account_type != "E-COMMERCE":
                    continue
                elif view_mode == "lead" and account_type != "LEAD_GENERATION":
                    continue
            
            # Fetch tất cả adsets từ account
            url = f"{FB_GRAPH_API_BASE}/{account_id_formatted}/adsets"
            params = {
                'access_token': access_token,
                'fields': 'id,effective_status,status,campaign{id}',
                'limit': 100
            }
            
            account_adsets_count = 0
            while url:
                try:
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'data' in data:
                        for adset in data['data']:
                            adset_id = adset.get('id')
                            if adset_id:
                                campaign = adset.get('campaign', {})
                                campaign_id = campaign.get('id') if isinstance(campaign, dict) else None
                                
                                all_adsets_map[adset_id] = {
                                    'effective_status': adset.get('effective_status', 'UNKNOWN'),
                                    'status': adset.get('status', 'UNKNOWN'),
                                    'campaign_id': campaign_id
                                }
                                account_adsets_count += 1
                    
                    # Check for next page
                    if 'paging' in data and 'next' in data['paging']:
                        url = data['paging']['next']
                        params = {}  # URL đã có params
                    else:
                        url = None
                except requests.exceptions.HTTPError as http_err:
                    # 🔹 NHIỆM VỤ PHỤ: Xử lý lỗi 400 một cách rõ ràng, không crash
                    if http_err.response and http_err.response.status_code == 400:
                        error_detail = http_err.response.text
                        logger.warning(
                            f"⚠️ Lỗi 400 khi fetch adsets từ account {account_id_formatted}: "
                            f"{error_detail[:200]}. Có thể do permission, token hết hạn, hoặc account không hợp lệ. "
                            f"Bỏ qua account này (summary & rows vẫn có đủ data từ insights)."
                        )
                        # Không raise exception, chỉ bỏ qua account này
                        url = None  # Dừng pagination
                    else:
                        # Các lỗi HTTP khác (500, 503, ...) vẫn log và bỏ qua
                        logger.warning(f"⚠️ Lỗi HTTP {http_err.response.status_code if http_err.response else 'unknown'} khi fetch adsets từ account {account_id_formatted}: {http_err}")
                        url = None
                except Exception as e:
                    logger.warning(f"⚠️ Lỗi khác khi fetch adsets từ account {account_id_formatted}: {e}")
                    url = None
            
            if account_adsets_count > 0:
                logger.info(f"   ✅ Đã fetch {account_adsets_count} adsets từ account {account_id_formatted}")
        except Exception as e:
            # 🔹 FIX: Log rõ ràng hơn, không crash, chỉ bỏ qua account này
            logger.warning(f"⚠️ Lỗi fetch adsets từ account {account_id}: {e}. Bỏ qua account này (summary & rows vẫn có đủ data từ insights).")
            continue
    
    logger.info(f"📊 Tổng cộng fetch được {len(all_adsets_map)} adsets từ tất cả accounts")
    return all_adsets_map


def fetch_struct_adsets_from_accounts(
    ad_account_ids: List[str],
    access_token: str,
    view_mode: str = "ecommerce",
    account_type_map: Optional[Dict[str, str]] = None,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetch TẤT CẢ adsets structure từ accounts (với đầy đủ fields: id, name, campaign, daily_budget, effective_status)
    Dùng để build adset_map đầy đủ, kể cả adsets không có insights data
    
    Returns: List[Dict] - List of adset objects với đầy đủ thông tin
    """
    if not ad_account_ids:
        return []
    
    all_struct_adsets = []
    
    for account_id in ad_account_ids:
        try:
            # Đảm bảo account_id có prefix "act_"
            if not account_id.startswith("act_"):
                account_id_formatted = f"act_{account_id}"
            else:
                account_id_formatted = account_id
            
            # Filter theo account_type nếu có
            if account_type_map:
                clean_id = account_id.replace('act_', '')
                account_type = account_type_map.get(clean_id)
                if view_mode == "ecommerce" and account_type != "E-COMMERCE":
                    continue
                elif view_mode == "lead" and account_type != "LEAD_GENERATION":
                    continue
            
            # Fetch tất cả adsets từ account với đầy đủ fields
            url = f"{FB_GRAPH_API_BASE}/{account_id_formatted}/adsets"
            params = {
                'access_token': access_token,
                'fields': 'id,name,campaign{id,name},daily_budget,lifetime_budget,effective_status,configured_status',
                'limit': 100
            }
            
            account_adsets_count = 0
            while url:
                try:
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                except requests.exceptions.HTTPError as http_err:
                    if response.status_code == 400:
                        logger.warning(f"⚠️ 400 Bad Request for {account_id_formatted}/adsets (struct) - skipping (likely permission issue)")
                        break
                    else:
                        raise
                except Exception as e:
                    logger.error(f"🚨 Error fetching struct adsets from {account_id_formatted}: {e}")
                    break
                
                if 'data' in data:
                    for adset in data['data']:
                        adset_id = adset.get('id')
                        if adset_id:
                            campaign = adset.get('campaign', {})
                            campaign_id = campaign.get('id') if isinstance(campaign, dict) else None
                            campaign_name = campaign.get('name') if isinstance(campaign, dict) else None
                            
                            # Lấy budget: daily_budget hoặc lifetime_budget
                            daily_budget = float(adset.get('daily_budget', 0) or 0)
                            lifetime_budget = float(adset.get('lifetime_budget', 0) or 0)
                            adset_budget = daily_budget if daily_budget > 0 else lifetime_budget
                            
                            struct_adset = {
                                'id': adset_id,
                                'name': adset.get('name', ''),
                                'campaign_id': campaign_id,
                                'campaign_name': campaign_name,
                                'daily_budget': daily_budget,
                                'lifetime_budget': lifetime_budget,
                                'adset_budget': adset_budget,
                                'effective_status': adset.get('effective_status', 'UNKNOWN'),
                                'configured_status': adset.get('configured_status', 'UNKNOWN'),
                                'account_id': account_id_formatted
                            }
                            all_struct_adsets.append(struct_adset)
                            account_adsets_count += 1
                
                # Check for next page
                if 'paging' in data and 'next' in data['paging']:
                    url = data['paging']['next']
                    params = {}  # URL đã có params
                else:
                    url = None
            
            logger.info(f"   ✅ Đã fetch {account_adsets_count} struct adsets từ account {account_id_formatted}")
        except Exception as e:
            logger.error(f"🚨 Lỗi fetch struct adsets từ account {account_id}: {e}")
            continue
    
    logger.info(f"📊 Tổng cộng fetch được {len(all_struct_adsets)} struct adsets từ tất cả accounts")
    return all_struct_adsets


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


def update_campaign_budget(
    campaign_id: str,
    access_token: str,
    new_budget: float
) -> Dict[str, Any]:
    """
    Update campaign budget (daily_budget)
    """
    try:
        # Lấy budget hiện tại
        url = f"{FB_GRAPH_API_BASE}/{campaign_id}"
        params = {
            'fields': 'daily_budget,lifetime_budget',
            'access_token': access_token
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        campaign_data = response.json()
        
        if 'error' in campaign_data:
            return {
                "success": False,
                "campaign_id": campaign_id,
                "error": campaign_data['error'].get('message', 'Unknown error')
            }
        
        old_budget = float(campaign_data.get('daily_budget') or campaign_data.get('lifetime_budget') or 0)
        budget_type = 'daily_budget' if campaign_data.get('daily_budget') else 'lifetime_budget'
        
        # Normalize budget thành integer
        new_budget_normalized = _normalize_budget(new_budget)
        
        # Update budget
        update_url = f"{FB_GRAPH_API_BASE}/{campaign_id}"
        update_params = {
            'access_token': access_token
        }
        update_data = {
            budget_type: new_budget_normalized
        }
        
        update_response = requests.post(update_url, params=update_params, data=update_data, timeout=30)
        update_response.raise_for_status()
        
        update_result = update_response.json()
        if 'error' in update_result:
            return {
                "success": False,
                "campaign_id": campaign_id,
                "old_budget": old_budget,
                "new_budget": new_budget,
                "error": update_result['error'].get('message', 'Unknown error')
            }
        
        logger.info(f"✅ Đã cập nhật budget campaign {campaign_id}: {old_budget} → {new_budget}")
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "old_budget": old_budget,
            "new_budget": new_budget,
            "budget_type": budget_type
        }
        
    except Exception as e:
        logger.error(f"🚨 Lỗi cập nhật budget campaign {campaign_id}: {e}")
        return {
            "success": False,
            "campaign_id": campaign_id,
            "error": str(e)
        }


def update_adsets_budget_batch(
    updates: List[Dict[str, Any]],
    access_token: str
) -> Dict[str, Any]:
    """
    Cập nhật ngân sách NHIỀU adsets bằng Graph API Batch (tối đa 50/request)
    
    Args:
        updates: List of dicts với keys: id, new_budget
        access_token: Facebook access token
    
    Returns:
        Dict với keys: success_count, error_count, results, errors
    """
    if not updates:
        return {"success_count": 0, "error_count": 0, "results": [], "errors": []}
    
    # Chunk thành nhóm 50
    batches = chunk_list(updates, 50)
    all_results = []
    all_errors = []
    
    for batch_idx, batch_updates in enumerate(batches):
        try:
            # Bước 1: Lấy budget hiện tại của tất cả adsets trong batch
            get_batch_payload = []
            for item in batch_updates:
                get_batch_payload.append({
                    "method": "GET",
                    "relative_url": f"{FB_API_VERSION}/{item['id']}?fields=daily_budget,lifetime_budget"
                })
            
            # Gửi batch GET request
            import json
            form_data = {
                'access_token': access_token,
                'batch': json.dumps(get_batch_payload)
            }
            
            url = f"{FB_GRAPH_API_BASE}/"
            get_response = requests.post(url, data=form_data, timeout=60)
            get_response.raise_for_status()
            get_results = get_response.json()
            
            # Parse kết quả GET
            adset_budgets = {}
            for i, item in enumerate(get_results):
                if isinstance(item, dict) and item.get('code') == 200:
                    try:
                        body_data = json.loads(item['body'])
                        adset_id = batch_updates[i]['id']
                        current_budget = float(body_data.get('daily_budget') or body_data.get('lifetime_budget') or 0)
                        budget_type = 'daily_budget' if body_data.get('daily_budget') else 'lifetime_budget'
                        adset_budgets[adset_id] = {
                            'current': current_budget,
                            'type': budget_type
                        }
                    except Exception as e:
                        logger.warning(f"Failed to parse GET response for batch item {i}: {e}")
            
            # Bước 2: Cập nhật budget với batch POST
            update_batch_payload = []
            update_mapping = []  # Track mapping giữa batch index và update item
            
            for item in batch_updates:
                adset_id = item['id']
                new_budget = _normalize_budget(item['new_budget'])
                
                if adset_id in adset_budgets:
                    budget_info = adset_budgets[adset_id]
                    budget_type = budget_info['type']
                    
                    update_batch_payload.append({
                        "method": "POST",
                        "relative_url": f"{FB_API_VERSION}/{adset_id}",
                        "body": f"{budget_type}={new_budget}"
                    })
                    update_mapping.append({
                        'id': adset_id,
                        'old_budget': budget_info['current'],
                        'new_budget': new_budget,
                        'budget_type': budget_type
                    })
                else:
                    # Không lấy được budget hiện tại
                    all_errors.append({
                        'id': adset_id,
                        'error': 'Failed to get current budget'
                    })
            
            if update_batch_payload:
                # Gửi batch UPDATE request
                update_form_data = {
                    'access_token': access_token,
                    'batch': json.dumps(update_batch_payload)
                }
                
                update_response = requests.post(url, data=update_form_data, timeout=60)
                update_response.raise_for_status()
                update_results = update_response.json()
                
                # Parse kết quả UPDATE
                for i, result_item in enumerate(update_results):
                    if i < len(update_mapping):
                        mapping = update_mapping[i]
                        
                        if isinstance(result_item, dict) and result_item.get('code') == 200:
                            all_results.append({
                                'id': mapping['id'],
                                'old_budget': mapping['old_budget'],
                                'new_budget': mapping['new_budget'],
                                'budget_type': mapping['budget_type'],
                                'success': True
                            })
                            logger.info(f"✅ Đã cập nhật budget adset {mapping['id']}: {mapping['old_budget']} → {mapping['new_budget']}")
                        else:
                            # Parse error
                            error_msg = "Unknown error"
                            try:
                                if 'body' in result_item:
                                    body_data = json.loads(result_item['body'])
                                    if 'error' in body_data:
                                        error_msg = body_data['error'].get('message', error_msg)
                            except Exception:
                                pass
                            
                            all_errors.append({
                                'id': mapping['id'],
                                'error': error_msg
                            })
                            logger.warning(f"❌ Lỗi cập nhật budget adset {mapping['id']}: {error_msg}")
        
        except Exception as e:
            logger.error(f"Batch budget update error for batch {batch_idx}: {e}")
            for item in batch_updates:
                all_errors.append({
                    'id': item['id'],
                    'error': f"Batch error: {str(e)}"
                })
    
    return {
        "success_count": len(all_results),
        "error_count": len(all_errors),
        "results": all_results,
        "errors": all_errors
    }


def update_adset_budget(
    adset_id: str,
    access_token: str,
    new_budget: Optional[float] = None,  # New budget value (absolute) - ưu tiên
    action_type: str = "increase",  # "increase", "decrease", "set" - chỉ dùng nếu new_budget=None
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
        
        # ✅ DEBUG LOG: Kiểm tra budget scope
        logger.debug(
            f"DEBUG_BUDGET_SCOPE | adset_id={adset_id}, "
            f"daily_budget={adset_data.get('daily_budget')}, "
            f"lifetime_budget={adset_data.get('lifetime_budget')}, "
            f"current_budget={current_budget}, budget_type={budget_type}"
        )
        
        # Tính toán budget mới
        # Nếu có new_budget (absolute value), dùng trực tiếp
        if new_budget is not None:
            new_budget = float(new_budget)
        elif percent is not None:
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
        
        # Normalize budget thành integer (Facebook yêu cầu)
        new_budget_normalized = _normalize_budget(new_budget)
        
        # Update budget
        update_url = f"{FB_GRAPH_API_BASE}/{adset_id}"
        update_params = {
            'access_token': access_token
        }
        update_data = {
            budget_type: new_budget_normalized
        }
        
        update_response = requests.post(update_url, params=update_params, data=update_data, timeout=30)
        
        # Kiểm tra lỗi 400 trước khi raise_for_status
        if update_response.status_code == 400:
            error_data = update_response.json()
            error_msg = error_data.get('error', {}).get('message', 'Bad Request')
            return {
                "success": False,
                "adset_id": adset_id,
                "old_budget": current_budget,
                "error": f"400: {error_msg}"
            }
        
        update_response.raise_for_status()
        
        result = update_response.json()
        
        if 'error' in result:
            return {
                "success": False,
                "adset_id": adset_id,
                "old_budget": current_budget,
                "error": result['error'].get('message', 'Unknown error')
            }
        
        logger.info(f"✅ Đã cập nhật budget adset {adset_id}: {current_budget} → {new_budget_normalized}")
        
        return {
            "success": True,
            "adset_id": adset_id,
            "old_budget": current_budget,
            "new_budget": new_budget_normalized,
            "budget_type": budget_type
        }
        
    except Exception as e:
        logger.error(f"🚨 Lỗi cập nhật budget adset {adset_id}: {e}")
        return {
            "success": False,
            "adset_id": adset_id,
            "error": str(e)
        }


def fetch_campaign_budgets_batch(campaign_ids: List[str], access_token: str) -> Dict[str, Dict[str, Any]]:
    """
    Lấy campaign budgets và CBO status từ campaign objects (batch request)
    Returns: {campaign_id: {'daily_budget': float, 'lifetime_budget': float, 'budget_level': 'CAMPAIGN'|'ADSET'}}
    """
    if not campaign_ids:
        return {}
    
    campaigns_info = {}
    campaign_batches = chunk_list(campaign_ids, 50)
    
    for batch in campaign_batches:
        try:
            batch_payload = []
            for campaign_id in batch:
                batch_payload.append({
                    "method": "GET",
                    "relative_url": f"{FB_API_VERSION}/{campaign_id}?fields=daily_budget,lifetime_budget"
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
                                
                                daily_budget = float(body_json.get('daily_budget', 0) or 0)
                                lifetime_budget = float(body_json.get('lifetime_budget', 0) or 0)
                                
                                # Nếu campaign có daily_budget hoặc lifetime_budget → budget_level = CAMPAIGN
                                budget_level = 'CAMPAIGN' if (daily_budget > 0 or lifetime_budget > 0) else 'ADSET'
                                
                                campaigns_info[campaign_id] = {
                                    'daily_budget': daily_budget,
                                    'lifetime_budget': lifetime_budget,
                                    'budget_level': budget_level
                                }
                            except Exception as e:
                                logger.warning(f"Lỗi parse campaign budget cho {campaign_id}: {e}")
        except Exception as e:
            logger.warning(f"Lỗi khi lấy campaign budgets batch: {e}")
            continue
    
    return campaigns_info


def pull_facebook_data(
    access_token: str,
    ad_account_ids: List[str],
    date_preset: Optional[str] = "today",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    account_type_map: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Kéo dữ liệu Insights level=ad từ Facebook API
    Thay thế cho hàm pullFacebookData() từ Facebook API.gs
    
    Args:
        account_type_map: Dict mapping account_id → account_type (E-COMMERCE/LEAD_GENERATION)
                         Dùng để detect campaign type khi không có objective rõ ràng
    
    Returns:
        List of ad metrics dictionaries
    """
    # 🔹 TỐI ƯU: Chỉ fetch những fields cần thiết (theo yêu cầu)
    # Fields hợp lệ cho insights - chỉ lấy những fields thực sự dùng
    fields = [
        'account_name', 'account_id', 'campaign_name', 'campaign_id',
        'adset_id', 'adset_name',
        'ad_id', 'ad_name',
        'spend', 'impressions', 'reach', 'frequency', 'clicks', 'ctr', 'cpc',
        # cost_per_initiate_checkout và cost_per_purchase có thể tính từ cost_per_action_type, nhưng giữ lại để đảm bảo tương thích
        'cost_per_action_type', 'actions', 'action_values'
    ]
    fields_string = ','.join(fields)
    
    all_rows = []
    
    # Dùng global cache cho objectives và budgets (cache lâu hơn)
    # Cache key dựa trên access_token
    cache_key_obj = f"objectives_{access_token[:20]}"
    cache_key_bud = f"budgets_{access_token[:20]}"
    
    # Check global cache cho objectives
    now = datetime.now()
    cached_obj_timestamp = _cache_timestamps.get(cache_key_obj)
    if cached_obj_timestamp:
        age_seconds = (now - cached_obj_timestamp).total_seconds()
        if age_seconds < CACHE_TTL_OBJECTIVES_BUDGETS:
            campaign_objectives_cache = _objectives_cache.get(access_token, {})
        else:
            # Cache expired
            _objectives_cache.pop(access_token, None)
            _cache_timestamps.pop(cache_key_obj, None)
            campaign_objectives_cache = {}
    else:
        campaign_objectives_cache = {}
    
    # Check global cache cho budgets
    cached_bud_timestamp = _cache_timestamps.get(cache_key_bud)
    if cached_bud_timestamp:
        age_seconds = (now - cached_bud_timestamp).total_seconds()
        if age_seconds < CACHE_TTL_OBJECTIVES_BUDGETS:
            adset_budgets_cache = _budgets_cache.get(access_token, {})
        else:
            # Cache expired
            _budgets_cache.pop(access_token, None)
            _cache_timestamps.pop(cache_key_bud, None)
            adset_budgets_cache = {}
    else:
        adset_budgets_cache = {}
    
    # Cache để lưu campaign budgets và budget_level (local trong function)
    campaign_budgets_cache = {}
    
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
            # Đảm bảo account_id có prefix "act_"
            if not account_id.startswith("act_"):
                account_id_formatted = f"act_{account_id}"
            else:
                account_id_formatted = account_id
            
            logger.info(f"Đang kéo dữ liệu cho tài khoản: {account_id_formatted} (Phạm vi: {date_preset})")
            
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
                        f"{FB_GRAPH_API_BASE}/{account_id_formatted}/insights"
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
                        # Kiểm tra xem có phải là "today" không (same date)
                        from datetime import timezone as tz
                        tz_hcm = tz(timedelta(hours=7))
                        now = datetime.now(tz_hcm)
                        today_str = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d')
                        
                        # Nếu là today, dùng time_range với today
                        if date_from == today_str and date_to == today_str:
                            # Dùng today (theo yêu cầu user)
                            since = today_str
                            until = (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime('%Y-%m-%d')  # until = tomorrow (exclusive)
                            time_range_json = json.dumps({"since": since, "until": until})
                            url += f'&time_range={quote(time_range_json)}'
                            logger.info(f"   ℹ️ Dùng today ({since})")
                        else:
                            # Dùng custom time_range
                            # Facebook API until là EXCLUSIVE, nên phải +1 ngày
                            try:
                                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                                # Kiểm tra không query ngày trong tương lai
                                if date_to_obj.date() > now.date():
                                    logger.warning(f"⚠️ Không thể query ngày trong tương lai: {date_to}, dùng today thay thế")
                                    url += '&date_preset=today'
                                else:
                                    date_to_obj = date_to_obj + timedelta(days=1)  # +1 vì until là exclusive
                                    date_to_str = date_to_obj.strftime('%Y-%m-%d')
                                    
                                    time_range_json = json.dumps({"since": date_from, "until": date_to_str})
                                    url += f'&time_range={quote(time_range_json)}'
                            except ValueError as e:
                                logger.warning(f"⚠️ Lỗi parse date: {e}, dùng today thay thế")
                                url += '&date_preset=today'
                    elif date_preset == 'yesterday':
                        # Convert yesterday sang time_range để chính xác hơn (giống Google Script)
                        from datetime import timezone as tz
                        # Dùng timezone Asia/Ho_Chi_Minh (UTC+7)
                        tz_hcm = tz(timedelta(hours=7))
                        now = datetime.now(tz_hcm)
                        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                        yesterday = today - timedelta(days=1)
                        
                        # QUAN TRỌNG: Facebook API until là EXCLUSIVE, nên phải +1 ngày
                        since = yesterday.strftime('%Y-%m-%d')
                        until = today.strftime('%Y-%m-%d')  # until = today (exclusive, nên lấy hết yesterday)
                        time_range_json = json.dumps({"since": since, "until": until})
                        url += f'&time_range={quote(time_range_json)}'
                    elif date_preset == 'today':
                        # Dùng today (theo yêu cầu user)
                        from datetime import timezone as tz
                        tz_hcm = tz(timedelta(hours=7))
                        now = datetime.now(tz_hcm)
                        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                        since = today.strftime('%Y-%m-%d')
                        until = (today + timedelta(days=1)).strftime('%Y-%m-%d')  # until = tomorrow (exclusive)
                        time_range_json = json.dumps({"since": since, "until": until})
                        url += f'&time_range={quote(time_range_json)}'
                        logger.info(f"   ℹ️ Dùng today ({since})")
                    else:
                        if date_preset:
                            url += f'&date_preset={date_preset}'
                        else:
                            # Default: today (theo yêu cầu user)
                            from datetime import timezone as tz
                            tz_hcm = tz(timedelta(hours=7))
                            now = datetime.now(tz_hcm)
                            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                            since = today.strftime('%Y-%m-%d')
                            until = (today + timedelta(days=1)).strftime('%Y-%m-%d')  # until = tomorrow (exclusive)
                            time_range_json = json.dumps({"since": since, "until": until})
                            url += f'&time_range={quote(time_range_json)}'
                            logger.info(f"   ℹ️ Default: dùng today ({since})")
                    
                    # Thêm action_report_time và attribution settings (giống Google Script)
                    url += (
                        '&action_report_time=conversion'
                        '&use_unified_attribution_setting=true'
                        '&action_attribution_windows=1d_click,7d_click,1d_view,7d_view'
                    )
                
                # Fetch data
                response = requests.get(url, timeout=60)
                
                # Parse error message trước khi raise
                try:
                    json_data = response.json()
                    if 'error' in json_data:
                        error_code = json_data['error'].get('code', 0)
                        error_msg = json_data['error'].get('message', 'Unknown error')
                        error_type = json_data['error'].get('type', '')
                        error_subcode = json_data['error'].get('error_subcode', '')
                        
                        # Log response body để debug
                        response_body = response.text if hasattr(response, 'text') else str(response.content) if hasattr(response, 'content') else ""
                        logger.error(f"🚨 Facebook API Error: Code={error_code}, Type={error_type}, Subcode={error_subcode}, Message={error_msg}")
                        logger.error(f"   URL: {url[:200]}...")
                        logger.error(f"   Response body: {response_body[:500]}...")
                        
                        # 🔹 XỬ LÝ RATE LIMIT: Raise custom exception
                        if error_code == 4 or error_code == 17 or 'rate limit' in error_msg.lower() or 'Application request limit reached' in error_msg:
                            logger.error(f"⚠️ RATE LIMIT REACHED - Code {error_code}")
                            raise FacebookRateLimitError(f"Facebook API rate limit reached: {error_msg}")
                        
                        if error_code in [190, 100]:
                            raise Exception(f"Lỗi Token hoặc Quyền (Code {error_code}). Chi tiết: {error_msg}")
                        elif error_code == 200:
                            raise Exception(f"Mất quyền truy cập TK (Code 200). Chi tiết: {error_msg}")
                        raise Exception(f"LỖI API (Code {error_code}): {error_msg}")
                except ValueError:
                    # Nếu không parse được JSON, dùng raise_for_status
                    response.raise_for_status()
                    json_data = response.json()
                except FacebookRateLimitError:
                    # Re-raise rate limit error để caller xử lý
                    raise                
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
                
                # Fetch campaign objectives và budgets nếu có campaigns mới
                if campaign_ids_to_fetch:
                    logger.info(f"   🔍 Đang lấy objectives cho {len(campaign_ids_to_fetch)} campaigns...")
                    new_objectives = fetch_campaign_objectives_batch(campaign_ids_to_fetch, access_token)
                    campaign_objectives_cache.update(new_objectives)
                    # Update global cache
                    if access_token not in _objectives_cache:
                        _objectives_cache[access_token] = {}
                    _objectives_cache[access_token].update(new_objectives)
                    _cache_timestamps[cache_key_obj] = datetime.now()
                    
                    # Fetch campaign budgets để xác định budget_level
                    logger.info(f"   💰 Đang lấy campaign budgets cho {len(campaign_ids_to_fetch)} campaigns...")
                    new_campaign_budgets = fetch_campaign_budgets_batch(campaign_ids_to_fetch, access_token)
                    campaign_budgets_cache.update(new_campaign_budgets)
                
                # Collect unique adset IDs để fetch budgets
                adset_ids_to_fetch = []
                for item in data:
                    adset_id = item.get('adset_id', '')
                    if adset_id and adset_id not in adset_budgets_cache:
                        adset_ids_to_fetch.append(adset_id)
                
                # Fetch adset budgets nếu có adsets mới (dùng global cache)
                if adset_ids_to_fetch:
                    logger.info(f"   💰 Đang lấy budgets cho {len(adset_ids_to_fetch)} adsets...")
                    new_budgets = fetch_adset_budgets(adset_ids_to_fetch, access_token, use_cache=True)
                    adset_budgets_cache.update(new_budgets)
                
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
                    
                    # 🔹 TỐI ƯU: Bỏ qua adsets có spend <= 0 HOẶC impressions <= 0
                    # Theo yêu cầu: chỉ load adsets có spend > 0 và impressions > 0
                    if spend <= 0 or impressions <= 0:
                        continue  # Skip adset này
                    
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
                    
                    # 🔹 CHUẨN HÓA METRICS MAPPING theo Facebook Ads Manager (theo spec)
                    # Danh sách các action type variants - ĐẦY ĐỦ để bắt được tất cả cách Facebook trả về
                    # Theo yêu cầu:
                    # - checkouts_initiated -> "omni_initiated_checkout" (ưu tiên cao nhất)
                    # - purchases -> "omni_purchase" (ưu tiên cao nhất)
                    # - messaging started -> "onsite_conversion.messaging_conversation_started_7d"
                    # - comment -> "comment" hoặc "post_comment"
                    
                    bases_ic = ['omni_initiated_checkout', 'initiate_checkout', 
                               'offsite_conversion.fb_pixel_initiate_checkout', 
                               'onsite_conversion.initiated_checkout']
                    bases_pur = ['omni_purchase', 'purchase', 
                                'offsite_conversion.fb_pixel_purchase', 
                                'onsite_conversion.purchase']
                    bases_cmt = ['comment', 'post_comment', 'onsite_conversion.post_comment']
                    bases_msg = ['onsite_conversion.messaging_conversation_started_7d',
                                'onsite_conversion.messaging_conversation_started', 
                                'messaging_conversation_started',
                                'messaging_conversation_started_7d_click',
                                'messaging_conversation_started_1d_click']
                    # onsite_conversion.post_save (Bắt đầu TT cho Lead Gen)
                    bases_post_save = ['onsite_conversion.post_save', 'post_save']
                    
                    # Lấy giá trị từ các variants
                    initiate_checkout = pick_first_variant(act_map, bases_ic)
                    purchases = pick_first_variant(act_map, bases_pur)
                    post_comments = pick_first_variant(act_map, bases_cmt)
                    msg_started = pick_first_variant(act_map, bases_msg)
                    post_save = pick_first_variant(act_map, bases_post_save)  # Bắt đầu TT
                    
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
                    post_saves = int(post_save)  # Bắt đầu TT (onsite_conversion.post_save)
                    
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
                    # Purchase value (E-Commerce): ưu tiên offsite_conversion.fb_pixel_purchase theo spec
                    bases_pur_value = ['offsite_conversion.fb_pixel_purchase', 'omni_purchase', 
                                      'purchase', 'onsite_conversion.purchase']
                    purchase_value = pick_first_variant(val_map, bases_pur_value)
                    
                    # Parse cost_per_action_type để lấy cost metrics đúng theo spec
                    # cost_per_action_type là array giống actions, có action_type và value
                    # Theo yêu cầu:
                    # - cost_per_checkout -> cost_per_action_type; action_type="omni_initiated_checkout"
                    # - cost_per_purchase -> cost_per_action_type; action_type="omni_purchase"
                    cost_per_action_type_list = item.get('cost_per_action_type', [])
                    cost_per_action_map = {}
                    if cost_per_action_type_list and isinstance(cost_per_action_type_list, list):
                        for cost_item in cost_per_action_type_list:
                            if not cost_item:
                                continue
                            action_type = str(cost_item.get('action_type', ''))
                            value = float(cost_item.get('value', 0) or 0)
                            if action_type:
                                if action_type in cost_per_action_map:
                                    cost_per_action_map[action_type] += value
                                else:
                                    cost_per_action_map[action_type] = value
                    
                    # Cost per checkout initiated: ưu tiên omni_initiated_checkout theo spec
                    cost_per_checkout = pick_first_variant(cost_per_action_map, bases_ic)
                    if cost_per_checkout == 0 and checkouts > 0:
                        # Fallback: tính từ spend / checkouts
                        cost_per_checkout = spend / checkouts
                    
                    # Cost per purchase: ưu tiên omni_purchase theo spec
                    cost_per_purchase = pick_first_variant(cost_per_action_map, bases_pur)
                    if cost_per_purchase == 0 and purchases > 0:
                        # Fallback: tính từ spend / purchases
                        cost_per_purchase = spend / purchases
                    
                    # Tính % ADS (KHÔNG nhân 100, giống Google Script)
                    percent_ads = (spend / purchase_value) if purchase_value > 0 else 0
                    
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
                        'checkouts_initiated': checkouts,
                        'onsite_conversion_post_save': post_saves  # Bắt đầu TT
                    }
                    
                    # Lấy account_type từ map để dùng làm fallback
                    account_id_clean = item.get('account_id', '').replace('act_', '')
                    fallback_account_type = None
                    if account_type_map:
                        fallback_account_type = account_type_map.get(account_id_clean)
                    
                    # Dùng hybrid detection (ưu tiên objective → metrics → account_type)
                    campaign_type = detect_campaign_type_hybrid(
                        objective=campaign_objective,
                        metrics=metrics_dict,
                        fallback_account_type=fallback_account_type
                    )
                    
                    # Log campaign type detection để debug
                    campaign_name = item.get('campaign_name', '')
                    logger.debug(f"Campaign '{campaign_name}' - Objective: '{campaign_objective}' → Type: {campaign_type}")
                    
                    # 🔹 FIX CBO BUDGET: Lấy budget và xác định budget_level theo spec
                    campaign_id = item.get('campaign_id', '')
                    adset_id = item.get('adset_id', '')
                    
                    # Xác định budget_level từ campaign info
                    campaign_info = campaign_budgets_cache.get(campaign_id, {})
                    campaign_has_budget = campaign_info.get('budget_level', 'ADSET') == 'CAMPAIGN'
                    campaign_daily_budget = campaign_info.get('daily_budget', 0.0) or 0.0
                    campaign_lifetime_budget = campaign_info.get('lifetime_budget', 0.0) or 0.0
                    campaign_budget_total = campaign_daily_budget if campaign_daily_budget > 0 else campaign_lifetime_budget
                    
                    # Lấy adset budget (daily và lifetime riêng biệt)
                    adset_budget_info = adset_budgets_cache.get(adset_id, {})
                    if isinstance(adset_budget_info, dict):
                        adset_daily_budget = adset_budget_info.get('daily_budget', 0.0) or 0.0
                        adset_lifetime_budget = adset_budget_info.get('lifetime_budget', 0.0) or 0.0
                    else:
                        # Backward compat: nếu cache cũ chỉ lưu số
                        adset_daily_budget = float(adset_budget_info or 0.0)
                        adset_lifetime_budget = 0.0
                    
                    # Theo spec: using_campaign_budget = adset_daily_budget in (None, 0) and campaign có budget
                    using_campaign_budget = (adset_daily_budget in (None, 0)) and campaign_budget_total > 0
                    
                    # Xác định budget_type: CAMPAIGN hoặc ADSET
                    if using_campaign_budget or campaign_has_budget:
                        budget_type = 'CAMPAIGN'
                        budget = campaign_budget_total
                    else:
                        budget_type = 'ADSET'
                        budget = adset_daily_budget
                    
                    # Lưu đầy đủ budget info để frontend hiển thị đúng
                    campaign_budget_value = campaign_budget_total
                    adset_budget_value = adset_daily_budget
                    
                    # FIX: Tính các derived metrics đúng theo spec - Giá DATA, TLC, Frequency
                    # Giá DATA = spend / (post_comments + messaging_conversations_started)
                    derived_gia_data = (spend / results) if results > 0 else 0
                    # TLC (tỷ lệ chốt) = purchases / messaging_conversations_started * 100
                    derived_tlc = (purchases / messages * 100) if messages > 0 else 0
                    # Frequency = impressions / reach
                    reach_val = int(item.get('reach', 0) or 0)
                    derived_frequency = (impressions / reach_val) if reach_val > 0 else 0
                    # % ADS = spend / purchase_value * 100 (KHÔNG nhân 100 ở frontend nữa)
                    derived_ads_percent = (spend / purchase_value * 100) if purchase_value > 0 else 0
                    
                    # Tạo row data với đầy đủ fields theo spec
                    row = {
                        'account_name': item.get('account_name', ''),
                        'account_id': item.get('account_id', ''),
                        'campaign_name': campaign_name,
                        'campaign_id': campaign_id,
                        'adset_id': adset_id,
                        'adset_name': item.get('adset_name', ''),
                        'ad_id': item.get('ad_id', ''),
                        'ad_name': item.get('ad_name', ''),
                        'prefix': prefix,
                        'campaign_type': campaign_type,
                        'campaign_objective': campaign_objective,
                        'adset_status': 'ACTIVE',  # Mặc định, sẽ được cập nhật sau
                        'effective_status': '',  # Sẽ được cập nhật sau
                        
                        # 🔹 Budget fields theo spec
                        'budget': budget,
                        'daily_budget': budget,  # Alias
                        'budget_type': budget_type,  # "CAMPAIGN" | "ADSET"
                        'budget_level': budget_type,  # Alias (backward compatible)
                        'adset_daily_budget': adset_daily_budget,
                        'adset_lifetime_budget': adset_lifetime_budget,
                        'campaign_daily_budget': campaign_daily_budget,
                        'campaign_lifetime_budget': campaign_lifetime_budget,
                        'using_campaign_budget': using_campaign_budget,
                        'campaign_budget': campaign_budget_value,  # Alias (backward compatible)
                        'adset_budget': adset_budget_value,  # Alias (backward compatible)
                        
                        'spend': spend,
                        'amount_spent': spend,
                        'results': results,
                        'ket_qua': results,
                        'gia_data': derived_gia_data,  # FIX: Dùng derived_gia_data
                        'data_cost': derived_gia_data,  # FIX: Alias
                        'percent_ads': derived_ads_percent,  # FIX: Dùng derived (đã nhân 100)
                        'ads_percent': derived_ads_percent,  # FIX: Alias
                        'tlc': derived_tlc,  # FIX: TLC (đã nhân 100)
                        'cost_per_checkout_initiated': cost_per_checkout,
                        'checkouts_initiated': checkouts,  # Đã parse từ actions theo spec (omni_initiated_checkout)
                        'initiated_checkout': checkouts,  # FIX: Alias
                        'cost_per_purchase': cost_per_purchase,
                        'purchases': purchases,  # Đã parse từ actions theo spec (omni_purchase)
                        'sdt': checkouts,  # SĐT = checkouts (alias)
                        'gia_tri_chuyen_doi_tu_luot_mua': purchase_value,  # Purchase value theo spec
                        'purchase_value': purchase_value,  # FIX: Alias cho frontend
                        'cpm': cpm,
                        'impressions': impressions,
                        'reach': reach_val,
                        'frequency': derived_frequency,  # FIX: Dùng derived_frequency
                        'clicks': clicks,
                        'clicks_all': clicks,
                        'ctr': ctr,
                        'ctr_all': ctr,
                        'cpc': cpc,
                        'cpc_all': cpc,
                        'cost_per_comment': (spend / comments) if comments > 0 else 0,
                        'cost_per_messaging_conversation': (spend / messages) if messages > 0 else 0,
                        'post_comments': comments,  # Đã parse từ actions theo spec
                        'messaging_conversations_started': messages,  # Đã parse từ actions theo spec
                        'onsite_conversion_post_save': post_saves,  # Bắt đầu TT (Lead Gen) theo spec
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
            
            logger.info(f"   ✅ Hoàn tất tài khoản {account_id_formatted}: Tổng {page_count} page(s)")
                
        except Exception as e:
            logger.error(f"🚨 Lỗi khi lấy dữ liệu từ account {account_id_formatted}: {e}")
            continue
    
    logger.info(f"✅ Đã lấy {len(all_rows)} ads từ Facebook API")
    return all_rows


async def pull_facebook_data_async(
    access_token: str,
    ad_account_ids: List[str],
    date_preset: Optional[str] = "today",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    account_type_map: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Async wrapper cho pull_facebook_data - chạy song song các accounts
    Sử dụng asyncio.to_thread để chạy sync function trong thread pool
    
    Args:
        account_type_map: Dict mapping account_id → account_type (E-COMMERCE/LEAD_GENERATION)
    """
    async def fetch_single_account(account_id: str) -> List[Dict[str, Any]]:
        """Fetch data cho 1 account trong thread pool"""
        loop = asyncio.get_event_loop()
        # Chạy sync function trong thread pool
        result = await loop.run_in_executor(
            None,
            pull_facebook_data,
            access_token,
            [account_id],  # Chỉ fetch 1 account
            date_preset,
            date_from,
            date_to,
            account_type_map  # Truyền account_type_map
        )
        return result
    
    # Chạy song song tất cả accounts
    logger.info(f"🚀 Bắt đầu fetch song song {len(ad_account_ids)} accounts...")
    tasks = [fetch_single_account(acc_id) for acc_id in ad_account_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results
    all_rows = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"🚨 Exception khi fetch account {ad_account_ids[i]}: {result}")
        elif isinstance(result, list):
            all_rows.extend(result)
    
    logger.info(f"✅ Đã lấy {len(all_rows)} ads từ Facebook API (async, {len(ad_account_ids)} accounts)")
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
            # Đảm bảo account_id có prefix "act_"
            if not account_id.startswith("act_"):
                account_id_formatted = f"act_{account_id}"
            else:
                account_id_formatted = account_id
            
            url = (
                f"{FB_GRAPH_API_BASE}/{account_id_formatted}/insights"
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
            logger.error(f"🚨 Lỗi khi lấy daily breakdown từ account {account_id_formatted}: {e}")
            continue
    
    return result

