"""
Competitor Research API
Tích hợp ScrapeGraphAI để nghiên cứu đối thủ
⚠️ CHỈ DÙNG CHO HỆ THỐNG NỘI BỘ
"""
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.services.scrapegraphai_service import (
    scrape_facebook_ad,
    scrape_competitor_ads,
    search_competitor_ads_by_keyword,
    CompetitorAdData
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/competitor", tags=["competitor-research"])


# Pydantic models
class ScrapeAdRequest(BaseModel):
    ad_url: str
    use_cache: bool = True


class ScrapeCompetitorRequest(BaseModel):
    page_id: str
    limit: int = 50
    use_cache: bool = True


class SearchAdsRequest(BaseModel):
    keyword: str
    limit: int = 20
    use_cache: bool = True


@router.post("/scrape/ad")
async def scrape_ad_endpoint(
    request: Request,
    payload: ScrapeAdRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db = Depends(get_db)
):
    """
    Scrape thông tin một quảng cáo Facebook cụ thể
    
    Args:
        payload: {ad_url: string, use_cache: bool}
    
    Returns:
        CompetitorAdData
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        ad_data = await scrape_facebook_ad(
            ad_url=payload.ad_url,
            use_cache=payload.use_cache
        )
        
        if not ad_data:
            raise HTTPException(status_code=404, detail="Không thể scrape quảng cáo này")
        
        return JSONResponse({
            "success": True,
            "data": {
                "ad_id": ad_data.ad_id,
                "ad_text": ad_data.ad_text,
                "ad_image_url": ad_data.ad_image_url,
                "ad_video_url": ad_data.ad_video_url,
                "page_name": ad_data.page_name,
                "page_id": ad_data.page_id,
                "impressions": ad_data.impressions,
                "engagement": ad_data.engagement,
                "created_time": ad_data.created_time.isoformat() if ad_data.created_time else None,
                "ad_type": ad_data.ad_type,
                "landing_page_url": ad_data.landing_page_url,
                "scraped_at": ad_data.scraped_at.isoformat()
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping ad: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error scraping ad: {str(e)}")


@router.post("/scrape/competitor")
async def scrape_competitor_endpoint(
    request: Request,
    payload: ScrapeCompetitorRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db = Depends(get_db)
):
    """
    Scrape tất cả quảng cáo của một đối thủ
    
    Args:
        payload: {page_id: string, limit: int, use_cache: bool}
    
    Returns:
        List[CompetitorAdData]
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        ads = await scrape_competitor_ads(
            competitor_page_id=payload.page_id,
            limit=payload.limit,
            use_cache=payload.use_cache
        )
        
        return JSONResponse({
            "success": True,
            "count": len(ads),
            "data": [
                {
                    "ad_id": ad.ad_id,
                    "ad_text": ad.ad_text,
                    "ad_image_url": ad.ad_image_url,
                    "ad_video_url": ad.ad_video_url,
                    "page_name": ad.page_name,
                    "page_id": ad.page_id,
                    "impressions": ad.impressions,
                    "engagement": ad.engagement,
                    "created_time": ad.created_time.isoformat() if ad.created_time else None,
                    "ad_type": ad.ad_type,
                    "landing_page_url": ad.landing_page_url,
                    "scraped_at": ad.scraped_at.isoformat()
                }
                for ad in ads
            ]
        })
        
    except Exception as e:
        logger.error(f"Error scraping competitor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error scraping competitor: {str(e)}")


@router.post("/search/ads")
async def search_ads_endpoint(
    request: Request,
    payload: SearchAdsRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db = Depends(get_db)
):
    """
    Tìm kiếm quảng cáo đối thủ theo keyword
    
    Args:
        payload: {keyword: string, limit: int, use_cache: bool}
    
    Returns:
        List[CompetitorAdData]
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        ads = await search_competitor_ads_by_keyword(
            keyword=payload.keyword,
            limit=payload.limit,
            use_cache=payload.use_cache
        )
        
        return JSONResponse({
            "success": True,
            "count": len(ads),
            "keyword": payload.keyword,
            "data": [
                {
                    "ad_id": ad.ad_id,
                    "ad_text": ad.ad_text,
                    "ad_image_url": ad.ad_image_url,
                    "ad_video_url": ad.ad_video_url,
                    "page_name": ad.page_name,
                    "page_id": ad.page_id,
                    "impressions": ad.impressions,
                    "engagement": ad.engagement,
                    "created_time": ad.created_time.isoformat() if ad.created_time else None,
                    "ad_type": ad.ad_type,
                    "landing_page_url": ad.landing_page_url,
                    "scraped_at": ad.scraped_at.isoformat()
                }
                for ad in ads
            ]
        })
        
    except Exception as e:
        logger.error(f"Error searching ads: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching ads: {str(e)}")


@router.get("/health")
async def competitor_research_health():
    """Health check endpoint"""
    from app.services.scrapegraphai_service import get_scrapegraphai_api_key
    
    api_key = get_scrapegraphai_api_key()
    has_api_key = api_key is not None
    
    return JSONResponse({
        "status": "healthy",
        "service": "competitor-research",
        "has_api_key": has_api_key,
        "message": "ScrapeGraphAI service ready" if has_api_key else "ScrapeGraphAI API key not configured"
    })

