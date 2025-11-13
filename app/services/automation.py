"""
Automation Service
Thay thế cho Code.gs từ Google Apps Script
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.core.config import get_settings
from app.core.database import get_db_session, AdMetrics, AutomationStatus
from app.services.facebook_api import pull_facebook_data, pause_adsets, resume_adsets, get_daily_breakdown_data, pause_campaign, get_campaign_adsets_count
from app.services.logics import build_logic_map, check_logic_1, check_logic_2, check_logic_3, get_prefix_from_name, check_logic_7days_filter
from app.services.telegram_bot import send_telegram_message_safe

logger = logging.getLogger(__name__)


def is_within_window(settings) -> bool:
    """
    Kiểm tra xem có trong khung giờ cho phép không
    Thay thế cho hàm isWithinWindow_() từ Code.gs
    """
    now = datetime.now()
    current_hour = now.hour
    
    start_hour = settings.RUN_WINDOW_START_HOUR
    end_hour = settings.RUN_WINDOW_END_HOUR
    
    return start_hour <= current_hour < end_hour


def run_automation():
    """
    Hàm MASTER chạy automation
    Thay thế cho hàm runAutomation() từ Code.gs
    """
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    access_token = settings.ACCESS_TOKEN
    ad_account_ids = settings.AD_ACCOUNT_IDS
    date_preset = settings.DATA_DATE_PRESET
    delay_ms = settings.DELAY_KHI_TAT_BATCH
    
    try:
        # Kiểm tra khung giờ cho phép
        if not is_within_window(settings):
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            error_msg = (
                f"⚠️ KHÔNG ĐƯỢC PHÉP CHẠY NGOÀI KHUNG GIỜ: "
                f"Hiện tại {current_time} "
                f"(Khung cho phép: {settings.RUN_WINDOW_START_HOUR}:00 - {settings.RUN_WINDOW_END_HOUR}:00).\n\n"
                f"Để chạy ngoài giờ, vui lòng dùng hàm test_run_automation() thay vì run_automation()."
            )
            logger.warning(error_msg)
            send_telegram_message_safe(error_msg, bot_token, chat_id)
            return
        
        # Kiểm tra cài đặt
        is_valid, error_msg = settings.validate()
        if not is_valid:
            logger.error(f"⚠️ Lỗi cấu hình: {error_msg}")
            send_telegram_message_safe(f"⚠️ Lỗi cấu hình: {error_msg}", bot_token, chat_id)
            return
        
        # Xây dựng logic map
        logic_map = build_logic_map()
        
        # Bước 1: Kéo dữ liệu mới
        logger.info("📥 Đang kéo dữ liệu từ Facebook API...")
        ad_metrics_list = pull_facebook_data(access_token, ad_account_ids, date_preset)
        
        # Lưu dữ liệu vào database
        from app.core.database import get_db_session
        db = get_db_session()
        try:
            # Xóa dữ liệu cũ (có thể giữ lại lịch sử nếu cần)
            # db.query(AdMetrics).delete()
            # db.commit()
            
            # Thêm dữ liệu mới
            for ad_metric in ad_metrics_list:
                # Kiểm tra xem đã có chưa
                existing = db.query(AdMetrics).filter(
                    AdMetrics.adset_id == ad_metric['adset_id'],
                    AdMetrics.ad_id == ad_metric['ad_id']
                ).first()
                
                if existing:
                    # Update
                    for key, value in ad_metric.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.now()
                else:
                    # Create new
                    new_metric = AdMetrics(**ad_metric)
                    db.add(new_metric)
            
            db.commit()
            logger.info(f"✅ Đã lưu {len(ad_metrics_list)} ads vào database")
        except Exception as e:
            db.rollback()
            logger.error(f"🚨 Lỗi khi lưu dữ liệu vào database: {e}")
        finally:
            db.close()
        
        # Bước 2: Chạy logic cắt lỗ
        logger.info("🔍 Đang kiểm tra và tắt quảng cáo...")
        check_and_toggle_ads(logic_map, access_token, bot_token, chat_id, delay_ms)
        
    except Exception as e:
        error_msg = f"LỖI SCRIPT NGHIÊM TRỌNG: {str(e)}"
        logger.error(error_msg)
        send_telegram_message_safe(error_msg, bot_token, chat_id)


def test_run_automation():
    """
    Hàm TEST - Chạy bất cứ lúc nào (Bỏ qua khung giờ)
    Thay thế cho hàm testRunAutomation() từ Code.gs
    """
    logger.info("--- BẮT ĐẦU TEST CHẠY AUTOMATION (Bỏ qua khung giờ) ---")
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    access_token = settings.ACCESS_TOKEN
    ad_account_ids = settings.AD_ACCOUNT_IDS
    date_preset = settings.DATA_DATE_PRESET
    delay_ms = settings.DELAY_KHI_TAT_BATCH
    
    try:
        # Kiểm tra cài đặt
        is_valid, error_msg = settings.validate()
        if not is_valid:
            logger.error(f"LỖI: {error_msg}")
            return
        
        # Xây dựng logic map
        logic_map = build_logic_map()
        
        # Bước 1: Kéo dữ liệu mới
        ad_metrics_list = pull_facebook_data(access_token, ad_account_ids, date_preset)
        
        # Bước 2: Chạy logic cắt lỗ
        check_and_toggle_ads(logic_map, access_token, bot_token, chat_id, delay_ms)
        
    except Exception as e:
        error_msg = f"LỖI TEST: {str(e)}"
        logger.error(error_msg)
        send_telegram_message_safe(error_msg, bot_token, chat_id)


def check_and_toggle_ads(
    logic_map: Dict[str, Dict[str, Any]],
    access_token: str,
    bot_token: str,
    chat_id: str,
    delay_ms: int
):
    """
    Kiểm tra và tắt/bật quảng cáo
    Thay thế cho hàm kiemTraVaTatQuangCao() từ Code.gs
    """
    from app.core.database import get_db_session
    db = get_db_session()
    
    try:
        # Lấy daily breakdown data
        settings = get_settings()
        daily_breakdown_data = get_daily_breakdown_data(
            access_token,
            settings.AD_ACCOUNT_IDS,
            settings.DATA_DATE_PRESET
        )
        
        adsets_to_pause = {}
        adsets_to_resume = {}
        
        # BƯỚC 1: Kiểm tra adsets ACTIVE để tắt (Logic 1 và Logic 2)
        active_metrics = db.query(AdMetrics).filter(
            AdMetrics.adset_status == "ACTIVE"
        ).all()
        
        for ad_metric in active_metrics:
            adset_id = ad_metric.adset_id
            account_id = ad_metric.account_id
            campaign_name = ad_metric.campaign_name
            prefix = get_prefix_from_name(campaign_name)
            
            spend = ad_metric.spend or 0
            results = ad_metric.results or 0
            gia_data = ad_metric.gia_data or 0
            
            # Kiểm tra Logic 1
            if check_logic_1(spend, results, logic_map, account_id, prefix):
                if adset_id not in adsets_to_pause:
                    adsets_to_pause[adset_id] = {
                        'adId': ad_metric.ad_id,
                        'adName': ad_metric.ad_name,
                        'adsetName': ad_metric.adset_name,
                        'campaignName': campaign_name,
                        'reason': 'Logic 1: Chi tiêu > ngưỡng và kết quả = 0',
                        'prefix': prefix,
                        'accountId': account_id
                    }
            
            # Kiểm tra Logic 2
            if check_logic_2(spend, gia_data, logic_map, account_id, prefix):
                if adset_id not in adsets_to_pause:
                    adsets_to_pause[adset_id] = {
                        'adId': ad_metric.ad_id,
                        'adName': ad_metric.ad_name,
                        'adsetName': ad_metric.adset_name,
                        'campaignName': campaign_name,
                        'reason': 'Logic 2: Chi tiêu > ngưỡng và giá DATA > ngưỡng',
                        'prefix': prefix,
                        'accountId': account_id
                    }
        
        # BƯỚC 2: Logic lọc 7 ngày (Logic mới - có thể cấu hình)
        # Lọc adsets trong N ngày qua (kể cả hôm nay) - N có thể cấu hình
        from datetime import datetime, timedelta
        from pytz import timezone as tz
        from sqlalchemy import func
        from app.services.logics import get_7days_config
        
        tz_vn = tz('Asia/Ho_Chi_Minh')
        now = datetime.now(tz_vn)
        
        # Lấy số ngày từ config (mặc định 7)
        # Sẽ lấy từ config của account/prefix đầu tiên, hoặc dùng default
        default_days = 7
        days_ago = (now - timedelta(days=default_days)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Lấy metrics trong N ngày qua, group by adset_id để tính tổng
        # Lấy config cho từng adset để biết số ngày cần lọc
        # Tạm thời dùng default_days, sẽ optimize sau
        seven_days_metrics = db.query(
            AdMetrics.adset_id,
            AdMetrics.campaign_id,
            AdMetrics.campaign_name,
            AdMetrics.account_id,
            func.sum(AdMetrics.impressions).label('total_impressions'),
            func.sum(AdMetrics.spend).label('total_spend'),
            func.avg(AdMetrics.gia_data).label('avg_gia_data'),
            func.sum(AdMetrics.results).label('total_results'),
            func.sum(AdMetrics.purchases).label('total_purchases'),
            func.sum(AdMetrics.purchase_value).label('total_purchase_value')
        ).filter(
            AdMetrics.date >= days_ago,
            AdMetrics.impressions > 0
        ).group_by(
            AdMetrics.adset_id,
            AdMetrics.campaign_id,
            AdMetrics.campaign_name,
            AdMetrics.account_id
        ).all()
        
        # Kiểm tra từng adset trong 7 ngày
        violations_7days = []  # List các adsets vi phạm
        
        for metric_row in seven_days_metrics:
            adset_id = metric_row.adset_id
            campaign_id = metric_row.campaign_id
            campaign_name = metric_row.campaign_name
            account_id = metric_row.account_id
            prefix = get_prefix_from_name(campaign_name)
            
            total_impressions = int(metric_row.total_impressions or 0)
            total_spend = float(metric_row.total_spend or 0)
            avg_gia_data = float(metric_row.avg_gia_data or 0)
            total_results = int(metric_row.total_results or 0)
            total_purchases = int(metric_row.total_purchases or 0)
            
            # Tính cost_per_purchase
            cost_per_purchase = (total_spend / total_purchases) if total_purchases > 0 else 0
            
            # Kiểm tra logic 7 ngày
            should_pause, reason = check_logic_7days_filter(
                total_impressions,
                total_spend,
                avg_gia_data,
                cost_per_purchase,
                total_results,
                logic_map,
                account_id,
                prefix
            )
            
            if should_pause:
                # Lấy thông tin adset từ database
                adset_info = db.query(AdMetrics).filter(
                    AdMetrics.adset_id == adset_id
                ).first()
                
                if adset_info:
                    violations_7days.append({
                        'adset_id': adset_id,
                        'adset_name': adset_info.adset_name or 'N/A',
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'account_id': account_id,
                        'prefix': prefix,
                        'reason': reason,
                        'total_spend': total_spend,
                        'avg_gia_data': avg_gia_data,
                        'total_results': total_results
                    })
        
        # Xử lý vi phạm: Tắt adset hoặc campaign
        campaigns_to_pause = set()  # Campaigns chỉ có 1 adset
        adsets_to_pause_7days = []  # Adsets trong campaigns có nhiều adsets
        
        for violation in violations_7days:
            campaign_id = violation['campaign_id']
            
            if not campaign_id:
                # Nếu không có campaign_id, tắt adset trực tiếp
                adsets_to_pause_7days.append(violation['adset_id'])
                continue
            
            # Lấy số adsets trong campaign
            try:
                adsets_count = get_campaign_adsets_count(campaign_id, access_token)
                
                if adsets_count <= 1:
                    # Campaign chỉ có 1 adset → tắt campaign
                    campaigns_to_pause.add(campaign_id)
                else:
                    # Campaign có nhiều adsets → chỉ tắt adset vi phạm
                    adsets_to_pause_7days.append(violation['adset_id'])
            except Exception as e:
                logger.error(f"🚨 Lỗi kiểm tra số adsets của campaign {campaign_id}: {e}")
                # Fallback: tắt adset
                adsets_to_pause_7days.append(violation['adset_id'])
        
        # Tắt campaigns (chỉ có 1 adset)
        for campaign_id in campaigns_to_pause:
            try:
                result = pause_campaign(campaign_id, access_token)
                if result.get('success'):
                    logger.info(f"✅ Đã tắt Campaign {campaign_id} (chỉ có 1 adset)")
                else:
                    logger.error(f"❌ Lỗi tắt Campaign {campaign_id}: {result.get('error')}")
            except Exception as e:
                logger.error(f"🚨 Lỗi tắt Campaign {campaign_id}: {e}")
        
        # Tắt adsets (trong campaigns có nhiều adsets)
        if adsets_to_pause_7days:
            pause_result = pause_adsets(adsets_to_pause_7days, access_token, delay_ms)
            logger.info(f"✅ Logic 7 ngày: Đã tắt {pause_result.get('success', 0)} adsets")
        
        # Gửi thông báo Telegram về các vi phạm
        if violations_7days:
            violation_msg = "🚨 *BÁO CÁO VI PHẠM 7 NGÀY QUA*\n\n"
            violation_msg += f"Tổng số adsets vi phạm: {len(violations_7days)}\n\n"
            
            for idx, violation in enumerate(violations_7days[:20], 1):  # Giới hạn 20 adsets
                violation_msg += f"*{idx}. {violation['adset_name']}*\n"
                violation_msg += f"   Campaign: {violation['campaign_name']}\n"
                violation_msg += f"   Prefix: {violation['prefix']}\n"
                violation_msg += f"   Lý do: {violation['reason']}\n"
                violation_msg += f"   Chi tiêu: {violation['total_spend']:,.0f}₫\n"
                violation_msg += f"   Giá DATA TB: {violation['avg_gia_data']:,.0f}₫\n"
                violation_msg += f"   Kết quả: {violation['total_results']}\n\n"
            
            if len(violations_7days) > 20:
                violation_msg += f"... và {len(violations_7days) - 20} adsets khác\n"
            
            send_telegram_message_safe(violation_msg, bot_token, chat_id)
        
        # BƯỚC 3: Kiểm tra adsets PAUSED để bật lại (Logic 3)
        # QUAN TRỌNG: Logic 3 chỉ chạy trên adsets đã bị tắt (PAUSED), không phải ACTIVE
        paused_metrics = db.query(AdMetrics).filter(
            AdMetrics.adset_status == "PAUSED"
        ).all()
        
        for ad_metric in paused_metrics:
            adset_id = ad_metric.adset_id
            account_id = ad_metric.account_id
            campaign_name = ad_metric.campaign_name
            prefix = get_prefix_from_name(campaign_name)
            
            spend = ad_metric.spend or 0
            results = ad_metric.results or 0
            gia_data = ad_metric.gia_data or 0
            
            # Kiểm tra Logic 3 (bật lại) - chỉ trên adsets PAUSED
            if check_logic_3(spend, results, logic_map, account_id, prefix):
                if adset_id not in adsets_to_resume:
                    adsets_to_resume[adset_id] = {
                        'adId': ad_metric.ad_id,
                        'adName': ad_metric.ad_name,
                        'adsetName': ad_metric.adset_name,
                        'campaignName': campaign_name,
                        'reason': 'Logic 3: Đáp ứng điều kiện bật lại',
                        'prefix': prefix,
                        'accountId': account_id
                    }
        
        # Tắt adsets
        if adsets_to_pause:
            adset_ids = list(adsets_to_pause.keys())
            logger.info(f"🛑 Đang tắt {len(adset_ids)} adsets...")
            pause_result = pause_adsets(adset_ids, access_token, delay_ms)
            
            if pause_result['success'] > 0:
                message = f"🛑 *ĐÃ TẮT {pause_result['success']} adset*\n\n"
                for adset_id, info in list(adsets_to_pause.items())[:10]:
                    message += f"▪️ *{info['adsetName']}* ({info['prefix']})\n"
                    message += f"   *Lý do:* {info['reason']}\n\n"
                
                send_telegram_message_safe(message, bot_token, chat_id)
        
        # Bật lại adsets
        if adsets_to_resume:
            adset_ids = list(adsets_to_resume.keys())
            logger.info(f"✅ Đang bật lại {len(adset_ids)} adsets...")
            resume_result = resume_adsets(adset_ids, access_token, delay_ms)
            
            if resume_result['success'] > 0:
                message = f"✅ *ĐÃ BẬT LẠI {resume_result['success']} adset*\n\n"
                for adset_id, info in list(adsets_to_resume.items())[:10]:
                    message += f"▪️ *{info['adsetName']}* ({info['prefix']})\n"
                    message += f"   *Lý do:* {info['reason']}\n\n"
                
                send_telegram_message_safe(message, bot_token, chat_id)
        
    except Exception as e:
        logger.error(f"🚨 Lỗi khi kiểm tra và tắt quảng cáo: {e}")
        send_telegram_message_safe(f"🚨 Lỗi: {str(e)}", bot_token, chat_id)
    finally:
        db.close()

