# -*- coding: utf-8 -*-
"""
Settings API Routes - Quản lý token Facebook, accounts, và prefixes cho mỗi user
"""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging
import threading
import time

from app.core.database import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.account_prefix import Account, Prefix, AccountPrefix
from app.core.security import encrypt_token, decrypt_token
from app.services.facebook_token_service import (
    test_facebook_token, 
    fetch_facebook_ad_accounts, 
    fetch_account_30_days_spend, 
    check_account_has_activity_last_7_days,
    check_account_has_activity_from_token_owner_or_bm
)
from app.api.routes.auth import get_current_user_optional
from app.services.telegram_token_service import test_telegram_bot_token
from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message
import requests
import re

router = APIRouter(prefix="/settings", tags=["settings"])
logger = logging.getLogger(__name__)

# In-memory storage for sync progress (per user)
# Format: {user_id: {"status": "running"|"completed"|"error", "progress": 0-100, "current": 0, "total": 0, "message": ""}}
sync_progress: Dict[int, Dict[str, Any]] = {}
sync_progress_lock = threading.Lock()


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
    enabled: bool = False  # Accounts thêm thủ công mặc định tắt logic tự động


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


class TelegramBotSaveRequest(BaseModel):
    bot_token: str
    chat_id: str


class TelegramBotTestResponse(BaseModel):
    valid: bool
    status: str
    message: str
    bot_info: Optional[Dict[str, Any]] = None
    chat_info: Optional[Dict[str, Any]] = None


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
    
    # Update status và lưu token owner name
    user_settings.token_status = test_result["status"]
    user_settings.token_last_checked = datetime.now()
    # Lưu tên của người tạo token để dùng cho activity log tracking
    if test_result.get("user_info", {}).get("name"):
        user_settings.token_owner_name = test_result["user_info"]["name"]
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


# ==================== TELEGRAM BOT ENDPOINTS ====================

