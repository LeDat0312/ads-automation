# -*- coding: utf-8 -*-
"""
Settings API Routes - Quản lý token Facebook, accounts, và prefixes cho mỗi user
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.core.security import encrypt_token, decrypt_token
from app.services.facebook_token_service import test_facebook_token, fetch_facebook_ad_accounts, fetch_account_30_days_spend
from app.api.routes.auth import get_current_user_optional

router = APIRouter(prefix="/settings", tags=["settings"])
logger = logging.getLogger(__name__)


# Schemas
class TokenSaveRequest(BaseModel):
    token: str


class TokenTestResponse(BaseModel):
    valid: bool
    status: str
    message: str
    permissions: List[str]
    user_info: Dict[str, Any]


class AccountResponse(BaseModel):
    id: int
    account_id: str
    account_name: Optional[str]
    account_type: str
    currency: str
    timezone: str
    enabled: bool
    status: str
    last_30_days_spend: float
    
    class Config:
        from_attributes = True


class AccountCreate(BaseModel):
    account_id: str
    account_name: Optional[str] = None
    account_type: str = "UNKNOWN"
    currency: str = "USD"
    timezone: str = "Asia/Ho_Chi_Minh"
    enabled: bool = True


class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    enabled: Optional[bool] = None
    status: Optional[str] = None


class PrefixResponse(BaseModel):
    id: int
    prefix: str
    prefix_name: Optional[str]
    enabled: bool
    
    class Config:
        from_attributes = True


class PrefixCreate(BaseModel):
    prefix: str
    prefix_name: Optional[str] = None
    enabled: bool = True


class PrefixUpdate(BaseModel):
    prefix_name: Optional[str] = None
    enabled: Optional[bool] = None


class AccountPrefixLink(BaseModel):
    account_id: int
    prefix_id: int


# ==================== TOKEN ENDPOINTS ====================

@router.post("/token/save")
def save_token(
    token_request: TokenSaveRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lưu Facebook token cho user (encrypted)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Encrypt token
    try:
        encrypted_token = encrypt_token(token_request.token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi mã hóa token: {str(e)}")
    
    # Get or create user settings
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(
            user_id=current_user.id,
            facebook_token_encrypted=encrypted_token,
            token_status="NOT_CHECKED"
        )
        db.add(user_settings)
    else:
        user_settings.facebook_token_encrypted = encrypted_token
        user_settings.token_status = "NOT_CHECKED"
        user_settings.token_last_checked = None
    
    db.commit()
    return {"message": "Token đã được lưu thành công"}


@router.post("/token/test", response_model=TokenTestResponse)
def test_token(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Test Facebook token"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Get user settings
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings or not user_settings.facebook_token_encrypted:
        raise HTTPException(status_code=404, detail="Chưa có token. Vui lòng lưu token trước.")
    
    # Decrypt token
    try:
        token = decrypt_token(user_settings.facebook_token_encrypted)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi giải mã token: {str(e)}")
    
    # Test token
    test_result = test_facebook_token(token)
    
    # Update status
    user_settings.token_status = test_result["status"]
    user_settings.token_last_checked = datetime.now()
    db.commit()
    
    return test_result


@router.get("/token/status")
def get_token_status(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy trạng thái token hiện tại"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings:
        return {
            "has_token": False,
            "status": "NOT_SET",
            "last_checked": None
        }
    
    return {
        "has_token": bool(user_settings.facebook_token_encrypted),
        "status": user_settings.token_status,
        "last_checked": user_settings.token_last_checked.isoformat() if user_settings.token_last_checked else None
    }


@router.delete("/token/delete")
def delete_token(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa Facebook token"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings or not user_settings.facebook_token_encrypted:
        raise HTTPException(status_code=404, detail="Chưa có token để xóa")
    
    user_settings.facebook_token_encrypted = None
    user_settings.token_status = "NOT_SET"
    user_settings.token_last_checked = None
    db.commit()
    
    return {"message": "Token đã được xóa thành công"}


# ==================== ACCOUNTS ENDPOINTS ====================

@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    limit: int = 15  # Chỉ lấy 15 accounts được sử dụng gần đây
):
    """
    Lấy danh sách accounts của user - chỉ lấy accounts có activity trên META ADS gần đây
    Logic: Accounts có dữ liệu trong ads_metrics (impressions > 0) trong 30 ngày gần nhất
    = Accounts đang được sử dụng trên META ADS (trình quản lý quảng cáo)
    Nếu không có activity thì không lấy account đó
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        from sqlalchemy import func, desc, distinct
        from datetime import datetime, timedelta
        from app.core.database import AdMetrics
        
        # Lấy accounts có activity trong 30 ngày gần nhất (có impressions > 0)
        # Điều này cho thấy account đang được sử dụng trên META ADS
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Subquery để lấy accounts có activity gần đây (impressions > 0)
        # và thời gian activity gần nhất
        active_accounts_subq = db.query(
            AdMetrics.account_id,
            func.max(AdMetrics.date).label('last_activity_date'),
            func.sum(AdMetrics.impressions).label('total_impressions')
        ).filter(
            AdMetrics.date >= thirty_days_ago,
            AdMetrics.account_id.isnot(None),
            AdMetrics.impressions > 0  # Chỉ lấy accounts có impressions > 0
        ).group_by(AdMetrics.account_id).having(
            func.sum(AdMetrics.impressions) > 0  # Đảm bảo có activity
        ).subquery()
        
        # Query chính: chỉ lấy accounts của user CÓ activity trên META ADS
        # Sắp xếp theo:
        # 1. last_activity_date (activity gần đây nhất)
        # 2. total_impressions (activity nhiều nhất)
        # 3. last_30_days_spend (spend cao nhất)
        accounts_query = db.query(Account).filter(
            Account.user_id == current_user.id
        ).join(
            active_accounts_subq,
            Account.account_id == active_accounts_subq.c.account_id
        ).order_by(
            desc(active_accounts_subq.c.last_activity_date),  # Activity gần đây nhất
            desc(active_accounts_subq.c.total_impressions),  # Activity nhiều nhất
            desc(Account.last_30_days_spend),  # Spend cao nhất
            Account.account_name  # Cuối cùng mới sort theo tên
        ).limit(limit)
        
        accounts = accounts_query.all()
        return accounts
    except Exception as e:
        logger.error(f"Error listing accounts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách accounts: {str(e)}")


