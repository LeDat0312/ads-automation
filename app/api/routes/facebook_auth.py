"""
Facebook OAuth Router
Handle Facebook OAuth flow for connecting Facebook Pages
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
import urllib.parse

from app.core.database import get_db
from app.core.config import get_settings
from app.models.user import User
from app.api.routes.auth import get_current_user_optional
from app.services.facebook_service import get_facebook_service, FacebookService
from app.services.channels_service import ChannelsService

router = APIRouter(prefix="/api/facebook", tags=["facebook-auth"])
logger = logging.getLogger(__name__)
settings = get_settings()


@router.get("/oauth-url")
async def get_facebook_oauth_url(
    current_user: User = Depends(get_current_user_optional),
):
    """
    Get Facebook OAuth URL for user to authorize the app
    
    Returns:
        JSON with OAuth URL to redirect user to Facebook Login
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Validate Facebook app configuration
    if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_REDIRECT_URI:
        logger.error("Facebook OAuth not configured: Missing APP_ID or REDIRECT_URI")
        raise HTTPException(
            status_code=500,
            detail="Chức năng kết nối Facebook chưa được cấu hình. Vui lòng liên hệ quản trị viên."
        )
    
    # Build OAuth URL
    # Scopes for Page Management:
    # - pages_show_list: Get list of pages
    # - pages_manage_metadata: Manage page settings  
    # - pages_read_engagement: Read page engagement
    # - pages_read_user_content: Read user content on page
    # - pages_messaging: Manage page messaging
    scopes = [
        "pages_show_list",
        "pages_manage_metadata",
        "pages_read_engagement",
        "pages_read_user_content",
        "pages_messaging"
    ]
    
    # Build OAuth URL
    oauth_params = {
        "client_id": settings.FACEBOOK_APP_ID,
        "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
        "scope": ",".join(scopes),
        "response_type": "code",
        "state": f"user_{current_user.id}"  # Can be used to verify in callback
    }
    
    oauth_url = f"https://www.facebook.com/{settings.FACEBOOK_API_VERSION}/dialog/oauth"
    full_url = f"{oauth_url}?{urllib.parse.urlencode(oauth_params)}"
    
    logger.info(f"✅ Generated Facebook OAuth URL for user {current_user.id}")
    
    return {"url": full_url}


@router.get("/callback")
async def facebook_oauth_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    fb_service: FacebookService = Depends(get_facebook_service)
):
    """
    Facebook OAuth callback endpoint
    
    This endpoint:
    1. Exchanges code for user access token
    2. Gets list of user's Facebook Pages
    3. Creates/updates Channel entries for each page
    4. Subscribes pages to webhook
    5. Redirects back to frontend
    
    Query params:
        code: Authorization code from Facebook (if successful)
        error: Error code from Facebook (if failed)
        error_description: Error description
        state: State parameter (contains user_id)
    """
    # Handle errors from Facebook
    if error:
        logger.error(f"❌ Facebook OAuth error: {error} - {error_description}")
        redirect_url = f"{settings.FRONTEND_BASE_URL}/settings/channels?connect=error&reason={urllib.parse.quote(error_description or error)}"
        return RedirectResponse(url=redirect_url)
    
    if not code:
        logger.error("❌ No authorization code received from Facebook")
        redirect_url = f"{settings.FRONTEND_BASE_URL}/settings/channels?connect=error&reason=no_code"
        return RedirectResponse(url=redirect_url)
    
    # Extract user_id from state (format: "user_123")
    user_id = None
    if state and state.startswith("user_"):
        try:
            user_id = int(state.split("_")[1])
        except (IndexError, ValueError):
            logger.warning(f"⚠️ Invalid state parameter: {state}")
    
    if not user_id:
        logger.error("❌ Could not extract user_id from state")
        redirect_url = f"{settings.FRONTEND_BASE_URL}/settings/channels?connect=error&reason=invalid_state"
        return RedirectResponse(url=redirect_url)
    
    try:
        # Step 1: Exchange code for user access token
        logger.info(f"🔄 Exchanging code for access token (user: {user_id})...")
        token_data = await fb_service.exchange_code_for_token(code)
        user_access_token = token_data.access_token
        
        # Optional: Get long-lived token (60 days instead of 1-2 hours)
        logger.info(f"🔄 Getting long-lived token...")
        long_lived_token_data = await fb_service.get_long_lived_token(user_access_token)
        user_access_token = long_lived_token_data.access_token
        
        # Step 2: Get user info (optional, for logging)
        try:
            user_info = await fb_service.get_user_info(user_access_token)
            logger.info(f"✅ User: {user_info.name} (FB ID: {user_info.id})")
        except Exception as e:
            logger.warning(f"⚠️ Could not get user info: {e}")
        
        # Step 3: Get user's Facebook Pages
        logger.info(f"🔄 Getting user's Facebook Pages...")
        pages = await fb_service.get_user_pages(user_access_token)
        
        if not pages:
            logger.warning("⚠️ No pages found for user")
            redirect_url = f"{settings.FRONTEND_BASE_URL}/settings/channels?connect=error&reason=no_pages"
            return RedirectResponse(url=redirect_url)
        
        logger.info(f"✅ Found {len(pages)} pages")
        
        # Step 4: Create/update Channel entries for each page
        channels_service = ChannelsService(db=db, user_id=user_id)
        created_count = 0
        updated_count = 0
        
        for page in pages:
            try:
                # Upsert channel
                channel = channels_service.upsert_facebook_page_channel(
                    page_id=page.id,
                    page_name=page.name,
                    page_access_token=page.access_token,
                    avatar_url=None  # TODO: Can fetch from Graph API if needed
                )
                
                # Track if created or updated
                if channel.created_at == channel.updated_at:
                    created_count += 1
                else:
                    updated_count += 1
                
                # Step 5: Subscribe page to webhook
                logger.info(f"🔄 Subscribing page {page.name} to webhook...")
                webhook_result = await fb_service.subscribe_page_webhook(
                    page_id=page.id,
                    page_access_token=page.access_token
                )
                
                if webhook_result.get("success"):
                    logger.info(f"✅ Page {page.name} subscribed to webhook")
                else:
                    logger.warning(f"⚠️ Page {page.name} webhook subscription failed (not critical)")
                
            except Exception as e:
                logger.error(f"❌ Error processing page {page.name}: {e}")
                # Continue with other pages
                continue
        
        logger.info(f"✅ OAuth flow complete: {created_count} created, {updated_count} updated")
        
        # Redirect back to frontend with success
        redirect_url = f"{settings.FRONTEND_BASE_URL}/settings/channels?connect=success&created={created_count}&updated={updated_count}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"❌ Facebook OAuth callback error: {e}", exc_info=True)
        redirect_url = f"{settings.FRONTEND_BASE_URL}/settings/channels?connect=error&reason=server_error"
        return RedirectResponse(url=redirect_url)
