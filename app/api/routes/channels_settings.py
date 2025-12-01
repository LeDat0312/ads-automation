"""
Channel Settings API Routes
API endpoints for Channel Management under /api/settings prefix
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.user import User
from app.api.routes.auth import get_current_user_optional
from app.services.channels_service import ChannelsService, get_channels_service
from app.schemas.channels import (
    ChannelRead, ChannelCreate, ChannelUpdate, FacebookPageImport, ManualFacebookChannelCreate,
    ChannelGroupRead, ChannelGroupCreate, ChannelGroupUpdate,
    ChannelWithPostingSettings, PostingSettingsBulkUpdateWithIds
)
from app.schemas.facebook_account import FacebookChannelFromAccount, ManualFacebookChannelCreateV2

router = APIRouter(prefix="/api", tags=["Channel Settings"])

# Note: Routes are:
# - /api/channels (GET, POST, PATCH, DELETE)
# - /api/channel-groups (GET, POST, PUT, DELETE)
# - /api/posting/settings (GET) and /api/posting/settings/{channel_id} (PUT)
logger = logging.getLogger(__name__)


def require_auth(current_user: Optional[User] = Depends(get_current_user_optional)) -> User:
    """Dependency to require authentication"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    return current_user


# ==================== CHANNELS API ====================

