"""
Media Downloader Service
Tải ảnh và video chất lượng cao từ Facebook Ads Library
"""
import logging
import httpx
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# Storage configuration
MEDIA_STORAGE_PATH = os.getenv("MEDIA_STORAGE_PATH", "./storage/competitor_media")
MAX_FILE_SIZE_MB = 100  # Maximum file size to download
DOWNLOAD_TIMEOUT = 60  # seconds


class MediaDownloader:
    """Service để download và quản lý media files"""
    
    def __init__(self, storage_path: str = MEDIA_STORAGE_PATH):
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Tạo folder structure nếu chưa có"""
        folders = ['images', 'videos', 'thumbnails']
        for folder in folders:
            (self.storage_path / folder).mkdir(parents=True, exist_ok=True)
    
    async def download_image(
        self,
        image_url: str,
        ad_id: str,
        page_name: str = "unknown",
        force_redownload: bool = False
    ) -> Optional[Dict[str, str]]:
        """
        Download ảnh chất lượng cao từ Facebook
        
        Args:
            image_url: URL của ảnh (có thể là low quality)
            ad_id: ID của ad
            page_name: Tên page (để organize files)
            force_redownload: Force download lại nếu file đã tồn tại
        
        Returns:
            Dict với info về file đã download
        """
        try:
            # Get highest quality image URL
            high_quality_url = self._get_highest_quality_image_url(image_url)
            
            # Generate unique filename
            file_hash = hashlib.md5(high_quality_url.encode()).hexdigest()[:12]
            file_extension = self._get_file_extension(high_quality_url, default='.jpg')
            filename = f"{ad_id}_{file_hash}{file_extension}"
            
            # Organize by page name
            page_folder = self._sanitize_filename(page_name)
            save_path = self.storage_path / 'images' / page_folder / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if already downloaded
            if save_path.exists() and not force_redownload:
                logger.info(f"Image already exists: {save_path}")
                return self._get_file_info(save_path, high_quality_url)
            
            # Download the image
            async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
                response = await client.get(high_quality_url)
                response.raise_for_status()
                
                # Check file size
                content_length = int(response.headers.get('content-length', 0))
                if content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
                    logger.warning(f"Image too large: {content_length / 1024 / 1024:.2f}MB")
                    return None
                
                # Save file
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✅ Downloaded image: {filename} ({content_length / 1024:.2f}KB)")
                return self._get_file_info(save_path, high_quality_url)
        
        except Exception as e:
            logger.error(f"❌ Error downloading image {image_url}: {e}")
            return None
    
    async def download_video(
        self,
        video_url: str,
        ad_id: str,
        page_name: str = "unknown",
        force_redownload: bool = False
    ) -> Optional[Dict[str, str]]:
        """
        Download video chất lượng cao từ Facebook
        
        Args:
            video_url: URL của video
            ad_id: ID của ad
            page_name: Tên page
            force_redownload: Force download lại
        
        Returns:
            Dict với info về file đã download
        """
        try:
            # Get highest quality video URL
            high_quality_url = self._get_highest_quality_video_url(video_url)
            
            # Generate filename
            file_hash = hashlib.md5(high_quality_url.encode()).hexdigest()[:12]
            file_extension = self._get_file_extension(high_quality_url, default='.mp4')
            filename = f"{ad_id}_{file_hash}{file_extension}"
            
            # Organize by page
            page_folder = self._sanitize_filename(page_name)
            save_path = self.storage_path / 'videos' / page_folder / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if exists
            if save_path.exists() and not force_redownload:
                logger.info(f"Video already exists: {save_path}")
                return self._get_file_info(save_path, high_quality_url)
            
            # Download video
            async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT * 3) as client:  # Videos take longer
                response = await client.get(high_quality_url)
                response.raise_for_status()
                
                content_length = int(response.headers.get('content-length', 0))
                if content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
                    logger.warning(f"Video too large: {content_length / 1024 / 1024:.2f}MB")
                    return None
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✅ Downloaded video: {filename} ({content_length / 1024 / 1024:.2f}MB)")
                return self._get_file_info(save_path, high_quality_url)
        
        except Exception as e:
            logger.error(f"❌ Error downloading video {video_url}: {e}")
            return None
    
    async def download_ad_media(
        self,
        ad_data: Dict,
        force_redownload: bool = False
    ) -> Dict[str, Optional[Dict]]:
        """
        Download tất cả media của một ad
        
        Args:
            ad_data: Dict chứa thông tin ad (ad_id, ad_image_url, ad_video_url, page_name)
        
        Returns:
            Dict với image_info và video_info
        """
        results = {
            "ad_id": ad_data.get('ad_id'),
            "image": None,
            "video": None,
            "thumbnail": None
        }
        
        ad_id = ad_data.get('ad_id', 'unknown')
        page_name = ad_data.get('page_name', 'unknown')
        
        # Download image
        if ad_data.get('ad_image_url'):
            results['image'] = await self.download_image(
                ad_data['ad_image_url'],
                ad_id,
                page_name,
                force_redownload
            )
        
        # Download video
        if ad_data.get('ad_video_url'):
            results['video'] = await self.download_video(
                ad_data['ad_video_url'],
                ad_id,
                page_name,
                force_redownload
            )
        
        return results
    
    async def batch_download_ads(
        self,
        ads: List[Dict],
        concurrent_limit: int = 3
    ) -> List[Dict]:
        """
        Download media cho nhiều ads cùng lúc (with concurrency limit)
        
        Args:
            ads: List of ad dictionaries
            concurrent_limit: Số lượng downloads đồng thời
        
        Returns:
            List of download results
        """
        import asyncio
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def download_with_limit(ad):
            async with semaphore:
                return await self.download_ad_media(ad)
        
        tasks = [download_with_limit(ad) for ad in ads]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        logger.info(f"✅ Batch downloaded media for {len(valid_results)}/{len(ads)} ads")
        
        return valid_results
    
    def _get_highest_quality_image_url(self, url: str) -> str:
        """
        Convert Facebook image URL to highest quality version
        
        Facebook image URLs have different quality parameters:
        - _s (small)
        - _n (normal) 
        - _o (original/highest)
        """
        # Replace quality indicators with highest quality
        high_quality_url = url
        
        # Remove size constraints from URL
        high_quality_url = re.sub(r'/s\d+x\d+/', '/s0x0/', high_quality_url)
        
        # Replace quality suffix
        high_quality_url = re.sub(r'_[sn]\.', '_o.', high_quality_url)
        
        # Remove width/height parameters
        parsed = urlparse(high_quality_url)
        if parsed.query:
            # Keep only essential params
            query_params = parse_qs(parsed.query)
            essential_params = ['fbid', 'id', 'set']
            filtered_params = {k: v for k, v in query_params.items() if k in essential_params}
            # Reconstruct URL without size params
            if filtered_params:
                new_query = '&'.join([f"{k}={v[0]}" for k, v in filtered_params.items()])
                high_quality_url = high_quality_url.split('?')[0] + '?' + new_query
        
        return high_quality_url
    
    def _get_highest_quality_video_url(self, url: str) -> str:
        """
        Get highest quality video URL
        
        Facebook video URLs might have SD/HD variants
        Try to get HD version
        """
        # Replace sd with hd if present
        high_quality_url = url.replace('_sd.', '_hd.')
        high_quality_url = high_quality_url.replace('_low.', '_high.')
        
        return high_quality_url
    
    def _get_file_extension(self, url: str, default: str = '.jpg') -> str:
        """Extract file extension from URL"""
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        
        # Validate extension
        valid_image_ext = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        valid_video_ext = ['.mp4', '.mov', '.avi', '.webm']
        
        if ext in valid_image_ext or ext in valid_video_ext:
            return ext
        
        return default
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename"""
        # Replace invalid chars with underscore
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Limit length
        return sanitized[:100]
    
    def _get_file_info(self, file_path: Path, original_url: str) -> Dict[str, str]:
        """Get info about downloaded file"""
        stat = file_path.stat()
        
        return {
            "filename": file_path.name,
            "path": str(file_path.absolute()),
            "relative_path": str(file_path.relative_to(self.storage_path)),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "original_url": original_url,
            "downloaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "file_hash": hashlib.md5(file_path.read_bytes()).hexdigest()
        }
    
    def get_file_by_ad_id(self, ad_id: str, media_type: str = 'image') -> Optional[Path]:
        """
        Tìm file đã download theo ad_id
        
        Args:
            ad_id: Ad ID
            media_type: 'image' or 'video'
        
        Returns:
            Path to file or None
        """
        search_folder = self.storage_path / (media_type + 's')
        
        # Search in all subfolders
        for file_path in search_folder.rglob(f"{ad_id}_*"):
            if file_path.is_file():
                return file_path
        
        return None
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Xóa files cũ hơn X ngày
        
        Args:
            days: Số ngày
        
        Returns:
            Số files đã xóa
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for file_path in self.storage_path.rglob('*'):
            if file_path.is_file():
                stat = file_path.stat()
                file_time = datetime.fromtimestamp(stat.st_mtime)
                
                if file_time < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"🗑️ Deleted old file: {file_path.name}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {e}")
        
        logger.info(f"🧹 Cleanup completed: {deleted_count} files deleted")
        return deleted_count
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        stats = {
            "total_images": 0,
            "total_videos": 0,
            "total_size_mb": 0,
            "storage_path": str(self.storage_path.absolute())
        }
        
        # Count images
        for img in (self.storage_path / 'images').rglob('*'):
            if img.is_file():
                stats['total_images'] += 1
                stats['total_size_mb'] += img.stat().st_size / 1024 / 1024
        
        # Count videos
        for vid in (self.storage_path / 'videos').rglob('*'):
            if vid.is_file():
                stats['total_videos'] += 1
                stats['total_size_mb'] += vid.stat().st_size / 1024 / 1024
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        stats['total_files'] = stats['total_images'] + stats['total_videos']
        
        return stats


# Singleton instance
_media_downloader = None

def get_media_downloader() -> MediaDownloader:
    """Get singleton instance of MediaDownloader"""
    global _media_downloader
    if _media_downloader is None:
        _media_downloader = MediaDownloader()
    return _media_downloader
