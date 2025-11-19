"""
Competitor Research API
Tích hợp ScrapeGraphAI để nghiên cứu đối thủ
⚠️ CHỈ DÙNG CHO HỆ THỐNG NỘI BỘ
"""
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.api.routes.auth import get_current_user_optional
from app.models.user import User
from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message
from app.services.scrapegraphai_service import (
    scrape_facebook_ad,
    scrape_competitor_ads,
    search_competitor_ads_by_keyword,
    CompetitorAdData,
    get_scrapegraphai_api_key
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/competitor", tags=["competitor-research"])


@router.get("/", response_class=HTMLResponse)
async def competitor_research_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Trang nghiên cứu đối thủ với ScrapeGraphAI"""
    
    if not current_user:
        return HTMLResponse(content="""
        <script>
            window.location.href = '/auth/login';
        </script>
        """)
    
    if not current_user.is_active:
        return HTMLResponse(content=get_account_locked_message())
    
    user_info = get_user_dropdown_menu(current_user)
    has_api_key = get_scrapegraphai_api_key() is not None
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nghiên Cứu Đối Thủ - ScrapeGraphAI</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
                color: #1e293b;
                line-height: 1.6;
                min-height: 100vh;
                position: relative;
                overflow-x: hidden;
            }}
            
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .user-menu-container {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 100px 32px 80px;
                position: relative;
                z-index: 1;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 60px;
                color: white;
            }}
            
            .header h1 {{
                font-size: 48px;
                font-weight: 800;
                margin-bottom: 16px;
                text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            }}
            
            .header p {{
                font-size: 18px;
                color: rgba(255, 255, 255, 0.9);
            }}
            
            .card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 40px;
                margin-bottom: 32px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }}
            
            .card h2 {{
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 24px;
                color: #1e293b;
            }}
            
            .form-group {{
                margin-bottom: 24px;
            }}
            
            .form-group label {{
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #1e293b;
            }}
            
            .form-group input {{
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s;
            }}
            
            .form-group input:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 14px 32px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }}
            
            .btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .alert {{
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 24px;
            }}
            
            .alert-warning {{
                background: #fef3c7;
                border: 2px solid #fbbf24;
                color: #92400e;
            }}
            
            .alert-error {{
                background: #fee2e2;
                border: 2px solid #ef4444;
                color: #991b1b;
            }}
            
            .alert-success {{
                background: #d1fae5;
                border: 2px solid #10b981;
                color: #065f46;
            }}
            
            .results {{
                margin-top: 32px;
            }}
            
            .ad-item {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 16px;
            }}
            
            .ad-item h3 {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }}
            
            .ad-item p {{
                color: #64748b;
                margin-bottom: 4px;
            }}
            
            .loading {{
                text-align: center;
                padding: 40px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        {user_info}
        
        <div class="container">
            <div class="header">
                <h1>🔍 Nghiên Cứu Đối Thủ</h1>
                <p>Scrape và phân tích quảng cáo của đối thủ với ScrapeGraphAI</p>
            </div>
            
            {f'<div class="alert alert-warning"><strong>⚠️ Lưu ý:</strong> ScrapeGraphAI API key chưa được cấu hình. Vui lòng set biến môi trường SCRAPEGRAPHAI_API_KEY.</div>' if not has_api_key else ''}
            
            <div class="card">
                <h2>🔎 Tìm kiếm quảng cáo theo keyword</h2>
                <div class="form-group">
                    <label>Từ khóa:</label>
                    <input type="text" id="keyword-input" placeholder="Ví dụ: điện thoại, laptop, quần áo...">
                </div>
                <button class="btn" onclick="searchAds()">Tìm kiếm</button>
                <div id="search-results" class="results"></div>
            </div>
            
            <div class="card">
                <h2>📄 Scrape quảng cáo cụ thể</h2>
                <div class="form-group">
                    <label>URL quảng cáo Facebook:</label>
                    <input type="text" id="ad-url-input" placeholder="https://www.facebook.com/ads/library/?id=...">
                </div>
                <button class="btn" onclick="scrapeAd()">Scrape</button>
                <div id="scrape-results" class="results"></div>
            </div>
            
            <div class="card">
                <h2>👤 Scrape ads của đối thủ</h2>
                <div class="form-group">
                    <label>Facebook Page ID:</label>
                    <input type="text" id="page-id-input" placeholder="123456789012345">
                </div>
                <button class="btn" onclick="scrapeCompetitor()">Scrape</button>
                <div id="competitor-results" class="results"></div>
            </div>
        </div>
        
        <script>
            async function searchAds() {{
                const keyword = document.getElementById('keyword-input').value;
                if (!keyword) {{
                    alert('Vui lòng nhập từ khóa');
                    return;
                }}
                
                const resultsDiv = document.getElementById('search-results');
                resultsDiv.innerHTML = '<div class="loading">Đang tìm kiếm...</div>';
                
                try {{
                    const response = await fetch('/competitor/search/ads', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ keyword, limit: 20, use_cache: true }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        if (data.data.length === 0) {{
                            resultsDiv.innerHTML = '<div class="alert alert-warning">Không tìm thấy quảng cáo nào.</div>';
                        }} else {{
                            resultsDiv.innerHTML = `<div class="alert alert-success">Tìm thấy ${{data.count}} quảng cáo:</div>` +
                                data.data.map(ad => `
                                    <div class="ad-item">
                                        <h3>${{ad.page_name}}</h3>
                                        <p><strong>Ad ID:</strong> ${{ad.ad_id}}</p>
                                        <p><strong>Nội dung:</strong> ${{ad.ad_text || 'N/A'}}</p>
                                        <p><strong>Loại:</strong> ${{ad.ad_type}}</p>
                                        ${{ad.landing_page_url ? `<p><strong>Landing Page:</strong> <a href="${{ad.landing_page_url}}" target="_blank">${{ad.landing_page_url}}</a></p>` : ''}}
                                    </div>
                                `).join('');
                        }}
                    }} else {{
                        resultsDiv.innerHTML = '<div class="alert alert-error">Lỗi: ' + (data.message || 'Không thể tìm kiếm') + '</div>';
                    }}
                }} catch (error) {{
                    resultsDiv.innerHTML = '<div class="alert alert-error">Lỗi: ' + error.message + '</div>';
                }}
            }}
            
            async function scrapeAd() {{
                const adUrl = document.getElementById('ad-url-input').value;
                if (!adUrl) {{
                    alert('Vui lòng nhập URL quảng cáo');
                    return;
                }}
                
                const resultsDiv = document.getElementById('scrape-results');
                resultsDiv.innerHTML = '<div class="loading">Đang scrape...</div>';
                
                try {{
                    const response = await fetch('/competitor/scrape/ad', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ ad_url: adUrl, use_cache: true }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        const ad = data.data;
                        resultsDiv.innerHTML = `
                            <div class="alert alert-success">Scrape thành công!</div>
                            <div class="ad-item">
                                <h3>${{ad.page_name}}</h3>
                                <p><strong>Ad ID:</strong> ${{ad.ad_id}}</p>
                                <p><strong>Nội dung:</strong> ${{ad.ad_text || 'N/A'}}</p>
                                <p><strong>Loại:</strong> ${{ad.ad_type}}</p>
                                ${{ad.ad_image_url ? `<p><strong>Hình ảnh:</strong> <a href="${{ad.ad_image_url}}" target="_blank">Xem</a></p>` : ''}}
                                ${{ad.landing_page_url ? `<p><strong>Landing Page:</strong> <a href="${{ad.landing_page_url}}" target="_blank">${{ad.landing_page_url}}</a></p>` : ''}}
                            </div>
                        `;
                    }} else {{
                        resultsDiv.innerHTML = '<div class="alert alert-error">Lỗi: ' + (data.message || 'Không thể scrape') + '</div>';
                    }}
                }} catch (error) {{
                    resultsDiv.innerHTML = '<div class="alert alert-error">Lỗi: ' + error.message + '</div>';
                }}
            }}
            
            async function scrapeCompetitor() {{
                const pageId = document.getElementById('page-id-input').value;
                if (!pageId) {{
                    alert('Vui lòng nhập Page ID');
                    return;
                }}
                
                const resultsDiv = document.getElementById('competitor-results');
                resultsDiv.innerHTML = '<div class="loading">Đang scrape...</div>';
                
                try {{
                    const response = await fetch('/competitor/scrape/competitor', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ page_id: pageId, limit: 50, use_cache: true }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        if (data.data.length === 0) {{
                            resultsDiv.innerHTML = '<div class="alert alert-warning">Không tìm thấy quảng cáo nào.</div>';
                        }} else {{
                            resultsDiv.innerHTML = `<div class="alert alert-success">Tìm thấy ${{data.count}} quảng cáo:</div>` +
                                data.data.map(ad => `
                                    <div class="ad-item">
                                        <h3>${{ad.page_name}}</h3>
                                        <p><strong>Ad ID:</strong> ${{ad.ad_id}}</p>
                                        <p><strong>Nội dung:</strong> ${{ad.ad_text || 'N/A'}}</p>
                                        <p><strong>Loại:</strong> ${{ad.ad_type}}</p>
                                    </div>
                                `).join('');
                        }}
                    }} else {{
                        resultsDiv.innerHTML = '<div class="alert alert-error">Lỗi: ' + (data.message || 'Không thể scrape') + '</div>';
                    }}
                }} catch (error) {{
                    resultsDiv.innerHTML = '<div class="alert alert-error">Lỗi: ' + error.message + '</div>';
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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

