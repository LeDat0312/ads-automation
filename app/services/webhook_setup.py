"""
Webhook Setup Service
Setup và quản lý Telegram webhook với drop_pending_updates
"""
import logging
import httpx
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def setup_webhook(webhook_url: Optional[str] = None, drop_pending: bool = True) -> bool:
    """
    Setup Telegram webhook với drop_pending_updates
    
    Args:
        webhook_url: URL webhook (nếu None, lấy từ settings)
        drop_pending: Có xóa pending updates không (mặc định True)
    
    Returns:
        True nếu thành công, False nếu thất bại
    """
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    webhook = webhook_url or settings.WEBHOOK_URL
    
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN không được cấu hình")
        return False
    
    if not webhook:
        logger.error("❌ WEBHOOK_URL không được cấu hình")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Bước 1: Xóa webhook cũ và drop pending updates
            if drop_pending:
                delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook?drop_pending_updates=true"
                try:
                    delete_response = await client.get(delete_url)
                    delete_result = delete_response.json()
                    if delete_result.get('ok'):
                        logger.info("✅ Đã xóa webhook cũ và pending updates")
                    else:
                        logger.warning(f"⚠️ Không thể xóa webhook cũ: {delete_result.get('description', 'Unknown error')}")
                except Exception as e:
                    logger.warning(f"⚠️ Lỗi khi xóa webhook cũ: {e}")
            
            # Bước 2: Set webhook mới
            set_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
            payload = {
                'url': webhook,
                'allowed_updates': ['message'],  # Chỉ nhận message updates
                'drop_pending_updates': drop_pending
            }
            
            response = await client.post(set_url, data=payload)
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"✅ Đã setup webhook thành công: {webhook}")
                logger.info(f"📋 Webhook info: {result.get('description', 'N/A')}")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                logger.error(f"❌ Lỗi setup webhook: {error_msg}")
                return False
                
    except Exception as e:
        logger.error(f"🚨 Lỗi khi setup webhook: {e}")
        return False


async def get_webhook_info() -> Optional[dict]:
    """Lấy thông tin webhook hiện tại"""
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    if not bot_token:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
            response = await client.get(url)
            result = response.json()
            
            if result.get('ok'):
                return result.get('result', {})
            return None
    except Exception as e:
        logger.error(f"🚨 Lỗi khi lấy webhook info: {e}")
        return None


async def delete_webhook(drop_pending: bool = True) -> bool:
    """Xóa webhook hiện tại"""
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    if not bot_token:
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook?drop_pending_updates={str(drop_pending).lower()}"
            response = await client.get(url)
            result = response.json()
            
            if result.get('ok'):
                logger.info("✅ Đã xóa webhook thành công")
                return True
            return False
    except Exception as e:
        logger.error(f"🚨 Lỗi khi xóa webhook: {e}")
        return False

