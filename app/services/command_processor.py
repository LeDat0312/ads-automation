"""
Command Processor Service
Xử lý các lệnh Telegram (nhẹ và nặng)
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from app.services.telegram_bot import send_message, send_chat_action, parse_command, edit_message, delete_message
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
            f"❌ **Lệnh không hợp lệ**\n\nLệnh `{cmd}` không tồn tại.\n\nVui lòng sử dụng lệnh `/help` để xem danh sách lệnh có sẵn.",
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
        from app.services.telegram_bot import send_message, edit_message
        from app.core.config import get_settings
        
        settings = get_settings()
        chat_id = payload.get('chat_id')
        message_id = payload.get('message_id')
        
        # Gửi message ban đầu và lấy message_id để edit
        progress_message_id = None
        if chat_id:
            try:
                success, result = send_message(
                    chat_id,
                    "⏳ Đang xử lý...",
                    settings.TELEGRAM_BOT_TOKEN,
                    reply_to_message_id=message_id
                )
                if success and isinstance(result, int):
                    progress_message_id = result
            except Exception as e:
                logger.error(f"❌ Error sending initial message: {e}")
        
        def send_progress(msg: str):
            """Gửi progress update - edit message nếu có progress_message_id"""
            if chat_id:
                try:
                    if progress_message_id:
                        edit_message(chat_id, progress_message_id, msg, settings.TELEGRAM_BOT_TOKEN)
                    else:
                        # Fallback: gửi message mới
                        send_message(chat_id, msg, settings.TELEGRAM_BOT_TOKEN, reply_to_message_id=message_id)
                except Exception as e:
                    logger.error(f"❌ Error sending progress: {e}")
        
        try:
            # Bước 1: Pull data mới từ Facebook
            send_progress("📥 Đang pull dữ liệu từ Facebook...")
            pull_msg, pull_count = CommandProcessor._pull_and_save_data(
                chat_id=chat_id,
                message_id=message_id,
                progress_message_id=progress_message_id,
                progress_callback=send_progress
            )
            pull_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Nếu có lỗi khi pull, trả về luôn
            if pull_msg.startswith("❌"):
                return pull_msg
            
            # Bước 2: Tạo báo cáo tổng hợp (theo logic tongKetCuoiNgay)
            send_progress("📊 Đang tạo báo cáo tổng hợp...")
            
            from app.core.database import get_db_session, AdMetrics
            from sqlalchemy import func
            from collections import defaultdict
            
            db = get_db_session()
            try:
                # Tổng kết theo account và prefix
                # Chỉ tính các ad có impressions > 0
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                metrics = db.query(AdMetrics).filter(
                    AdMetrics.impressions > 0,
                    AdMetrics.date >= today
                ).all()
                
                # Aggregate: { account_id: { prefix: {spend, interactions, phones} } }
                agg = defaultdict(lambda: defaultdict(lambda: {'spend': 0, 'interactions': 0, 'phones': 0}))
                
                for m in metrics:
                    if not m.account_id or not m.prefix:
                        continue
                    
                    # Interactions = results (comments + messages)
                    interactions = m.results or 0
                    # Phones = purchases (checkouts initiated)
                    phones = m.purchases or 0
                    
                    agg[m.account_id][m.prefix]['spend'] += m.spend or 0
                    agg[m.account_id][m.prefix]['interactions'] += interactions
                    agg[m.account_id][m.prefix]['phones'] += phones
                
                # Tạo báo cáo
                lines = []
                lines.append('🧾 **TỔNG KẾT CUỐI NGÀY**')
                lines.append('━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                
                for account_id in sorted(agg.keys()):
                    lines.append(f'\n📛 **Tài khoản:** `{account_id}`')
                    
                    for prefix in sorted(agg[account_id].keys()):
                        a = agg[account_id][prefix]
                        cpd = (a['spend'] / a['interactions']) if a['interactions'] > 0 else 0
                        cpphone = (a['spend'] / a['phones']) if a['phones'] > 0 else 0
                        phone_rate = (a['phones'] / a['interactions'] * 100) if a['interactions'] > 0 else 0
                        
                        lines.append(f'  — **{prefix}:**')
                        lines.append(f'    • Chi tiêu: {a["spend"]:,.0f} ₫')
                        lines.append(f'    • Tương tác: {int(a["interactions"])}')
                        lines.append(f'    • Giá DATA: {cpd:,.0f} ₫')
                        lines.append(f'    • SĐT (checkout): {int(a["phones"])}')
                        lines.append(f'    • Giá SĐT: {cpphone:,.0f} ₫')
                        lines.append(f'    • Tỷ lệ SĐT/Tương tác: {phone_rate:.1f}%')
                
                lines.append(f'\n⏰ **Thời gian:** {datetime.now().strftime("%H:%M ngày %d/%m/%Y")}')
                
                report = '\n'.join(lines)
                return report
            except Exception as e:
                logger.error(f"❌ Error generating report: {e}", exc_info=True)
                return f"❌ Lỗi tạo báo cáo: {str(e)}"
            finally:
                db.close()
            
        except Exception as e:
            error_msg = f"❌ **LỖI NGHIÊM TRỌNG:** {str(e)}"
            logger.error(f"❌ Error generating report: {e}", exc_info=True)
            send_progress(error_msg)
            return error_msg
    
    @staticmethod
    def _pull_and_save_data(chat_id: Optional[str] = None, message_id: Optional[int] = None, progress_message_id: Optional[int] = None, progress_callback=None) -> Tuple[str, int]:
        """
        Pull data từ Facebook và lưu vào database
        Returns: (message, count)
        
        Args:
            chat_id: Chat ID để gửi progress updates
            message_id: Message ID để reply
            progress_message_id: Message ID của progress message (để edit)
            progress_callback: Callback function(progress_msg) để gửi updates
        """
        from app.services.facebook_api import pull_facebook_data
        from app.core.database import get_db_session, AdMetrics
        from app.core.config import get_settings
        from app.services.telegram_bot import send_message, edit_message
        
        settings = get_settings()
        start_time = datetime.now()
        
        def send_progress(msg: str):
            """Gửi progress update - chỉ edit 1 message duy nhất"""
            if progress_callback:
                progress_callback(msg)
            elif chat_id and progress_message_id:
                try:
                    # Chỉ edit message hiện có, không tạo mới
                    edit_message(chat_id, progress_message_id, msg, settings.TELEGRAM_BOT_TOKEN)
                except Exception as e:
                    logger.error(f"❌ Error editing progress: {e}")
                    pass
        
        try:
            # Bước 1: Pull data - chỉ hiển thị 1 lần
            send_progress("📥 Đang pull dữ liệu từ Facebook...")
            logger.info("📥 Đang pull dữ liệu từ Facebook API...")
            
            ad_metrics_list = pull_facebook_data(
                settings.ACCESS_TOKEN,
                settings.ad_account_ids_list,
                settings.DATA_DATE_PRESET
            )
            
            if not ad_metrics_list:
                send_progress("⚠️ Không có dữ liệu mới từ Facebook")
                return "⚠️ Không có dữ liệu mới từ Facebook", 0
            
            # Bước 2: Lưu vào database - chỉ hiển thị khi bắt đầu và kết thúc
            send_progress(f"💾 Đang lưu {len(ad_metrics_list)} ads vào database...")
            db = get_db_session()
            try:
                count = 0
                total = len(ad_metrics_list)
                for idx, ad_metric in enumerate(ad_metrics_list):
                    # KHÔNG gửi progress update trong loop - chỉ edit khi hoàn thành
                    
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
                        # Chỉ giữ các fields có trong model AdMetrics
                        valid_fields = {
                            'adset_id', 'ad_id', 'ad_name', 'adset_name', 'campaign_name',
                            'account_id', 'prefix', 'spend', 'impressions', 'clicks', 'results',
                            'ctr', 'cpc', 'cpa', 'roas', 'gia_data', 'sdt', 'gia_sdt', 'ty_le_sdt',
                            'adset_status', 'effective_status', 'date', 'date_preset',
                            'campaign_type', 'campaign_objective', 'amount_spent', 'ket_qua',
                            'purchases', 'purchase_value', 'revenue', 'leads', 'phone_calls',
                            'cost_per_lead'
                            # Loại bỏ: 'reach', 'frequency', 'account_name', 'percent_ads', 
                            # 'cost_per_checkout_initiated', 'checkouts_initiated', 'gia_tri_chuyen_doi_tu_luot_mua',
                            # 'cpm', 'clicks_all', 'ctr_all', 'cpc_all', 'cost_per_comment',
                            # 'cost_per_messaging_conversation', 'post_comments', 'messaging_conversations_started'
                        }
                        filtered_metric = {k: v for k, v in ad_metric.items() if k in valid_fields}
                        new_metric = AdMetrics(**filtered_metric)
                        db.add(new_metric)
                        count += 1
                
                db.commit()
                elapsed = (datetime.now() - start_time).total_seconds()
                message = f"✅ Đã pull {len(ad_metrics_list)} ads ({count} mới) trong {elapsed:.1f}s"
                logger.info(message)
                # Không gửi progress ở đây - để handler gửi kết quả cuối cùng
                # Chỉ log, không gửi Telegram
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
        from app.services.telegram_bot import send_message, edit_message
        from app.core.config import get_settings
        from sqlalchemy import func, distinct
        
        settings = get_settings()
        chat_id = payload.get('chat_id')
        message_id = payload.get('message_id')
        
        # Gửi message ban đầu và lấy message_id để edit
        progress_message_id = None
        if chat_id:
            try:
                success, result = send_message(
                    chat_id,
                    "⏳ Đang xử lý...",
                    settings.TELEGRAM_BOT_TOKEN,
                    reply_to_message_id=message_id
                )
                if success and isinstance(result, int):
                    progress_message_id = result
            except Exception as e:
                logger.error(f"❌ Error sending initial message: {e}")
        
        def send_progress(msg: str):
            """Gửi progress update - edit message nếu có progress_message_id"""
            if chat_id:
                try:
                    if progress_message_id:
                        edit_message(chat_id, progress_message_id, msg, settings.TELEGRAM_BOT_TOKEN)
                    else:
                        # Fallback: gửi message mới
                        send_message(chat_id, msg, settings.TELEGRAM_BOT_TOKEN, reply_to_message_id=message_id)
                except Exception as e:
                    logger.error(f"❌ Error sending progress: {e}")
        
        try:
            # Bước 1: Pull data mới từ Facebook
            send_progress("📥 Đang pull dữ liệu từ Facebook...")
            pull_msg, pull_count = CommandProcessor._pull_and_save_data(
                chat_id=chat_id,
                message_id=message_id,
                progress_message_id=progress_message_id,
                progress_callback=send_progress
            )
            pull_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Nếu có lỗi khi pull, trả về luôn
            if pull_msg.startswith("❌"):
                return pull_msg
            
            # Bước 2: Tạo báo cáo (theo logic từ Google Script)
            send_progress("📊 Đang tạo báo cáo...")
            db = get_db_session()
            
            try:
                from collections import defaultdict
                
                # Lấy tất cả metrics hôm nay
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                metrics = db.query(AdMetrics).filter(
                    AdMetrics.date >= today
                ).all()
                
                # Thống kê theo account và prefix: { accountId: { prefix: { enabled, active, paused, total } } }
                stats_by_account = defaultdict(lambda: defaultdict(lambda: {
                    'enabled': 0,  # Ads bật hôm nay (impressions > 0 và status = ACTIVE)
                    'active': 0,   # Adsets đang bật
                    'paused': 0,   # Adsets đã tắt
                    'total': 0     # Tổng adsets
                }))
                
                adset_ids_seen = set()  # Để đếm unique adsets
                
                for m in metrics:
                    if not m.account_id or not m.prefix or not m.adset_id:
                        continue
                    
                    # Key để check unique adset
                    adset_key = f"{m.account_id}|{m.adset_id}"
                    
                    if adset_key not in adset_ids_seen:
                        adset_ids_seen.add(adset_key)
                        stats_by_account[m.account_id][m.prefix]['total'] += 1
                        
                        # Đếm ads bật hôm nay (impressions > 0 và status = ACTIVE)
                        if m.adset_status == 'ACTIVE' and (m.impressions or 0) > 0:
                            stats_by_account[m.account_id][m.prefix]['enabled'] += 1
                            stats_by_account[m.account_id][m.prefix]['active'] += 1
                        elif m.adset_status == 'ACTIVE':
                            stats_by_account[m.account_id][m.prefix]['active'] += 1
                        elif m.adset_status == 'PAUSED':
                            stats_by_account[m.account_id][m.prefix]['paused'] += 1
                
                # Tạo báo cáo
                lines = []
                lines.append('📊 **BÁO CÁO TỔNG KẾT**')
                lines.append('━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                
                total_enabled_all = 0
                total_active_all = 0
                total_paused_all = 0
                total_adsets_all = 0
                
                for account_id in sorted(stats_by_account.keys()):
                    lines.append(f'\n📌 **Tài khoản:** `{account_id}`')
                    
                    account_enabled = 0
                    account_active = 0
                    account_paused = 0
                    account_total = 0
                    
                    for prefix in sorted(stats_by_account[account_id].keys()):
                        prefix_stats = stats_by_account[account_id][prefix]
                        lines.append(f'  • **{prefix}:**')
                        lines.append(f'    - Ads bật hôm nay (impressions > 0): {prefix_stats["enabled"]}')
                        lines.append(f'    - Adsets đang bật: {prefix_stats["active"]}')
                        lines.append(f'    - Adsets đã tắt: {prefix_stats["paused"]}')
                        lines.append(f'    - Tổng adsets: {prefix_stats["total"]}')
                        
                        account_enabled += prefix_stats['enabled']
                        account_active += prefix_stats['active']
                        account_paused += prefix_stats['paused']
                        account_total += prefix_stats['total']
                    
                    lines.append(f'  **Tổng Account:** Bật={account_enabled}, Đang bật={account_active}, Đã tắt={account_paused}, Tổng={account_total}\n')
                    
                    total_enabled_all += account_enabled
                    total_active_all += account_active
                    total_paused_all += account_paused
                    total_adsets_all += account_total
                
                lines.append('━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                lines.append('**TỔNG TẤT CẢ:**')
                lines.append(f'  • Ads bật hôm nay (impressions > 0): {total_enabled_all}')
                lines.append(f'  • Adsets đang bật: {total_active_all}')
                lines.append(f'  • Adsets đã tắt: {total_paused_all}')
                lines.append(f'  • Tổng adsets: {total_adsets_all}')
                lines.append(f'\n⏰ **Thời gian:** {datetime.now().strftime("%H:%M ngày %d/%m/%Y")}')
                
                report = '\n'.join(lines)
                return report
            except Exception as e:
                error_msg = f"❌ **LỖI khi đọc database:** {str(e)}"
                logger.error(error_msg, exc_info=True)
                send_progress(error_msg)
                return error_msg
            finally:
                db.close()
            
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

