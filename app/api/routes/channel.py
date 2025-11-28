"""
Channel Management Routes
Quản lý Facebook Pages, Channel Groups và Auto Comment

NOTE: Không đụng vào Ad Studio routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
import httpx
import requests

from app.core.database import get_db
from app.models.user import User
from app.models.channel import FacebookPage, ChannelGroup, ChannelGroupItem, AutoCommentSchedule
from app.models.user_settings import UserSettings
from app.core.security import encrypt_token, decrypt_token
from app.api.routes.auth import get_current_user_optional

router = APIRouter(prefix="/api/channel", tags=["channel"])
logger = logging.getLogger(__name__)

FB_API_VERSION = "v24.0"
FB_GRAPH_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"


# ==================== SCHEMAS ====================

class FacebookPageResponse(BaseModel):
    id: str
    user_id: int
    page_id: str
    page_name: str
    page_avatar: Optional[str]
    category: Optional[str]
    connected_at: datetime
    enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FacebookPageEnableRequest(BaseModel):
    enabled: bool


class ChannelGroupResponse(BaseModel):
    id: str
    user_id: int
    name: str
    color: str
    created_at: datetime
    updated_at: datetime
    pages: List[FacebookPageResponse] = []  # Pages in this group
    
    class Config:
        from_attributes = True


class ChannelGroupCreate(BaseModel):
    name: str
    color: str = "#3B82F6"


class ChannelGroupUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class ChannelGroupItemCreate(BaseModel):
    page_id: str


class AutoCommentScheduleCreate(BaseModel):
    group_id: str
    post_id: str  # Facebook post ID to comment on
    comment_text: str
    media_url: Optional[str] = None
    scheduled_at: datetime


class AutoCommentScheduleResponse(BaseModel):
    id: str
    user_id: int
    group_id: str
    post_id: str
    comment_text: str
    media_url: Optional[str]
    scheduled_at: datetime
    posted_at: Optional[datetime]
    status: str
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== HELPER FUNCTIONS ====================

def get_user_facebook_token(user_id: int, db: Session) -> Optional[str]:
    """Lấy Facebook access token của user (decrypted)"""
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if user_settings and user_settings.facebook_token_encrypted:
        try:
            token = decrypt_token(user_settings.facebook_token_encrypted)
            return token
        except Exception as e:
            logger.error(f"Error decrypting token for user {user_id}: {e}")
            return None
    return None


async def fetch_facebook_pages(access_token: str) -> List[dict]:
    """Lấy danh sách Facebook pages từ Graph API"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{FB_GRAPH_API_BASE}/me/accounts",
                params={
                    "access_token": access_token,
                    "fields": "id,name,picture,category,access_token"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
    except Exception as e:
        logger.error(f"Error fetching Facebook pages: {e}")
        raise HTTPException(status_code=400, detail=f"Không thể lấy danh sách pages: {str(e)}")


# ==================== PAGES API ====================

@router.get("/pages", response_model=List[FacebookPageResponse])
def get_pages(
    search: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách Facebook pages của user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    query = db.query(FacebookPage).filter(FacebookPage.user_id == current_user.id)
    
    if enabled is not None:
        query = query.filter(FacebookPage.enabled == enabled)
    
    if search:
        query = query.filter(
            or_(
                FacebookPage.page_name.ilike(f"%{search}%"),
                FacebookPage.page_id.ilike(f"%{search}%")
            )
        )
    
    pages = query.order_by(FacebookPage.page_name).all()
    return pages


@router.post("/pages/sync")
async def sync_pages(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Đồng bộ danh sách Facebook pages từ Graph API"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Lấy Facebook token
    access_token = get_user_facebook_token(current_user.id, db)
    if not access_token:
        raise HTTPException(status_code=400, detail="Chưa kết nối Facebook token. Vui lòng cấu hình tại /settings")
    
    # Lấy pages từ Facebook
    fb_pages = await fetch_facebook_pages(access_token)
    
    # Sync vào database
    synced_count = 0
    updated_count = 0
    
    for fb_page in fb_pages:
        page_id = fb_page.get("id")
        page_name = fb_page.get("name", "")
        page_avatar = fb_page.get("picture", {}).get("data", {}).get("url") if fb_page.get("picture") else None
        category = fb_page.get("category", "")
        page_token = fb_page.get("access_token", "")
        
        if not page_id or not page_token:
            continue
        
        # Encrypt page token
        try:
            encrypted_token = encrypt_token(page_token)
        except Exception as e:
            logger.error(f"Error encrypting page token: {e}")
            continue
        
        # Tìm page trong DB
        existing_page = db.query(FacebookPage).filter(
            and_(
                FacebookPage.user_id == current_user.id,
                FacebookPage.page_id == page_id
            )
        ).first()
        
        if existing_page:
            # Update existing
            existing_page.page_name = page_name
            existing_page.page_avatar = page_avatar
            existing_page.category = category
            existing_page.access_token = encrypted_token
            updated_count += 1
        else:
            # Create new
            new_page = FacebookPage(
                user_id=current_user.id,
                page_id=page_id,
                page_name=page_name,
                page_avatar=page_avatar,
                category=category,
                access_token=encrypted_token,
                enabled=True
            )
            db.add(new_page)
            synced_count += 1
    
    db.commit()
    
    return {
        "message": "Đồng bộ thành công",
        "synced": synced_count,
        "updated": updated_count,
        "total": len(fb_pages)
    }


@router.post("/pages/{page_id}/enable")
def enable_page(
    page_id: str,
    request: FacebookPageEnableRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Bật/tắt page"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    page = db.query(FacebookPage).filter(
        and_(
            FacebookPage.id == page_id,
            FacebookPage.user_id == current_user.id
        )
    ).first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Không tìm thấy page")
    
    page.enabled = request.enabled
    db.commit()
    
    return {"message": f"Page đã được {'bật' if request.enabled else 'tắt'}"}


@router.delete("/pages/{page_id}")
def delete_page(
    page_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa page (ngắt kết nối)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    page = db.query(FacebookPage).filter(
        and_(
            FacebookPage.id == page_id,
            FacebookPage.user_id == current_user.id
        )
    ).first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Không tìm thấy page")
    
    db.delete(page)
    db.commit()
    
    return {"message": "Đã ngắt kết nối page"}


# ==================== GROUPS API ====================

@router.get("/groups", response_model=List[ChannelGroupResponse])
def get_groups(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách groups của user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    groups = db.query(ChannelGroup).filter(
        ChannelGroup.user_id == current_user.id
    ).order_by(ChannelGroup.created_at).all()
    
    # Load pages for each group
    result = []
    for group in groups:
        group_dict = {
            "id": group.id,
            "user_id": group.user_id,
            "name": group.name,
            "color": group.color,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
            "pages": []
        }
        
        # Get pages in this group with item_id
        items = db.query(ChannelGroupItem).filter(
            ChannelGroupItem.group_id == group.id
        ).all()
        
        for item in items:
            page = db.query(FacebookPage).filter(
                FacebookPage.id == item.page_id
            ).first()
            if page:
                page_dict = FacebookPageResponse.from_orm(page).dict()
                page_dict["item_id"] = item.id  # Add item_id for removal
                group_dict["pages"].append(page_dict)
        
        result.append(group_dict)
    
    return result


@router.post("/groups", response_model=ChannelGroupResponse)
def create_group(
    group_data: ChannelGroupCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tạo group mới"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    new_group = ChannelGroup(
        user_id=current_user.id,
        name=group_data.name,
        color=group_data.color
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    return ChannelGroupResponse(
        id=new_group.id,
        user_id=new_group.user_id,
        name=new_group.name,
        color=new_group.color,
        created_at=new_group.created_at,
        updated_at=new_group.updated_at,
        pages=[]
    )


@router.put("/groups/{group_id}", response_model=ChannelGroupResponse)
def update_group(
    group_id: str,
    group_data: ChannelGroupUpdate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Cập nhật group (đổi tên, đổi màu)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    group = db.query(ChannelGroup).filter(
        and_(
            ChannelGroup.id == group_id,
            ChannelGroup.user_id == current_user.id
        )
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Không tìm thấy group")
    
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.color is not None:
        group.color = group_data.color
    
    db.commit()
    db.refresh(group)
    
    # Load pages
    items = db.query(ChannelGroupItem).filter(
        ChannelGroupItem.group_id == group.id
    ).all()
    
    pages = []
    for item in items:
        page = db.query(FacebookPage).filter(
            FacebookPage.id == item.page_id
        ).first()
        if page:
            pages.append(FacebookPageResponse.from_orm(page))
    
    return ChannelGroupResponse(
        id=group.id,
        user_id=group.user_id,
        name=group.name,
        color=group.color,
        created_at=group.created_at,
        updated_at=group.updated_at,
        pages=pages
    )


@router.delete("/groups/{group_id}")
def delete_group(
    group_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa group"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    group = db.query(ChannelGroup).filter(
        and_(
            ChannelGroup.id == group_id,
            ChannelGroup.user_id == current_user.id
        )
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Không tìm thấy group")
    
    db.delete(group)
    db.commit()
    
    return {"message": "Đã xóa group"}


# ==================== GROUP ITEMS API ====================

@router.post("/groups/{group_id}/items")
def add_page_to_group(
    group_id: str,
    item_data: ChannelGroupItemCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Thêm page vào group"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check group belongs to user
    group = db.query(ChannelGroup).filter(
        and_(
            ChannelGroup.id == group_id,
            ChannelGroup.user_id == current_user.id
        )
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Không tìm thấy group")
    
    # Check page belongs to user
    page = db.query(FacebookPage).filter(
        and_(
            FacebookPage.id == item_data.page_id,
            FacebookPage.user_id == current_user.id
        )
    ).first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Không tìm thấy page")
    
    # Check if already in group
    existing = db.query(ChannelGroupItem).filter(
        and_(
            ChannelGroupItem.group_id == group_id,
            ChannelGroupItem.page_id == item_data.page_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Page đã có trong group này")
    
    # Create item
    new_item = ChannelGroupItem(
        group_id=group_id,
        page_id=item_data.page_id
    )
    db.add(new_item)
    db.commit()
    
    return {"message": "Đã thêm page vào group"}


@router.delete("/groups/items/{item_id}")
def remove_page_from_group(
    item_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa page khỏi group"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check item exists and belongs to user's group
    item = db.query(ChannelGroupItem).join(ChannelGroup).filter(
        and_(
            ChannelGroupItem.id == item_id,
            ChannelGroup.user_id == current_user.id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy item")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Đã xóa page khỏi group"}


# ==================== AUTO COMMENT API ====================

@router.post("/auto-comment/schedule", response_model=AutoCommentScheduleResponse)
def schedule_auto_comment(
    schedule_data: AutoCommentScheduleCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tạo lịch auto comment"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check group belongs to user
    group = db.query(ChannelGroup).filter(
        and_(
            ChannelGroup.id == schedule_data.group_id,
            ChannelGroup.user_id == current_user.id
        )
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Không tìm thấy group")
    
    # Create schedule
    new_schedule = AutoCommentSchedule(
        user_id=current_user.id,
        group_id=schedule_data.group_id,
        post_id=schedule_data.post_id,
        comment_text=schedule_data.comment_text,
        media_url=schedule_data.media_url,
        scheduled_at=schedule_data.scheduled_at,
        status="PENDING"
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    
    return AutoCommentScheduleResponse.from_orm(new_schedule)


@router.get("/auto-comment/schedules", response_model=List[AutoCommentScheduleResponse])
def get_auto_comment_schedules(
    status: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách lịch auto comment"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    query = db.query(AutoCommentSchedule).filter(
        AutoCommentSchedule.user_id == current_user.id
    )
    
    if status:
        query = query.filter(AutoCommentSchedule.status == status)
    
    schedules = query.order_by(AutoCommentSchedule.scheduled_at).all()
    return [AutoCommentScheduleResponse.from_orm(s) for s in schedules]

