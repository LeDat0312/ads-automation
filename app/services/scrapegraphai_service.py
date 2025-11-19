"""
ScrapeGraphAI Service
Tích hợp ScrapeGraphAI để nghiên cứu và scraping đối thủ Facebook Ads
⚠️ CHỈ DÙNG CHO HỆ THỐNG NỘI BỘ
"""
import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ScrapeGraphAI API Configuration
# Documentation: https://docs.scrapegraphai.com/api-reference/introduction
SCRAPEGRAPHAI_BASE_URL = "https://api.scrapegraphai.com/v1"
SCRAPEGRAPHAI_API_KEY = None  # Sẽ được set từ environment hoặc settings
SCRAPEGRAPHAI_TIMEOUT = 120  # 120 giây timeout (API có thể mất thời gian)

# Cache cho dữ liệu scraping (tránh scrape quá thường xuyên)
_scraping_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, datetime] = {}
CACHE_TTL_SECONDS = 3600  # Cache 1 giờ để tránh rate limit


@dataclass
class CompetitorAdData:
    """Dữ liệu quảng cáo của đối thủ"""
    ad_id: str
    ad_text: str
    ad_image_url: Optional[str]
    ad_video_url: Optional[str]
    page_name: str
    page_id: str
    impressions: Optional[int]
    engagement: Optional[int]
    created_time: Optional[datetime]
    ad_type: str  # IMAGE, VIDEO, CAROUSEL, etc.
    landing_page_url: Optional[str]
    scraped_at: datetime


def get_scrapegraphai_api_key(user_id: Optional[int] = None, db: Optional['Session'] = None) -> Optional[str]:
    """
    Lấy API key từ database (UserSettings) hoặc environment variable
    Ưu tiên lấy từ database nếu có user_id và db
    """
    # Ưu tiên lấy từ database nếu có user_id và db
    if user_id and db:
        try:
            from app.models.user_settings import UserSettings
            from app.core.security import decrypt_token
            
            user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if user_settings and user_settings.scrapegraphai_api_key_encrypted:
                try:
                    api_key = decrypt_token(user_settings.scrapegraphai_api_key_encrypted)
                    return api_key
                except Exception as e:
                    logger.error(f"Error decrypting ScrapeGraphAI API key for user {user_id}: {e}")
        except Exception as e:
            logger.error(f"Error getting ScrapeGraphAI API key from database: {e}")
    
    # Fallback: lấy từ environment variable
    import os
    api_key = os.getenv("SCRAPEGRAPHAI_API_KEY")
    if not api_key:
        logger.warning("ScrapeGraphAI API key not found in database or environment")
    return api_key


