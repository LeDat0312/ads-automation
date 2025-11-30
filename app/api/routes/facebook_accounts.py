"""
Facebook Account API Routes
Endpoints for managing Facebook Accounts (Via tokens)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import httpx

from app.core.database import get_db
from app.models.user import User
from app.models.facebook_account import FacebookAccountType
from app.api.routes.auth import get_current_user_optional
from app.services.facebook_account_service import FacebookAccountService, get_facebook_account_service
from app.schemas.facebook_account import (
    FacebookAccountRead, FacebookAccountCreate, FacebookAccountUpdate,
    FacebookPageSimple
)
from app.core.config import get_settings

router = APIRouter(prefix="/api/facebook-accounts", tags=["Facebook Accounts"])
logger = logging.getLogger(__name__)
settings = get_settings()


def require_auth(current_user: Optional[User] = Depends(get_current_user_optional)) -> User:
    """Dependency to require authentication"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    return current_user


@router.get("", response_model=List[FacebookAccountRead])
def list_facebook_accounts(
    type: Optional[str] = Query(None, description="Filter by token type: fanpage, ads, both"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    List Facebook accounts (Via) for current user
    
    Query params:
    - type: fanpage (includes both), ads (includes both), or both
    - is_active: true/false
    """
    service = get_facebook_account_service(db, current_user.id)
    
    token_type = None
    if type:
        try:
            token_type = FacebookAccountType(type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Loại token không hợp lệ. Chọn: fanpage, ads, hoặc both"
            )
    
    accounts = service.list_accounts(token_type=token_type, is_active=is_active)
    
    # Add token preview for display
    result = []
    for acc in accounts:
        acc_dict = FacebookAccountRead.from_orm(acc).dict()
        # Mask token: show first 10 + last 4 chars
        if acc.access_token:
            token_len = len(acc.access_token)
            if token_len > 20:
                acc_dict['access_token_preview'] = f"{acc.access_token[:10]}...{acc.access_token[-4:]}"
            else:
                acc_dict['access_token_preview'] = f"{acc.access_token[:6]}..."
        result.append(FacebookAccountRead(**acc_dict))
    
    return result


@router.post("", response_model=FacebookAccountRead)
def create_facebook_account(
    account_data: FacebookAccountCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new Facebook account (Via)"""
    service = get_facebook_account_service(db, current_user.id)
    
    try:
        account = service.create_account(account_data)
        
        # Add token preview
        acc_dict = FacebookAccountRead.from_orm(account).dict()
        if account.access_token:
            token_len = len(account.access_token)
            if token_len > 20:
                acc_dict['access_token_preview'] = f"{account.access_token[:10]}...{account.access_token[-4:]}"
            else:
                acc_dict['access_token_preview'] = f"{account.access_token[:6]}..."
        
        return FacebookAccountRead(**acc_dict)
    except Exception as e:
        logger.error(f"Error creating Facebook account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Không thể tạo tài khoản Facebook: {str(e)}"
        )


@router.patch("/{account_id}", response_model=FacebookAccountRead)
def update_facebook_account(
    account_id: int,
    account_data: FacebookAccountUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update a Facebook account"""
    service = get_facebook_account_service(db, current_user.id)
    
    try:
        account = service.update_account(account_id, account_data)
        
        # Add token preview
        acc_dict = FacebookAccountRead.from_orm(account).dict()
        if account.access_token:
            token_len = len(account.access_token)
            if token_len > 20:
                acc_dict['access_token_preview'] = f"{account.access_token[:10]}...{account.access_token[-4:]}"
            else:
                acc_dict['access_token_preview'] = f"{account.access_token[:6]}..."
        
        return FacebookAccountRead(**acc_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Facebook account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Không thể cập nhật tài khoản Facebook: {str(e)}"
        )


@router.delete("/{account_id}")
def delete_facebook_account(
    account_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete a Facebook account"""
    service = get_facebook_account_service(db, current_user.id)
    
    try:
        service.delete_account(account_id)
        return {"message": "Đã xóa tài khoản Facebook"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Facebook account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Không thể xóa tài khoản Facebook: {str(e)}"
        )


@router.post("/{account_id}/verify")
def verify_facebook_account(
    account_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Verify Facebook account token"""
    service = get_facebook_account_service(db, current_user.id)
    
    try:
        result = service.verify_token(account_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Facebook account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Không thể xác thực token: {str(e)}"
        )


@router.get("/{account_id}/pages", response_model=List[FacebookPageSimple])
async def get_pages_from_account(
    account_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get list of Facebook Pages managed by this account
    Calls Facebook Graph API /me/accounts
    """
    service = get_facebook_account_service(db, current_user.id)
    
    account = service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản Facebook")
    
    if not account.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản Facebook đã bị vô hiệu hóa")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/accounts",
                params={
                    "access_token": account.access_token,
                    "fields": "id,name,picture,category,access_token"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get pages: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Không thể lấy danh sách Fanpage. Token có thể đã hết hạn hoặc không có quyền."
                )
            
            data = response.json()
            pages_data = data.get("data", [])
            
            if not pages_data:
                return []
            
            # Transform to FacebookPageSimple
            pages = []
            for page in pages_data:
                picture_url = None
                picture_data = page.get("picture")
                if isinstance(picture_data, dict):
                    picture_url = picture_data.get("data", {}).get("url")
                
                pages.append(FacebookPageSimple(
                    id=page.get("id"),
                    name=page.get("name"),
                    picture_url=picture_url,
                    category=page.get("category"),
                    access_token=page.get("access_token")
                ))
            
            logger.info(f"✅ Found {len(pages)} pages for account {account.name}")
            return pages
            
    except httpx.RequestError as e:
        logger.error(f"❌ Network error calling Facebook API: {e}")
        raise HTTPException(
            status_code=500,
            detail="Lỗi kết nối với Facebook. Vui lòng thử lại."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting pages: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi không xác định: {str(e)}"
        )
