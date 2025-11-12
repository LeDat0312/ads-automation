"""
Telegram Bot Service - IMPROVED
Thay thế cho Telegram.gs từ Google Apps Script
Với retry, backoff, rate limit handling
"""
import re
import html
import requests
import logging
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def markdown_to_html(text: str) -> str:
    """Chuyển đổi Markdown sang HTML"""
    if not text:
        return ''
    
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*([^*\n]+?)\*', r'<b>\1</b>', text)
    text = re.sub(r'_([^_\n]+?)_', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def parse_command(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse command từ Telegram update
    Trả về {cmd, args, chat_id, user_id, message_id, update_id}
    """
    if 'message' not in update:
        return None
    
    message = update['message']
    text = message.get('text', '').strip()
    
    if not text or not text.startswith('/'):
        return None
    
    # Extract command
    cmd_match = re.match(r'^/([a-zA-Z0-9_]+)(@\S+)?\s*(.*)$', text)
    if not cmd_match:
        return None
    
    cmd = '/' + cmd_match.group(1).lower()
    args = cmd_match.group(3).strip() if cmd_match.group(3) else ''
    
    return {
        'cmd': cmd,
        'args': args,
        'chat_id': str(message.get('chat', {}).get('id', '')),
        'user_id': str(message.get('from', {}).get('id', '')),
        'message_id': message.get('message_id'),
        'update_id': update.get('update_id'),
        'text': text,
        'full_message': message
    }


def send_message(
    chat_id: str,
    text: str,
    bot_token: str,
    reply_to_message_id: Optional[int] = None,
    parse_mode: str = 'HTML',
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Tuple[bool, Optional[Any]]:
    """
    Gửi message với retry và backoff
    Tuân thủ rate limit 429
    
    Returns:
        (success, message_id_or_error)
        - Nếu success=True: trả về message_id (int)
        - Nếu success=False: trả về error_message (str)
    """
    # Kiểm tra tham số
    if not text or not bot_token or not chat_id:
        return False, "Missing required parameters"
    
    # Chặn gửi vào chat cá nhân
    try:
        chat_id_num = int(str(chat_id).strip())
        if chat_id_num > 0:
            logger.warning(f"⚠️ Blocked: Chat ID {chat_id} is private chat")
            return False, "Cannot send to private chat"
    except ValueError:
        pass
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Convert markdown to HTML if needed
    if parse_mode == 'HTML':
        text = markdown_to_html(text)
    
    payload = {
        'chat_id': str(chat_id).strip(),
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': False
    }
    
    if reply_to_message_id:
        payload['reply_to_message_id'] = int(reply_to_message_id)
    
    # Retry với exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            # Handle rate limit 429
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"⚠️ Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            
            response.raise_for_status()
            json_response = response.json()
            
            if json_response.get('ok') is True:
                # Trả về message_id nếu có
                result = json_response.get('result', {})
                message_id = result.get('message_id')
                return True, message_id
            
            # Parse error - thử plain text
            error_desc = json_response.get('description', '')
            if 'parse' in error_desc.lower() or 'entities' in error_desc.lower():
                if parse_mode == 'HTML':
                    logger.warning("⚠️ HTML parse error, retrying with plain text...")
                    result = send_message(
                        chat_id, text, bot_token, reply_to_message_id,
                        parse_mode='', max_retries=1, backoff_factor=0
                    )
                    return result
            
            return False, error_desc
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.warning(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return False, str(e)
    
    return False, "Max retries exceeded"


def send_chat_action(chat_id: str, action: str, bot_token: str) -> bool:
    """
    Gửi chat action (typing, uploading photo, etc.)
    Dùng cho job nặng để user biết bot đang xử lý
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendChatAction"
    payload = {
        'chat_id': str(chat_id),
        'action': action  # 'typing', 'upload_photo', etc.
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"🚨 Error sending chat action: {e}")
        return False


def delete_message(
    chat_id: str,
    message_id: int,
    bot_token: str,
    max_retries: int = 3
) -> Tuple[bool, Optional[str]]:
    """
    Xóa message đã gửi
    
    Returns:
        (success, error_message)
    """
    if not bot_token or not chat_id or not message_id:
        return False, "Missing required parameters"
    
    url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
    payload = {
        'chat_id': str(chat_id).strip(),
        'message_id': int(message_id)
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"⚠️ Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            
            response.raise_for_status()
            json_response = response.json()
            
            if json_response.get('ok') is True:
                return True, None
            
            error_desc = json_response.get('description', '')
            return False, error_desc
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2.0 ** attempt
                logger.warning(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return False, str(e)
    
    return False, "Max retries exceeded"


def edit_message(
    chat_id: str,
    message_id: int,
    text: str,
    bot_token: str,
    parse_mode: str = 'HTML',
    max_retries: int = 3
) -> Tuple[bool, Optional[str]]:
    """
    Edit message đã gửi (dùng cho progress updates)
    
    Returns:
        (success, error_message)
    """
    if not text or not bot_token or not chat_id or not message_id:
        return False, "Missing required parameters"
    
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    
    # Convert markdown to HTML if needed
    if parse_mode == 'HTML':
        text = markdown_to_html(text)
    
    payload = {
        'chat_id': str(chat_id).strip(),
        'message_id': int(message_id),
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': False
    }
    
    # Retry với exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            # Handle rate limit 429
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"⚠️ Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            
            response.raise_for_status()
            json_response = response.json()
            
            if json_response.get('ok') is True:
                return True, None
            
            error_desc = json_response.get('description', '')
            return False, error_desc
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2.0 ** attempt
                logger.warning(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return False, str(e)
    
    return False, "Max retries exceeded"


def send_telegram_message_safe(
    message: str,
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
    reply_to_message_id: Optional[int] = None
) -> bool:
    """Gửi Telegram message an toàn (với error handling)"""
    from app.core.config import get_settings
    
    settings = get_settings()
    
    if not bot_token:
        bot_token = settings.TELEGRAM_BOT_TOKEN
    
    if not chat_id:
        chat_id = settings.TELEGRAM_CHAT_ID
    
    if not bot_token or not chat_id:
        logger.warning("⚠️ Missing Bot Token or Chat ID")
        return False
    
    success, error = send_message(chat_id, message, bot_token, reply_to_message_id)
    if not success:
        logger.error(f"🚨 Failed to send Telegram message: {error}")
    
    return success
