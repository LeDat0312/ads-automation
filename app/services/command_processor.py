"""
Command Processor Service
Xử lý các lệnh Telegram (nhẹ và nặng)
"""
import logging
from typing import Dict, Any, Optional
from app.services.telegram_bot import send_message, send_chat_action, parse_command
from app.services.job_queue import JobQueue, JobPriority
from app.core.config import get_settings

logger = logging.getLogger(__name__)


# Lệnh nhẹ - xử lý inline
LIGHT_COMMANDS = {
    '/help': 'handle_help',
    '/myid': 'handle_myid',
    '/check_webhook': 'handle_check_webhook',
    '/start': 'handle_start',
}

# Lệnh nặng - cần enqueue job
HEAVY_COMMANDS = {
    '/report': 'handle_report',
    '/statusads': 'handle_statusads',
    '/run': 'handle_run_automation',
    '/test': 'handle_test_automation',
}


class CommandProcessor:
    """Xử lý commands từ Telegram"""
    
    def __init__(self):
        self.settings = get_settings()
        self.job_queue = JobQueue()
    
    def process_command(self, parsed: Dict[str, Any]) -> bool:
        """
        Xử lý command
        Trả về True nếu đã xử lý (inline hoặc enqueued)
        """
        cmd = parsed.get('cmd')
        chat_id = parsed.get('chat_id')
        user_id = parsed.get('user_id')
        message_id = parsed.get('message_id')
        
        if not cmd:
            return False
        
        # Lệnh nhẹ - xử lý inline
        if cmd in LIGHT_COMMANDS:
            handler_name = LIGHT_COMMANDS[cmd]
            handler = getattr(self, handler_name, None)
            if handler:
                try:
                    response = handler(parsed)
                    if response:
                        send_message(
                            chat_id,
                            response,
                            self.settings.TELEGRAM_BOT_TOKEN,
                            reply_to_message_id=message_id
                        )
                    return True
                except Exception as e:
                    logger.error(f"❌ Error handling {cmd}: {e}")
                    send_message(
                        chat_id,
                        f"❌ Lỗi: {str(e)}",
                        self.settings.TELEGRAM_BOT_TOKEN,
                        reply_to_message_id=message_id
                    )
            return False
        
        # Lệnh nặng - enqueue job
        if cmd in HEAVY_COMMANDS:
            try:
                # Gửi "Đang xử lý..."
                send_chat_action(chat_id, 'typing', self.settings.TELEGRAM_BOT_TOKEN)
                send_message(
                    chat_id,
                    "⏳ Đang xử lý...",
                    self.settings.TELEGRAM_BOT_TOKEN,
                    reply_to_message_id=message_id
                )
                
                # Enqueue job
                self.job_queue.enqueue_job(
                    job_type='telegram_command',
                    payload={
                        'command': cmd,
                        'args': parsed.get('args', ''),
                        'chat_id': chat_id,
                        'user_id': user_id,
                        'message_id': message_id,
                        'update_id': parsed.get('update_id')
                    },
                    priority=JobPriority.LOW,
                    chat_id=chat_id,
                    user_id=user_id
                )
                return True
            except ValueError as e:
                # Rate limit
                send_message(
                    chat_id,
                    f"⚠️ {str(e)}",
                    self.settings.TELEGRAM_BOT_TOKEN,
                    reply_to_message_id=message_id
                )
                return True
            except Exception as e:
                logger.error(f"❌ Error enqueueing {cmd}: {e}")
                send_message(
                    chat_id,
                    f"❌ Lỗi: {str(e)}",
                    self.settings.TELEGRAM_BOT_TOKEN,
                    reply_to_message_id=message_id
                )
                return False
        
        # Command không tồn tại
        send_message(
            chat_id,
            f"❓ Lệnh không tồn tại. Dùng /help để xem danh sách lệnh.",
            self.settings.TELEGRAM_BOT_TOKEN,
            reply_to_message_id=message_id
        )
        return False
    
    # ===== Light command handlers =====
    
    def handle_help(self, parsed: Dict[str, Any]) -> str:
        """Xử lý /help"""
        return """📋 **Danh sách lệnh:**

**Lệnh nhanh:**
/help - Hiển thị danh sách lệnh
/myid - Lấy Chat ID
/check_webhook - Kiểm tra webhook

**Lệnh báo cáo:**
/report - Báo cáo tổng hợp
/statusads - Trạng thái quảng cáo
/run - Chạy automation
/test - Test automation (bỏ qua khung giờ)
"""
    
    def handle_myid(self, parsed: Dict[str, Any]) -> str:
        """Xử lý /myid"""
        chat_id = parsed.get('chat_id', 'N/A')
        user_id = parsed.get('user_id', 'N/A')
        return f"""🆔 **Thông tin:**

Chat ID: `{chat_id}`
User ID: `{user_id}`
"""
    
    def handle_check_webhook(self, parsed: Dict[str, Any]) -> str:
        """Xử lý /check_webhook"""
        webhook_url = self.settings.WEBHOOK_URL or "Chưa cấu hình"
        return f"""🔗 **Webhook:**

URL: `{webhook_url}`
Status: ✅ Hoạt động
"""
    
    def handle_start(self, parsed: Dict[str, Any]) -> str:
        """Xử lý /start"""
        return """👋 **Chào mừng!**

Bot Facebook Ads Automation đã sẵn sàng.

Dùng /help để xem danh sách lệnh.
"""
    
    # ===== Heavy command handlers (sẽ được gọi từ worker) =====
    
    @staticmethod
    def handle_report(payload: Dict[str, Any]) -> str:
        """Xử lý /report (được gọi từ worker)"""
        # TODO: Implement report logic
        return "📊 Báo cáo đang được tạo..."
    
    @staticmethod
    def handle_statusads(payload: Dict[str, Any]) -> str:
        """Xử lý /statusads (được gọi từ worker)"""
        # TODO: Implement statusads logic
        return "📈 Trạng thái quảng cáo đang được kiểm tra..."
    
    @staticmethod
    def handle_run_automation(payload: Dict[str, Any]) -> str:
        """Xử lý /run (được gọi từ worker)"""
        # TODO: Implement run automation logic
        return "🚀 Automation đang chạy..."
    
    @staticmethod
    def handle_test_automation(payload: Dict[str, Any]) -> str:
        """Xử lý /test (được gọi từ worker)"""
        # TODO: Implement test automation logic
        return "🧪 Test automation đang chạy..."