@router.get("/channels", response_model=List[ChannelRead], summary="List channels")
def list_channels(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    search: Optional[str] = Query(None, description="Search by name/id"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    List all channels for current user
    Supports filtering by platform, search, and active status
    """
    service = get_channels_service(db, current_user.id)
    channels = service.list_channels(platform=platform, search=search, is_active=is_active)
    return channels


@router.post("/channels/import-facebook", response_model=List[ChannelRead])
def import_facebook_pages(
    pages: List[FacebookPageImport] = Body(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Import/upsert Facebook pages from OAuth flow
    Creates or updates channels for each page in the list
    """
    if not pages:
        raise HTTPException(status_code=400, detail="Danh sách pages không được để trống")
    
    service = get_channels_service(db, current_user.id)
    try:
        imported_channels = service.import_facebook_pages(pages)
        return imported_channels
    except Exception as e:
        logger.error(f"Error importing Facebook pages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi import pages: {str(e)}")


@router.post("/channels/facebook/manual", response_model=ChannelRead)
async def add_facebook_channel_manually(
    channel_data: ManualFacebookChannelCreate = Body(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Add Facebook channel manually by Page ID (with optional Page Access Token)
    
    - If page_access_token provided: verify with Facebook Graph API and enable comment/inbox features
    - If no token: use app token to get basic page info (name only)
    - Subscribe to webhook if token provided
    """
    import httpx
    from app.core.config import get_settings
    from app.services.facebook_service import facebook_service
    
    settings = get_settings()
    service = get_channels_service(db, current_user.id)
    
    page_id = channel_data.page_id
    page_access_token = channel_data.page_access_token
    page_name_override = channel_data.page_name_override
    
    # Step 1: Get page info from Facebook Graph API
    page_name = None
    avatar_url = None
    
    try:
        if page_access_token:
            # Use provided Page Access Token to get info
            logger.info(f"🔍 Verifying Page Access Token for Page ID: {page_id}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{page_id}",
                    params={
                        "fields": "id,name,picture",
                        "access_token": page_access_token
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Facebook Graph API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Không thể xác thực Page Access Token hoặc ID Trang. Vui lòng kiểm tra lại."
                    )
                
                page_data = response.json()
                page_name = page_data.get("name")
                picture_data = page_data.get("picture", {})
                if isinstance(picture_data, dict):
                    avatar_url = picture_data.get("data", {}).get("url")
                
                logger.info(f"✅ Verified page: {page_name} (ID: {page_id})")
        
        else:
            # No token provided - use App Token to get public page info
            logger.info(f"🔍 Getting public info for Page ID: {page_id} (no token provided)")
            
            if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_APP_SECRET:
                raise HTTPException(
                    status_code=500,
                    detail="Cấu hình Facebook App chưa đầy đủ. Vui lòng liên hệ quản trị viên."
                )
            
            # Get app access token
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First, get app token
                app_token_response = await client.get(
                    f"https://graph.facebook.com/oauth/access_token",
                    params={
                        "client_id": settings.FACEBOOK_APP_ID,
                        "client_secret": settings.FACEBOOK_APP_SECRET,
                        "grant_type": "client_credentials"
                    }
                )
                
                if app_token_response.status_code != 200:
                    logger.error(f"❌ Failed to get app token: {app_token_response.text}")
                    raise HTTPException(
                        status_code=500,
                        detail="Không thể lấy thông tin từ Facebook. Vui lòng thử lại."
                    )
                
                app_token = app_token_response.json().get("access_token")
                
                # Then get page info
                page_response = await client.get(
                    f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{page_id}",
                    params={
                        "fields": "id,name,picture",
                        "access_token": app_token
                    }
                )
                
                if page_response.status_code != 200:
                    logger.error(f"❌ Failed to get page info: {page_response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Không tìm thấy Trang Facebook với ID này. Vui lòng kiểm tra lại."
                    )
                
                page_data = page_response.json()
                page_name = page_data.get("name")
                picture_data = page_data.get("picture", {})
                if isinstance(picture_data, dict):
                    avatar_url = picture_data.get("data", {}).get("url")
                
                logger.info(f"✅ Got public page info: {page_name} (ID: {page_id})")
        
        # Use override name if provided
        if page_name_override:
            page_name = page_name_override
            logger.info(f"📝 Using override name: {page_name}")
        
        if not page_name:
            raise HTTPException(
                status_code=400,
                detail="Không thể lấy tên Trang từ Facebook. Vui lòng thử lại."
            )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Network error calling Facebook API: {e}")
        raise HTTPException(
            status_code=500,
            detail="Lỗi kết nối với Facebook. Vui lòng thử lại."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error verifying page: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Lỗi không xác định. Vui lòng thử lại."
        )
    
    # Step 2: Upsert channel to database
    try:
        channel = service.upsert_manual_facebook_channel(
            page_id=page_id,
            page_name=page_name,
            page_access_token=page_access_token,
            avatar_url=avatar_url
        )
        
        # Step 3: Subscribe to webhook if token provided
        if page_access_token:
            try:
                logger.info(f"🔔 Subscribing page {page_id} to webhook...")
                webhook_result = await facebook_service.subscribe_page_webhook(
                    page_id=page_id,
                    page_access_token=page_access_token
                )
                
                if webhook_result.get("success"):
                    logger.info(f"✅ Page {page_name} subscribed to webhook")
                else:
                    logger.warning(f"⚠️ Webhook subscription failed (not critical): {webhook_result}")
            except Exception as webhook_error:
                # Don't fail the whole request if webhook subscription fails
                logger.error(f"❌ Error subscribing to webhook: {webhook_error}")
        
        logger.info(f"✅ Manual channel created/updated: {page_name} (ID: {channel.id})")
        return channel
        
    except Exception as e:
        logger.error(f"❌ Error creating manual channel: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lưu kênh: {str(e)}"
        )


@router.post("/channels/facebook/from-saved-account", response_model=List[ChannelRead])
async def create_channels_from_saved_account(
    data: FacebookChannelFromAccount = Body(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Create/update multiple Facebook channels from saved Facebook Account
    
    Uses token from saved account to fetch Page Access Tokens and permissions
    """
    from app.services.facebook_account_service import get_facebook_account_service
    from app.services.facebook_service import facebook_service
    
    logger.info(f"🔵 Connect pages - facebook_account_id={data.facebook_account_id}, page_ids={data.page_ids}, user_id={current_user.id}")
    
    # Get Facebook account
    fb_account_service = get_facebook_account_service(db, current_user.id)
    fb_account = fb_account_service.get_account(data.facebook_account_id)
    
    if not fb_account:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản Facebook (Via)"
        )
    
    if not fb_account.is_active:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản Facebook đã bị vô hiệu hóa"
        )
    
    # Fetch pages with permissions from /me/accounts to get Page Access Tokens
    try:
        pages_with_perms = await fb_account_service.get_pages_with_permissions(data.facebook_account_id)
        pages_map = {p["id"]: p for p in pages_with_perms}
    except HTTPException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=f"Không thể lấy thông tin quyền của Fanpage: {e.detail}"
        )
    except Exception as e:
        logger.error(f"❌ Failed to get pages with permissions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Lỗi khi kiểm tra quyền Fanpage"
        )
    
    service = get_channels_service(db, current_user.id)
    created_channels = []
    errors = []
    warnings = []
    
    for page_id in data.page_ids:
        try:
            page_info = pages_map.get(page_id)
            
            if not page_info:
                logger.warning(f"⚠️ Page {page_id} not found in /me/accounts")
                errors.append(f"Page {page_id}: Không tìm thấy trong danh sách quản lý")
                continue
            
            # Extract data
            page_name = page_info["name"]
            picture_url = page_info.get("picture_url")
            page_access_token = page_info.get("access_token")
            is_admin = page_info.get("is_admin", False)
            can_publish = page_info.get("can_publish", False)
            can_moderate = page_info.get("can_moderate", False)
            warning_message = page_info.get("warning_message")
            
            logger.info(
                f"📄 Page {page_id} ({page_name}): "
                f"has_token={bool(page_access_token)}, is_admin={is_admin}, "
                f"can_publish={can_publish}, can_moderate={can_moderate}"
            )
            
            # Create/update channel
            channel = service.upsert_manual_facebook_channel(
                page_id=page_id,
                page_name=page_name,
                page_access_token=page_access_token if page_access_token else None,
                avatar_url=picture_url
            )
            
            created_channels.append(channel)
            
            # Subscribe to webhook only if has page token and can moderate
            if page_access_token and (can_publish or can_moderate):
                try:
                    await facebook_service.subscribe_page_webhook(
                        page_id=page_id,
                        page_access_token=page_access_token
                    )
                    logger.info(f"✅ Subscribed page {page_id} to webhook")
                except Exception as webhook_error:
                    logger.error(f"⚠️ Webhook subscription failed for {page_id}: {webhook_error}")
                    warnings.append(f"{page_name}: Webhook subscription failed")
            else:
                logger.warning(
                    f"⚠️ Skip webhook for {page_id}: "
                    f"has_token={bool(page_access_token)}, can_publish={can_publish}, can_moderate={can_moderate}"
                )
                if warning_message:
                    warnings.append(f"{page_name}: {warning_message}")
                elif not page_access_token:
                    warnings.append(f"{page_name}: Không lấy được Page Access Token")
            
        except Exception as page_error:
            logger.error(f"❌ Error processing page {page_id}: {page_error}", exc_info=True)
            errors.append(f"Page {page_id}: {str(page_error)}")
    
    if not created_channels and errors:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể kết nối Fanpage. {'; '.join(errors[:2])}"
        )
    
    logger.info(f"✅ Created/updated {len(created_channels)} channels from account {fb_account.name}")
    
    if errors:
        logger.warning(f"⚠️ Errors: {errors}")
    if warnings:
        logger.warning(f"⚠️ Warnings: {warnings}")
    
    return created_channels


