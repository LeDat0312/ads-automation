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
    ChannelRead, ChannelCreate, ChannelUpdate, FacebookPageImport,
    ChannelGroupRead, ChannelGroupCreate, ChannelGroupUpdate,
    ChannelWithPostingSettings, PostingSettingsBulkUpdateWithIds
)

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

