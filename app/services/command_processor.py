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
    '/report': 'handle_report',  # Kết hợp cả báo cáo tài chính và trạng thái
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
/report - Báo cáo tổng hợp (tài chính + trạng thái)
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
    def handle_report(payload: Dict[str, Any]) -> Optional[str]:
        """
        Xử lý /report - Kết hợp báo cáo tài chính và trạng thái
        Bao gồm:
        1. Báo cáo tài chính (từ tongKetCuoiNgay): Chi tiêu, Tương tác, Giá DATA, SĐT, Giá SĐT
        2. Báo cáo trạng thái (từ generateSummaryReport): Ads bật, Adsets đang bật, Adsets đã tắt
        """
        from app.services.telegram_bot import send_message, edit_message
        from app.core.config import get_settings
        from app.core.database import get_db_session, AdMetrics
        from app.services.prefix_helper import extract_prefixes_from_logic_rules, has_allowed_prefix
        from collections import defaultdict
        from sqlalchemy import func, and_
        from pytz import timezone as tz
        
        settings = get_settings()
        chat_id = payload.get('chat_id')
        message_id = payload.get('message_id')
        progress_message_id = payload.get('progress_message_id')
        
        def send_progress(msg: str):
            """Gửi progress update - chỉ edit message, không tạo mới"""
            if chat_id and progress_message_id:
                try:
                    edit_message(chat_id, progress_message_id, msg, settings.TELEGRAM_BOT_TOKEN)
                except Exception as e:
                    logger.error(f"❌ Error editing progress: {e}")
        
        try:
            # Bước 1: Pull data mới từ Facebook
            # _pull_and_save_data sẽ tự gửi progress qua progress_callback
            pull_msg, pull_count = CommandProcessor._pull_and_save_data(
                chat_id=chat_id,
                message_id=message_id,
                progress_message_id=progress_message_id,
                progress_callback=send_progress
            )
            
            # Nếu có lỗi khi pull, edit message và return None
            if pull_msg.startswith("❌"):
                if chat_id and progress_message_id:
                    try:
                        edit_message(chat_id, progress_message_id, pull_msg, settings.TELEGRAM_BOT_TOKEN)
                    except:
                        pass
                return None  # Không trả về để worker không gửi duplicate
            
            # Bước 2: Tạo báo cáo kết hợp (tài chính + trạng thái)
            send_progress("📊 Đang tạo báo cáo tổng hợp...")
            
            db = get_db_session()
            try:
                # Lấy danh sách prefix được phép từ LogicRules
                allowed_prefixes = extract_prefixes_from_logic_rules()
                
                if not allowed_prefixes:
                    logger.warning("⚠️ Không đọc được prefix từ LogicRules, dùng danh sách mặc định")
                    allowed_prefixes = ['PX', 'TL', 'FL', 'NM', 'CCHL', 'DHHL', 'HSHL', 'CCB']
                
                logger.info(f"📋 Prefix được sử dụng: {', '.join(allowed_prefixes)}")
                
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                # ===== PHẦN 1: BÁO CÁO TÀI CHÍNH (từ tongKetCuoiNgay) =====
                # Lấy metrics có impressions > 0 để tính tài chính
                metrics_financial = db.query(AdMetrics).filter(
                    AdMetrics.impressions > 0
                ).all()
                
                # Aggregate tài chính: { account_id: { prefix: {spend, interactions, phones} } }
                agg_financial = defaultdict(lambda: defaultdict(lambda: {'spend': 0.0, 'interactions': 0, 'phones': 0}))
                account_ids = set()
                
                for m in metrics_financial:
                    if not m.account_id or not m.campaign_name:
                        continue
                    
                    prefix = has_allowed_prefix(m.campaign_name, allowed_prefixes)
                    if not prefix:
                        continue
                    
                    account_id = str(m.account_id).strip()
                    account_ids.add(account_id)
                    
                    interactions = int(m.results or 0)
                    phones = int(m.sdt or 0)
                    spend = float(m.spend or 0)
                    
                    agg_financial[account_id][prefix]['spend'] += spend
                    agg_financial[account_id][prefix]['interactions'] += interactions
                    agg_financial[account_id][prefix]['phones'] += phones
                
                # ===== PHẦN 2: BÁO CÁO TRẠNG THÁI (từ generateSummaryReport) =====
                # Lấy metrics hôm nay để tính spend và enabled
                metrics_today = db.query(AdMetrics).filter(
                    AdMetrics.date >= today
                ).all()
                
                # Lấy tất cả unique adsets với status mới nhất
                latest_updates = db.query(
                    AdMetrics.adset_id,
                    AdMetrics.account_id,
                    func.max(AdMetrics.updated_at).label('max_updated_at')
                ).group_by(
                    AdMetrics.adset_id,
                    AdMetrics.account_id
                ).subquery()
                
                all_adsets = db.query(
                    AdMetrics.adset_id,
                    AdMetrics.account_id,
                    AdMetrics.campaign_name,
                    AdMetrics.adset_status
                ).join(
                    latest_updates,
                    and_(
                        AdMetrics.adset_id == latest_updates.c.adset_id,
                        AdMetrics.account_id == latest_updates.c.account_id,
                        AdMetrics.updated_at == latest_updates.c.max_updated_at
                    )
                ).distinct().all()
                
                # Thống kê trạng thái: { accountId: { prefix: { enabled, active, paused, spend } } }
                stats_by_account = defaultdict(lambda: defaultdict(lambda: {
                    'enabled': 0,  # Ads bật hôm nay (impressions > 0 của ngày hôm nay)
                    'active': 0,   # Adsets đang bật (impressions > 0 và status = ACTIVE)
                    'paused': 0,   # Adsets đã tắt (impressions > 0 và status = PAUSED)
                    'spend': 0.0  # Tổng số tiền chi tiêu (hôm nay)
                }))
                
                # Dictionary để lưu status mới nhất của mỗi adset
                adset_status_map = {}
                
                # Thu thập status của tất cả adsets
                for row in all_adsets:
                    if not row.account_id or not row.campaign_name or not row.adset_id:
                        continue
                    
                    prefix = has_allowed_prefix(row.campaign_name, allowed_prefixes)
                    if not prefix:
                        continue
                    
                    adset_key = f"{row.account_id}|{row.adset_id}"
                    if adset_key not in adset_status_map:
                        adset_status_map[adset_key] = {
                            'status': row.adset_status,
                            'account_id': row.account_id,
                            'prefix': prefix,
                            'campaign_name': row.campaign_name
                        }
                
                # Tính spend, enabled, active, paused từ metrics hôm nay
                # Logic chính xác:
                # - enabled: đếm số ads có impressions > 0 hôm nay (theo prefix)
                # - active: đếm số adsets unique có impressions > 0 và status = ACTIVE (theo prefix)
                # - paused: đếm số adsets unique có impressions > 0 và status = PAUSED (theo prefix)
                adset_keys_with_impressions = {}  # {adset_key: {account_id, prefix, status}} để đếm unique adsets
                
                for m in metrics_today:
                    if not m.account_id or not m.campaign_name or not m.adset_id:
                        continue
                    
                    prefix = has_allowed_prefix(m.campaign_name, allowed_prefixes)
                    if not prefix:
                        continue
                    
                    impressions = m.impressions or 0
                    adset_key = f"{m.account_id}|{m.adset_id}"
                    
                    if impressions > 0:
                        # Tính spend
                        stats_by_account[m.account_id][prefix]['spend'] += m.spend or 0
                        
                        # Đếm ads bật hôm nay (mỗi ad có impressions > 0 = 1 ads bật)
                        stats_by_account[m.account_id][prefix]['enabled'] += 1
                        
                        # Lưu thông tin adset có impressions > 0 (chỉ lưu 1 lần cho mỗi adset)
                        if adset_key not in adset_keys_with_impressions:
                            # Ưu tiên lấy status từ metric hiện tại (chính xác nhất)
                            # Nếu không có, lấy từ adset_status_map
                            status = m.adset_status
                            if not status or status == '':
                                if adset_key in adset_status_map:
                                    status = adset_status_map[adset_key]['status']
                            
                            # Nếu vẫn không có, mặc định là ACTIVE
                            if not status or status == '':
                                status = 'ACTIVE'
                            
                            adset_keys_with_impressions[adset_key] = {
                                'account_id': m.account_id,
                                'prefix': prefix,
                                'status': status
                            }
                            
                            # Đếm adsets theo status (chỉ đếm 1 lần cho mỗi adset)
                            if status == 'ACTIVE':
                                stats_by_account[m.account_id][prefix]['active'] += 1
                            elif status == 'PAUSED':
                                stats_by_account[m.account_id][prefix]['paused'] += 1
                
                # ===== TẠO BÁO CÁO KẾT HỢP =====
                # Format block card style - dễ đọc trên cả mobile và desktop
                lines = []
                lines.append('📊 *BÁO CÁO TỔNG HỢP*')
                lines.append('━' * 23)
                
                # Tổng kết theo từng account
                sorted_account_ids = sorted(account_ids)
                
                total_enabled_all = 0
                total_active_all = 0
                total_paused_all = 0
                total_spend_all = 0.0
                
                for account_id in sorted_account_ids:
                    lines.append(f'\n📌 *Tài khoản:* `{account_id}`')
                    
                    account_enabled = 0
                    account_active = 0
                    account_paused = 0
                    account_spend_today = 0.0
                    
                    # Lấy danh sách prefix từ cả 2 báo cáo
                    financial_prefixes = set(agg_financial[account_id].keys())
                    status_prefixes = set(stats_by_account[account_id].keys())
                    all_prefixes = sorted(financial_prefixes | status_prefixes)
                    
                    for prefix in all_prefixes:
                        lines.append(f'\n🏷 *{prefix}*')
                        
                        # Phần tài chính - format block card
                        if prefix in agg_financial[account_id]:
                            a = agg_financial[account_id][prefix]
                            cpd = (a['spend'] / a['interactions']) if a['interactions'] > 0 else 0
                            cpphone = (a['spend'] / a['phones']) if a['phones'] > 0 else 0
                            phone_rate = (a['phones'] / a['interactions'] * 100) if a['interactions'] > 0 else 0
                            
                            # Format block card - mỗi metric 1 dòng
                            lines.append(f'💰 *Chi tiêu:* {a["spend"]:,.0f}₫')
                            lines.append(f'📈 *Tương tác:* {int(a["interactions"])}')
                            lines.append(f'💵 *Giá DATA:* {cpd:,.0f}₫')
                            lines.append(f'📞 *SĐT:* {int(a["phones"])}')
                            lines.append(f'💳 *Giá SĐT:* {cpphone:,.0f}₫')
                            lines.append(f'📊 *Tỷ lệ SĐT/Tương tác:* {phone_rate:.1f}%')
                        
                        # Phần trạng thái - format block card
                        if prefix in stats_by_account[account_id]:
                            s = stats_by_account[account_id][prefix]
                            lines.append(f'🟢 *Ads bật hôm nay:* {s["enabled"]}')
                            lines.append(f'🟩 *Adsets ACTIVE:* {s["active"]}')
                            lines.append(f'🟥 *Adsets PAUSED:* {s["paused"]}')
                            
                            account_enabled += s['enabled']
                            account_active += s['active']
                            account_paused += s['paused']
                            account_spend_today += s['spend']
                        
                        # Separator giữa các prefix
                        lines.append('━' * 23)
                    
                    # Tổng account - format compact
                    lines.append(f'\n📈 *Tổng Account*')
                    lines.append(f'✅ Bật: {account_enabled} | 🟩 Đang bật: {account_active} | 🟥 Đã tắt: {account_paused}')
                    lines.append(f'💰 *Chi tiêu hôm nay:* {account_spend_today:,.0f}₫')
                    
                    total_enabled_all += account_enabled
                    total_active_all += account_active
                    total_paused_all += account_paused
                    total_spend_all += account_spend_today
                
                # Tổng kết tất cả
                lines.append('\n' + '━' * 23)
                lines.append('📊 *TỔNG TẤT CẢ*')
                lines.append(f'✅ Bật: {total_enabled_all} | 🟩 Đang bật: {total_active_all} | 🟥 Đã tắt: {total_paused_all}')
                lines.append(f'💰 *Chi tiêu hôm nay:* {total_spend_all:,.0f}₫')
                
                # Thêm thời gian báo cáo
                tz_vn = tz('Asia/Ho_Chi_Minh')
                now = datetime.now(tz_vn)
                time_str = now.strftime('%H:%M')
                date_str = now.strftime('%d/%m/%Y')
                lines.append(f'\n⏰ *Cập nhật:* {time_str} ngày {date_str}')
                
                report = '\n'.join(lines)
                
                # Edit message cuối cùng và return None để tránh duplicate
                if chat_id and progress_message_id:
                    try:
                        edit_message(chat_id, progress_message_id, report, settings.TELEGRAM_BOT_TOKEN)
                        return None  # QUAN TRỌNG: Return None để worker không gửi duplicate
                    except Exception as e:
                        logger.error(f"❌ Error editing final message: {e}")
            return report
                
                return report
            except Exception as e:
                logger.error(f"❌ Error generating report: {e}", exc_info=True)
                error_msg = f"❌ **LỖI tạo báo cáo:** {str(e)}"
                send_progress(error_msg)
                if chat_id and progress_message_id:
                    try:
                        edit_message(chat_id, progress_message_id, error_msg, settings.TELEGRAM_BOT_TOKEN)
                    except:
                        pass
                return None  # Return None để tránh duplicate
            finally:
                db.close()
            
        except Exception as e:
            error_msg = f"❌ **LỖI NGHIÊM TRỌNG:** {str(e)}"
            logger.error(f"❌ Error generating report: {e}", exc_info=True)
            send_progress(error_msg)
            if chat_id and progress_message_id:
                try:
                    edit_message(chat_id, progress_message_id, error_msg, settings.TELEGRAM_BOT_TOKEN)
                except:
                    pass
            return None  # Return None để tránh duplicate
    
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
            # Ưu tiên dùng progress_callback nếu có (để tránh duplicate)
            if progress_callback:
                try:
                progress_callback(msg)
                except Exception as e:
                    logger.error(f"❌ Error in progress_callback: {e}")
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
    def handle_statusads(payload: Dict[str, Any]) -> Optional[str]:
        """Xử lý /statusads - Pull data mới và tạo báo cáo trạng thái"""
        from app.core.database import get_db_session, AdMetrics
        from app.services.telegram_bot import send_message, edit_message
        from app.core.config import get_settings
        from sqlalchemy import func, distinct
        
        settings = get_settings()
        chat_id = payload.get('chat_id')
        message_id = payload.get('message_id')
        
        # Lấy progress_message_id từ payload (đã được webhook gửi)
        progress_message_id = payload.get('progress_message_id')
        
        def send_progress(msg: str):
            """Gửi progress update - chỉ edit message, không tạo mới"""
            if chat_id and progress_message_id:
                try:
                    edit_message(chat_id, progress_message_id, msg, settings.TELEGRAM_BOT_TOKEN)
                except Exception as e:
                    logger.error(f"❌ Error editing progress: {e}")
        
        try:
            # Bước 1: Pull data mới từ Facebook
            # _pull_and_save_data sẽ tự gửi progress qua progress_callback, KHÔNG gửi ở đây
            pull_msg, pull_count = CommandProcessor._pull_and_save_data(
                chat_id=chat_id,
                message_id=message_id,
                progress_message_id=progress_message_id,
                progress_callback=send_progress
            )
            
            # Nếu có lỗi khi pull, edit message và return None
            if pull_msg.startswith("❌"):
                if chat_id and progress_message_id:
                    try:
                        edit_message(chat_id, progress_message_id, pull_msg, settings.TELEGRAM_BOT_TOKEN)
                    except:
                        pass
                return None  # Không trả về để worker không gửi duplicate
            
            # Bước 2: Tạo báo cáo (theo logic từ Google Script)
            send_progress("📊 Đang tạo báo cáo...")
            db = get_db_session()
            
            try:
                from collections import defaultdict
                from app.services.prefix_helper import extract_prefixes_from_logic_rules, has_allowed_prefix
                from pytz import timezone as tz
                
                # Lấy danh sách prefix được phép từ LogicRules
                allowed_prefixes = extract_prefixes_from_logic_rules()
                
                # Lấy tất cả unique adsets (không chỉ hôm nay) để đếm status chính xác
                # Query để lấy adset_id, account_id, campaign_name, status mới nhất
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Lấy metrics hôm nay để tính spend và enabled
                metrics_today = db.query(AdMetrics).filter(
                    AdMetrics.date >= today
                ).all()
                
                # Lấy tất cả unique adsets với status mới nhất
                # Dùng subquery để lấy record mới nhất của mỗi adset
                from sqlalchemy import desc, and_
                
                # Subquery: Lấy updated_at mới nhất của mỗi adset
                latest_updates = db.query(
                    AdMetrics.adset_id,
                    AdMetrics.account_id,
                    func.max(AdMetrics.updated_at).label('max_updated_at')
                ).group_by(
                    AdMetrics.adset_id,
                    AdMetrics.account_id
                ).subquery()
                
                # Query chính: Lấy status từ record có updated_at mới nhất
                all_adsets = db.query(
                    AdMetrics.adset_id,
                    AdMetrics.account_id,
                    AdMetrics.campaign_name,
                    AdMetrics.adset_status
                ).join(
                    latest_updates,
                    and_(
                        AdMetrics.adset_id == latest_updates.c.adset_id,
                        AdMetrics.account_id == latest_updates.c.account_id,
                        AdMetrics.updated_at == latest_updates.c.max_updated_at
                    )
                ).distinct().all()
                
                # Thống kê theo account và prefix: { accountId: { prefix: { enabled, active, paused, total, spend } } }
                stats_by_account = defaultdict(lambda: defaultdict(lambda: {
                    'enabled': 0,  # Ads bật hôm nay (impressions > 0 và status = ACTIVE)
                    'active': 0,   # Adsets đang bật (status = ACTIVE)
                    'paused': 0,   # Adsets đã tắt (status = PAUSED)
                    'total': 0,   # Tổng adsets
                    'spend': 0.0  # Tổng số tiền chi tiêu
                }))
                
                # Dictionary để lưu status mới nhất của mỗi adset
                adset_status_map = {}  # { adset_key: { status, account_id, prefix, campaign_name } }
                
                # Thu thập status của tất cả adsets
                for row in all_adsets:
                    if not row.account_id or not row.campaign_name or not row.adset_id:
                        continue
                    
                    prefix = has_allowed_prefix(row.campaign_name, allowed_prefixes)
                    if not prefix:
                        continue
                    
                    adset_key = f"{row.account_id}|{row.adset_id}"
                    if adset_key not in adset_status_map:
                        adset_status_map[adset_key] = {
                            'status': row.adset_status,
                            'account_id': row.account_id,
                            'prefix': prefix,
                            'campaign_name': row.campaign_name
                        }
                
                # Đếm adsets theo status
                for adset_key, adset_info in adset_status_map.items():
                    account_id = adset_info['account_id']
                    prefix = adset_info['prefix']
                    status = adset_info['status']
                    
                    stats_by_account[account_id][prefix]['total'] += 1
                    
                    if status == 'ACTIVE':
                        stats_by_account[account_id][prefix]['active'] += 1
                    elif status == 'PAUSED':
                        stats_by_account[account_id][prefix]['paused'] += 1
                
                # Tính spend và enabled từ metrics hôm nay
                for m in metrics_today:
                    if not m.account_id or not m.campaign_name or not m.adset_id:
                        continue
                    
                    prefix = has_allowed_prefix(m.campaign_name, allowed_prefixes)
                    if not prefix:
                        continue
                    
                    impressions = m.impressions or 0
                    adset_key = f"{m.account_id}|{m.adset_id}"
                    
                    # Tính tổng số tiền chi tiêu (chỉ tính các ad có impressions > 0)
                    if impressions > 0:
                        stats_by_account[m.account_id][prefix]['spend'] += m.spend or 0
                        
                        # Đếm ads bật hôm nay (impressions > 0 và status = ACTIVE)
                        if adset_key in adset_status_map and adset_status_map[adset_key]['status'] == 'ACTIVE':
                            stats_by_account[m.account_id][prefix]['enabled'] += 1
                
                # Tạo báo cáo với format đẹp và chuyên nghiệp
                lines = []
                lines.append('📊 **BÁO CÁO TỔNG KẾT**')
                lines.append('━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                
                total_enabled_all = 0
                total_active_all = 0
                total_paused_all = 0
                total_adsets_all = 0
                total_spend_all = 0.0
                
                for account_id in sorted(stats_by_account.keys()):
                    lines.append(f'\n📌 **Tài khoản:** `{account_id}`')
                    
                    account_enabled = 0
                    account_active = 0
                    account_paused = 0
                    account_total = 0
                    account_spend = 0.0
                    
                    for prefix in sorted(stats_by_account[account_id].keys()):
                        prefix_stats = stats_by_account[account_id][prefix]
                        lines.append(f'\n  🔹 **{prefix}:**')
                        lines.append(f'     ✅ Ads bật hôm nay: `{prefix_stats["enabled"]}`')
                        lines.append(f'     🟢 Adsets đang bật: `{prefix_stats["active"]}`')
                        lines.append(f'     🔴 Adsets đã tắt: `{prefix_stats["paused"]}`')
                        lines.append(f'     📦 Tổng adsets: `{prefix_stats["total"]}`')
                        lines.append(f'     💰 Chi tiêu: `{prefix_stats["spend"]:,.0f} ₫`')
                        
                        account_enabled += prefix_stats['enabled']
                        account_active += prefix_stats['active']
                        account_paused += prefix_stats['paused']
                        account_total += prefix_stats['total']
                        account_spend += prefix_stats['spend']
                    
                    lines.append(f'\n  📈 **Tổng Account:**')
                    lines.append(f'     ✅ Bật: `{account_enabled}` | 🟢 Đang bật: `{account_active}` | 🔴 Đã tắt: `{account_paused}` | 📦 Tổng: `{account_total}`')
                    lines.append(f'     💰 Chi tiêu: `{account_spend:,.0f} ₫`')
                    
                    total_enabled_all += account_enabled
                    total_active_all += account_active
                    total_paused_all += account_paused
                    total_adsets_all += account_total
                    total_spend_all += account_spend
                
                lines.append('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                lines.append('📊 **TỔNG TẤT CẢ:**')
                lines.append(f'  ✅ Ads bật hôm nay: `{total_enabled_all}`')
                lines.append(f'  🟢 Adsets đang bật: `{total_active_all}`')
                lines.append(f'  🔴 Adsets đã tắt: `{total_paused_all}`')
                lines.append(f'  📦 Tổng adsets: `{total_adsets_all}`')
                lines.append(f'  💰 Tổng chi tiêu: `{total_spend_all:,.0f} ₫`')
                
                # Thêm thời gian báo cáo (dùng timezone Asia/Ho_Chi_Minh - UTC+7)
                tz_vn = tz('Asia/Ho_Chi_Minh')
                now = datetime.now(tz_vn)
                time_str = now.strftime('%H:%M')
                date_str = now.strftime('%d/%m/%Y')
                lines.append(f'\n⏰ **Thời gian:** {time_str} ngày {date_str}')
                
                report = '\n'.join(lines)
                
                # Edit message cuối cùng thay vì trả về (để tránh duplicate)
                if chat_id and progress_message_id:
                    try:
                        edit_message(chat_id, progress_message_id, report, settings.TELEGRAM_BOT_TOKEN)
                        return None  # Không trả về để worker không gửi message mới
                    except Exception as e:
                        logger.error(f"❌ Error editing final message: {e}")
                        # Fallback: trả về để worker gửi message mới
                        return report
                
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