@router.post("/channels/facebook/manual-v2")
async def add_facebook_channel_manually_v2(
    channel_data: ManualFacebookChannelCreateV2 = Body(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Add Facebook channel manually (Version 2) with permission checking
    
    - If facebook_account_id provided: check page in Via's managed pages first
    - Otherwise: use app token (public info only, no admin rights)
    - Returns channel info with permission flags
    """
    import httpx
    from app.core.config import get_settings
    from app.services.facebook_service import facebook_service
    from app.services.facebook_account_service import get_facebook_account_service
    
    settings = get_settings()
    service = get_channels_service(db, current_user.id)
    
    page_id = channel_data.page_id
    page_name_override = channel_data.page_name_override
    
    # Permission flags
    is_admin = False
    can_publish = False
    can_moderate = False
    warning_message = None
    
    # Determine which token to use and check permissions
    access_token = None
    page_access_token = None
    
    if channel_data.facebook_account_id:
        # Use token from saved account - check in managed pages
        fb_account_service = get_facebook_account_service(db, current_user.id)
        fb_account = fb_account_service.get_account(channel_data.facebook_account_id)
        
        if not fb_account:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài khoản Facebook (Via)"
            )
        
        if not fb_account.is_active:
            raise HTTPException(
                status_code=400,
                detail="Tài khoản Facebook đã bị vô hiệu hóa"
            )
        
        access_token = fb_account.access_token
        
        # Try to find page in Via's managed pages to get permissions
        try:
            pages_with_perms = await fb_account_service.get_pages_with_permissions(channel_data.facebook_account_id)
            page_in_managed = next((p for p in pages_with_perms if p["id"] == page_id), None)
            
            if page_in_managed:
                # Via manages this page - use its permissions
                is_admin = page_in_managed.get("is_admin", False)
                can_publish = page_in_managed.get("can_publish", False)
                can_moderate = page_in_managed.get("can_moderate", False)
                page_access_token = page_in_managed.get("access_token")
                
                if not is_admin:
                    warning_message = "Via này chưa là Quản trị viên của Fanpage. Bạn cần thêm Via làm QTV để sử dụng tính năng đăng bài, lên lịch và tự động bình luận."
            else:
                # Page not in managed list - Via has no permissions
                warning_message = "Via không có quyền quản lý Fanpage này. Kênh sẽ được tạo nhưng không thể sử dụng tính năng đăng bài và tự động bình luận."
                
        except Exception as e:
            logger.warning(f"⚠️ Could not check page permissions: {e}")
            # Continue with public info
            
    else:
        # No Via specified - use app token (public info only)
        warning_message = "Kênh được tạo không có Via quản lý. Chỉ xem thông tin công khai, không thể đăng bài hay tự động bình luận."
        
        if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_APP_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Cấu hình Facebook App chưa đầy đủ. Vui lòng liên hệ quản trị viên."
            )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                app_token_response = await client.get(
                    "https://graph.facebook.com/oauth/access_token",
                    params={
                        "client_id": settings.FACEBOOK_APP_ID,
                        "client_secret": settings.FACEBOOK_APP_SECRET,
                        "grant_type": "client_credentials"
                    }
                )
                
                if app_token_response.status_code == 200:
                    access_token = app_token_response.json().get("access_token")
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Không thể lấy App Token từ Facebook"
                    )
        except httpx.RequestError as e:
            logger.error(f"❌ Network error getting app token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Lỗi kết nối với Facebook"
            )
    
    # Get page info
    page_name = None
    avatar_url = None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{page_id}",
                params={
                    "fields": "id,name,picture",
                    "access_token": access_token
                }
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_message = error_data.get("error", {}).get("message", "Không xác định")
                logger.error(f"❌ Failed to get page info: {response.status_code} - {error_message}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Không tìm thấy Trang Facebook với ID {page_id}. {error_message}"
                )
            
            page_data = response.json()
            page_name = page_data.get("name")
            picture_data = page_data.get("picture", {})
            if isinstance(picture_data, dict):
                avatar_url = picture_data.get("data", {}).get("url")
        
        # Use override name if provided
        if page_name_override:
            page_name = page_name_override
        
        if not page_name:
            raise HTTPException(
                status_code=400,
                detail="Không thể lấy tên Trang từ Facebook"
            )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Network error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Lỗi kết nối với Facebook. Vui lòng thử lại."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting page info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Lỗi không xác định"
        )
    
    # Create/update channel
    try:
        channel = service.upsert_manual_facebook_channel(
            page_id=page_id,
            page_name=page_name,
            page_access_token=page_access_token if channel_data.facebook_account_id else None,
            avatar_url=avatar_url
        )
        
        # Subscribe to webhook if admin and using saved account
        if channel_data.facebook_account_id and is_admin and page_access_token:
            try:
                await facebook_service.subscribe_page_webhook(
                    page_id=page_id,
                    page_access_token=page_access_token
                )
                logger.info(f"✅ Subscribed page {page_id} to webhook")
            except Exception as webhook_error:
                logger.error(f"⚠️ Webhook subscription failed: {webhook_error}")
        
        logger.info(f"✅ Manual channel V2 created: {page_name} (admin={is_admin})")
        
        # Return channel info with permission flags
        return {
            "channel": channel,
            "is_admin": is_admin,
            "can_publish": can_publish,
            "can_moderate": can_moderate,
            "warning_message": warning_message
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating manual channel V2: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lưu kênh: {str(e)}"
        )


@router.patch("/channels/{channel_id}", response_model=ChannelRead)
def update_channel(
    channel_id: str,
    channel_data: ChannelUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Update a channel
    Only allows updating page_name, page_username, avatar_url, and is_active
    """
    service = get_channels_service(db, current_user.id)
    try:
        channel = service.update_channel(channel_id, channel_data)
        return channel
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating channel: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật kênh: {str(e)}")


@router.delete("/channels/{channel_id}", status_code=204)
def delete_channel(
    channel_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Delete a channel
    Cascades to memberships, posting settings, and auto-comment templates
    """
    service = get_channels_service(db, current_user.id)
    try:
        service.delete_channel(channel_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting channel: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa kênh: {str(e)}")


# ==================== CHANNEL GROUPS API ====================

@router.get("/channel-groups", response_model=List[ChannelGroupRead])
def list_channel_groups(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    List all channel groups for current user
    Includes nested channel information
    """
    service = get_channels_service(db, current_user.id)
    groups = service.list_groups()
    
    # Convert to read schema with nested channels
    result = []
    for group in groups:
        # Load channels through memberships
        memberships = group.memberships
        channels = [m.channel for m in memberships]
        
        group_dict = {
            "id": group.id,
            "user_id": group.user_id,
            "name": group.name,
            "color_hex": group.color_hex,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
            "channels": channels
        }
        result.append(ChannelGroupRead(**group_dict))
    
    return result


@router.post("/channel-groups", response_model=ChannelGroupRead, status_code=201)
def create_channel_group(
    group_data: ChannelGroupCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Create a new channel group
    Optionally include initial channel_ids to add to the group
    """
    service = get_channels_service(db, current_user.id)
    try:
        group = service.create_group(group_data)
        
        # Load channels for response
        memberships = group.memberships
        channels = [m.channel for m in memberships]
        
        group_dict = {
            "id": group.id,
            "user_id": group.user_id,
            "name": group.name,
            "color_hex": group.color_hex,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
            "channels": channels
        }
        return ChannelGroupRead(**group_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating channel group: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo nhóm kênh: {str(e)}")


@router.put("/channel-groups/{group_id}", response_model=ChannelGroupRead)
def update_channel_group(
    group_id: str,
    group_data: ChannelGroupUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Update a channel group
    Can update name, color_hex, and channel_ids
    If channel_ids is provided, replaces all existing memberships
    """
    service = get_channels_service(db, current_user.id)
    try:
        group = service.update_group(group_id, group_data)
        
        # Load channels for response
        memberships = group.memberships
        channels = [m.channel for m in memberships]
        
        group_dict = {
            "id": group.id,
            "user_id": group.user_id,
            "name": group.name,
            "color_hex": group.color_hex,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
            "channels": channels
        }
        return ChannelGroupRead(**group_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating channel group: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật nhóm kênh: {str(e)}")


@router.delete("/channel-groups/{group_id}", status_code=204)
def delete_channel_group(
    group_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Delete a channel group
    Cascades to memberships
    """
    service = get_channels_service(db, current_user.id)
    try:
        service.delete_group(group_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting channel group: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa nhóm kênh: {str(e)}")


# ==================== POSTING SETTINGS API ====================

@router.get("/posting/settings", response_model=List[ChannelWithPostingSettings])
def get_posting_settings(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get posting settings for all channels
    Returns list with channel, settings, and auto-comment templates for each channel
    """
    service = get_channels_service(db, current_user.id)
    try:
        settings_list = service.get_posting_settings_for_all_channels()
        
        result = []
        for item in settings_list:
            result.append(ChannelWithPostingSettings(
                channel=item["channel"],
                settings=item["settings"],
                auto_comments=item["auto_comments"]
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error getting posting settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy cài đặt đăng bài: {str(e)}")


@router.put("/posting/settings/{channel_id}")
def update_posting_settings(
    channel_id: str,
    settings_data: PostingSettingsBulkUpdateWithIds = Body(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Upsert posting settings and auto-comment templates for a channel
    If template has id: update existing template
    If template has no id: create new template
    Templates not in the list will be deleted
    """
    service = get_channels_service(db, current_user.id)
    try:
        # Convert to PostingSettingsUpdate
        from app.schemas.channels import PostingSettingsUpdate
        posting_settings_update = PostingSettingsUpdate(
            default_signature=settings_data.default_signature,
            auto_comment_enabled=settings_data.auto_comment_enabled,
            auto_comment_delay_seconds=settings_data.auto_comment_delay_seconds
        )
        
        result = service.upsert_posting_settings(
            channel_id=channel_id,
            settings_data=posting_settings_update,
            auto_comment_templates=settings_data.auto_comments
        )
        
        return ChannelWithPostingSettings(
            channel=result["channel"],
            settings=result["settings"],
            auto_comments=result["auto_comments"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating posting settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật cài đặt đăng bài: {str(e)}")

