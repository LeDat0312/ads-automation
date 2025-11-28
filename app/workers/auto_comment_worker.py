"""
Auto Comment Worker
Xử lý auto comment cho các Facebook posts theo lịch

NOTE: Không đụng vào ad_studio_publisher.py
"""
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import init_db, get_db_session, engine
from app.models.channel import AutoCommentSchedule, FacebookPage, ChannelGroup, ChannelGroupItem
from app.core.security import decrypt_token

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FB_API_VERSION = "v24.0"
FB_GRAPH_API_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"


def get_page_token(page: FacebookPage) -> Optional[str]:
    """Lấy và decrypt page access token"""
    try:
        token = decrypt_token(page.access_token)
        return token
    except Exception as e:
        logger.error(f"Error decrypting page token for page {page.page_id}: {e}")
        return None


def post_comment_to_facebook(
    post_id: str,
    comment_text: str,
    page_token: str,
    media_url: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Post comment lên Facebook post
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    try:
        url = f"{FB_GRAPH_API_BASE}/{post_id}/comments"
        
        params = {
            "access_token": page_token,
            "message": comment_text
        }
        
        # Nếu có media, cần upload riêng (Facebook API không hỗ trợ media trong comment trực tiếp)
        # Tạm thời chỉ support text comment
        if media_url:
            logger.warning(f"Media URL provided but not supported in comments: {media_url}")
        
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        comment_id = result.get("id")
        
        if comment_id:
            logger.info(f"✅ Comment posted successfully: {comment_id}")
            return True, None
        else:
            error_msg = f"Facebook API không trả về comment ID: {result}"
            logger.error(error_msg)
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error posting comment: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error posting comment: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def process_auto_comment_schedule(schedule: AutoCommentSchedule, db: Session) -> bool:
    """
    Xử lý một auto comment schedule
    
    Returns:
        bool: True nếu thành công, False nếu cần retry
    """
    try:
        # Lấy group
        group = db.query(ChannelGroup).filter(ChannelGroup.id == schedule.group_id).first()
        if not group:
            logger.error(f"Group {schedule.group_id} not found")
            schedule.status = "FAILED"
            schedule.error_message = "Group không tồn tại"
            db.commit()
            return False
        
        # Lấy tất cả pages trong group
        items = db.query(ChannelGroupItem).filter(
            ChannelGroupItem.group_id == schedule.group_id
        ).all()
        
        if not items:
            logger.warning(f"No pages in group {schedule.group_id}")
            schedule.status = "COMPLETED"  # Không có page nào, coi như completed
            schedule.posted_at = datetime.utcnow()
            db.commit()
            return True
        
        # Lấy pages
        page_ids = [item.page_id for item in items]
        pages = db.query(FacebookPage).filter(
            and_(
                FacebookPage.id.in_(page_ids),
                FacebookPage.enabled == True
            )
        ).all()
        
        if not pages:
            logger.warning(f"No enabled pages in group {schedule.group_id}")
            schedule.status = "COMPLETED"
            schedule.posted_at = datetime.utcnow()
            db.commit()
            return True
        
        # Post comment to all pages in group
        success_count = 0
        error_count = 0
        
        for page in pages:
            page_token = get_page_token(page)
            if not page_token:
                error_count += 1
                logger.error(f"Cannot get token for page {page.page_id}")
                continue
            
            success, error_msg = post_comment_to_facebook(
                post_id=schedule.post_id,
                comment_text=schedule.comment_text,
                page_token=page_token,
                media_url=schedule.media_url
            )
            
            if success:
                success_count += 1
            else:
                error_count += 1
                logger.error(f"Failed to post comment on page {page.page_id}: {error_msg}")
        
        if success_count > 0:
            schedule.status = "COMPLETED"
            schedule.posted_at = datetime.utcnow()
            db.commit()
            return True
        else:
            # Tất cả đều fail, cần retry
            schedule.retry_count += 1
            if schedule.retry_count >= schedule.max_retries:
                schedule.status = "FAILED"
                schedule.error_message = f"Failed after {schedule.max_retries} retries"
            else:
                schedule.status = "PENDING"  # Retry
            db.commit()
            return False
        
    except Exception as e:
        logger.error(f"Error processing auto comment schedule {schedule.id}: {e}")
        schedule.status = "FAILED"
        schedule.error_message = str(e)
        schedule.retry_count += 1
        db.commit()
        return False


def run_auto_comment_worker():
    """Main worker loop - chạy mỗi 1 phút"""
    logger.info("🚀 Auto Comment Worker started")
    
    # Initialize database
    init_db()
    
    while True:
        try:
            db = get_db_session()
            
            try:
                # Lấy các schedule cần xử lý (PENDING và scheduled_at <= now)
                now = datetime.utcnow()
                
                schedules = db.query(AutoCommentSchedule).filter(
                    and_(
                        AutoCommentSchedule.status == "PENDING",
                        AutoCommentSchedule.scheduled_at <= now
                    )
                ).limit(10).all()  # Process 10 at a time
                
                if schedules:
                    logger.info(f"📝 Found {len(schedules)} pending auto comment schedules")
                    
                    for schedule in schedules:
                        # Mark as processing
                        schedule.status = "PROCESSING"
                        db.commit()
                        
                        # Process
                        process_auto_comment_schedule(schedule, db)
                
                # Clean up old completed/failed schedules (older than 7 days)
                cutoff_date = now - timedelta(days=7)
                old_schedules = db.query(AutoCommentSchedule).filter(
                    and_(
                        AutoCommentSchedule.status.in_(["COMPLETED", "FAILED"]),
                        AutoCommentSchedule.updated_at < cutoff_date
                    )
                ).all()
                
                if old_schedules:
                    for old_schedule in old_schedules:
                        db.delete(old_schedule)
                    db.commit()
                    logger.info(f"🧹 Cleaned up {len(old_schedules)} old schedules")
                
            finally:
                db.close()
            
            # Sleep 1 phút
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("⏹️  Auto Comment Worker stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in auto comment worker: {e}")
            time.sleep(60)  # Sleep before retry


if __name__ == "__main__":
    run_auto_comment_worker()