@router.post("/accounts/sync")
def sync_accounts(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Sync accounts từ Facebook API"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        # Get token
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=404, detail="Chưa có token. Vui lòng lưu token trước.")
        
        try:
            token = decrypt_token(user_settings.facebook_token_encrypted)
        except Exception as e:
            logger.error(f"Error decrypting token: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Lỗi giải mã token: {str(e)}")
        
        # Fetch accounts from Facebook
        try:
            fb_accounts = fetch_facebook_ad_accounts(token)
        except Exception as e:
            logger.error(f"Error fetching accounts from Facebook: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Lỗi khi lấy accounts từ Facebook: {str(e)}")
        
        # Sync to database
        synced_count = 0
        updated_count = 0
        
        for fb_acc in fb_accounts:
            try:
                # Check if account exists
                existing = db.query(Account).filter(
                    Account.user_id == current_user.id,
                    Account.account_id == fb_acc["account_id"]
                ).first()
                
                if existing:
                    # Update existing
                    existing.account_name = fb_acc["name"]
                    existing.status = "ACTIVE" if fb_acc["account_status"] == 1 else "PAUSED"
                    existing.timezone = fb_acc["timezone_name"]
                    existing.currency = fb_acc.get("currency", "USD")  # Lưu currency từ Facebook
                    # Update updated_at để đánh dấu account được sync gần đây
                    existing.updated_at = datetime.now()
                    # Try to get 30 days spend
                    try:
                        existing.last_30_days_spend = fetch_account_30_days_spend(token, fb_acc["id"])
                    except Exception as spend_error:
                        logger.warning(f"Could not fetch spend for account {fb_acc['account_id']}: {spend_error}")
                    updated_count += 1
                else:
                    # Create new
                    new_account = Account(
                        user_id=current_user.id,
                        account_id=fb_acc["account_id"],
                        account_name=fb_acc["name"],
                        status="ACTIVE" if fb_acc["account_status"] == 1 else "PAUSED",
                        timezone=fb_acc["timezone_name"],
                        currency=fb_acc.get("currency", "USD"),  # Lưu currency từ Facebook
                        account_type="UNKNOWN",
                        enabled=True
                    )
                    # Try to get 30 days spend
                    try:
                        new_account.last_30_days_spend = fetch_account_30_days_spend(token, fb_acc["id"])
                    except Exception as spend_error:
                        logger.warning(f"Could not fetch spend for account {fb_acc['account_id']}: {spend_error}")
                    db.add(new_account)
                    synced_count += 1
            except Exception as acc_error:
                logger.error(f"Error syncing account {fb_acc.get('account_id', 'unknown')}: {acc_error}", exc_info=True)
                continue
        
        db.commit()
        
        return {
            "message": f"Đã sync {synced_count} accounts mới, cập nhật {updated_count} accounts",
            "synced": synced_count,
            "updated": updated_count,
            "total": len(fb_accounts)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in sync_accounts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi đồng bộ accounts: {str(e)}")


@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tạo account mới (manual)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check duplicate
    existing = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.account_id == account_data.account_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Account {account_data.account_id} đã tồn tại")
    
    account = Account(
        user_id=current_user.id,
        **account_data.dict()
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(
    request: Request,
    account_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy thông tin một account"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == current_user.id
        ).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account {account_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin account: {str(e)}")


@router.put("/accounts/{account_id}", response_model=AccountResponse)
def update_account(
    request: Request,
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Cập nhật account"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == current_user.id
        ).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        for key, value in account_data.dict(exclude_unset=True).items():
            setattr(account, key, value)
        
        # Update updated_at để đánh dấu account được user quản lý gần đây
        account.updated_at = datetime.now()
        
        db.commit()
        db.refresh(account)
        return account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật account: {str(e)}")


@router.post("/accounts/{account_id}/refresh")
def refresh_account(
    request: Request,
    account_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Refresh account - cập nhật thông tin từ Facebook API (quyền, quản trị viên, etc.)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        # Get account
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == current_user.id
        ).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get token
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=404, detail="Chưa có token. Vui lòng lưu token trước.")
        
        try:
            token = decrypt_token(user_settings.facebook_token_encrypted)
        except Exception as e:
            logger.error(f"Error decrypting token: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Lỗi giải mã token: {str(e)}")
        
        # Fetch account info from Facebook
        try:
            # Get account info from Facebook API
            import requests
            from app.services.facebook_token_service import FB_GRAPH_API_BASE
            
            url = f"{FB_GRAPH_API_BASE}/{account.account_id}"
            params = {
                "fields": "id,name,account_id,account_status,currency,timezone_name,spend_cap,amount_spent",
                "access_token": token
            }
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                raise Exception(f"Facebook API error: {data['error']['message']}")
            
            # Update account info
            account.account_name = data.get('name', account.account_name)
            account.status = "ACTIVE" if data.get('account_status', 1) == 1 else "PAUSED"
            account.timezone = data.get('timezone_name', account.timezone)
            account.currency = data.get('currency', account.currency)
            account.updated_at = datetime.now()
            
            # Try to get 30 days spend
            try:
                from app.services.facebook_token_service import fetch_account_30_days_spend
                account.last_30_days_spend = fetch_account_30_days_spend(token, data.get('id', account.account_id))
            except Exception as spend_error:
                logger.warning(f"Could not fetch spend for account {account.account_id}: {spend_error}")
            
            db.commit()
            db.refresh(account)
            
            return {
                "message": "Đã cập nhật thông tin account thành công",
                "account": account
            }
        except Exception as e:
            logger.error(f"Error refreshing account from Facebook: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Lỗi khi lấy thông tin từ Facebook: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_account: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi refresh account: {str(e)}")


@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa account"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Also delete account-prefix links
    db.query(AccountPrefix).filter(AccountPrefix.account_id == account_id).delete()
    
    db.delete(account)
    db.commit()
    return None


# ==================== PREFIXES ENDPOINTS ====================

@router.get("/prefixes", response_model=List[PrefixResponse])
def list_prefixes(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách prefixes của user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        prefixes = db.query(Prefix).filter(Prefix.user_id == current_user.id).order_by(Prefix.prefix).all()
        return prefixes
    except Exception as e:
        logger.error(f"Error listing prefixes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách prefixes: {str(e)}")


@router.post("/prefixes", response_model=PrefixResponse, status_code=201)
def create_prefix(
    prefix_data: PrefixCreate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Tạo prefix mới"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check duplicate
    existing = db.query(Prefix).filter(
        Prefix.user_id == current_user.id,
        Prefix.prefix == prefix_data.prefix
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Prefix {prefix_data.prefix} đã tồn tại")
    
    prefix = Prefix(
        user_id=current_user.id,
        **prefix_data.dict()
    )
    db.add(prefix)
    db.commit()
    db.refresh(prefix)
    return prefix


@router.get("/prefixes/{prefix_id}", response_model=PrefixResponse)
def get_prefix(
    request: Request,
    prefix_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy thông tin một prefix"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        prefix = db.query(Prefix).filter(
            Prefix.id == prefix_id,
            Prefix.user_id == current_user.id
        ).first()
        if not prefix:
            raise HTTPException(status_code=404, detail="Prefix not found")
        
        return prefix
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prefix {prefix_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin prefix: {str(e)}")


@router.put("/prefixes/{prefix_id}", response_model=PrefixResponse)
def update_prefix(
    request: Request,
    prefix_id: int,
    prefix_data: PrefixUpdate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Cập nhật prefix"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        prefix = db.query(Prefix).filter(
            Prefix.id == prefix_id,
            Prefix.user_id == current_user.id
        ).first()
        if not prefix:
            raise HTTPException(status_code=404, detail="Prefix not found")
        
        for key, value in prefix_data.dict(exclude_unset=True).items():
            setattr(prefix, key, value)
        
        db.commit()
        db.refresh(prefix)
        return prefix
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prefix {prefix_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật prefix: {str(e)}")


@router.delete("/prefixes/{prefix_id}", status_code=204)
def delete_prefix(
    prefix_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa prefix"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    prefix = db.query(Prefix).filter(
        Prefix.id == prefix_id,
        Prefix.user_id == current_user.id
    ).first()
    if not prefix:
        raise HTTPException(status_code=404, detail="Prefix not found")
    
    # Also delete account-prefix links
    db.query(AccountPrefix).filter(AccountPrefix.prefix_id == prefix_id).delete()
    
    db.delete(prefix)
    db.commit()
    return None


# ==================== ACCOUNT-PREFIX LINKS ====================

@router.get("/accounts/{account_id}/prefixes", response_model=List[PrefixResponse])
def get_account_prefixes(
    account_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách prefixes của một account"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Verify account belongs to user
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get linked prefixes
    links = db.query(AccountPrefix).filter(AccountPrefix.account_id == account_id).all()
    prefix_ids = [link.prefix_id for link in links]
    
    if not prefix_ids:
        return []
    
    prefixes = db.query(Prefix).filter(
        Prefix.id.in_(prefix_ids),
        Prefix.user_id == current_user.id
    ).all()
    return prefixes


@router.post("/accounts/{account_id}/prefixes/{prefix_id}")
def link_account_prefix(
    account_id: int,
    prefix_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Liên kết account với prefix"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Verify account and prefix belong to user
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    prefix = db.query(Prefix).filter(
        Prefix.id == prefix_id,
        Prefix.user_id == current_user.id
    ).first()
    if not prefix:
        raise HTTPException(status_code=404, detail="Prefix not found")
    
    # Check if link already exists
    existing = db.query(AccountPrefix).filter(
        AccountPrefix.account_id == account_id,
        AccountPrefix.prefix_id == prefix_id
    ).first()
    if existing:
        return {"message": "Đã liên kết sẵn"}
    
    # Create link
    link = AccountPrefix(
        user_id=current_user.id,
        account_id=account_id,
        prefix_id=prefix_id
    )
    db.add(link)
    db.commit()
    
    return {"message": "Đã liên kết thành công"}


@router.delete("/accounts/{account_id}/prefixes/{prefix_id}", status_code=204)
def unlink_account_prefix(
    account_id: int,
    prefix_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Hủy liên kết account với prefix"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    link = db.query(AccountPrefix).filter(
        AccountPrefix.account_id == account_id,
        AccountPrefix.prefix_id == prefix_id,
        AccountPrefix.user_id == current_user.id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()
    return None


# ==================== UI ROUTE ====================

@router.get("", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Trang Settings UI - Quản lý token, accounts, và prefixes"""
    
    if not current_user:
        # Redirect to login
        return HTMLResponse(
            content="<script>window.location.href='/auth/login';</script>",
            status_code=200
        )
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cài Đặt - Facebook Ads Automation</title>
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
            
            body::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                    radial-gradient(circle at 40% 20%, rgba(120, 200, 255, 0.3) 0%, transparent 50%);
                pointer-events: none;
                z-index: 0;
            }}
            
            .header {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.3);
                padding: 16px 32px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 100;
            }}
            
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .header-actions {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .btn-back {{
                padding: 8px 16px;
                background: rgba(102, 126, 234, 0.1);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 8px;
                color: #667eea;
                cursor: pointer;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .btn-back:hover {{
                background: rgba(102, 126, 234, 0.2);
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 100px 32px 40px;
                position: relative;
                z-index: 1;
            }}
            
            .section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 24px;
                padding: 32px;
                margin-bottom: 32px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }}
            
            .section-title {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 24px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .section-title .icon {{
                font-size: 28px;
            }}
            
            .form-group {{
                margin-bottom: 20px;
            }}
            
            .form-group label {{
                display: block;
                font-weight: 500;
                color: #475569;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            
            .form-group input,
            .form-group select,
            .form-group textarea {{
                width: 100%;
                padding: 12px 16px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                font-family: inherit;
                transition: all 0.2s;
            }}
            
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }}
            
            .btn-primary {{
                background: #667eea;
                color: white;
            }}
            
            .btn-primary:hover {{
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }}
            
            .btn-secondary {{
                background: #e2e8f0;
                color: #475569;
            }}
            
            .btn-secondary:hover {{
                background: #cbd5e1;
            }}
            
            .btn-success {{
                background: #10b981;
                color: white;
            }}
            
            .btn-success:hover {{
                background: #059669;
            }}
            
            .btn-danger {{
                background: #ef4444;
                color: white;
            }}
            
            .btn-danger:hover {{
                background: #dc2626;
            }}
            
            .token-status {{
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 14px;
            }}
            
            .token-status.valid {{
                background: #d1fae5;
                color: #065f46;
                border: 1px solid #6ee7b7;
            }}
            
            .token-status.invalid {{
                background: #fee2e2;
                color: #991b1b;
                border: 1px solid #fca5a5;
            }}
            
            .token-status.not-set {{
                background: #fef3c7;
                color: #92400e;
                border: 1px solid #fcd34d;
            }}
            
            .table-container {{
                overflow-x: auto;
                margin-top: 20px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
            }}
            
            th {{
                background: #f8fafc;
                font-weight: 600;
                color: #475569;
                font-size: 12px;
                text-transform: uppercase;
            }}
            
            tr:hover {{
                background: #f8fafc;
            }}
            
            .status-badge {{
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            
            .status-active {{
                background: #d1fae5;
                color: #065f46;
            }}
            
            .status-paused {{
                background: #fee2e2;
                color: #991b1b;
            }}
            
            .status-archived {{
                background: #e2e8f0;
                color: #475569;
            }}
            
            .account-type-badge {{
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            
            .type-ecommerce {{
                background: #dbeafe;
                color: #1e40af;
            }}
            
            .type-lead {{
                background: #fce7f3;
                color: #9f1239;
            }}
            
            .type-mobile {{
                background: #f3e8ff;
                color: #6b21a8;
            }}
            
            .action-buttons {{
                display: flex;
                gap: 8px;
            }}
            
            .btn-icon {{
                padding: 6px 12px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }}
            
            .btn-icon:hover {{
                transform: scale(1.05);
            }}
            
            .loading {{
                text-align: center;
                padding: 40px;
                color: #64748b;
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #64748b;
            }}
            
            .empty-state .icon {{
                font-size: 64px;
                margin-bottom: 16px;
                opacity: 0.5;
            }}
            
            /* Modal styles */
            .modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }}
            
            .modal.show {{
                display: flex;
            }}
            
            .modal-content {{
                background: white;
                border-radius: 16px;
                padding: 32px;
                max-width: 500px;
                width: 90%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: modalSlideIn 0.3s ease;
            }}
            
            @keyframes modalSlideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(-20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .modal-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
            }}
            
            .modal-header h2 {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .modal-close {{
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #64748b;
                padding: 0;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
            }}
            
            .modal-close:hover {{
                background: #f1f5f9;
            }}
            
            .modal-footer {{
                display: flex;
                gap: 12px;
                justify-content: flex-end;
                margin-top: 24px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚙️ Cài Đặt</h1>
            <div class="header-actions">
                <span style="color: #475569; font-weight: 500;">{current_user.display_name or current_user.username}</span>
                <a href="/" class="btn-back">← Về Trang Chủ</a>
            </div>
        </div>
        
        <div class="container">
            <!-- Section 1: Facebook Token -->
            <div class="section">
                <div class="section-title">
                    <span class="icon">🔑</span>
                    <span>Facebook Access Token</span>
                </div>
                
                <div id="tokenStatus" class="token-status not-set">
                    Đang kiểm tra trạng thái token...
                </div>
                
                <div id="tokenInfo" style="display: none; margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Token đã lưu:</strong>
                            <span id="tokenMasked" style="font-family: monospace; color: #64748b; margin-left: 8px;"></span>
                        </div>
                        <button class="btn btn-danger" onclick="deleteToken()" style="padding: 6px 12px; font-size: 12px;">🗑️ Xóa Token</button>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Nhập Facebook Access Token <span id="tokenActionText">mới</span></label>
                    <input type="password" id="tokenInput" placeholder="EAAxxxxxxxxxxxxx" />
                    <small style="color: #64748b; margin-top: 4px; display: block;">Nhập token mới để thay thế token hiện tại</small>
                </div>
                
                <div style="display: flex; gap: 12px;">
                    <button class="btn btn-primary" onclick="saveToken()">💾 <span id="saveTokenText">Lưu Token</span></button>
                    <button class="btn btn-secondary" onclick="testToken()">✅ Kiểm Tra Token</button>
                </div>
                
                <div id="tokenTestResult" style="margin-top: 20px;"></div>
            </div>
            
            <!-- Section 2: Quản Lý Accounts -->
            <div class="section">
                <div class="section-title">
                    <span class="icon">👥</span>
                    <span>Quản Lý Facebook Ad Accounts</span>
                </div>
                
                <div style="display: flex; gap: 12px; margin-bottom: 20px;">
                    <button class="btn btn-success" onclick="syncAccounts()">🔄 Đồng Bộ Từ Facebook</button>
                    <button class="btn btn-primary" onclick="showAddAccountModal()">➕ Thêm Account Thủ Công</button>
                </div>
                
                <div id="accountsTable" class="table-container">
                    <div class="loading">Đang tải...</div>
                </div>
                <div style="margin-top: 12px; padding: 12px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <small style="color: #1e40af;">
                        💡 <strong>Lưu ý:</strong> Chỉ hiển thị 15 tài khoản được sử dụng gần đây nhất (có dữ liệu trong 7 ngày qua hoặc có chi tiêu trong 30 ngày qua).
                    </small>
                </div>
            </div>
            
            <!-- Section 3: Quản Lý Prefixes -->
            <div class="section">
                <div class="section-title">
                    <span class="icon">🏷️</span>
                    <span>Quản Lý Prefixes</span>
                </div>
                
                <div style="display: flex; gap: 12px; margin-bottom: 20px;">
                    <button class="btn btn-primary" onclick="showAddPrefixModal()">➕ Thêm Prefix</button>
                </div>
                
                <div id="prefixesTable" class="table-container">
                    <div class="loading">Đang tải...</div>
                </div>
            </div>
        </div>
        
        <!-- Modal Add/Edit Account -->
        <div id="accountModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="accountModalTitle">Thêm Account</h2>
                    <button class="modal-close" onclick="closeAccountModal()">×</button>
                </div>
                <form id="accountForm" onsubmit="saveAccount(event)">
                    <input type="hidden" id="accountId" />
                    <div class="form-group">
                        <label>Account ID *</label>
                        <input type="text" id="accountAccountId" required placeholder="act_123456789" />
                    </div>
                    <div class="form-group">
                        <label>Tên Account</label>
                        <input type="text" id="accountName" placeholder="Tên hiển thị" />
                    </div>
                    <div class="form-group">
                        <label>Loại Account</label>
                        <select id="accountType">
                            <option value="UNKNOWN">Chưa xác định</option>
                            <option value="E-COMMERCE">E-commerce</option>
                            <option value="LEAD_GENERATION">Lead Generation</option>
                            <option value="MOBILE_APP">Mobile App</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Timezone</label>
                        <input type="text" id="accountTimezone" value="Asia/Ho_Chi_Minh" />
                    </div>
                    <div class="form-group" id="accountPrefixesGroup" style="display: none;">
                        <label>Prefixes (Một account có thể có nhiều prefixes)</label>
                        <div id="accountPrefixesList" style="max-height: 200px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; background: #f8fafc;">
                            <div style="color: #64748b; font-size: 14px;">Đang tải prefixes...</div>
                        </div>
                        <small style="color: #64748b; margin-top: 4px; display: block;">
                            Chọn các prefixes để liên kết với account này. Một prefix có thể được liên kết với nhiều accounts.
                        </small>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeAccountModal()">Hủy</button>
                        <button type="submit" class="btn btn-primary">Lưu</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Modal Add/Edit Prefix -->
        <div id="prefixModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="prefixModalTitle">Thêm Prefix</h2>
                    <button class="modal-close" onclick="closePrefixModal()">×</button>
                </div>
                <form id="prefixForm" onsubmit="savePrefix(event)">
                    <input type="hidden" id="prefixId" />
                    <div class="form-group">
                        <label>Prefix *</label>
                        <input type="text" id="prefixPrefix" required placeholder="FL, PX, TL, etc." maxlength="10" />
                    </div>
                    <div class="form-group">
                        <label>Tên Hiển Thị</label>
                        <input type="text" id="prefixName" placeholder="Tên hiển thị (tùy chọn)" />
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closePrefixModal()">Hủy</button>
                        <button type="submit" class="btn btn-primary">Lưu</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            // Helper function to get token
            function getAuthToken() {{
                return localStorage.getItem('access_token') || getCookie('access_token');
            }}
            
            function getCookie(name) {{
                const value = `; ${{document.cookie}}`;
                const parts = value.split(`; ${{name}}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }}
            
            // Helper function to get headers with auth
            function getAuthHeaders(contentType = 'application/json') {{
                const headers = {{}};
                if (contentType) {{
                    headers['Content-Type'] = contentType;
                }}
                // Cookie will be sent automatically, but we can also send Bearer token
                const token = getAuthToken();
                if (token) {{
                    headers['Authorization'] = `Bearer ${{token}}`;
                }}
                return headers;
            }}
            
            // Load token status
            async function loadTokenStatus() {{
                try {{
                    const response = await fetch('/settings/token/status', {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        throw new Error(`HTTP ${{response.status}}: ${{errorText.substring(0, 100)}}`);
                    }}
                    
                    const data = await response.json();
                    
                    const statusDiv = document.getElementById('tokenStatus');
                    const tokenInfo = document.getElementById('tokenInfo');
                    const tokenMasked = document.getElementById('tokenMasked');
                    const tokenActionText = document.getElementById('tokenActionText');
                    const saveTokenText = document.getElementById('saveTokenText');
                    
                    if (!data.has_token) {{
                        statusDiv.className = 'token-status not-set';
                        statusDiv.textContent = '⚠️ Chưa có token. Vui lòng nhập và lưu token.';
                        tokenInfo.style.display = 'none';
                        tokenActionText.textContent = 'mới';
                        saveTokenText.textContent = 'Lưu Token';
                    }} else {{
                        const statusMap = {{
                            'VALID': {{ class: 'valid', text: '✅ Token hợp lệ và có đủ quyền' }},
                            'INVALID': {{ class: 'invalid', text: '❌ Token không hợp lệ' }},
                            'EXPIRED': {{ class: 'invalid', text: '⏰ Token đã hết hạn' }},
                            'INSUFFICIENT_PERMISSIONS': {{ class: 'invalid', text: '⚠️ Token thiếu quyền' }},
                            'NOT_CHECKED': {{ class: 'not-set', text: '⏳ Chưa kiểm tra token' }}
                        }};
                        const statusInfo = statusMap[data.status] || statusMap['NOT_CHECKED'];
                        statusDiv.className = `token-status ${{statusInfo.class}}`;
                        statusDiv.textContent = statusInfo.text;
                        if (data.last_checked) {{
                            // Format theo timezone Hồ Chí Minh (UTC+7)
                            const date = new Date(data.last_checked);
                            const hcmDate = new Date(date.toLocaleString('en-US', {{ timeZone: 'Asia/Ho_Chi_Minh' }}));
                            const formatted = hcmDate.toLocaleString('vi-VN', {{
                                timeZone: 'Asia/Ho_Chi_Minh',
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                                hour12: false
                            }});
                            statusDiv.textContent += ` (Kiểm tra lần cuối: ${{formatted}})`;
                        }}
                        
                        // Show token info (masked)
                        tokenInfo.style.display = 'block';
                        tokenMasked.textContent = 'EAA••••••••••••••••••••••••••••••••';
                        tokenActionText.textContent = 'mới (thay thế)';
                        saveTokenText.textContent = 'Cập Nhật Token';
                    }}
                }} catch (error) {{
                    console.error('Error loading token status:', error);
                    document.getElementById('tokenStatus').innerHTML = `
                        <div class="token-status invalid">
                            ❌ Lỗi khi tải trạng thái token: ${{error.message}}
                        </div>
                    `;
                }}
            }}
            
            // Delete token
            async function deleteToken() {{
                if (!confirm('Bạn có chắc muốn xóa token? Bạn sẽ cần nhập token mới để sử dụng các tính năng liên quan đến Facebook API.')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch('/settings/token/delete', {{
                        method: 'DELETE',
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        throw new Error(`HTTP ${{response.status}}: ${{errorText.substring(0, 100)}}`);
                    }}
                    
                    const data = await response.json();
                    alert('✅ ' + data.message);
                    loadTokenStatus();
                    document.getElementById('tokenInput').value = '';
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            // Save token
            async function saveToken() {{
                const token = document.getElementById('tokenInput').value.trim();
                if (!token) {{
                    alert('Vui lòng nhập token');
                    return;
                }}
                
                try {{
                    const response = await fetch('/settings/token/save', {{
                        method: 'POST',
                        headers: getAuthHeaders('application/json'),
                        body: JSON.stringify({{ token }})
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMsg = 'Không thể lưu token';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMsg = errorJson.detail || errorMsg;
                        }} catch {{
                            errorMsg = errorText.substring(0, 100);
                        }}
                        alert('❌ Lỗi: ' + errorMsg);
                        return;
                    }}
                    
                    const data = await response.json();
                    alert('✅ ' + (data.message || 'Token đã được lưu thành công!'));
                    document.getElementById('tokenInput').value = '';
                    loadTokenStatus();
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            // Test token
            async function testToken() {{
                const resultDiv = document.getElementById('tokenTestResult');
                resultDiv.innerHTML = '<div class="loading">Đang kiểm tra token...</div>';
                
                try {{
                    const response = await fetch('/settings/token/test', {{
                        method: 'POST',
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMsg = 'Không thể kiểm tra token';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMsg = errorJson.detail || errorMsg;
                        }} catch {{
                            errorMsg = errorText.substring(0, 100);
                        }}
                        resultDiv.innerHTML = `
                            <div class="token-status invalid">
                                <strong>❌ Lỗi:</strong><br>
                                ${{errorMsg}}
                            </div>
                        `;
                        return;
                    }}
                    
                    const data = await response.json();
                    
                    if (data.valid) {{
                        resultDiv.innerHTML = `
                            <div class="token-status valid">
                                <strong>✅ Token hợp lệ!</strong><br>
                                <div style="margin-top: 8px;">
                                    <strong>Thông tin:</strong> ${{data.user_info.name || data.user_info.id}}<br>
                                    <strong>Quyền:</strong> ${{data.permissions.join(', ') || 'N/A'}}<br>
                                    <strong>Trạng thái:</strong> ${{data.message}}
                                </div>
                            </div>
                        `;
                    }} else {{
                        resultDiv.innerHTML = `
                            <div class="token-status invalid">
                                <strong>❌ Token không hợp lệ!</strong><br>
                                <div style="margin-top: 8px;">
                                    <strong>Lỗi:</strong> ${{data.message}}
                                </div>
                            </div>
                        `;
                    }}
                    
                    loadTokenStatus();
                }} catch (error) {{
                    resultDiv.innerHTML = `
                        <div class="token-status invalid">
                            <strong>❌ Lỗi khi kiểm tra token:</strong><br>
                            ${{error.message}}
                        </div>
                    `;
                }}
            }}
            
            // Load accounts
            async function loadAccounts() {{
                try {{
                    const response = await fetch('/settings/accounts', {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        // Try to parse as JSON for error detail
                        let errorMessage = `HTTP ${{response.status}}: Internal Server Error`;
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            // If not JSON, use first 200 chars of error text
                            errorMessage = `HTTP ${{response.status}}: ${{errorText.substring(0, 200)}}`;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const accounts = await response.json();
                    
                    const tableDiv = document.getElementById('accountsTable');
                    if (accounts.length === 0) {{
                        tableDiv.innerHTML = `
                            <div class="empty-state">
                                <div class="icon">📭</div>
                                <div>Chưa có accounts. Hãy đồng bộ từ Facebook hoặc thêm thủ công.</div>
                            </div>
                        `;
                        return;
                    }}
                    
                    let html = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Trạng Thái</th>
                                    <th>Tên Account</th>
                                    <th>Chi Tiêu 30 Ngày</th>
                                    <th>Loại Account</th>
                                    <th>Timezone</th>
                                    <th>Thao Tác</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    accounts.forEach(acc => {{
                        const statusClass = acc.status === 'ACTIVE' ? 'status-active' : 
                                          acc.status === 'PAUSED' ? 'status-paused' : 'status-archived';
                        const typeClass = acc.account_type === 'E-COMMERCE' ? 'type-ecommerce' :
                                        acc.account_type === 'LEAD_GENERATION' ? 'type-lead' :
                                        acc.account_type === 'MOBILE_APP' ? 'type-mobile' : '';
                        const typeText = acc.account_type === 'E-COMMERCE' ? 'E-commerce' :
                                       acc.account_type === 'LEAD_GENERATION' ? 'Lead Generation' :
                                       acc.account_type === 'MOBILE_APP' ? 'Mobile App' : 'Chưa xác định';
                        
                        // Format tiền tệ
                        const currency = acc.currency || 'USD';
                        const spend = acc.last_30_days_spend || 0;
                        let spendDisplay = '';
                        if (currency === 'VND') {{
                            // Chỉ hiển thị VND
                            spendDisplay = `${{Math.round(spend).toLocaleString('vi-VN')}} ₫`;
                        }                        } else {{
                            // USD: hiển thị USD trên, VND dưới
                            // Tỷ giá USD/VND cố định: 26,350
                            const USD_TO_VND_RATE = 26350;
                            const usdAmount = spend.toFixed(2);
                            const vndAmount = Math.round(spend * USD_TO_VND_RATE);
                            spendDisplay = `${{usdAmount}} US$<br><small style="color: #64748b;">(${{vndAmount.toLocaleString('vi-VN')}} ₫)</small>`;
                        }}
                        
                        // Format timezone với GMT offset
                        const timezone = acc.timezone || 'Asia/Ho_Chi_Minh';
                        let timezoneDisplay = timezone;
                        try {{
                            // Tính GMT offset từ timezone
                            const now = new Date();
                            const utcTime = new Date(now.toLocaleString('en-US', {{ timeZone: 'UTC' }}));
                            const localTime = new Date(now.toLocaleString('en-US', {{ timeZone: timezone }}));
                            const offsetMs = localTime - utcTime;
                            const offsetHours = Math.round(offsetMs / (1000 * 60 * 60));
                            const offsetStr = offsetHours >= 0 ? 
                                `+${{offsetHours.toString().padStart(2, '0')}}:00` : 
                                `-${{Math.abs(offsetHours).toString().padStart(2, '0')}}:00`;
                            timezoneDisplay = `${{timezone}} (GMT ${{offsetStr}})`;
                        }} catch (e) {{
                            // Nếu không parse được, dùng timezone gốc
                            timezoneDisplay = timezone;
                        }}
                        
                        const accId = acc.id;
                        html += `
                            <tr>
                                <td><span class="status-badge ${{statusClass}}">${{acc.status}}</span></td>
                                <td><strong>${{acc.account_name || acc.account_id}}</strong><br><small style="color: #64748b;">${{acc.account_id}}</small></td>
                                <td>${{spendDisplay}}</td>
                                <td><span class="account-type-badge ${{typeClass}}">${{typeText}}</span></td>
                                <td>${{timezoneDisplay}}</td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn-icon" style="background: #dcfce7; color: #166534;" onclick="refreshAccount(${{accId}})" title="Refresh account">🔄</button>
                                        <button class="btn-icon" style="background: #dbeafe; color: #1e40af;" onclick="editAccount(${{accId}})" title="Sửa">✏️</button>
                                        <button class="btn-icon" style="background: #fee2e2; color: #991b1b;" onclick="deleteAccount(${{accId}})" title="Xóa">🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }});
                    
                    html += '</tbody></table>';
                    tableDiv.innerHTML = html;
                }} catch (error) {{
                    document.getElementById('accountsTable').innerHTML = `
                        <div class="token-status invalid">Lỗi khi tải accounts: ${{error.message}}</div>
                    `;
                }}
            }}
            
            // Sync accounts from Facebook
            async function syncAccounts() {{
                if (!confirm('Bạn có chắc muốn đồng bộ accounts từ Facebook? Các accounts hiện có sẽ được cập nhật.')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch('/settings/accounts/sync', {{
                        method: 'POST',
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        // Try to parse as JSON for error detail
                        let errorMessage = `HTTP ${{response.status}}: Internal Server Error`;
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            // If not JSON, use first 200 chars of error text
                            errorMessage = `HTTP ${{response.status}}: ${{errorText.substring(0, 200)}}`;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const data = await response.json();
                    alert(`✅ ${{data.message}}`);
                    loadAccounts();
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            // Load prefixes
            async function loadPrefixes() {{
                try {{
                    const response = await fetch('/settings/prefixes', {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        // Try to parse as JSON for error detail
                        let errorMessage = `HTTP ${{response.status}}: Internal Server Error`;
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            // If not JSON, use first 200 chars of error text
                            errorMessage = `HTTP ${{response.status}}: ${{errorText.substring(0, 200)}}`;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const prefixes = await response.json();
                    
                    const tableDiv = document.getElementById('prefixesTable');
                    if (prefixes.length === 0) {{
                        tableDiv.innerHTML = `
                            <div class="empty-state">
                                <div class="icon">🏷️</div>
                                <div>Chưa có prefixes. Hãy thêm prefix mới.</div>
                            </div>
                        `;
                        return;
                    }}
                    
                    let html = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Prefix</th>
                                    <th>Tên Hiển Thị</th>
                                    <th>Trạng Thái</th>
                                    <th>Thao Tác</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    prefixes.forEach(prefix => {{
                        const prefixId = prefix.id;
                        html += `
                            <tr>
                                <td><strong>${{prefix.prefix}}</strong></td>
                                <td>${{prefix.prefix_name || '-'}}</td>
                                <td><span class="status-badge ${{prefix.enabled ? 'status-active' : 'status-paused'}}">${{prefix.enabled ? 'Bật' : 'Tắt'}}</span></td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn-icon" style="background: #dbeafe; color: #1e40af;" onclick="editPrefix(${{prefixId}})" title="Sửa">✏️</button>
                                        <button class="btn-icon" style="background: #fee2e2; color: #991b1b;" onclick="deletePrefix(${{prefixId}})" title="Xóa">🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }});
                    
                    html += '</tbody></table>';
                    tableDiv.innerHTML = html;
                }} catch (error) {{
                    document.getElementById('prefixesTable').innerHTML = `
                        <div class="token-status invalid">Lỗi khi tải prefixes: ${{error.message}}</div>
                    `;
                }}
            }}
            
            // Account Modal Functions
            function showAddAccountModal() {{
                document.getElementById('accountModalTitle').textContent = 'Thêm Account';
                document.getElementById('accountForm').reset();
                document.getElementById('accountId').value = '';
                document.getElementById('accountType').value = 'UNKNOWN';
                document.getElementById('accountTimezone').value = 'Asia/Ho_Chi_Minh';
                document.getElementById('accountPrefixesGroup').style.display = 'none';
                document.getElementById('accountModal').classList.add('show');
            }}
            
            // Load prefixes để chọn trong modal edit account
            async function loadPrefixesForAccount(accountId = null) {{
                try {{
                    // Load tất cả prefixes của user
                    const response = await fetch('/settings/prefixes', {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        console.error('Error loading prefixes');
                        return;
                    }}
                    
                    const allPrefixes = await response.json();
                    const prefixesListDiv = document.getElementById('accountPrefixesList');
                    
                    if (allPrefixes.length === 0) {{
                        prefixesListDiv.innerHTML = '<div style="color: #64748b; font-size: 14px;">Chưa có prefixes. Hãy tạo prefix trước.</div>';
                        return;
                    }}
                    
                    // Nếu đang edit account, load prefixes đã liên kết
                    let linkedPrefixIds = [];
                    if (accountId) {{
                        try {{
                            const linkedResponse = await fetch('/settings/accounts/' + accountId + '/prefixes', {{
                                headers: getAuthHeaders()
                            }});
                            if (linkedResponse.ok) {{
                                const linkedPrefixes = await linkedResponse.json();
                                linkedPrefixIds = linkedPrefixes.map(p => p.id);
                            }}
                        }} catch (e) {{
                            console.error('Error loading linked prefixes:', e);
                        }}
                    }}
                    
                    // Render checkboxes
                    let html = '';
                    allPrefixes.forEach(prefix => {{
                        const isChecked = linkedPrefixIds.includes(prefix.id);
                        const prefixName = prefix.prefix_name || '';
                        const prefixNameHtml = prefixName ? '<br><small style="color: #64748b;">' + prefixName + '</small>' : '';
                        const prefixId = prefix.id;
                        const prefixValue = prefix.prefix;
                        const checkedAttr = isChecked ? 'checked' : '';
                        html += `
                            <label style="display: flex; align-items: center; padding: 8px; border-radius: 4px; cursor: pointer; margin-bottom: 4px; background: white; border: 1px solid #e2e8f0;">
                                <input type="checkbox" value="${{prefixId}}" ${{checkedAttr}} 
                                    style="margin-right: 8px; width: 18px; height: 18px; cursor: pointer;">
                                <div>
                                    <strong>${{prefixValue}}</strong>
                                    ${{prefixNameHtml}}
                                </div>
                            </label>
                        `;
                    }});
                    prefixesListDiv.innerHTML = html;
                }} catch (error) {{
                    console.error('Error loading prefixes for account:', error);
                    document.getElementById('accountPrefixesList').innerHTML = 
                        '<div style="color: #ef4444; font-size: 14px;">Lỗi khi tải prefixes</div>';
                }}
            }}
            
            function closeAccountModal() {{
                document.getElementById('accountModal').classList.remove('show');
            }}
            
            async function refreshAccount(id) {{
                if (!confirm('Bạn có chắc muốn refresh account này? Thông tin sẽ được cập nhật từ Facebook API.')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch('/settings/accounts/' + id + '/refresh', {{
                        method: 'POST',
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMessage = `HTTP ${{response.status}}: Internal Server Error`;
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            errorMessage = `HTTP ${{response.status}}: ${{errorText.substring(0, 200)}}`;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const data = await response.json();
                    alert('✅ ' + data.message);
                    loadAccounts();
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            async function editAccount(id) {{
                try {{
                    const response = await fetch('/settings/accounts/' + id, {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMessage = `HTTP ${{response.status}}: Internal Server Error`;
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            errorMessage = `HTTP ${{response.status}}: ${{errorText.substring(0, 200)}}`;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const account = await response.json();
                    document.getElementById('accountModalTitle').textContent = 'Sửa Account';
                    document.getElementById('accountId').value = account.id;
                    document.getElementById('accountAccountId').value = account.account_id;
                    document.getElementById('accountName').value = account.account_name || '';
                    document.getElementById('accountType').value = account.account_type || 'UNKNOWN';
                    document.getElementById('accountTimezone').value = account.timezone || 'Asia/Ho_Chi_Minh';
                    
                    // Hiển thị phần chọn prefixes và load prefixes
                    document.getElementById('accountPrefixesGroup').style.display = 'block';
                    await loadPrefixesForAccount(id);
                    
                    document.getElementById('accountModal').classList.add('show');
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            async function saveAccount(event) {{
                event.preventDefault();
                const id = document.getElementById('accountId').value;
                const accountData = {{
                    account_id: document.getElementById('accountAccountId').value.trim(),
                    account_name: document.getElementById('accountName').value.trim() || null,
                    account_type: document.getElementById('accountType').value,
                    timezone: document.getElementById('accountTimezone').value.trim(),
                    enabled: true
                }};
                
                try {{
                    let response;
                    if (id) {{
                        // Update account
                        const accountId = ${{id}};
                        response = await fetch('/settings/accounts/' + accountId, {{
                            method: 'PUT',
                            headers: getAuthHeaders('application/json'),
                            body: JSON.stringify(accountData)
                        }});
                        
                        if (response.ok) {{
                            // Update Account-Prefix links
                            const checkboxes = document.querySelectorAll('#accountPrefixesList input[type="checkbox"]');
                            const selectedPrefixIds = Array.from(checkboxes)
                                .filter(cb => cb.checked)
                                .map(cb => parseInt(cb.value));
                            
                            // Get current linked prefixes
                            const accountId = ${{id}};
                            const currentResponse = await fetch('/settings/accounts/' + accountId + '/prefixes', {{
                                headers: getAuthHeaders()
                            }});
                            let currentPrefixIds = [];
                            if (currentResponse.ok) {{
                                const currentPrefixes = await currentResponse.json();
                                currentPrefixIds = currentPrefixes.map(p => p.id);
                            }}
                            
                            // Add new links
                            for (const prefixId of selectedPrefixIds) {{
                                if (!currentPrefixIds.includes(prefixId)) {{
                                    try {{
                                        await fetch('/settings/accounts/' + accountId + '/prefixes/' + prefixId, {{
                                            method: 'POST',
                                            headers: getAuthHeaders()
                                        }});
                                    }} catch (e) {{
                                        console.error('Error linking prefix:', e);
                                    }}
                                }}
                            }}
                            
                            // Remove unselected links
                            for (const prefixId of currentPrefixIds) {{
                                if (!selectedPrefixIds.includes(prefixId)) {{
                                    try {{
                                        await fetch('/settings/accounts/' + accountId + '/prefixes/' + prefixId, {{
                                            method: 'DELETE',
                                            headers: getAuthHeaders()
                                        }});
                                    }} catch (e) {{
                                        console.error('Error unlinking prefix:', e);
                                    }}
                                }}
                            }}
                            
                            alert('✅ Đã cập nhật account và prefixes thành công!');
                            closeAccountModal();
                            loadAccounts();
                        }} else {{
                            const error = await response.json();
                            alert('❌ Lỗi: ' + (error.detail || 'Không thể lưu account'));
                        }}
                    }} else {{
                        // Create new account
                        response = await fetch('/settings/accounts', {{
                            method: 'POST',
                            headers: getAuthHeaders('application/json'),
                            body: JSON.stringify(accountData)
                        }});
                        
                        if (response.ok) {{
                            alert('✅ Đã thêm account thành công!');
                            closeAccountModal();
                            loadAccounts();
                        }} else {{
                            const error = await response.json();
                            alert('❌ Lỗi: ' + (error.detail || 'Không thể lưu account'));
                        }}
                    }}
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            async function deleteAccount(id) {{
                if (!confirm('Bạn có chắc muốn xóa account này? Tất cả các liên kết với prefixes cũng sẽ bị xóa.')) return;
                
                try {{
                    const response = await fetch('/settings/accounts/' + id, {{
                        method: 'DELETE',
                        headers: getAuthHeaders()
                    }});
                    
                    if (response.ok || response.status === 204) {{
                        alert('✅ Đã xóa account thành công!');
                        loadAccounts();
                    }} else {{
                        const error = await response.json();
                        alert('❌ Lỗi: ' + (error.detail || 'Không thể xóa account'));
                    }}
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            // Prefix Modal Functions
            function showAddPrefixModal() {{
                document.getElementById('prefixModalTitle').textContent = 'Thêm Prefix';
                document.getElementById('prefixForm').reset();
                document.getElementById('prefixId').value = '';
                document.getElementById('prefixModal').classList.add('show');
            }}
            
            function closePrefixModal() {{
                document.getElementById('prefixModal').classList.remove('show');
            }}
            
            async function editPrefix(id) {{
                try {{
                    const response = await fetch('/settings/prefixes/' + id, {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMessage = `HTTP ${{response.status}}: Internal Server Error`;
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            errorMessage = `HTTP ${{response.status}}: ${{errorText.substring(0, 200)}}`;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const prefix = await response.json();
                    document.getElementById('prefixModalTitle').textContent = 'Sửa Prefix';
                    document.getElementById('prefixId').value = prefix.id;
                    document.getElementById('prefixPrefix').value = prefix.prefix;
                    document.getElementById('prefixName').value = prefix.prefix_name || '';
                    document.getElementById('prefixModal').classList.add('show');
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            async function savePrefix(event) {{
                event.preventDefault();
                const id = document.getElementById('prefixId').value;
                const prefixData = {{
                    prefix: document.getElementById('prefixPrefix').value.trim().toUpperCase(),
                    prefix_name: document.getElementById('prefixName').value.trim() || null,
                    enabled: true
                }};
                
                try {{
                    let response;
                    if (id) {{
                        // Update
                        const prefixId = ${{id}};
                        response = await fetch('/settings/prefixes/' + prefixId, {{
                            method: 'PUT',
                            headers: getAuthHeaders('application/json'),
                            body: JSON.stringify(prefixData)
                        }});
                    }} else {{
                        // Create
                        response = await fetch('/settings/prefixes', {{
                            method: 'POST',
                            headers: getAuthHeaders('application/json'),
                            body: JSON.stringify(prefixData)
                        }});
                    }}
                    
                    if (response.ok) {{
                        alert('✅ ' + (id ? 'Đã cập nhật' : 'Đã thêm') + ' prefix thành công!');
                        closePrefixModal();
                        loadPrefixes();
                    }} else {{
                        const error = await response.json();
                        alert('❌ Lỗi: ' + (error.detail || 'Không thể lưu prefix'));
                    }}
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            async function deletePrefix(id) {{
                if (!confirm('Bạn có chắc muốn xóa prefix này? Tất cả các liên kết với accounts cũng sẽ bị xóa.')) return;
                
                try {{
                    const response = await fetch('/settings/prefixes/' + id, {{
                        method: 'DELETE',
                        headers: getAuthHeaders()
                    }});
                    
                    if (response.ok || response.status === 204) {{
                        alert('✅ Đã xóa prefix thành công!');
                        loadPrefixes();
                    }} else {{
                        const error = await response.json();
                        alert('❌ Lỗi: ' + (error.detail || 'Không thể xóa prefix'));
                    }}
                }} catch (error) {{
                    alert('❌ Lỗi: ' + error.message);
                }}
            }}
            
            // Close modal when clicking outside
            window.onclick = function(event) {{
                const accountModal = document.getElementById('accountModal');
                const prefixModal = document.getElementById('prefixModal');
                if (event.target === accountModal) {{
                    closeAccountModal();
                }}
                if (event.target === prefixModal) {{
                    closePrefixModal();
                }}
            }}
            
            // Load data on page load
            loadTokenStatus();
            loadAccounts();
            loadPrefixes();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

