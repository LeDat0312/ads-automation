"""
Per-Chat Lock Service
Đảm bảo mỗi chat chỉ xử lý 1 command nặng tại một thời điểm
"""
import asyncio
import logging
from typing import Dict
from collections import defaultdict

logger = logging.getLogger(__name__)

# In-memory locks per chat (có thể nâng cấp lên Redis sau)
_chat_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


def get_chat_lock(chat_id: str) -> asyncio.Lock:
    """
    Lấy lock cho chat_id
    
    Args:
        chat_id: Chat ID
    
    Returns:
        asyncio.Lock cho chat này
    """
    return _chat_locks[chat_id]


async def acquire_chat_lock(chat_id: str, timeout: float = 5.0) -> bool:
    """
    Acquire lock cho chat (non-blocking với timeout)
    
    Args:
        chat_id: Chat ID
        timeout: Timeout để acquire lock (giây)
    
    Returns:
        True nếu acquire thành công, False nếu timeout hoặc đã có lock
    """
    lock = get_chat_lock(chat_id)
    
    try:
        # Thử acquire lock với timeout
        await asyncio.wait_for(lock.acquire(), timeout=timeout)
        return True
    except asyncio.TimeoutError:
        logger.warning(f"⏱️ Timeout khi acquire lock cho chat {chat_id}")
        return False
    except Exception as e:
        logger.error(f"❌ Lỗi khi acquire lock cho chat {chat_id}: {e}")
        return False


def release_chat_lock(chat_id: str):
    """
    Release lock cho chat
    
    Args:
        chat_id: Chat ID
    """
    lock = _chat_locks.get(chat_id)
    if lock and lock.locked():
        lock.release()
        logger.debug(f"🔓 Đã release lock cho chat {chat_id}")


def is_chat_locked(chat_id: str) -> bool:
    """
    Kiểm tra xem chat có đang bị lock không
    
    Args:
        chat_id: Chat ID
    
    Returns:
        True nếu đang locked, False nếu không
    """
    lock = _chat_locks.get(chat_id)
    return lock is not None and lock.locked()

