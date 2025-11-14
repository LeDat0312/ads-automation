# -*- coding: utf-8 -*-
"""
Code cần thêm vào app/api/routes/settings.py
Thêm sau dòng 224 (sau function delete_token)
"""

# Thêm import ở đầu file (sau dòng 26):
from app.services.telegram_token_service import test_telegram_bot_token

# Thêm các schemas (sau dòng 109):
class TelegramBotSaveRequest(BaseModel):
    bot_token: str
    chat_id: str


class TelegramBotTestResponse(BaseModel):
    valid: bool
    status: str
    message: str
    bot_info: Optional[Dict[str, Any]] = None
    chat_info: Optional[Dict[str, Any]] = None


# Thêm các endpoints (sau dòng 224, sau function delete_token):

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

