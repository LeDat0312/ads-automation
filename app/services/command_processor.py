"""
Command Processor Service
Xử lý các lệnh Telegram (nhẹ và nặng)
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
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
        """Xử lý /report - Pull data mới và tạo báo cáo tổng hợp"""
        from app.services.telegram_bot import send_message
        from app.core.config import get_settings
        
        settings = get_settings()
        chat_id = payload.get('chat_id')
        message_id = payload.get('message_id')
        last_progress_msg = None  # Track last message để tránh duplicate
        
        def send_progress(msg: str):
            """Gửi progress update - chỉ gửi nếu message khác message trước"""
            nonlocal last_progress_msg
            if msg == last_progress_msg:
                return  # Skip duplicate
            last_progress_msg = msg
            
            if chat_id:
                try:
                    send_message(chat_id, msg, settings.TELEGRAM_BOT_TOKEN, reply_to_message_id=message_id)
                except Exception as e:
                    logger.error(f"❌ Error sending progress: {e}")
        
        try:
            # Bước 1: Pull data mới từ Facebook
            send_progress("📥 **Bắt đầu pull dữ liệu từ Facebook...**")
            pull_msg, pull_count = CommandProcessor._pull_and_save_data(
                chat_id=chat_id,
                message_id=message_id,
                progress_callback=send_progress
            )
            pull_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Nếu có lỗi khi pull, trả về luôn
            if pull_msg.startswith("❌"):
                return pull_msg
            
            # Bước 2: Tạo báo cáo tổng hợp
            send_progress("📊 **Đang tạo báo cáo tổng hợp...**")
            # TODO: Implement detailed report logic
            report = f"""📊 **BÁO CÁO TỔNG HỢP**

**Dữ liệu mới:**
{pull_msg}
⏰ Pull lúc: `{pull_time}`

**Báo cáo chi tiết đang được tạo...**

_Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}_
"""
            return report
            
        except Exception as e:
            error_msg = f"❌ **LỖI NGHIÊM TRỌNG:** {str(e)}"
            logger.error(f"❌ Error generating report: {e}", exc_info=True)
            send_progress(error_msg)
            return error_msg
    
    @staticmethod
    def _pull_and_save_data(chat_id: Optional[str] = None, message_id: Optional[int] = None, progress_callback=None) -> Tuple[str, int]:
        """
        Pull data từ Facebook và lưu vào database
        Returns: (message, count)
        
        Args:
            chat_id: Chat ID để gửi progress updates
            message_id: Message ID để reply
            progress_callback: Callback function(progress_msg) để gửi updates
        """
        from app.services.facebook_api import pull_facebook_data
        from app.core.database import get_db_session, AdMetrics
        from app.core.config import get_settings
        from app.services.telegram_bot import send_message
        
        settings = get_settings()
        start_time = datetime.now()
        last_progress_msg = None  # Track last message để tránh duplicate
        
        def send_progress(msg: str):
            """Gửi progress update - chỉ gửi nếu message khác message trước"""
            nonlocal last_progress_msg
            if msg == last_progress_msg:
                return  # Skip duplicate
            last_progress_msg = msg
            
            if progress_callback:
                progress_callback(msg)
            elif chat_id:
                try:
                    send_message(chat_id, msg, settings.TELEGRAM_BOT_TOKEN, reply_to_message_id=message_id)
                except:
                    pass
        
        try:
            # Bước 1: Bắt đầu pull
            send_progress("📥 **Bước 1/3:** Đang kết nối Facebook API...")
            logger.info("📥 Đang pull dữ liệu từ Facebook API...")
            
            # Pull data
            send_progress("📥 **Bước 2/3:** Đang pull dữ liệu từ Facebook...\n⏳ Vui lòng đợi, có thể mất 10-60 giây...")
            ad_metrics_list = pull_facebook_data(
                settings.ACCESS_TOKEN,
                settings.ad_account_ids_list,
                settings.DATA_DATE_PRESET
            )
            
            if not ad_metrics_list:
                send_progress("⚠️ Không có dữ liệu mới từ Facebook")
                return "⚠️ Không có dữ liệu mới từ Facebook", 0
            
            # Bước 2: Lưu vào database
            send_progress(f"💾 **Bước 3/3:** Đang lưu {len(ad_metrics_list)} ads vào database...")
            db = get_db_session()
            try:
                count = 0
                total = len(ad_metrics_list)
                for idx, ad_metric in enumerate(ad_metrics_list):
                    # Progress update mỗi 20%
                    if total > 10 and idx % max(1, total // 5) == 0:
                        progress_pct = int((idx / total) * 100)
                        send_progress(f"💾 Đang lưu: {progress_pct}% ({idx}/{total} ads)...")
                    
                    # Kiểm tra xem đã có chưa
                    existing = db.query(AdMetrics).filter(
                        AdMetrics.adset_id == ad_metric.get('adset_id'),
                        AdMetrics.ad_id == ad_metric.get('ad_id'),
                        AdMetrics.date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    ).first()
                    
                    if existing:
                        # Update - chỉ update các fields hợp lệ
                        for key, value in ad_metric.items():
                            if hasattr(existing, key) and not key.startswith('_'):
                                setattr(existing, key, value)
                        existing.updated_at = datetime.now()
                    else:
                        # Create new - chỉ lấy các fields hợp lệ cho AdMetrics
                        valid_fields = {
                            'adset_id', 'ad_id', 'ad_name', 'adset_name', 'campaign_name',
                            'account_id', 'prefix', 'spend', 'impressions', 'clicks', 'results',
                            'ctr', 'cpc', 'cpa', 'roas', 'gia_data', 'sdt', 'gia_sdt', 'ty_le_sdt',
                            'adset_status', 'effective_status', 'date', 'date_preset',
                            'campaign_type', 'campaign_objective', 'amount_spent', 'ket_qua',
                            'purchases', 'purchase_value', 'revenue', 'leads', 'phone_calls',
                            'cost_per_lead', 'reach', 'frequency'
                        }
                        filtered_metric = {k: v for k, v in ad_metric.items() if k in valid_fields}
                        new_metric = AdMetrics(**filtered_metric)
                        db.add(new_metric)
                        count += 1
                
                db.commit()
                elapsed = (datetime.now() - start_time).total_seconds()
                message = f"✅ Đã pull {len(ad_metrics_list)} ads ({count} mới) trong {elapsed:.1f}s"
                logger.info(message)
                send_progress(f"✅ {message}")
                return message, len(ad_metrics_list)
            except Exception as e:
                db.rollback()
                error_detail = f"❌ Lỗi khi lưu database: {str(e)}"
                logger.error(error_detail, exc_info=True)
                send_progress(error_detail)
                raise
            finally:
                db.close()
                
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            error_msg = f"❌ **LỖI:** {str(e)}\n⏱️ Sau {elapsed:.1f}s"
            logger.error(f"❌ Error pulling data: {e}", exc_info=True)
            send_progress(error_msg)
            return error_msg, 0
    
    @staticmethod
    def handle_statusads(payload: Dict[str, Any]) -> str:
        """Xử lý /statusads - Pull data mới và tạo báo cáo trạng thái"""
        from app.core.database import get_db_session, AdMetrics
        from app.services.telegram_bot import send_message
        from app.core.config import get_settings
        from sqlalchemy import func, distinct
        
        settings = get_settings()
        chat_id = payload.get('chat_id')
        message_id = payload.get('message_id')
        last_progress_msg = None  # Track last message để tránh duplicate
        
        def send_progress(msg: str):
            """Gửi progress update - chỉ gửi nếu message khác message trước"""
            nonlocal last_progress_msg
            if msg == last_progress_msg:
                return  # Skip duplicate
            last_progress_msg = msg
            
            if chat_id:
                try:
                    send_message(chat_id, msg, settings.TELEGRAM_BOT_TOKEN, reply_to_message_id=message_id)
                except Exception as e:
                    logger.error(f"❌ Error sending progress: {e}")
        
        try:
            # Bước 1: Pull data mới từ Facebook
            send_progress("📥 **Bắt đầu pull dữ liệu từ Facebook...**")
            pull_msg, pull_count = CommandProcessor._pull_and_save_data(
                chat_id=chat_id,
                message_id=message_id,
                progress_callback=send_progress
            )
            pull_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Nếu có lỗi khi pull, trả về luôn
            if pull_msg.startswith("❌"):
                return pull_msg
            
            # Bước 2: Tạo báo cáo
            send_progress("📊 **Đang tạo báo cáo...**")
            db = get_db_session()
            
            try:
                # Đếm adsets theo status
                active_adsets = db.query(func.count(distinct(AdMetrics.adset_id))).filter(
                    AdMetrics.adset_status == "ACTIVE"
                ).scalar() or 0
                
                paused_adsets = db.query(func.count(distinct(AdMetrics.adset_id))).filter(
                    AdMetrics.adset_status == "PAUSED"
                ).scalar() or 0
                
                # Tổng số adsets
                total_adsets = db.query(func.count(distinct(AdMetrics.adset_id))).scalar() or 0
                
                # Tổng số ads
                total_ads = db.query(func.count(AdMetrics.ad_id)).scalar() or 0
                
                # Tổng spend
                total_spend = db.query(func.sum(AdMetrics.spend)).scalar() or 0
                
                # Tổng results
                total_results = db.query(func.sum(AdMetrics.results)).scalar() or 0
            except Exception as e:
                error_msg = f"❌ **LỖI khi đọc database:** {str(e)}"
                logger.error(error_msg, exc_info=True)
                send_progress(error_msg)
                return error_msg
            finally:
                db.close()
            
            # Format báo cáo
            report = f"""📊 **BÁO CÁO TRẠNG THÁI ADS**

