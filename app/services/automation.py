"""
Automation Service
Thay thế cho Code.gs từ Google Apps Script
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.core.config import get_settings
from app.core.database import get_db_session, AdMetrics, AutomationStatus
from app.services.facebook_api import pull_facebook_data, pause_adsets, resume_adsets, get_daily_breakdown_data
from app.services.logics import build_logic_map, check_logic_1, check_logic_2, check_logic_3, get_prefix_from_name
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
        
        # BƯỚC 2: Kiểm tra adsets PAUSED để bật lại (Logic 3)
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

