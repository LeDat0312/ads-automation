"""
Automation Service cho Logic 7 Ngày
Chạy riêng logic lọc 7 ngày, không chạy logic 1, 2, 3
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pytz import timezone as tz
from sqlalchemy import func

from app.core.config import get_settings
from app.core.database import get_db_session, AdMetrics
from app.services.facebook_api import pause_adsets, pause_campaign, get_campaign_adsets_count
from app.services.logics import build_logic_map, check_logic_7days_filter, get_prefix_from_name, get_7days_config
from app.services.telegram_bot import send_telegram_message_safe

logger = logging.getLogger(__name__)


def run_7days_filter_automation(
    account_ids: Optional[List[str]] = None,
    prefixes: Optional[List[str]] = None
):
    """
    Chạy logic lọc 7 ngày riêng
    Không chạy logic 1, 2, 3
    
    Args:
        account_ids: List account IDs cụ thể để chạy (None = tất cả accounts có config enabled)
        prefixes: List prefixes cụ thể để chạy (None = tất cả prefixes có config enabled)
    """
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    access_token = settings.ACCESS_TOKEN
    delay_ms = settings.DELAY_KHI_TAT_BATCH
    
    try:
        # Xây dựng logic map (để lấy SL_2_GIA_DATA)
        logic_map = build_logic_map()
        
        # Nếu không chỉ định account_ids/prefixes, lấy từ config enabled
        if account_ids is None or prefixes is None:
            from app.core.database import get_db_session
            from app.models.logic_7days_config import Logic7DaysConfig
            
            db = get_db_session()
            try:
                configs = db.query(Logic7DaysConfig).filter(
                    Logic7DaysConfig.enabled == True
                ).all()
                
                if account_ids is None:
                    # Lấy tất cả account_ids có config enabled
                    account_ids_set = set()
                    for config in configs:
                        if config.account_id:
                            account_ids_set.add(config.account_id)
                        else:
                            # Config cho tất cả accounts → dùng settings
                            account_ids_set.update(settings.ad_account_ids_list)
                            break
                    account_ids = list(account_ids_set) if account_ids_set else settings.ad_account_ids_list
                
                if prefixes is None:
                    # Lấy tất cả prefixes có config enabled
                    prefixes_set = set()
                    for config in configs:
                        if config.prefix:
                            prefixes_set.add(config.prefix)
                        else:
                            # Config cho tất cả prefixes → lấy từ database
                            from app.models.account_prefix import Prefix
                            all_prefixes = db.query(Prefix).filter(Prefix.enabled == True).all()
                            prefixes_set.update([p.prefix for p in all_prefixes])
                            break
                    prefixes = list(prefixes_set) if prefixes_set else []
            finally:
                db.close()
        
        # Chạy logic 7 ngày với filter
        result = check_and_toggle_ads_7days(
            logic_map, 
            access_token, 
            bot_token, 
            chat_id, 
            delay_ms,
            account_ids=account_ids,
            prefixes=prefixes
        )
        
        return result
    except Exception as e:
        error_msg = f"LỖI LOGIC 7 NGÀY: {str(e)}"
        logger.error(error_msg, exc_info=True)
        send_telegram_message_safe(error_msg, bot_token, chat_id)
        return {"success": False, "error": str(e)}


def check_and_toggle_ads_7days(
    logic_map: Dict[str, Dict[str, Any]],
    access_token: str,
    bot_token: str,
    chat_id: str,
    delay_ms: int,
    account_ids: Optional[List[str]] = None,
    prefixes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Chỉ chạy logic lọc 7 ngày
    """
    db = get_db_session()
    
    try:
        tz_vn = tz('Asia/Ho_Chi_Minh')
        now = datetime.now(tz_vn)
        
        # Lấy số ngày từ config (mặc định 7)
        # Tạm thời dùng default, sẽ optimize sau để lấy theo từng account/prefix
        default_days = 7
        days_ago = (now - timedelta(days=default_days)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Lấy metrics trong N ngày qua, group by adset_id để tính tổng
        # Filter theo account_ids và prefixes nếu có
        query = db.query(
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
        )
        
        # Filter theo account_ids nếu có
        if account_ids:
            query = query.filter(AdMetrics.account_id.in_(account_ids))
        
        # Filter theo prefixes nếu có (qua campaign_name)
        if prefixes:
            # Lấy tất cả campaign_names có prefix trong list
            all_campaigns = db.query(AdMetrics.campaign_name).distinct().all()
            matching_campaigns = []
            for (campaign_name,) in all_campaigns:
                if campaign_name:
                    prefix = get_prefix_from_name(campaign_name)
                    if prefix in prefixes:
                        matching_campaigns.append(campaign_name)
            if matching_campaigns:
                query = query.filter(AdMetrics.campaign_name.in_(matching_campaigns))
        
        seven_days_metrics = query.group_by(
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
        paused_campaigns = 0
        for campaign_id in campaigns_to_pause:
            try:
                result = pause_campaign(campaign_id, access_token)
                if result.get('success'):
                    logger.info(f"✅ Đã tắt Campaign {campaign_id} (chỉ có 1 adset)")
                    paused_campaigns += 1
                else:
                    logger.error(f"❌ Lỗi tắt Campaign {campaign_id}: {result.get('error')}")
            except Exception as e:
                logger.error(f"🚨 Lỗi tắt Campaign {campaign_id}: {e}")
        
        # Tắt adsets (trong campaigns có nhiều adsets)
        paused_adsets = 0
        if adsets_to_pause_7days:
            pause_result = pause_adsets(adsets_to_pause_7days, access_token, delay_ms)
            paused_adsets = pause_result.get('success', 0)
            logger.info(f"✅ Logic 7 ngày: Đã tắt {paused_adsets} adsets")
        
        # Gửi thông báo Telegram về các vi phạm
        if violations_7days:
            violation_msg = "🚨 *BÁO CÁO VI PHẠM 7 NGÀY QUA*\n\n"
            violation_msg += f"Tổng số adsets vi phạm: {len(violations_7days)}\n"
            violation_msg += f"Đã tắt: {paused_campaigns} campaigns, {paused_adsets} adsets\n\n"
            
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
        else:
            send_telegram_message_safe("✅ Logic 7 ngày: Không có adsets vi phạm", bot_token, chat_id)
        
        return {
            "success": True,
            "violations": len(violations_7days),
            "paused_campaigns": paused_campaigns,
            "paused_adsets": paused_adsets
        }
        
    except Exception as e:
        logger.error(f"🚨 Lỗi khi chạy logic 7 ngày: {e}", exc_info=True)
        send_telegram_message_safe(f"🚨 Lỗi logic 7 ngày: {str(e)}", bot_token, chat_id)
        return {"success": False, "error": str(e)}
    finally:
        db.close()

