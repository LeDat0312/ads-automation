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
SCRAPEGRAPHAI_BASE_URL = "https://dashboard.scrapegraphai.com/api"  # Cần xác nhận URL thực tế
SCRAPEGRAPHAI_API_KEY = None  # Sẽ được set từ environment hoặc settings
SCRAPEGRAPHAI_TIMEOUT = 60  # 60 giây timeout

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
            # Gọi ScrapeGraphAI API
            # ⚠️ Cần xác nhận endpoint thực tế từ ScrapeGraphAI documentation
            response = await client.post(
                f"{SCRAPEGRAPHAI_BASE_URL}/scrape",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": ad_url,
                    "platform": "facebook",
                    "extract_fields": [
                        "ad_text",
                        "ad_image",
                        "ad_video",
                        "page_name",
                        "page_id",
                        "landing_page",
                        "ad_type"
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response thành CompetitorAdData
                ad_data = CompetitorAdData(
                    ad_id=data.get("ad_id", ""),
                    ad_text=data.get("ad_text", ""),
                    ad_image_url=data.get("ad_image_url"),
                    ad_video_url=data.get("ad_video_url"),
                    page_name=data.get("page_name", ""),
                    page_id=data.get("page_id", ""),
                    impressions=data.get("impressions"),
                    engagement=data.get("engagement"),
                    created_time=datetime.fromisoformat(data["created_time"]) if data.get("created_time") else None,
                    ad_type=data.get("ad_type", "UNKNOWN"),
                    landing_page_url=data.get("landing_page_url"),
                    scraped_at=datetime.now()
                )
                
                # Lưu vào cache
                if use_cache:
                    _scraping_cache[cache_key] = ad_data
                    _cache_timestamps[cache_key] = datetime.now()
                
                logger.info(f"✅ Đã scrape thành công ad: {ad_url}")
                return ad_data
            else:
                logger.error(f"❌ ScrapeGraphAI API error: {response.status_code} - {response.text}")
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
            # Gọi ScrapeGraphAI API để lấy danh sách ads
            response = await client.post(
                f"{SCRAPEGRAPHAI_BASE_URL}/scrape/competitor",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "page_id": competitor_page_id,
                    "limit": limit,
                    "platform": "facebook"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                ads = []
                
                for ad_data in data.get("ads", []):
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
                logger.error(f"❌ ScrapeGraphAI API error: {response.status_code} - {response.text}")
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
            response = await client.post(
                f"{SCRAPEGRAPHAI_BASE_URL}/search/ads",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "keyword": keyword,
                    "platform": "facebook",
                    "limit": limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                ads = []
                
                for ad_data in data.get("results", []):
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
                logger.error(f"❌ ScrapeGraphAI API error: {response.status_code} - {response.text}")
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