**Dữ liệu mới:**
{pull_msg}
⏰ Pull lúc: `{pull_time}`

**Trạng thái Adsets:**
• ✅ Đang bật: `{active_adsets:,}`
• ⏸️ Đã tắt: `{paused_adsets:,}`
• 📊 Tổng: `{total_adsets:,}`

**Tổng quan:**
• 📈 Tổng Ads: `{total_ads:,}`
• 💰 Tổng Spend: `{total_spend:,.0f}`
• 🎯 Tổng Results: `{total_results:,}`

_Thời gian báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}_
"""
            return report
            
        except Exception as e:
            error_msg = f"❌ **LỖI NGHIÊM TRỌNG:** {str(e)}"
            logger.error(f"❌ Error generating statusads report: {e}", exc_info=True)
            send_progress(error_msg)
            return error_msg
    
    @staticmethod
    def handle_run_automation(payload: Dict[str, Any]) -> str:
        """Xử lý /run - Chạy automation (trong khung giờ)"""
        from app.services.automation import run_automation
        
        try:
            # Chạy automation trong background thread
            import threading
            thread = threading.Thread(target=run_automation, daemon=True)
            thread.start()
            
            return "🚀 Automation đã được khởi động!\n\n⏳ Đang chạy trong background..."
        except Exception as e:
            logger.error(f"❌ Error running automation: {e}", exc_info=True)
            return f"❌ Lỗi khi chạy automation: {str(e)}"
    
    @staticmethod
    def handle_test_automation(payload: Dict[str, Any]) -> str:
        """Xử lý /test - Test automation (bỏ qua khung giờ)"""
        from app.services.automation import test_run_automation
        
        try:
            # Chạy test automation trong background thread
            import threading
            thread = threading.Thread(target=test_run_automation, daemon=True)
            thread.start()
            
            return "🧪 Test automation đã được khởi động!\n\n⏳ Đang chạy trong background (bỏ qua khung giờ)..."
        except Exception as e:
            logger.error(f"❌ Error running test automation: {e}", exc_info=True)
            return f"❌ Lỗi khi chạy test automation: {str(e)}"

