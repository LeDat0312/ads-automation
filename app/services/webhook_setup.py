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
    Chỉ set webhook nếu URL/secret khác với hiện tại (tránh spam 429/Conflict)
    
    Args:
        webhook_url: URL webhook (nếu None, lấy từ settings)
        drop_pending: Có xóa pending updates không (mặc định True)
    
    Returns:
        True nếu thành công, False nếu thất bại
    """
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    webhook = webhook_url or settings.WEBHOOK_URL
    webhook_secret = settings.TELEGRAM_WEBHOOK_SECRET
    
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN không được cấu hình")
        return False
    
    if not webhook:
        logger.error("❌ WEBHOOK_URL không được cấu hình")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Bước 1: Kiểm tra webhook hiện tại
            webhook_info = await get_webhook_info()
            if webhook_info:
                current_url = webhook_info.get('url', '')
                # Nếu URL đã đúng và có secret_token → không cần set lại
                if current_url == webhook:
                    logger.info("✅ Webhook đã đúng, bỏ qua setWebhook")
                    return True
                else:
                    logger.info(f"📋 Webhook hiện tại: {current_url}, cần update sang: {webhook}")
            
            # Bước 2: Xóa webhook cũ nếu cần
            if drop_pending or (webhook_info and webhook_info.get('url')):
                delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook?drop_pending_updates={str(drop_pending).lower()}"
                try:
                    delete_response = await client.get(delete_url, timeout=10.0)
                    if delete_response.status_code == 200:
                        delete_result = delete_response.json()
                        if delete_result.get('ok'):
                            logger.info("✅ Đã xóa webhook cũ và pending updates")
                        else:
                            # Không log warning nếu webhook chưa được set (bình thường)
                            if 'not found' not in delete_result.get('description', '').lower():
                                logger.warning(f"⚠️ Không thể xóa webhook cũ: {delete_result.get('description', 'Unknown error')}")
                except httpx.HTTPStatusError as e:
                    # Nếu 429 (Too Many Requests), chỉ log 1 lần và bỏ qua
                    if e.response.status_code == 429:
                        logger.warning(f"⚠️ Rate limit khi xóa webhook (429), bỏ qua...")
                    else:
                        logger.warning(f"⚠️ Lỗi khi xóa webhook cũ: {e}")
                except Exception as e:
                    logger.warning(f"⚠️ Lỗi khi xóa webhook cũ: {e}")
            
            # Bước 3: Set webhook mới với secret_token
            set_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
            payload = {
                'url': webhook,
                'allowed_updates': ['message'],  # Chỉ nhận message updates
                'drop_pending_updates': drop_pending
            }
            
            # Thêm secret_token nếu có
            if webhook_secret:
                payload['secret_token'] = webhook_secret
                logger.info("🔐 Sử dụng webhook secret token để xác thực")
            
            try:
                response = await client.post(set_url, data=payload, timeout=10.0)
                result = response.json()
                
                if result.get('ok'):
                    logger.info(f"✅ Đã setup webhook thành công: {webhook}")
                    logger.info(f"📋 Webhook info: {result.get('description', 'N/A')}")
                    return True
                else:
                    error_msg = result.get('description', 'Unknown error')
                    # Không log error nếu là 429 (rate limit) hoặc Conflict
                    if '429' not in error_msg and 'conflict' not in error_msg.lower():
                        logger.error(f"❌ Lỗi setup webhook: {error_msg}")
                    else:
                        logger.warning(f"⚠️ Webhook setup bị rate limit hoặc conflict, bỏ qua...")
                    return False
            except httpx.HTTPStatusError as e:
                # Nếu 429, chỉ log warning 1 lần
                if e.response.status_code == 429:
                    logger.warning(f"⚠️ Rate limit khi set webhook (429), bỏ qua...")
                    return False
                else:
                    raise
                
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

