"""
Ad Studio Publisher Worker
NOTE: added for AdStudio only

Background worker to publish scheduled posts to Facebook.
Uses local video files instead of Apify URLs.
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings
from app.models.ad_studio import AdStudioAsset, AdStudioScheduledPost
from app.core.database import SystemSetting

logger = logging.getLogger(__name__)
settings = get_settings()


def get_db_session() -> Session:
    """Create database session for worker"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def get_facebook_page_token(page_id: str, db: Session) -> Optional[str]:
    """
    Get Facebook page access token from database.
    
    NOTE: AdStudio - Fetches page token from /me/accounts using user token
    
    Args:
        page_id: Facebook page ID
        db: Database session
        
    Returns:
        Page access token or None if not found
    """
    try:
        # Get user's Facebook token from SystemSetting
        fb_token_setting = db.query(SystemSetting).filter(
            SystemSetting.key == "facebook_access_token"
        ).first()
        
        if not fb_token_setting or not fb_token_setting.value:
            logger.error("Facebook access token not configured in SystemSetting")
            return None
        
        user_token = fb_token_setting.value
        
        # Call Facebook Graph API to get page token
        response = requests.get(
            "https://graph.facebook.com/v18.0/me/accounts",
            params={"access_token": user_token},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        for page in data.get("data", []):
            if page.get("id") == page_id:
                return page.get("access_token")
        
        logger.error(f"Page {page_id} not found in /me/accounts")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching page token: {str(e)}")
        return None


def publish_post_to_facebook(
    post: AdStudioScheduledPost,
    asset: AdStudioAsset,
    page_id: str,
    page_token: str,
    db: Session
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Publish single post to one Facebook page.
    
    NOTE: AdStudio - Uses LOCAL video file, not Apify URL
    
    Args:
        post: Scheduled post record
        asset: Asset with local video path
        page_id: Facebook page ID
        page_token: Page access token
        db: Database session for updates
        
    Returns:
        Tuple of (success, fb_post_id, error_message)
    """
    try:
        # Validate local video exists
        if not asset.local_video_path:
            logger.error(f"Asset {asset.id} missing local_video_path, falling back to Apify URL")
            video_url = asset.video_url  # Fallback to Apify
            use_local_file = False
        else:
            video_path = Path(asset.local_video_path)
            if not video_path.exists():
                logger.error(f"Local video not found: {video_path}, falling back to Apify URL")
                video_url = asset.video_url
                use_local_file = False
            else:
                use_local_file = True
        
        # Prepare Facebook Graph API request
        graph_url = f"https://graph.facebook.com/v18.0/{page_id}/videos"
        
        data = {
            "description": post.caption,
            "access_token": page_token,
        }
        
        # Add CTA if specified
        if post.cta_text and post.cta_text != "NONE" and post.target_url:
            data["call_to_action"] = {
                "type": post.cta_text,
                "value": {
                    "link": post.target_url
                }
            }
        
        # Upload video
        if use_local_file:
            # Use local file
            video_path = Path(asset.local_video_path)
            mime_type = asset.video_mime_type or "video/mp4"
            
            logger.info(f"Uploading video from local file: {video_path} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)")
            
            with open(video_path, "rb") as video_file:
                files = {
                    "source": (
                        video_path.name,
                        video_file,
                        mime_type
                    )
                }
                
                response = requests.post(
                    graph_url,
                    data=data,
                    files=files,
                    timeout=300  # 5 minutes for large videos
                )
        else:
            # Fallback: use URL (Apify or other)
            logger.warning(f"Using fallback URL upload: {video_url[:80]}...")
            data["file_url"] = video_url
            
            response = requests.post(
                graph_url,
                data=data,
                timeout=300
            )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            fb_post_id = result.get("id")
            
            logger.info(f"✅ Successfully published to Facebook - Post ID: {fb_post_id}")
            return True, fb_post_id, None
        else:
            error_msg = response.text[:500]
            logger.error(f"❌ Facebook API error: {response.status_code} - {error_msg}")
            return False, None, f"Facebook API error: {response.status_code}"
            
    except FileNotFoundError as e:
        logger.error(f"❌ Video file not found: {str(e)}")
        return False, None, f"Video file not found: {str(e)}"
    except requests.exceptions.Timeout:
        logger.error(f"❌ Upload timeout after 300s")
        return False, None, "Upload timeout"
    except Exception as e:
        logger.error(f"❌ Unexpected error publishing to Facebook: {str(e)}", exc_info=True)
        return False, None, str(e)


def process_scheduled_posts():
    """
    Main worker loop - process scheduled posts that are due.
    
    NOTE: AdStudio - Runs continuously, checking every 60 seconds
    """
    logger.info("🚀 Ad Studio Publisher Worker started")
    
    db = get_db_session()
    
    try:
        # Find posts that are due (schedule_time <= now AND status = SCHEDULED)
        now = datetime.utcnow()
        
        due_posts = db.query(AdStudioScheduledPost).filter(
            AdStudioScheduledPost.status == "SCHEDULED",
            AdStudioScheduledPost.schedule_time <= now
        ).all()
        
        if not due_posts:
            logger.debug(f"No posts due at {now.isoformat()}")
            return
        
        logger.info(f"Found {len(due_posts)} posts to publish")
        
        for post in due_posts:
            logger.info(f"Processing post {post.id} (scheduled for {post.schedule_time.isoformat()})")
            
            # Get asset
            asset = db.query(AdStudioAsset).filter(
                AdStudioAsset.id == post.asset_id
            ).first()
            
            if not asset:
                logger.error(f"Asset {post.asset_id} not found for post {post.id}")
                post.status = "FAILED"
                post.error = "Asset not found"
                db.commit()
                continue
            
            # Update status to PUBLISHING
            post.status = "PUBLISHING"
            db.commit()
            
            # Publish to each selected page
            fb_post_ids = {}
            all_success = True
            errors = []
            
            for page_id in post.page_ids:
                # Get page token from database
                page_token = get_facebook_page_token(page_id, db)
                
                if not page_token:
                    logger.error(f"Cannot get token for page {page_id}, skipping")
                    all_success = False
                    errors.append(f"{page_id}: Token not found")
                    continue
                
                logger.info(f"Publishing to page {page_id}...")
                
                success, fb_post_id, error = publish_post_to_facebook(
                    post, asset, page_id, page_token, db
                )
                
                if success:
                    fb_post_ids[page_id] = fb_post_id
                else:
                    all_success = False
                    errors.append(f"{page_id}: {error}")
                
                # Rate limiting: wait 2 seconds between pages
                time.sleep(2)
            
            # Update post status
            if all_success:
                post.status = "PUBLISHED"
                post.fb_post_ids = fb_post_ids
                post.published_at = datetime.utcnow()
                post.error = None
                logger.info(f"✅ Post {post.id} published successfully to all pages")
            else:
                post.status = "FAILED"
                post.error = "; ".join(errors)
                post.fb_post_ids = fb_post_ids if fb_post_ids else None
                logger.error(f"❌ Post {post.id} failed: {post.error}")
            
            db.commit()
    
    except Exception as e:
        logger.error(f"❌ Worker error: {str(e)}", exc_info=True)
    finally:
        db.close()


def run_worker_loop(interval_seconds: int = 60):
    """
    Run worker in continuous loop.
    
    Args:
        interval_seconds: Seconds between checks (default: 60)
    """
    logger.info(f"Starting Ad Studio Publisher worker (check interval: {interval_seconds}s)")
    
    while True:
        try:
            process_scheduled_posts()
        except Exception as e:
            logger.error(f"Worker loop error: {str(e)}", exc_info=True)
        
        time.sleep(interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    run_worker_loop()