async def scrape_facebook_ad(
    ad_url: str,
    use_cache: bool = True,
    user_id: Optional[int] = None,
    db: Optional['Session'] = None
) -> Optional[CompetitorAdData]:
    """
    Scrape thông tin một quảng cáo Facebook cụ thể
    
    Args:
        ad_url: URL của quảng cáo Facebook (từ Ads Library hoặc direct link)
        use_cache: Có dùng cache không
    
    Returns:
        CompetitorAdData hoặc None nếu lỗi
    """
    # Check cache
    if use_cache:
        cache_key = f"ad_{ad_url}"
        if cache_key in _scraping_cache:
            cached_time = _cache_timestamps.get(cache_key)
            if cached_time and (datetime.now() - cached_time).total_seconds() < CACHE_TTL_SECONDS:
                logger.info(f"✅ Cache hit cho ad: {ad_url}")
                return _scraping_cache[cache_key]
    
    api_key = get_scrapegraphai_api_key(user_id, db)
    if not api_key:
        logger.error("ScrapeGraphAI API key not configured")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=SCRAPEGRAPHAI_TIMEOUT) as client:
            # Sử dụng SmartScraper để scrape Facebook Ad URL
            # Documentation: https://docs.scrapegraphai.com/api-reference/endpoint/smartscraper/start
            user_prompt = f"""Extract all information from this Facebook ad URL: {ad_url}
            
Please extract the following information in JSON format:
- ad_id: The Facebook ad ID
- ad_text: The ad text/copy
- ad_image_url: URL of the ad image (if any)
- ad_video_url: URL of the ad video (if any)
- page_name: Name of the Facebook page running the ad
- page_id: Facebook page ID
- landing_page_url: The landing page URL the ad links to
- ad_type: Type of ad (IMAGE, VIDEO, CAROUSEL, etc.)
- impressions: Number of impressions (if available)
- engagement: Number of engagements (if available)
- created_time: When the ad was created (if available)"""
            
            output_schema = {
                "type": "object",
                "properties": {
                    "ad_id": {"type": "string"},
                    "ad_text": {"type": "string"},
                    "ad_image_url": {"type": "string"},
                    "ad_video_url": {"type": "string"},
                    "page_name": {"type": "string"},
                    "page_id": {"type": "string"},
                    "landing_page_url": {"type": "string"},
                    "ad_type": {"type": "string"},
                    "impressions": {"type": "integer"},
                    "engagement": {"type": "integer"},
                    "created_time": {"type": "string"}
                }
            }
            
            response = await client.post(
                f"{SCRAPEGRAPHAI_BASE_URL}/smartscraper",
                headers={
                    "SGAI-APIKEY": api_key,  # Đúng format theo documentation
                    "Content-Type": "application/json"
                },
                json={
                    "url": ad_url,
                    "user_prompt": user_prompt,
                    "output_schema": output_schema,
                    "stealth": True  # Bypass bot protection
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Kiểm tra status
                if data.get("status") == "completed":
                    result = data.get("result", {})
                    
                    # Parse response thành CompetitorAdData
                    ad_data = CompetitorAdData(
                        ad_id=result.get("ad_id", ""),
                        ad_text=result.get("ad_text", ""),
                        ad_image_url=result.get("ad_image_url"),
                        ad_video_url=result.get("ad_video_url"),
                        page_name=result.get("page_name", ""),
                        page_id=result.get("page_id", ""),
                        impressions=result.get("impressions"),
                        engagement=result.get("engagement"),
                        created_time=datetime.fromisoformat(result["created_time"]) if result.get("created_time") else None,
                        ad_type=result.get("ad_type", "UNKNOWN"),
                        landing_page_url=result.get("landing_page_url"),
                        scraped_at=datetime.now()
                    )
                    
                    # Lưu vào cache
                    if use_cache:
                        _scraping_cache[cache_key] = ad_data
                        _cache_timestamps[cache_key] = datetime.now()
                    
                    logger.info(f"✅ Đã scrape thành công ad: {ad_url}")
                    return ad_data
                elif data.get("status") == "processing":
                    logger.warning(f"⏳ Ad đang được xử lý: {ad_url}, request_id: {data.get('request_id')}")
                    return None
                else:
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"❌ ScrapeGraphAI API error: {error_msg}")
                    return None
            else:
                error_text = response.text
                logger.error(f"❌ ScrapeGraphAI API HTTP error: {response.status_code} - {error_text}")
                return None
                
    except httpx.TimeoutException:
        logger.error(f"⏱️ Timeout khi scrape ad: {ad_url}")
        return None
    except Exception as e:
        logger.error(f"❌ Lỗi khi scrape ad {ad_url}: {e}", exc_info=True)
        return None


async def scrape_competitor_ads(
    competitor_page_id: str,
    limit: int = 50,
    use_cache: bool = True,
    user_id: Optional[int] = None,
    db: Optional['Session'] = None
) -> List[CompetitorAdData]:
    """
    Scrape tất cả quảng cáo của một đối thủ
    
    Args:
        competitor_page_id: Facebook Page ID của đối thủ
        limit: Số lượng quảng cáo tối đa
        use_cache: Có dùng cache không
    
    Returns:
        List[CompetitorAdData]
    """
    cache_key = f"competitor_{competitor_page_id}_{limit}"
    
    # Check cache
    if use_cache:
        if cache_key in _scraping_cache:
            cached_time = _cache_timestamps.get(cache_key)
            if cached_time and (datetime.now() - cached_time).total_seconds() < CACHE_TTL_SECONDS:
                logger.info(f"✅ Cache hit cho competitor: {competitor_page_id}")
                return _scraping_cache[cache_key]
    
    api_key = get_scrapegraphai_api_key(user_id, db)
    if not api_key:
        logger.error("ScrapeGraphAI API key not configured")
        return []
    
    try:
        async with httpx.AsyncClient(timeout=SCRAPEGRAPHAI_TIMEOUT) as client:
            # Sử dụng SearchScraper để tìm ads của competitor
            # Documentation: https://docs.scrapegraphai.com/api-reference/endpoint/searchscraper/start
            user_prompt = f"""Find all Facebook ads from page ID {competitor_page_id}. 
            
Please search Facebook Ads Library and return up to {limit} ads from this page.
For each ad, extract:
- ad_id: The Facebook ad ID
- ad_text: The ad text/copy
- ad_image_url: URL of the ad image (if any)
- ad_video_url: URL of the ad video (if any)
- page_name: Name of the Facebook page
- page_id: Facebook page ID
- landing_page_url: The landing page URL
- ad_type: Type of ad (IMAGE, VIDEO, CAROUSEL, etc.)
- impressions: Number of impressions (if available)
- engagement: Number of engagements (if available)
- created_time: When the ad was created (if available)"""
            
            output_schema = {
                "type": "object",
                "properties": {
                    "ads": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ad_id": {"type": "string"},
                                "ad_text": {"type": "string"},
                                "ad_image_url": {"type": "string"},
                                "ad_video_url": {"type": "string"},
                                "page_name": {"type": "string"},
                                "page_id": {"type": "string"},
                                "landing_page_url": {"type": "string"},
                                "ad_type": {"type": "string"},
                                "impressions": {"type": "integer"},
                                "engagement": {"type": "integer"},
                                "created_time": {"type": "string"}
                            }
                        }
                    }
                }
            }
            
            response = await client.post(
                f"{SCRAPEGRAPHAI_BASE_URL}/searchscraper",
                headers={
                    "SGAI-APIKEY": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "user_prompt": user_prompt,
                    "output_schema": output_schema,
                    "stealth": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "completed":
                    result = data.get("result", {})
                    ads_list = result.get("ads", [])
                    ads = []
                    
                    for ad_data in ads_list[:limit]:  # Limit results
                        ad = CompetitorAdData(
                            ad_id=ad_data.get("ad_id", ""),
                            ad_text=ad_data.get("ad_text", ""),
                            ad_image_url=ad_data.get("ad_image_url"),
                            ad_video_url=ad_data.get("ad_video_url"),
                            page_name=ad_data.get("page_name", ""),
                            page_id=ad_data.get("page_id", competitor_page_id),
                            impressions=ad_data.get("impressions"),
                            engagement=ad_data.get("engagement"),
                            created_time=datetime.fromisoformat(ad_data["created_time"]) if ad_data.get("created_time") else None,
                            ad_type=ad_data.get("ad_type", "UNKNOWN"),
                            landing_page_url=ad_data.get("landing_page_url"),
                            scraped_at=datetime.now()
                        )
                        ads.append(ad)
                    
                    # Lưu vào cache
                    if use_cache:
                        _scraping_cache[cache_key] = ads
                        _cache_timestamps[cache_key] = datetime.now()
                    
                    logger.info(f"✅ Đã scrape {len(ads)} ads từ competitor: {competitor_page_id}")
                    return ads
                else:
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"❌ ScrapeGraphAI API error: {error_msg}")
                    return []
            else:
                error_text = response.text
                logger.error(f"❌ ScrapeGraphAI API HTTP error: {response.status_code} - {error_text}")
                return []
                
    except Exception as e:
        logger.error(f"❌ Lỗi khi scrape competitor {competitor_page_id}: {e}", exc_info=True)
        return []


async def search_competitor_ads_by_keyword(
    keyword: str,
    limit: int = 20,
    use_cache: bool = True,
    user_id: Optional[int] = None,
    db: Optional['Session'] = None
) -> List[CompetitorAdData]:
    """
    Tìm kiếm quảng cáo đối thủ theo keyword
    
    Args:
        keyword: Từ khóa tìm kiếm
        limit: Số lượng kết quả tối đa
        use_cache: Có dùng cache không
    
    Returns:
        List[CompetitorAdData]
    """
    cache_key = f"search_{keyword}_{limit}"
    
    # Check cache
    if use_cache:
        if cache_key in _scraping_cache:
            cached_time = _cache_timestamps.get(cache_key)
            if cached_time and (datetime.now() - cached_time).total_seconds() < CACHE_TTL_SECONDS:
                logger.info(f"✅ Cache hit cho search: {keyword}")
                return _scraping_cache[cache_key]
    
    api_key = get_scrapegraphai_api_key(user_id, db)
    if not api_key:
        logger.error("ScrapeGraphAI API key not configured")
        return []
    
    try:
        async with httpx.AsyncClient(timeout=SCRAPEGRAPHAI_TIMEOUT) as client:
            # Sử dụng SearchScraper để tìm kiếm ads theo keyword
            # Documentation: https://docs.scrapegraphai.com/api-reference/endpoint/searchscraper/start
            user_prompt = f"""Search Facebook Ads Library for ads related to the keyword: "{keyword}"

Please find up to {limit} Facebook ads that match this keyword.
For each ad, extract:
- ad_id: The Facebook ad ID
- ad_text: The ad text/copy
- ad_image_url: URL of the ad image (if any)
- ad_video_url: URL of the ad video (if any)
- page_name: Name of the Facebook page running the ad
- page_id: Facebook page ID
- landing_page_url: The landing page URL the ad links to
- ad_type: Type of ad (IMAGE, VIDEO, CAROUSEL, etc.)
- impressions: Number of impressions (if available)
- engagement: Number of engagements (if available)
- created_time: When the ad was created (if available)"""
            
            output_schema = {
                "type": "object",
                "properties": {
                    "ads": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ad_id": {"type": "string"},
                                "ad_text": {"type": "string"},
                                "ad_image_url": {"type": "string"},
                                "ad_video_url": {"type": "string"},
                                "page_name": {"type": "string"},
                                "page_id": {"type": "string"},
                                "landing_page_url": {"type": "string"},
                                "ad_type": {"type": "string"},
                                "impressions": {"type": "integer"},
                                "engagement": {"type": "integer"},
                                "created_time": {"type": "string"}
                            }
                        }
                    }
                }
            }
            
            response = await client.post(
                f"{SCRAPEGRAPHAI_BASE_URL}/searchscraper",
                headers={
                    "SGAI-APIKEY": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "user_prompt": user_prompt,
                    "output_schema": output_schema,
                    "stealth": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "completed":
                    result = data.get("result", {})
                    ads_list = result.get("ads", [])
                    ads = []
                    
                    for ad_data in ads_list[:limit]:  # Limit results
                        ad = CompetitorAdData(
                            ad_id=ad_data.get("ad_id", ""),
                            ad_text=ad_data.get("ad_text", ""),
                            ad_image_url=ad_data.get("ad_image_url"),
                            ad_video_url=ad_data.get("ad_video_url"),
                            page_name=ad_data.get("page_name", ""),
                            page_id=ad_data.get("page_id", ""),
                            impressions=ad_data.get("impressions"),
                            engagement=ad_data.get("engagement"),
                            created_time=datetime.fromisoformat(ad_data["created_time"]) if ad_data.get("created_time") else None,
                            ad_type=ad_data.get("ad_type", "UNKNOWN"),
                            landing_page_url=ad_data.get("landing_page_url"),
                            scraped_at=datetime.now()
                        )
                        ads.append(ad)
                    
                    # Lưu vào cache
                    if use_cache:
                        _scraping_cache[cache_key] = ads
                        _cache_timestamps[cache_key] = datetime.now()
                    
                    logger.info(f"✅ Đã tìm thấy {len(ads)} ads cho keyword: {keyword}")
                    return ads
                else:
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"❌ ScrapeGraphAI API error: {error_msg}")
                    return []
            else:
                error_text = response.text
                logger.error(f"❌ ScrapeGraphAI API HTTP error: {response.status_code} - {error_text}")
                return []
                
    except Exception as e:
        logger.error(f"❌ Lỗi khi search ads cho keyword {keyword}: {e}", exc_info=True)
        return []


def clear_scraping_cache():
    """Xóa toàn bộ cache scraping (dùng khi cần force refresh)"""
    global _scraping_cache, _cache_timestamps
    _scraping_cache.clear()
    _cache_timestamps.clear()
    logger.info("🧹 Đã xóa toàn bộ scraping cache")

