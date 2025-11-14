# -*- coding: utf-8 -*-
"""
Telegram Bot Token Service - Test và validate Telegram Bot Token và Chat ID
"""
import requests
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def test_telegram_bot_token(bot_token: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Test Telegram bot token và chat ID
    
    Args:
        bot_token: Telegram Bot Token (format: số:dấu:chuỗi)
        chat_id: Chat ID (Group ID - số âm) để nhận thông báo
    
    Returns:
        {
            "valid": bool,
            "status": str,
            "message": str,
            "bot_info": dict,
            "chat_info": dict
        }
    """
    try:
        if not bot_token:
            return {
                "valid": False,
                "status": "INVALID",
                "message": "Bot Token không được để trống",
                "bot_info": None,
                "chat_info": None
            }
        
        bot_token = bot_token.strip()
        
        # Kiểm tra format bot token (số:dấu:chuỗi)
        if not re.match(r'^\d+:[A-Za-z0-9_-]+$', bot_token):
            return {
                "valid": False,
                "status": "INVALID",
                "message": "Bot Token không đúng format. Phải có dạng: số:dấu:chuỗi",
                "bot_info": None,
                "chat_info": None
            }
        
        # Test bot token với Telegram API
        test_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(test_url, timeout=10)
        
        if response.status_code != 200:
            result = response.json()
            return {
                "valid": False,
                "status": "INVALID",
                "message": result.get("description", "Lỗi không xác định khi kiểm tra Bot Token"),
                "bot_info": None,
                "chat_info": None
            }
        
        result = response.json()
        if not result.get("ok"):
            return {
                "valid": False,
                "status": "INVALID",
                "message": result.get("description", "Bot Token không hợp lệ"),
                "bot_info": None,
                "chat_info": None
            }
        
        bot_info = result.get("result", {})
        
        # Nếu có chat_id, test chat ID
        chat_info = None
        if chat_id:
            chat_id = chat_id.strip()
            try:
                chat_id_num = int(chat_id)
                # Kiểm tra chat ID phải là số âm (group)
                if chat_id_num > 0:
                    return {
                        "valid": False,
                        "status": "INVALID",
                        "message": "Chat ID phải là số âm (Group ID). Chat ID dương là chat cá nhân, không được phép.",
                        "bot_info": bot_info,
                        "chat_info": None
                    }
            except ValueError:
                return {
                    "valid": False,
                    "status": "INVALID",
                    "message": "Chat ID không hợp lệ. Phải là số (Group ID phải là số âm).",
                    "bot_info": bot_info,
                    "chat_info": None
                }
            
            # Test chat ID bằng cách lấy thông tin chat
            chat_url = f"https://api.telegram.org/bot{bot_token}/getChat"
            chat_response = requests.get(chat_url, params={"chat_id": chat_id}, timeout=10)
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                if chat_result.get("ok"):
                    chat_info = chat_result.get("result", {})
                else:
                    return {
                        "valid": False,
                        "status": "INVALID",
                        "message": f"Không thể truy cập chat với ID {chat_id}. Bot có thể chưa được thêm vào nhóm hoặc Chat ID không đúng.",
                        "bot_info": bot_info,
                        "chat_info": None
                    }
            else:
                return {
                    "valid": False,
                    "status": "INVALID",
                    "message": f"Lỗi khi kiểm tra Chat ID: {chat_response.status_code}",
                    "bot_info": bot_info,
                    "chat_info": None
                }
        
        return {
            "valid": True,
            "status": "VALID",
            "message": "Bot Token và Chat ID hợp lệ" if chat_id else "Bot Token hợp lệ",
            "bot_info": bot_info,
            "chat_info": chat_info
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error testing Telegram bot token: {e}", exc_info=True)
        return {
            "valid": False,
            "status": "ERROR",
            "message": f"Lỗi kết nối đến Telegram API: {str(e)}",
            "bot_info": None,
            "chat_info": None
        }
    except Exception as e:
        logger.error(f"Error testing Telegram bot token: {e}", exc_info=True)
        return {
            "valid": False,
            "status": "ERROR",
            "message": f"Lỗi không mong muốn: {str(e)}",
            "bot_info": None,
            "chat_info": None
        }