@router.post("/telegram/save")
def save_telegram_bot(
    telegram_request: TelegramBotSaveRequest,
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lưu Telegram Bot Token và Chat ID cho user (encrypted)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Test token và chat ID trước khi lưu
    test_result = test_telegram_bot_token(telegram_request.bot_token, telegram_request.chat_id)
    if not test_result["valid"]:
        raise HTTPException(status_code=400, detail=test_result["message"])
    
    # Get or create user settings
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.add(user_settings)
    
    # Encrypt và lưu bot token
    user_settings.telegram_bot_token_encrypted = encrypt_token(telegram_request.bot_token)
    user_settings.telegram_chat_id = telegram_request.chat_id
    user_settings.telegram_bot_status = "VALID"
    user_settings.telegram_bot_last_checked = datetime.now()
    user_settings.updated_at = datetime.now()
    
    db.commit()
    db.refresh(user_settings)
    
    return {
        "success": True,
        "message": "Đã lưu Telegram Bot Token và Chat ID thành công",
        "bot_info": test_result.get("bot_info"),
        "chat_info": test_result.get("chat_info")
    }


@router.post("/telegram/test", response_model=TelegramBotTestResponse)
def test_telegram_bot(
    telegram_request: TelegramBotSaveRequest,
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Test Telegram Bot Token và Chat ID"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    test_result = test_telegram_bot_token(telegram_request.bot_token, telegram_request.chat_id)
    
    return TelegramBotTestResponse(**test_result)


@router.get("/telegram/status")
def get_telegram_bot_status(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy trạng thái Telegram Bot Token và Chat ID"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not user_settings or not user_settings.telegram_bot_token_encrypted:
        return {
            "status": "NOT_SET",
            "message": "Chưa cấu hình Telegram Bot",
            "bot_token_set": False,
            "chat_id_set": False,
            "last_checked": None
        }
    
    try:
        bot_token = decrypt_token(user_settings.telegram_bot_token_encrypted)
        bot_token_masked = bot_token[:10] + "..." + bot_token[-5:] if len(bot_token) > 15 else "***"
    except Exception as e:
        logger.error(f"Error decrypting Telegram bot token: {e}")
        return {
            "status": "ERROR",
            "message": "Lỗi khi giải mã Bot Token",
            "bot_token_set": True,
            "chat_id_set": bool(user_settings.telegram_chat_id),
            "last_checked": user_settings.telegram_bot_last_checked.isoformat() if user_settings.telegram_bot_last_checked else None
        }
    
    # Format last checked time in Ho Chi Minh timezone
    last_checked_str = None
    if user_settings.telegram_bot_last_checked:
        import pytz
        hcm_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        last_checked_utc = user_settings.telegram_bot_last_checked
        if last_checked_utc.tzinfo is None:
            last_checked_utc = pytz.UTC.localize(last_checked_utc)
        last_checked_hcm = last_checked_utc.astimezone(hcm_tz)
        last_checked_str = last_checked_hcm.strftime("%H:%M:%S %d/%m/%Y")
    
    return {
        "status": user_settings.telegram_bot_status,
        "message": f"Bot Token đã được cấu hình (Kiểm tra lần cuối: {last_checked_str})" if last_checked_str else "Bot Token đã được cấu hình",
        "bot_token_set": True,
        "bot_token_masked": bot_token_masked,
        "chat_id_set": bool(user_settings.telegram_chat_id),
        "chat_id": user_settings.telegram_chat_id if user_settings.telegram_chat_id else None,
        "last_checked": last_checked_str
    }


@router.delete("/telegram/delete")
def delete_telegram_bot(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa Telegram Bot Token và Chat ID"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings or not user_settings.telegram_bot_token_encrypted:
        raise HTTPException(status_code=404, detail="Chưa có Telegram Bot Token để xóa")
    
    user_settings.telegram_bot_token_encrypted = None
    user_settings.telegram_chat_id = None
    user_settings.telegram_bot_status = "NOT_SET"
    user_settings.telegram_bot_last_checked = None
    db.commit()
    
    return {"message": "Telegram Bot Token và Chat ID đã được xóa thành công"}


# ==================== ACCOUNTS ENDPOINTS ====================

@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    limit: int = 100  # Tăng limit để hiển thị tất cả accounts
):
    """
    Lấy danh sách accounts của user từ database
    KHÔNG gọi Facebook API để tránh chậm khi load page
    Chỉ đọc từ database - nhanh và hiệu quả
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        # Lấy tất cả accounts của user từ database
        accounts = db.query(Account).filter(
            Account.user_id == current_user.id
        ).all()
        
        # Sắp xếp: enabled trước, sau đó theo last_30_days_spend, cuối cùng theo tên
        accounts.sort(
            key=lambda x: (
                not x.enabled,  # enabled=True trước
                -(x.last_30_days_spend or 0),  # spend cao trước
                x.account_name or ''  # tên alphabetically
            )
        )
        
        # Trả về tất cả accounts (không giới hạn để user thấy hết)
        return accounts
        
    except Exception as e:
        logger.error(f"Error listing accounts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách accounts: {str(e)}")


def _sync_accounts_background(user_id: int, token: str):
    """Background task để sync accounts - chạy trong thread riêng"""
    from app.core.database import get_db_session
    
    db = get_db_session()
    try:
        # Initialize progress
        with sync_progress_lock:
            sync_progress[user_id] = {
                "status": "running",
                "progress": 0,
                "current": 0,
                "total": 0,
                "message": "Đang lấy danh sách accounts từ Facebook..."
            }
        
        # Fetch accounts from Facebook
        try:
            fb_accounts = fetch_facebook_ad_accounts(token)
            total = len(fb_accounts)
            
            with sync_progress_lock:
                sync_progress[user_id]["total"] = total
                sync_progress[user_id]["message"] = f"Đã lấy {total} accounts. Đang đồng bộ..."
        except Exception as e:
            logger.error(f"Error fetching accounts from Facebook: {e}", exc_info=True)
            with sync_progress_lock:
                sync_progress[user_id] = {
                    "status": "error",
                    "progress": 0,
                    "current": 0,
                    "total": 0,
                    "message": f"Lỗi khi lấy accounts từ Facebook: {str(e)}"
                }
            return
        
        # Sync to database
        synced_count = 0
        updated_count = 0
        
        for idx, fb_acc in enumerate(fb_accounts):
            try:
                # Update progress
                progress = int((idx + 1) / total * 100)
                with sync_progress_lock:
                    sync_progress[user_id]["progress"] = progress
                    sync_progress[user_id]["current"] = idx + 1
                    sync_progress[user_id]["message"] = f"Đang đồng bộ account {idx + 1}/{total}: {fb_acc.get('name', fb_acc.get('account_id', 'Unknown'))}"
                
                # Check if account exists
                existing = db.query(Account).filter(
                    Account.user_id == user_id,
                    Account.account_id == fb_acc["account_id"]
                ).first()
                
                if existing:
                    # Update existing
                    existing.account_name = fb_acc["name"]
                    existing.status = "ACTIVE" if fb_acc["account_status"] == 1 else "PAUSED"
                    existing.timezone = fb_acc["timezone_name"]
                    existing.currency = fb_acc.get("currency", "USD")
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
                        user_id=user_id,
                        account_id=fb_acc["account_id"],
                        account_name=fb_acc["name"],
                        status="ACTIVE" if fb_acc["account_status"] == 1 else "PAUSED",
                        timezone=fb_acc["timezone_name"],
                        currency=fb_acc.get("currency", "USD"),
                        account_type="UNKNOWN",
                        enabled=True  # Accounts sync từ Facebook mặc định enabled=True
                    )
                    # Try to get 30 days spend
                    try:
                        new_account.last_30_days_spend = fetch_account_30_days_spend(token, fb_acc["id"])
                    except Exception as spend_error:
                        logger.warning(f"Could not fetch spend for account {fb_acc['account_id']}: {spend_error}")
                    db.add(new_account)
                    synced_count += 1
                
                # Thêm delay nhỏ giữa các requests để tránh rate limit của Facebook API
                # Delay 200ms giữa mỗi account để đảm bảo an toàn
                if idx < total - 1:  # Không delay sau account cuối cùng
                    time.sleep(0.2)
                    
            except Exception as acc_error:
                logger.error(f"Error syncing account {fb_acc.get('account_id', 'unknown')}: {acc_error}", exc_info=True)
                continue
        
        db.commit()
        
        # Mark as completed
        with sync_progress_lock:
            sync_progress[user_id] = {
                "status": "completed",
                "progress": 100,
                "current": total,
                "total": total,
                "message": f"Hoàn thành! Đã sync {synced_count} accounts mới, cập nhật {updated_count} accounts."
            }
    except Exception as e:
        logger.error(f"Error in sync_accounts_background: {e}", exc_info=True)
        with sync_progress_lock:
            sync_progress[user_id] = {
                "status": "error",
                "progress": 0,
                "current": 0,
                "total": 0,
                "message": f"Lỗi khi đồng bộ: {str(e)}"
            }
    finally:
        db.close()


@router.post("/accounts/sync")
def sync_accounts(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Sync accounts từ Facebook API - chạy trong background để tránh timeout"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Check if sync is already running
    with sync_progress_lock:
        if current_user.id in sync_progress:
            current_status = sync_progress[current_user.id].get("status")
            if current_status == "running":
                raise HTTPException(status_code=400, detail="Đang trong quá trình đồng bộ. Vui lòng đợi hoàn thành.")
    
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
        
        # Start background task
        background_tasks.add_task(_sync_accounts_background, current_user.id, token)
        
        return {
            "message": "Đã bắt đầu quá trình đồng bộ. Vui lòng theo dõi tiến trình ở bên dưới.",
            "status": "started"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi bắt đầu đồng bộ: {str(e)}")


@router.get("/accounts/sync/progress")
def get_sync_progress(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Lấy tiến trình đồng bộ accounts"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    with sync_progress_lock:
        progress = sync_progress.get(current_user.id, {
            "status": "idle",
            "progress": 0,
            "current": 0,
            "total": 0,
            "message": "Chưa có quá trình đồng bộ nào"
        })
    
    return progress


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
    
    # Accounts thêm thủ công mặc định enabled=False (không áp dụng logic tự động)
    account_dict = account_data.dict()
    account_dict['enabled'] = False  # Đảm bảo accounts thêm thủ công luôn tắt logic tự động
    
    account = Account(
        user_id=current_user.id,
        **account_dict
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


@router.patch("/accounts/{account_id}/toggle-enabled")
def toggle_account_enabled(
    request: Request,
    account_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Bật/tắt account (enabled/disabled) - ảnh hưởng đến việc áp dụng logic tự động"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == current_user.id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account không tồn tại")
        
        account.enabled = not account.enabled
        db.commit()
        db.refresh(account)
        
        status_text = "bật" if account.enabled else "tắt"
        return {
            "message": f"Đã {status_text} account thành công",
            "enabled": account.enabled
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling account enabled: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi bật/tắt account: {str(e)}")


@router.patch("/accounts/{account_id}/type")
async def update_account_type(
    account_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Cập nhật account type inline"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        body = await request.json()
        account_type = body.get("account_type")
        
        if not account_type:
            raise HTTPException(status_code=400, detail="Missing account_type in request body")
        
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == current_user.id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate account_type
        valid_types = ["UNKNOWN", "E-COMMERCE", "LEAD_GENERATION", "MOBILE_APP"]
        if account_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid account type. Must be one of: {', '.join(valid_types)}")
        
        account.account_type = account_type
        account.updated_at = datetime.now()
        db.commit()
        db.refresh(account)
        
        return {"message": "Đã cập nhật loại account thành công", "account_type": account.account_type}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account type: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật loại account: {str(e)}")


@router.post("/accounts/fetch-info")
async def fetch_account_info(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy thông tin account từ Facebook API (name, timezone) - dùng khi thêm account mới"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    try:
        body = await request.json()
        account_id = body.get("account_id")
        
        if not account_id:
            raise HTTPException(status_code=400, detail="Missing account_id in request body")
        
        # Get token
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not user_settings or not user_settings.facebook_token_encrypted:
            raise HTTPException(status_code=404, detail="Chưa có token. Vui lòng lưu token trước.")
        
        try:
            token = decrypt_token(user_settings.facebook_token_encrypted)
        except Exception as e:
            logger.error(f"Error decrypting token: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Lỗi giải mã token: {str(e)}")
        
        # Normalize account_id
        account_id_for_api = account_id
        if not account_id_for_api.startswith("act_"):
            account_id_for_api = f"act_{account_id_for_api}"
        
        # Fetch account info from Facebook API
        try:
            import requests
            from app.services.facebook_token_service import FB_GRAPH_API_BASE
            
            url = f"{FB_GRAPH_API_BASE}/{account_id_for_api}"
            params = {
                "fields": "id,name,account_id,timezone_name",
                "access_token": token
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            # Parse error response từ Facebook API
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_info = error_data['error']
                        error_message = error_info.get('message', 'Unknown error')
                        error_code = error_info.get('code', 0)
                        error_type = error_info.get('type', 'Unknown')
                        
                        # Map common error codes to user-friendly messages
                        if error_code == 190:
                            error_message = "Token không hợp lệ hoặc đã hết hạn"
                        elif error_code == 200:
                            error_message = f"Không có quyền truy cập tài khoản này: {error_message}"
                        elif error_code == 100:
                            error_message = f"Account ID không hợp lệ: {error_message}"
                        
                        raise HTTPException(
                            status_code=400,
                            detail=f"Facebook API error ({error_type}, Code {error_code}): {error_message}"
                        )
                    else:
                        raise HTTPException(status_code=400, detail=f"HTTP {response.status_code}: {response.text[:200]}")
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"HTTP {response.status_code}: {response.text[:200]}")
            
            data = response.json()
            if 'error' in data:
                error_info = data['error']
                error_message = error_info.get('message', 'Unknown error')
                error_code = error_info.get('code', 0)
                error_type = error_info.get('type', 'Unknown')
                
                if error_code == 190:
                    error_message = "Token không hợp lệ hoặc đã hết hạn"
                elif error_code == 200:
                    error_message = f"Không có quyền truy cập tài khoản này: {error_message}"
                elif error_code == 100:
                    error_message = f"Account ID không hợp lệ: {error_message}"
                
                raise HTTPException(
                    status_code=400,
                    detail=f"Facebook API error ({error_type}, Code {error_code}): {error_message}"
                )
            
            return {
                "account_id": data.get('account_id') or data.get('id', account_id),
                "name": data.get('name', ''),
                "timezone": data.get('timezone_name', 'Asia/Ho_Chi_Minh')
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching account info from Facebook: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Lỗi khi lấy thông tin từ Facebook: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fetch_account_info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin account: {str(e)}")


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
            
            # Normalize account_id: đảm bảo có prefix "act_"
            account_id_for_api = account.account_id
            if not account_id_for_api.startswith("act_"):
                account_id_for_api = f"act_{account_id_for_api}"
            
            # Chỉ lấy các field cơ bản và cần thiết (tránh lỗi 400 do field không hợp lệ)
            url = f"{FB_GRAPH_API_BASE}/{account_id_for_api}"
            params = {
                "fields": "id,name,account_id,account_status,currency,timezone_name",
                "access_token": token
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            # Parse error response từ Facebook API
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_info = error_data['error']
                        error_message = error_info.get('message', 'Unknown error')
                        error_code = error_info.get('code', 0)
                        error_type = error_info.get('type', 'Unknown')
                        raise Exception(f"Facebook API error ({error_type}, Code {error_code}): {error_message}")
                    else:
                        raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
                except ValueError:
                    # Nếu không parse được JSON
                    raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
            
            data = response.json()
            if 'error' in data:
                error_info = data['error']
                error_message = error_info.get('message', 'Unknown error')
                error_code = error_info.get('code', 0)
                error_type = error_info.get('type', 'Unknown')
                raise Exception(f"Facebook API error ({error_type}, Code {error_code}): {error_message}")
            
            # Update account info
            account.account_name = data.get('name', account.account_name)
            account.status = "ACTIVE" if data.get('account_status', 1) == 1 else "PAUSED"
            account.timezone = data.get('timezone_name', account.timezone)
            account.currency = data.get('currency', account.currency or 'USD')
            account.updated_at = datetime.now()
            
            # Try to get 30 days spend
            try:
                from app.services.facebook_token_service import fetch_account_30_days_spend
                # Dùng account_id đã normalize
                account.last_30_days_spend = fetch_account_30_days_spend(token, account_id_for_api)
            except Exception as spend_error:
                logger.warning(f"Could not fetch spend for account {account.account_id}: {spend_error}")
            
            db.commit()
            db.refresh(account)
            
            return {
                "message": "Đã cập nhật thông tin account thành công",
                "account": account
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing account from Facebook: {e}", exc_info=True)
            error_msg = str(e)
            # Nếu là lỗi từ Facebook API, giữ nguyên message
            if "Facebook API error" in error_msg or "HTTP" in error_msg:
                raise HTTPException(status_code=400, detail=f"Lỗi khi lấy thông tin từ Facebook: {error_msg}")
            else:
                raise HTTPException(status_code=400, detail=f"Lỗi khi lấy thông tin từ Facebook: {error_msg}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_account: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi refresh account: {str(e)}")


@router.delete("/accounts/all", status_code=200)
def delete_all_accounts(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Xóa tất cả accounts của user hiện tại"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Lấy tất cả accounts của user
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    if not accounts:
        return {"message": "Không có accounts nào để xóa", "deleted_count": 0}
    
    # Xóa tất cả account-prefix links
    account_ids = [acc.id for acc in accounts]
    db.query(AccountPrefix).filter(AccountPrefix.account_id.in_(account_ids)).delete(synchronize_session=False)
    
    # Xóa tất cả accounts
    deleted_count = len(accounts)
    for account in accounts:
        db.delete(account)
    
    db.commit()
    
    return {"message": f"Đã xóa {deleted_count} accounts thành công", "deleted_count": deleted_count}


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
    
    # Check if user is locked
    if not current_user.is_active:
        return HTMLResponse(content=get_account_locked_message())
    
    user_menu = get_user_dropdown_menu(current_user)
    
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
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 100px 16px 40px;
                }}
                
                .section {{
                    padding: 24px;
                }}
                
                .section-title {{
                    font-size: 20px;
                }}
                
                .header {{
                    padding: 12px 16px;
                }}
                
                .header h1 {{
                    font-size: 20px;
                }}
                
                table {{
                    font-size: 12px;
                }}
                
                th, td {{
                    padding: 8px;
                }}
                
                .action-buttons {{
                    flex-direction: column;
                }}
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
            
            /* Toggle Switch */
            .toggle-switch {{
                position: relative;
                display: inline-block;
                width: 44px;
                height: 24px;
                cursor: pointer;
            }}
            
            .toggle-switch input {{
                opacity: 0;
                width: 0;
                height: 0;
            }}
            
            .toggle-slider {{
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #cbd5e1;
                transition: .3s;
                border-radius: 24px;
            }}
            
            .toggle-slider:before {{
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .3s;
                border-radius: 50%;
            }}
            
            .toggle-switch input:checked + .toggle-slider {{
                background-color: #10b981;
            }}
            
            .toggle-switch input:checked + .toggle-slider:before {{
                transform: translateX(20px);
            }}
            
            .toggle-switch input:disabled + .toggle-slider {{
                opacity: 0.5;
                cursor: not-allowed;
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
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 16px;
            }}
            
            .loading::before {{
                content: '';
                width: 40px;
                height: 40px;
                border: 4px solid #e2e8f0;
                border-top-color: #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }}
            
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            
            /* Skeleton Loader */
            .skeleton {{
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s ease-in-out infinite;
                border-radius: 4px;
            }}
            
            @keyframes loading {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
            
            .skeleton-row {{
                height: 48px;
                margin-bottom: 12px;
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
            
            .empty-state h3 {{
                font-size: 18px;
                font-weight: 600;
                color: #475569;
                margin-bottom: 8px;
            }}
            
            .empty-state p {{
                font-size: 14px;
                color: #64748b;
                margin-bottom: 20px;
            }}
            
            /* Button disabled state */
            .btn:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
                pointer-events: none;
            }}
            
            .btn.loading {{
                position: relative;
                color: transparent;
            }}
            
            .btn.loading::after {{
                content: '';
                position: absolute;
                width: 16px;
                height: 16px;
                top: 50%;
                left: 50%;
                margin-left: -8px;
                margin-top: -8px;
                border: 2px solid #ffffff;
                border-top-color: transparent;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
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
            
            /* Toast Notification Styles */
            .toast-container {{
                position: fixed;
                top: 100px;
                right: 32px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            
            .toast {{
                background: white;
                border-radius: 12px;
                padding: 16px 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: center;
                gap: 12px;
                min-width: 300px;
                max-width: 500px;
                animation: toastSlideIn 0.3s ease;
                border-left: 4px solid #667eea;
            }}
            
            .toast.success {{
                border-left-color: #10b981;
            }}
            
            .toast.error {{
                border-left-color: #ef4444;
            }}
            
            .toast.warning {{
                border-left-color: #f59e0b;
            }}
            
            .toast.info {{
                border-left-color: #3b82f6;
            }}
            
            @keyframes toastSlideIn {{
                from {{
                    transform: translateX(400px);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}
            
            .toast-icon {{
                font-size: 24px;
                flex-shrink: 0;
            }}
            
            .toast-content {{
                flex: 1;
            }}
            
            .toast-title {{
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 4px;
            }}
            
            .toast-message {{
                font-size: 14px;
                color: #64748b;
            }}
            
            .toast-close {{
                background: none;
                border: none;
                font-size: 20px;
                color: #94a3b8;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 4px;
                flex-shrink: 0;
            }}
            
            .toast-close:hover {{
                background: #f1f5f9;
                color: #475569;
            }}
            
            /* Inline dropdown for account type */
            .account-type-select {{
                padding: 4px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                background: white;
                transition: all 0.2s;
            }}
            
            .account-type-select:hover {{
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .account-type-select:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚙️ Cài Đặt</h1>
            <div class="header-actions">
                {user_menu}
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
                    <!-- Tạm thời ẩn nút đồng bộ, chỉ dùng thêm thủ công -->
                    <!-- <button class="btn btn-success" onclick="syncAccounts()">🔄 Đồng Bộ Từ Facebook</button> -->
                    <button class="btn btn-primary" onclick="showAddAccountModal()">➕ Thêm Account Thủ Công</button>
                    <button class="btn btn-danger" onclick="deleteAllAccounts()">🗑️ Xóa Tất Cả Accounts</button>
                </div>
                
                <!-- Progress indicator for sync -->
                <div id="syncProgressContainer" style="display: none; margin-bottom: 20px;"></div>
                
                <div id="accountsTable" class="table-container">
                    <div class="loading">Đang tải...</div>
                </div>
                <div style="margin-top: 12px; padding: 12px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <small style="color: #1e40af;">
                        💡 <strong>Lưu ý:</strong> Hiện tại chỉ hỗ trợ thêm tài khoản thủ công. Tài khoản thêm thủ công mặc định tắt logic tự động (enabled=False) để tránh lỗi. Sử dụng toggle bên cạnh trạng thái để bật/tắt áp dụng logic tự động. Nút xóa để xóa các tài khoản không sử dụng.
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
            
            <!-- Section 4: Telegram Bot -->
            <div class="section">
                <div class="section-title">
                    <span class="icon">📱</span>
                    <span>Telegram Bot</span>
                </div>
                
                <div id="telegramStatus" class="token-status not-set">
                    Đang kiểm tra trạng thái...
                </div>
                
                <div id="telegramInfo" style="display: none; margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Bot Token đã lưu:</strong>
                            <span id="telegramTokenMasked" style="font-family: monospace; color: #64748b; margin-left: 8px;"></span>
                            <br>
                            <strong>Chat ID:</strong>
                            <span id="telegramChatId" style="font-family: monospace; color: #64748b; margin-left: 8px;"></span>
                        </div>
                        <button class="btn btn-danger" onclick="deleteTelegramBot()" style="padding: 6px 12px; font-size: 12px;">🗑️ Xóa Cấu Hình</button>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Bot Token *</label>
                    <input type="password" id="telegramBotToken" placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz" />
                    <small style="color: #64748b; margin-top: 4px; display: block;">Lấy Bot Token từ @BotFather trên Telegram</small>
                </div>
                
                <div class="form-group">
                    <label>Chat ID (Group ID) *</label>
                    <input type="text" id="telegramChatIdInput" placeholder="-1001234567890" />
                    <small style="color: #64748b; margin-top: 4px; display: block;">Chat ID phải là số âm (Group ID). Lấy Chat ID bằng cách thêm bot vào nhóm và gửi message, sau đó dùng getUpdates API.</small>
                </div>
                
                <div style="display: flex; gap: 12px;">
                    <button class="btn btn-primary" onclick="saveTelegramBot()">💾 Lưu Cấu Hình</button>
                    <button class="btn btn-secondary" onclick="testTelegramBot()">✅ Kiểm Tra</button>
                </div>
                
                <div id="telegramTestResult" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <!-- Modal Add/Edit Account -->
        <div id="accountModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="accountModalTitle">Thêm Account</h2>
                    <button class="modal-close" onclick="closeAccountModal()">×</button>
                </div>
                <form id="accountForm" onsubmit="event.preventDefault(); saveAccount(event); return false;">
                    <input type="hidden" id="accountId" />
                    <div class="form-group">
                        <label>Account ID *</label>
                        <div style="display: flex; gap: 8px;">
                            <input type="text" id="accountAccountId" required placeholder="act_123456789" style="flex: 1;" />
                            <button type="button" class="btn btn-secondary" onclick="syncAccountInfo()" id="syncAccountInfoBtn" style="white-space: nowrap;">🔄 Đồng Bộ</button>
                        </div>
                        <small style="color: #64748b; margin-top: 4px; display: block;">Nhập Account ID và click "Đồng Bộ" để lấy thông tin từ Facebook</small>
                    </div>
                    <div class="form-group">
                        <label>Tên Account</label>
                        <input type="text" id="accountName" placeholder="Tên hiển thị (sẽ được điền tự động sau khi đồng bộ)" readonly style="background: #f8fafc; cursor: not-allowed;" />
                        <small style="color: #64748b; margin-top: 4px; display: block;">Tên tài khoản sẽ được lấy từ Facebook sau khi đồng bộ</small>
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
                        <input type="text" id="accountTimezone" value="Asia/Ho_Chi_Minh" readonly style="background: #f8fafc; cursor: not-allowed;" />
                        <small style="color: #64748b; margin-top: 4px; display: block;">Timezone không thể chỉnh sửa</small>
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
                <form id="prefixForm" onsubmit="event.preventDefault(); savePrefix(event); return false;">
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
        
        <!-- Toast Container -->
        <div id="toastContainer" class="toast-container"></div>
        
        <script>
            console.log('✅ Settings page script loaded!');
            
            // Toast Notification System
            function showToast(title, message, type = 'info') {{
                const container = document.getElementById('toastContainer');
                if (!container) return;
                
                const icons = {{
                    success: '✅',
                    error: '❌',
                    warning: '⚠️',
                    info: 'ℹ️'
                }};
                
                const toast = document.createElement('div');
                toast.className = `toast ${{type}}`;
                toast.innerHTML = `
                    <span class="toast-icon">${{icons[type] || icons.info}}</span>
                    <div class="toast-content">
                        <div class="toast-title">${{title}}</div>
                        <div class="toast-message">${{message}}</div>
                    </div>
                    <button class="toast-close" onclick="this.parentElement.remove()">×</button>
                `;
                
                container.appendChild(toast);
                
                // Auto remove after 5 seconds
                setTimeout(() => {{
                    if (toast.parentElement) {{
                        toast.style.animation = 'toastSlideIn 0.3s ease reverse';
                        setTimeout(() => toast.remove(), 300);
                    }}
                }}, 5000);
            }}
            
            function showConfirm(title, message, onConfirm, onCancel = null) {{
                const container = document.getElementById('toastContainer');
                if (!container) return;
                
                const toast = document.createElement('div');
                toast.className = 'toast warning';
                const toastId = 'toast-' + Date.now();
                toast.id = toastId;
                
                toast.innerHTML = `
                    <span class="toast-icon">⚠️</span>
                    <div class="toast-content">
                        <div class="toast-title">${{title}}</div>
                        <div class="toast-message">${{message}}</div>
                        <div style="display: flex; gap: 8px; margin-top: 12px;">
                            <button class="btn btn-primary confirm-action-btn" style="padding: 6px 16px; font-size: 12px;">Xác nhận</button>
                            <button class="btn btn-secondary cancel-action-btn" style="padding: 6px 16px; font-size: 12px;">Hủy</button>
                        </div>
                    </div>
                    <button class="toast-close" onclick="document.getElementById('${{toastId}}').remove()">×</button>
                `;
                
                container.appendChild(toast);
                
                // Attach event listeners
                const confirmBtn = toast.querySelector('.confirm-action-btn');
                const cancelBtn = toast.querySelector('.cancel-action-btn');
                
                confirmBtn.addEventListener('click', () => {{
                    toast.remove();
                    if (typeof onConfirm === 'function') {{
                        onConfirm();
                    }}
                }});
                
                cancelBtn.addEventListener('click', () => {{
                    toast.remove();
                    if (typeof onCancel === 'function') {{
                        onCancel();
                    }}
                }});
            }}
            
            // Helper function to get token
            function getAuthToken() {{
                return localStorage.getItem('access_token') || getCookie('access_token');
            }}
            
            function getCookie(name) {{
                const cookieStr = document.cookie;
                const value = '; ' + cookieStr;
                const nameStr = name;
                const parts = value.split('; ' + nameStr + '=');
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
                    headers['Authorization'] = 'Bearer ' + token;
                }}
                return headers;
            }}
            
            // Load token status
            async function loadTokenStatus() {{
                console.log('🔑 loadTokenStatus() called');
                try {{
                    const headers = getAuthHeaders();
                    console.log('📤 Fetching /settings/token/status with headers:', headers);
                    const response = await fetch('/settings/token/status', {{
                        headers: headers
                    }});
                    console.log('📥 Response status:', response.status, response.statusText);
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        const statusCode = response.status;
                        const errorMsg = errorText.substring(0, 100);
                        throw new Error('HTTP ' + statusCode + ': ' + errorMsg);
                    }}
                    
                    const data = await response.json();
                    
                    const statusDiv = document.getElementById('tokenStatus');
                    if (!statusDiv) {{
                        console.error('tokenStatus element not found');
                        return;
                    }}
                    
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
                        statusDiv.className = 'token-status ' + statusInfo.class;
                        statusDiv.textContent = statusInfo.text;
                        if (data.last_checked) {{
                            // Format theo timezone Hồ Chí Minh (UTC+7)
                            const date = new Date(data.last_checked);
                            // Format trực tiếp với timezone Hồ Chí Minh
                            const formatted = date.toLocaleString('vi-VN', {{
                                timeZone: 'Asia/Ho_Chi_Minh',
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                                hour12: false
                            }});
                            statusDiv.textContent += ' (Kiểm tra lần cuối: ' + formatted + ')';
                        }}
                        
                        // Show token info (masked)
                        tokenInfo.style.display = 'block';
                        tokenMasked.textContent = 'EAA••••••••••••••••••••••••••••••••';
                        tokenActionText.textContent = 'mới (thay thế)';
                        saveTokenText.textContent = 'Cập Nhật Token';
                    }}
                }} catch (error) {{
                    console.error('Error loading token status:', error);
                    const errorMsg = error.message;
                    document.getElementById('tokenStatus').innerHTML = 
                        '<div class="token-status invalid">' +
                        '❌ Lỗi khi tải trạng thái token: ' + errorMsg +
                        '</div>';
                }}
            }}
            
            // Delete token
            async function deleteToken() {{
                showConfirm(
                    'Xác nhận Xóa Token',
                    'Bạn có chắc muốn xóa token? Bạn sẽ cần nhập token mới để sử dụng các tính năng liên quan đến Facebook API.',
                    async () => {{
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
                            showToast('Thành công', data.message, 'success');
                            loadTokenStatus();
                            document.getElementById('tokenInput').value = '';
                        }} catch (error) {{
                            showToast('Lỗi', 'Lỗi khi xóa token: ' + error.message, 'error');
                        }}
                    }}
                );
            }}
            
            // Save token
            async function saveToken() {{
                const token = document.getElementById('tokenInput').value.trim();
                if (!token) {{
                    showToast('Cảnh báo', 'Vui lòng nhập token', 'warning');
                    return;
                }}
                
                const saveBtn = document.querySelector('button[onclick="saveToken()"]');
                const originalText = saveBtn ? saveBtn.innerHTML : '';
                if (saveBtn) {{
                    saveBtn.disabled = true;
                    saveBtn.classList.add('loading');
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
                        showToast('Lỗi', errorMsg, 'error');
                        return;
                    }}
                    
                    const data = await response.json();
                    showToast('Thành công', data.message || 'Token đã được lưu thành công!', 'success');
                    document.getElementById('tokenInput').value = '';
                    loadTokenStatus();
                }} catch (error) {{
                    showToast('Lỗi', 'Lỗi khi lưu token: ' + error.message, 'error');
                }} finally {{
                    if (saveBtn) {{
                        saveBtn.disabled = false;
                        saveBtn.classList.remove('loading');
                        saveBtn.innerHTML = originalText;
                    }}
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
                        const userName = data.user_info.name || data.user_info.id;
                        const dataMessage = data.message;
                        resultDiv.innerHTML = 
                            '<div class="token-status valid">' +
                            '<strong>✅ Token hợp lệ!</strong><br>' +
                            '<div style="margin-top: 8px;">' +
                            '<strong>Thông tin:</strong> ' + userName + '<br>' +
                            '<strong>Trạng thái:</strong> ' + dataMessage +
                            '</div>' +
                            '</div>';
                    }} else {{
                        const errorMsg = data.message;
                        resultDiv.innerHTML = 
                            '<div class="token-status invalid">' +
                            '<strong>❌ Token không hợp lệ!</strong><br>' +
                            '<div style="margin-top: 8px;">' +
                            '<strong>Lỗi:</strong> ' + errorMsg +
                            '</div>' +
                            '</div>';
                    }}
                    
                    loadTokenStatus();
                }} catch (error) {{
                    const errorMsg = error.message;
                    resultDiv.innerHTML = 
                        '<div class="token-status invalid">' +
                        '<strong>❌ Lỗi khi kiểm tra token:</strong><br>' +
                        errorMsg +
                        '</div>';
                }}
            }}
            
            // Load accounts
            async function loadAccounts() {{
                console.log('📊 loadAccounts() called');
                try {{
                    const headers = getAuthHeaders();
                    console.log('📤 Fetching /settings/accounts with headers:', headers);
                    const response = await fetch('/settings/accounts', {{
                        headers: headers
                    }});
                    console.log('📥 Response status:', response.status, response.statusText);
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        // Try to parse as JSON for error detail
                        const statusCode = response.status;
                        let errorMessage = 'HTTP ' + statusCode + ': Internal Server Error';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            // If not JSON, use first 200 chars of error text
                            const errorSubstr = errorText.substring(0, 200);
                            errorMessage = 'HTTP ' + statusCode + ': ' + errorSubstr;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const accounts = await response.json();
                    
                    const tableDiv = document.getElementById('accountsTable');
                    if (!tableDiv) {{
                        console.error('accountsTable element not found');
                        return;
                    }}
                    
                    if (accounts.length === 0) {{
                        tableDiv.innerHTML = `
                            <div class="empty-state">
                                <div class="icon">📭</div>
                                <h3>Chưa có tài khoản quảng cáo</h3>
                                <p>Bạn chưa có tài khoản quảng cáo nào. Hãy thêm tài khoản thủ công để bắt đầu.</p>
                                <button class="btn btn-primary" onclick="showAddAccountModal()" style="margin-top: 16px;">
                                    ➕ Thêm Account Thủ Công
                                </button>
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
                        
                        // Format tiền tệ: VND trên, USD dưới
                        const currency = acc.currency || 'USD';
                        const spend = acc.last_30_days_spend || 0;
                        let spendDisplay = '';
                        if (currency === 'VND') {{
                            // VND: hiển thị VND trên, USD dưới
                            const USD_TO_VND_RATE = 26350;
                            const vndAmount = Math.round(spend);
                            const usdAmount = (spend / USD_TO_VND_RATE).toFixed(2);
                            spendDisplay = vndAmount.toLocaleString('vi-VN') + ' ₫<br><small style="color: #64748b;">(' + usdAmount + ' US$)</small>';
                        }} else {{
                            // USD: hiển thị VND trên, USD dưới
                            // Tỷ giá USD/VND cố định: 26,350
                            const USD_TO_VND_RATE = 26350;
                            const usdAmount = spend.toFixed(2);
                            const vndAmount = Math.round(spend * USD_TO_VND_RATE);
                            const vndFormatted = vndAmount.toLocaleString('vi-VN');
                            spendDisplay = vndFormatted + ' ₫<br><small style="color: #64748b;">(' + usdAmount + ' US$)</small>';
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
                            const offsetHoursStr = offsetHours >= 0 ? 
                                '+' + offsetHours.toString().padStart(2, '0') + ':00' : 
                                '-' + Math.abs(offsetHours).toString().padStart(2, '0') + ':00';
                            timezoneDisplay = timezone + ' (GMT ' + offsetHoursStr + ')';
                        }} catch (e) {{
                            // Nếu không parse được, dùng timezone gốc
                            timezoneDisplay = timezone;
                        }}
                        
                        const accId = acc.id;
                        const accStatus = acc.status;
                        const accName = acc.account_name || acc.account_id;
                        const accAccountId = acc.account_id;
                        const accType = acc.account_type || 'UNKNOWN';
                        const isEnabled = acc.enabled !== false; // Default true nếu undefined
                        
                        html += `
                            <tr style="opacity: ${{isEnabled ? '1' : '0.6'}};">
                                <td>
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <label class="toggle-switch">
                                            <input type="checkbox" ${{isEnabled ? 'checked' : ''}} 
                                                   onchange="toggleAccountEnabled(${{accId}}, this.checked)"
                                                   style="display: none;">
                                            <span class="toggle-slider"></span>
                                        </label>
                                        <span class="status-badge ${{statusClass}}" style="margin-left: 4px;">${{accStatus}}</span>
                                    </div>
                                    <small style="color: #64748b; font-size: 11px; display: block; margin-top: 4px;">
                                        ${{isEnabled ? '✅ Áp dụng logic' : '⛔ Tắt logic'}}
                                    </small>
                                </td>
                                <td><strong>${{accName}}</strong><br><small style="color: #64748b;">${{accAccountId}}</small></td>
                                <td>${{spendDisplay}}</td>
                                <td>
                                    <select class="account-type-select ${{typeClass}}" 
                                            onchange="updateAccountType(${{accId}}, this.value)" 
                                            style="background: ${{typeClass === 'type-ecommerce' ? '#dbeafe' : typeClass === 'type-lead' ? '#fce7f3' : typeClass === 'type-mobile' ? '#f3e8ff' : '#f8fafc'}}; color: ${{typeClass === 'type-ecommerce' ? '#1e40af' : typeClass === 'type-lead' ? '#9f1239' : typeClass === 'type-mobile' ? '#6b21a8' : '#475569'}};">
                                        <option value="UNKNOWN" ${{accType === 'UNKNOWN' ? 'selected' : ''}}>Chưa xác định</option>
                                        <option value="E-COMMERCE" ${{accType === 'E-COMMERCE' ? 'selected' : ''}}>E-commerce</option>
                                        <option value="LEAD_GENERATION" ${{accType === 'LEAD_GENERATION' ? 'selected' : ''}}>Lead Generation</option>
                                        <option value="MOBILE_APP" ${{accType === 'MOBILE_APP' ? 'selected' : ''}}>Mobile App</option>
                                    </select>
                                </td>
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
                    const errorMsg = error.message;
                    document.getElementById('accountsTable').innerHTML = 
                        '<div class="token-status invalid">Lỗi khi tải accounts: ' + errorMsg + '</div>';
                }}
            }}
            
            // Sync accounts from Facebook with progress tracking
            let syncInProgress = false;
            let syncProgressInterval = null;
            
            async function syncAccounts() {{
                // Prevent duplicate sync
                if (syncInProgress) {{
                    showToast('Cảnh báo', 'Đang trong quá trình đồng bộ. Vui lòng đợi hoàn thành.', 'warning');
                    return;
                }}
                
                showConfirm(
                    'Xác nhận Đồng Bộ',
                    'Bạn có chắc muốn đồng bộ accounts từ Facebook? Tất cả accounts mà bạn có quyền sẽ được đồng bộ.',
                    async () => {{
                        try {{
                            syncInProgress = true;
                            
                            // Disable sync button
                            const syncBtn = document.querySelector('button[onclick="syncAccounts()"]');
                            if (syncBtn) {{
                                syncBtn.disabled = true;
                                syncBtn.innerHTML = '⏳ Đang đồng bộ...';
                            }}
                            
                            // Show progress container
                            const progressContainer = document.getElementById('syncProgressContainer');
                            if (progressContainer) {{
                                progressContainer.style.display = 'block';
                                progressContainer.innerHTML = '<div class="loading">Đang khởi động quá trình đồng bộ...</div>';
                            }}
                            
                            // Start sync
                            const response = await fetch('/settings/accounts/sync', {{
                                method: 'POST',
                                headers: getAuthHeaders()
                            }});
                            
                            if (!response.ok) {{
                                const errorText = await response.text();
                                console.error('Error response:', errorText);
                                let errorMessage = 'HTTP ' + response.status + ': Internal Server Error';
                                try {{
                                    const errorJson = JSON.parse(errorText);
                                    errorMessage = errorJson.detail || errorJson.message || errorMessage;
                                }} catch {{
                                    const errorSubstr = errorText.substring(0, 200);
                                    errorMessage = 'HTTP ' + response.status + ': ' + errorSubstr;
                                }}
                                throw new Error(errorMessage);
                            }}
                            
                            const data = await response.json();
                            showToast('Thành công', data.message, 'success');
                            
                            // Start polling for progress
                            if (syncProgressInterval) {{
                                clearInterval(syncProgressInterval);
                            }}
                            syncProgressInterval = setInterval(checkSyncProgress, 1000); // Check every 1 second
                            
                        }} catch (error) {{
                            syncInProgress = false;
                            const syncBtn = document.querySelector('button[onclick="syncAccounts()"]');
                            if (syncBtn) {{
                                syncBtn.disabled = false;
                                syncBtn.innerHTML = '🔄 Đồng Bộ Từ Facebook';
                            }}
                            if (syncProgressInterval) {{
                                clearInterval(syncProgressInterval);
                                syncProgressInterval = null;
                            }}
                            showToast('Lỗi', 'Lỗi khi đồng bộ accounts: ' + error.message, 'error');
                        }}
                    }}
                );
            }}
            
            // Check sync progress
            async function checkSyncProgress() {{
                try {{
                    const response = await fetch('/settings/accounts/sync/progress', {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        return;
                    }}
                    
                    const progress = await response.json();
                    const progressContainer = document.getElementById('syncProgressContainer');
                    
                    if (!progressContainer) return;
                    
                    // Update progress display
                    let progressHtml = '';
                    if (progress.status === 'running') {{
                        progressHtml = `
                            <div style="padding: 16px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="color: #1e40af;">🔄 Đang đồng bộ...</strong>
                                    <span style="color: #1e40af; font-weight: 600;">${{progress.progress}}%</span>
                                </div>
                                <div style="background: #e0e7ff; border-radius: 4px; height: 8px; overflow: hidden; margin-bottom: 8px;">
                                    <div style="background: #3b82f6; height: 100%; width: ${{progress.progress}}%; transition: width 0.3s;"></div>
                                </div>
                                <div style="color: #64748b; font-size: 13px;">
                                    ${{progress.message}} (${{progress.current}}/${{progress.total}})
                                </div>
                            </div>
                        `;
                    }} else if (progress.status === 'completed') {{
                        progressHtml = `
                            <div style="padding: 16px; background: #dcfce7; border-radius: 8px; border-left: 4px solid #10b981;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="color: #166534;">✅ Hoàn thành!</strong>
                                    <span style="color: #166534; font-weight: 600;">100%</span>
                                </div>
                                <div style="background: #bbf7d0; border-radius: 4px; height: 8px; overflow: hidden; margin-bottom: 8px;">
                                    <div style="background: #10b981; height: 100%; width: 100%;"></div>
                                </div>
                                <div style="color: #166534; font-size: 13px;">
                                    ${{progress.message}}
                                </div>
                            </div>
                        `;
                        syncInProgress = false;
                        if (syncProgressInterval) {{
                            clearInterval(syncProgressInterval);
                            syncProgressInterval = null;
                        }}
                        const syncBtn = document.querySelector('button[onclick="syncAccounts()"]');
                        if (syncBtn) {{
                            syncBtn.disabled = false;
                            syncBtn.innerHTML = '🔄 Đồng Bộ Từ Facebook';
                        }}
                        // Reload accounts after 2 seconds
                        setTimeout(() => {{
                            loadAccounts();
                            // Hide progress after 5 seconds
                            setTimeout(() => {{
                                if (progressContainer) {{
                                    progressContainer.style.display = 'none';
                                }}
                            }}, 5000);
                        }}, 2000);
                    }} else if (progress.status === 'error') {{
                        progressHtml = `
                            <div style="padding: 16px; background: #fee2e2; border-radius: 8px; border-left: 4px solid #ef4444;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="color: #991b1b;">❌ Lỗi</strong>
                                </div>
                                <div style="color: #991b1b; font-size: 13px;">
                                    ${{progress.message}}
                                </div>
                            </div>
                        `;
                        syncInProgress = false;
                        if (syncProgressInterval) {{
                            clearInterval(syncProgressInterval);
                            syncProgressInterval = null;
                        }}
                        const syncBtn = document.querySelector('button[onclick="syncAccounts()"]');
                        if (syncBtn) {{
                            syncBtn.disabled = false;
                            syncBtn.innerHTML = '🔄 Đồng Bộ Từ Facebook';
                        }}
                    }} else {{
                        // Idle - hide progress
                        progressContainer.style.display = 'none';
                    }}
                    
                    progressContainer.innerHTML = progressHtml;
                }} catch (error) {{
                    console.error('Error checking sync progress:', error);
                }}
            }}
            
            // Load prefixes
            async function loadPrefixes() {{
                console.log('🏷️ loadPrefixes() called');
                try {{
                    const headers = getAuthHeaders();
                    console.log('📤 Fetching /settings/prefixes with headers:', headers);
                    const response = await fetch('/settings/prefixes', {{
                        headers: headers
                    }});
                    console.log('📥 Response status:', response.status, response.statusText);
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        // Try to parse as JSON for error detail
                        const statusCode = response.status;
                        let errorMessage = 'HTTP ' + statusCode + ': Internal Server Error';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMessage = errorJson.detail || errorJson.message || errorMessage;
                        }} catch {{
                            // If not JSON, use first 200 chars of error text
                            const errorSubstr = errorText.substring(0, 200);
                            errorMessage = 'HTTP ' + statusCode + ': ' + errorSubstr;
                        }}
                        throw new Error(errorMessage);
                    }}
                    
                    const prefixes = await response.json();
                    
                    const tableDiv = document.getElementById('prefixesTable');
                    if (!tableDiv) {{
                        console.error('prefixesTable element not found');
                        return;
                    }}
                    
                    if (prefixes.length === 0) {{
                        tableDiv.innerHTML = `
                            <div class="empty-state">
                                <div class="icon">🏷️</div>
                                <h3>Chưa có prefixes</h3>
                                <p>Bạn chưa có prefix nào. Hãy thêm prefix mới để bắt đầu quản lý.</p>
                                <button class="btn btn-primary" onclick="showAddPrefixModal()" style="margin-top: 16px;">
                                    ➕ Thêm Prefix
                                </button>
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
                        const prefixValue = prefix.prefix;
                        const prefixName = prefix.prefix_name || '-';
                        const statusClass = prefix.enabled ? 'status-active' : 'status-paused';
                        const statusText = prefix.enabled ? 'Bật' : 'Tắt';
                        html += `
                            <tr>
                                <td><strong>${{prefixValue}}</strong></td>
                                <td>${{prefixName}}</td>
                                <td><span class="status-badge ${{statusClass}}">${{statusText}}</span></td>
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
                    const errorMsg = error.message;
                    document.getElementById('prefixesTable').innerHTML = 
                        '<div class="token-status invalid">Lỗi khi tải prefixes: ' + errorMsg + '</div>';
                }}
            }}
            
            // Account Modal Functions
            function showAddAccountModal() {{
                document.getElementById('accountModalTitle').textContent = 'Thêm Account';
                document.getElementById('accountForm').reset();
                document.getElementById('accountId').value = '';
                document.getElementById('accountAccountId').value = '';
                document.getElementById('accountAccountId').readOnly = false;
                document.getElementById('accountAccountId').style.background = 'white';
                document.getElementById('accountAccountId').style.cursor = 'text';
                document.getElementById('accountName').value = '';
                document.getElementById('accountName').readOnly = true;
                document.getElementById('accountName').style.background = '#f8fafc';
                document.getElementById('accountName').style.cursor = 'not-allowed';
                document.getElementById('accountType').value = 'UNKNOWN';
                document.getElementById('accountTimezone').value = 'Asia/Ho_Chi_Minh';
                document.getElementById('accountTimezone').readOnly = true;
                document.getElementById('accountTimezone').style.background = '#f8fafc';
                document.getElementById('accountTimezone').style.cursor = 'not-allowed';
                document.getElementById('accountPrefixesGroup').style.display = 'none';
                document.getElementById('syncAccountInfoBtn').style.display = 'inline-flex';
                document.getElementById('accountModal').classList.add('show');
            }}
            
            // Sync account info from Facebook (chỉ lấy name và timezone)
            async function syncAccountInfo() {{
                const accountIdInput = document.getElementById('accountAccountId');
                const accountId = accountIdInput.value.trim();
                
                if (!accountId) {{
                    showToast('Cảnh báo', 'Vui lòng nhập Account ID trước', 'warning');
                    accountIdInput.focus();
                    return;
                }}
                
                const syncBtn = document.getElementById('syncAccountInfoBtn');
                const originalText = syncBtn.innerHTML;
                syncBtn.disabled = true;
                syncBtn.innerHTML = '⏳ Đang đồng bộ...';
                
                try {{
                    const response = await fetch('/settings/accounts/fetch-info', {{
                        method: 'POST',
                        headers: getAuthHeaders('application/json'),
                        body: JSON.stringify({{ account_id: accountId }})
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMsg = 'Không thể lấy thông tin account';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMsg = errorJson.detail || errorMsg;
                        }} catch {{
                            errorMsg = errorText.substring(0, 200);
                        }}
                        showToast('Lỗi', errorMsg, 'error');
                        return;
                    }}
                    
                    const data = await response.json();
                    
                    // Điền thông tin vào form
                    document.getElementById('accountAccountId').value = data.account_id;
                    document.getElementById('accountName').value = data.name || '';
                    document.getElementById('accountTimezone').value = data.timezone || 'Asia/Ho_Chi_Minh';
                    
                    showToast('Thành công', 'Đã lấy thông tin account từ Facebook thành công!', 'success');
                }} catch (error) {{
                    showToast('Lỗi', 'Lỗi khi đồng bộ thông tin: ' + error.message, 'error');
                }} finally {{
                    syncBtn.disabled = false;
                    syncBtn.innerHTML = originalText;
                }}
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
            
            // Toggle account enabled/disabled
            async function toggleAccountEnabled(accountId, enabled) {{
                try {{
                    const response = await fetch('/settings/accounts/' + accountId + '/toggle-enabled', {{
                        method: 'PATCH',
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMsg = 'Không thể bật/tắt account';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMsg = errorJson.detail || errorMsg;
                        }} catch {{
                            errorMsg = errorText.substring(0, 100);
                        }}
                        showToast('Lỗi', errorMsg, 'error');
                        // Reload để revert toggle
                        loadAccounts();
                        return;
                    }}
                    
                    const data = await response.json();
                    showToast('Thành công', data.message, 'success');
                    // Reload để cập nhật UI
                    loadAccounts();
                }} catch (error) {{
                    showToast('Lỗi', 'Lỗi khi bật/tắt account: ' + error.message, 'error');
                    // Reload để revert toggle
                    loadAccounts();
                }}
            }}
            
            // Update account type inline
            async function updateAccountType(accountId, newType) {{
                try {{
                    const response = await fetch('/settings/accounts/' + accountId + '/type', {{
                        method: 'PATCH',
                        headers: getAuthHeaders('application/json'),
                        body: JSON.stringify({{ account_type: newType }})
                    }});
                    
                    if (!response.ok) {{
                        const errorText = await response.text();
                        let errorMsg = 'Không thể cập nhật loại account';
                        try {{
                            const errorJson = JSON.parse(errorText);
                            errorMsg = errorJson.detail || errorMsg;
                        }} catch {{
                            errorMsg = errorText.substring(0, 100);
                        }}
                        showToast('Lỗi', errorMsg, 'error');
                        // Reload để revert dropdown
                        loadAccounts();
                        return;
                    }}
                    
                    const data = await response.json();
                    showToast('Thành công', data.message, 'success');
                }} catch (error) {{
                    showToast('Lỗi', 'Lỗi khi cập nhật loại account: ' + error.message, 'error');
                    // Reload để revert dropdown
                    loadAccounts();
                }}
            }}
            
            async function refreshAccount(id) {{
                showConfirm(
                    'Xác nhận Refresh',
                    'Bạn có chắc muốn refresh account này? Thông tin sẽ được cập nhật từ Facebook API.',
                    async () => {{
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
                            showToast('Thành công', data.message, 'success');
                            loadAccounts();
                        }} catch (error) {{
                            showToast('Lỗi', 'Lỗi khi refresh account: ' + error.message, 'error');
                        }}
                    }}
                );
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
                    document.getElementById('accountAccountId').readOnly = true;
                    document.getElementById('accountAccountId').style.background = '#f8fafc';
                    document.getElementById('accountAccountId').style.cursor = 'not-allowed';
                    document.getElementById('accountName').value = account.account_name || '';
                    document.getElementById('accountName').readOnly = true;
                    document.getElementById('accountName').style.background = '#f8fafc';
                    document.getElementById('accountName').style.cursor = 'not-allowed';
                    document.getElementById('accountType').value = account.account_type || 'UNKNOWN';
                    document.getElementById('accountTimezone').value = account.timezone || 'Asia/Ho_Chi_Minh';
                    document.getElementById('accountTimezone').readOnly = true;
                    document.getElementById('accountTimezone').style.background = '#f8fafc';
                    document.getElementById('accountTimezone').style.cursor = 'not-allowed';
                    
                    // Ẩn nút đồng bộ khi edit (chỉ hiện khi thêm mới)
                    const syncBtn = document.getElementById('syncAccountInfoBtn');
                    if (syncBtn) {{
                        syncBtn.style.display = 'none';
                    }}
                    
                    // Hiển thị phần chọn prefixes và load prefixes
                    document.getElementById('accountPrefixesGroup').style.display = 'block';
                    await loadPrefixesForAccount(id);
                    
                    document.getElementById('accountModal').classList.add('show');
                }} catch (error) {{
                    showToast('Lỗi', 'Lỗi khi tải thông tin account: ' + error.message, 'error');
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
                        const accountId = id;
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
                            const accountIdForPrefixes = id;
                            const currentResponse = await fetch('/settings/accounts/' + accountIdForPrefixes + '/prefixes', {{
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
                                        await fetch('/settings/accounts/' + accountIdForPrefixes + '/prefixes/' + prefixId, {{
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
                                        await fetch('/settings/accounts/' + accountIdForPrefixes + '/prefixes/' + prefixId, {{
                                            method: 'DELETE',
                                            headers: getAuthHeaders()
                                        }});
                                    }} catch (e) {{
                                        console.error('Error unlinking prefix:', e);
                                    }}
                                }}
                            }}
                            
                            showToast('Thành công', 'Đã cập nhật account và prefixes thành công!', 'success');
                            closeAccountModal();
                            loadAccounts();
                        }} else {{
                            const error = await response.json();
                            showToast('Lỗi', error.detail || 'Không thể lưu account', 'error');
                        }}
                    }} else {{
                        // Create new account - sau khi tạo, fetch status và spend
                        response = await fetch('/settings/accounts', {{
                            method: 'POST',
                            headers: getAuthHeaders('application/json'),
                            body: JSON.stringify(accountData)
                        }});
                        
                        if (response.ok) {{
                            const newAccount = await response.json();
                            
                            // Sau khi tạo account, fetch status và spend từ Facebook
                            try {{
                                const refreshResponse = await fetch('/settings/accounts/' + newAccount.id + '/refresh', {{
                                    method: 'POST',
                                    headers: getAuthHeaders()
                                }});
                                
                                if (refreshResponse.ok) {{
                                    showToast('Thành công', 'Đã thêm account và cập nhật thông tin từ Facebook thành công!', 'success');
                                }} else {{
                                    showToast('Thành công', 'Đã thêm account thành công! (Lưu ý: Không thể cập nhật trạng thái và chi tiêu từ Facebook)', 'warning');
                                }}
                            }} catch (refreshError) {{
                                showToast('Thành công', 'Đã thêm account thành công! (Lưu ý: Không thể cập nhật trạng thái và chi tiêu từ Facebook)', 'warning');
                            }}
                            
                            closeAccountModal();
                            loadAccounts();
                        }} else {{
                            const error = await response.json();
                            showToast('Lỗi', error.detail || 'Không thể lưu account', 'error');
                        }}
                    }}
                }} catch (error) {{
                    showToast('Lỗi', 'Lỗi khi lưu account: ' + error.message, 'error');
                }}
            }}
            
            async function deleteAllAccounts() {{
                showConfirm(
                    'Xác nhận Xóa Tất Cả Accounts',
                    'Bạn có chắc muốn xóa TẤT CẢ accounts? Hành động này không thể hoàn tác! Tất cả các liên kết với prefixes cũng sẽ bị xóa.',
                    async () => {{
                        try {{
                            const response = await fetch('/settings/accounts/all', {{
                                method: 'DELETE',
                                headers: getAuthHeaders()
                            }});
                            
                            if (response.ok) {{
                                const data = await response.json();
                                showToast('Thành công', data.message || 'Đã xóa tất cả accounts thành công!', 'success');
                                loadAccounts();
                            }} else {{
                                const error = await response.json();
                                showToast('Lỗi', error.detail || 'Lỗi khi xóa accounts', 'error');
                            }}
                        }} catch (error) {{
                            showToast('Lỗi', 'Lỗi khi xóa accounts: ' + error.message, 'error');
                        }}
                    }}
                );
            }}
            
            async function deleteAccount(id) {{
                showConfirm(
                    'Xác nhận Xóa Account',
                    'Bạn có chắc muốn xóa account này? Tất cả các liên kết với prefixes cũng sẽ bị xóa.',
                    async () => {{
                        try {{
                            const response = await fetch('/settings/accounts/' + id, {{
                                method: 'DELETE',
                                headers: getAuthHeaders()
                            }});
                            
                            if (response.ok || response.status === 204) {{
                                showToast('Thành công', 'Đã xóa account thành công!', 'success');
                                loadAccounts();
                            }} else {{
                                const error = await response.json();
                                showToast('Lỗi', error.detail || 'Không thể xóa account', 'error');
                            }}
                        }} catch (error) {{
                            showToast('Lỗi', 'Lỗi khi xóa account: ' + error.message, 'error');
                        }}
                    }}
                );
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
                    showToast('Lỗi', 'Lỗi khi tải thông tin prefix: ' + error.message, 'error');
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
                        const prefixId = id;
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
                        showToast('Thành công', (id ? 'Đã cập nhật' : 'Đã thêm') + ' prefix thành công!', 'success');
                        closePrefixModal();
                        loadPrefixes();
                    }} else {{
                        const error = await response.json();
                        showToast('Lỗi', error.detail || 'Không thể lưu prefix', 'error');
                    }}
                }} catch (error) {{
                    showToast('Lỗi', 'Lỗi khi lưu prefix: ' + error.message, 'error');
                }}
            }}
            
            async function deletePrefix(id) {{
                showConfirm(
                    'Xác nhận Xóa Prefix',
                    'Bạn có chắc muốn xóa prefix này? Tất cả các liên kết với accounts cũng sẽ bị xóa.',
                    async () => {{
                        try {{
                            const response = await fetch('/settings/prefixes/' + id, {{
                                method: 'DELETE',
                                headers: getAuthHeaders()
                            }});
                            
                            if (response.ok || response.status === 204) {{
                                showToast('Thành công', 'Đã xóa prefix thành công!', 'success');
                                loadPrefixes();
                            }} else {{
                                const error = await response.json();
                                showToast('Lỗi', error.detail || 'Không thể xóa prefix', 'error');
                            }}
                        }} catch (error) {{
                            showToast('Lỗi', 'Lỗi khi xóa prefix: ' + error.message, 'error');
                        }}
                    }}
                );
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
            
            // Load data on page load - wait for DOM to be ready
            async function initializePage() {{
                console.log('🚀 Initializing page...');
                console.log('Document ready state:', document.readyState);
                console.log('Token status element:', document.getElementById('tokenStatus'));
                console.log('Accounts table element:', document.getElementById('accountsTable'));
                console.log('Prefixes table element:', document.getElementById('prefixesTable'));
                
                // Load tất cả dữ liệu song song để tăng tốc độ
                console.log('📡 Loading all data in parallel...');
                await Promise.all([
                    loadTokenStatus().catch(error => {{
                        console.error('❌ Error loading token status:', error);
                        const statusDiv = document.getElementById('tokenStatus');
                        if (statusDiv) {{
                            statusDiv.innerHTML = '<div class="token-status invalid">❌ Lỗi khi tải trạng thái token: ' + error.message + '</div>';
                        }}
                    }}),
                    loadAccounts().catch(error => {{
                        console.error('❌ Error loading accounts:', error);
                        const tableDiv = document.getElementById('accountsTable');
                        if (tableDiv) {{
                            tableDiv.innerHTML = '<div class="token-status invalid">Lỗi khi tải accounts: ' + error.message + '</div>';
                        }}
                    }}),
                    loadPrefixes().catch(error => {{
                        console.error('❌ Error loading prefixes:', error);
                        const tableDiv = document.getElementById('prefixesTable');
                        if (tableDiv) {{
                            tableDiv.innerHTML = '<div class="token-status invalid">Lỗi khi tải prefixes: ' + error.message + '</div>';
                        }}
                    }}),
                    loadTelegramStatus().catch(error => {{
                        console.error('❌ Error loading Telegram Bot status:', error);
                    }})
                ]);
                console.log('✅ All data loaded');
                
                console.log('✅ Page initialization complete');
            }}
            
            // Telegram Bot Functions
            async function loadTelegramStatus() {{
                try {{
                    const response = await fetch('/settings/telegram/status', {{
                        headers: getAuthHeaders()
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }}
                    
                    const data = await response.json();
                    const statusDiv = document.getElementById('telegramStatus');
                    const infoDiv = document.getElementById('telegramInfo');
                    
                    if (data.status === 'NOT_SET') {{
                        statusDiv.className = 'token-status not-set';
                        statusDiv.textContent = '❌ Chưa cấu hình Telegram Bot';
                        infoDiv.style.display = 'none';
                    }} else if (data.status === 'VALID') {{
                        statusDiv.className = 'token-status valid';
                        statusDiv.innerHTML = '✅ ' + data.message;
                        infoDiv.style.display = 'block';
                        document.getElementById('telegramTokenMasked').textContent = data.bot_token_masked || '***';
                        document.getElementById('telegramChatId').textContent = data.chat_id || 'Chưa có';
                    }} else {{
                        statusDiv.className = 'token-status invalid';
                        statusDiv.innerHTML = '❌ ' + data.message;
                        infoDiv.style.display = 'none';
                    }}
                }} catch (error) {{
                    console.error('Error loading Telegram status:', error);
                    const statusDiv = document.getElementById('telegramStatus');
                    statusDiv.className = 'token-status invalid';
                    statusDiv.textContent = '❌ Lỗi khi tải trạng thái: ' + error.message;
                }}
            }}
            
            async function saveTelegramBot() {{
                const botToken = document.getElementById('telegramBotToken').value.trim();
                const chatId = document.getElementById('telegramChatIdInput').value.trim();
                
                if (!botToken) {{
                    showToast('Vui lòng nhập Bot Token', 'error');
                    return;
                }}
                
                if (!chatId) {{
                    showToast('Vui lòng nhập Chat ID', 'error');
                    return;
                }}
                
                try {{
                    const response = await fetch('/settings/telegram/save', {{
                        method: 'POST',
                        headers: {{
                            ...getAuthHeaders(),
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            bot_token: botToken,
                            chat_id: chatId
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok && data.success) {{
                        showToast('Đã lưu cấu hình Telegram Bot thành công!');
                        document.getElementById('telegramBotToken').value = '';
                        document.getElementById('telegramChatIdInput').value = '';
                        loadTelegramStatus();
                    }} else {{
                        showToast(data.message || data.detail || 'Lỗi khi lưu cấu hình', 'error');
                    }}
                }} catch (error) {{
                    console.error('Error saving Telegram bot:', error);
                    showToast('Lỗi khi lưu cấu hình: ' + error.message, 'error');
                }}
            }}
            
            async function testTelegramBot() {{
                const botToken = document.getElementById('telegramBotToken').value.trim();
                const chatId = document.getElementById('telegramChatIdInput').value.trim();
                
                if (!botToken) {{
                    showToast('Vui lòng nhập Bot Token', 'error');
                    return;
                }}
                
                if (!chatId) {{
                    showToast('Vui lòng nhập Chat ID', 'error');
                    return;
                }}
                
                const resultDiv = document.getElementById('telegramTestResult');
                resultDiv.innerHTML = '<div class="loading">Đang kiểm tra...</div>';
                
                try {{
                    const response = await fetch('/settings/telegram/test', {{
                        method: 'POST',
                        headers: {{
                            ...getAuthHeaders(),
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            bot_token: botToken,
                            chat_id: chatId
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.valid) {{
                        let html = '<div style="padding: 16px; background: #d1fae5; border-radius: 8px; border: 1px solid #10b981;">';
                        html += '<strong>✅ ' + data.message + '</strong><br>';
                        if (data.bot_info) {{
                            html += '<br><strong>Thông tin Bot:</strong><br>';
                            html += 'Username: @' + (data.bot_info.username || 'N/A') + '<br>';
                            html += 'Tên: ' + (data.bot_info.first_name || 'N/A') + '<br>';
                        }}
                        if (data.chat_info) {{
                            html += '<br><strong>Thông tin Chat:</strong><br>';
                            html += 'Tên: ' + (data.chat_info.title || data.chat_info.first_name || 'N/A') + '<br>';
                            html += 'Loại: ' + (data.chat_info.type || 'N/A') + '<br>';
                        }}
                        html += '</div>';
                        resultDiv.innerHTML = html;
                    }} else {{
                        resultDiv.innerHTML = '<div style="padding: 16px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;"><strong>❌ ' + data.message + '</strong></div>';
                    }}
                }} catch (error) {{
                    console.error('Error testing Telegram bot:', error);
                    resultDiv.innerHTML = '<div style="padding: 16px; background: #fee2e2; border-radius: 8px; border: 1px solid #ef4444;"><strong>❌ Lỗi khi kiểm tra: ' + error.message + '</strong></div>';
                }}
            }}
            
            async function deleteTelegramBot() {{
                if (!confirm('Bạn có chắc muốn xóa cấu hình Telegram Bot?')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch('/settings/telegram/delete', {{
                        method: 'DELETE',
                        headers: getAuthHeaders()
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showToast('Đã xóa cấu hình Telegram Bot thành công!');
                        loadTelegramStatus();
                    }} else {{
                        showToast(data.message || data.detail || 'Lỗi khi xóa cấu hình', 'error');
                    }}
                }} catch (error) {{
                    console.error('Error deleting Telegram bot:', error);
                    showToast('Lỗi khi xóa cấu hình: ' + error.message, 'error');
                }}
            }}
            
            // Wait for DOM to be ready
            console.log('🔍 Script loaded, readyState:', document.readyState);
            if (document.readyState === 'loading') {{
                console.log('⏳ Waiting for DOMContentLoaded...');
                document.addEventListener('DOMContentLoaded', function() {{
                    console.log('✅ DOMContentLoaded fired');
                    initializePage();
                }});
            }} else {{
                console.log('✅ DOM already ready, initializing immediately');
                // DOM is already ready, call immediately
                initializePage();
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

