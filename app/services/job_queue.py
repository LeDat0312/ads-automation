"""
Job Queue Service
Quản lý hàng đợi jobs để xử lý các task nặng
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.job import Job, JobStatus, JobPriority
from app.core.database import get_db_session
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class JobQueue:
    """Service để quản lý job queue"""
    
    def __init__(self, db: Session = None):
        self.db = db or get_db_session()
        self.settings = get_settings()
    
    def enqueue_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: JobPriority = JobPriority.LOW,
        chat_id: Optional[str] = None,
        user_id: Optional[str] = None,
        max_attempts: int = None
    ) -> Job:
        """
        Thêm job vào queue
        
        Args:
            job_type: Loại job ("telegram_command", "automation", etc.)
            payload: Dữ liệu job
            priority: Độ ưu tiên (HIGH/LOW)
            chat_id: Chat ID (để rate limit)
            user_id: User ID
            max_attempts: Số lần thử tối đa
        """
        # Check rate limit per chat
        if chat_id and priority == JobPriority.LOW:
            if self._is_rate_limited(chat_id):
                raise ValueError(f"Rate limit: Too many jobs for chat {chat_id}")
        
        # Check duplicate job - tránh tạo job trùng cho cùng command và chat_id
        # Sử dụng unique job_id dựa trên chat_id:command:message_id
        if job_type == 'telegram_command' and chat_id:
            command = payload.get('command') or payload.get('cmd')
            message_id = payload.get('message_id')
            
            if command:
                # Tạo unique job_id để tránh duplicate
                job_id = f"{chat_id}:{command}:{message_id or 'none'}"
                
                # Query jobs và filter trong Python (vì JSON query phức tạp)
                existing_jobs = self.db.query(Job).filter(
                    and_(
                        Job.job_type == job_type,
                        Job.chat_id == chat_id,
                        Job.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
                    )
                ).all()
                
                # Check payload trong Python
                for existing_job in existing_jobs:
                    job_command = existing_job.payload.get('command') or existing_job.payload.get('cmd')
                    job_message_id = existing_job.payload.get('message_id')
                    existing_job_id = f"{chat_id}:{job_command}:{job_message_id or 'none'}"
                    
                    # Nếu cùng command và message_id (hoặc cùng command nếu message_id None)
                    if job_command == command and (message_id is None or job_message_id == message_id):
                        logger.warning(f"⏭️ Duplicate job skipped: {command} for chat {chat_id} (existing job: {existing_job.id})")
                        raise ValueError(f"Đang xử lý lệnh {command}, vui lòng đợi...")
        
        job = Job(
            job_type=job_type,
            priority=priority,
            status=JobStatus.PENDING,
            payload=payload,
            chat_id=chat_id,
            user_id=user_id,
            max_attempts=max_attempts or self.settings.JOB_MAX_ATTEMPTS
        )
        
        try:
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            logger.info(f"✅ Enqueued job: {job.id} (type: {job_type}, priority: {priority})")
            return job
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error enqueueing job: {e}")
            raise
    
    def _is_rate_limited(self, chat_id: str) -> bool:
        """Kiểm tra rate limit cho chat_id"""
        rate_limit_seconds = self.settings.JOB_RATE_LIMIT_SECONDS
        cutoff_time = datetime.now() - timedelta(seconds=rate_limit_seconds)
        
        # Đếm số jobs đã xử lý trong khoảng thời gian
        count = self.db.query(Job).filter(
            and_(
                Job.chat_id == chat_id,
                Job.priority == JobPriority.LOW,
                Job.status.in_([JobStatus.COMPLETED, JobStatus.PROCESSING]),
                Job.created_at >= cutoff_time
            )
        ).count()
        
        # Cho phép tối đa 1 job nặng trong khoảng thời gian
        return count >= 1
    
    def get_next_job(self, worker_id: Optional[str] = None) -> Optional[Job]:
        """
        Lấy job tiếp theo để xử lý
        Ưu tiên HIGH trước, sau đó LOW
        """
        # Tìm job PENDING hoặc RETRY, ưu tiên HIGH
        job = self.db.query(Job).filter(
            Job.status.in_([JobStatus.PENDING, JobStatus.RETRY])
        ).order_by(
            Job.priority.desc(),  # HIGH trước
            Job.created_at.asc()  # Cũ nhất trước
        ).first()
        
        if job:
            # Mark as PROCESSING
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now()
            job.attempts += 1
            self.db.commit()
            self.db.refresh(job)
            logger.info(f"🔧 Processing job: {job.id} (type: {job.job_type}, attempt: {job.attempts})")
        
        return job
    
    def complete_job(self, job_id: int) -> bool:
        """Đánh dấu job hoàn thành"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now()
        self.db.commit()
        logger.info(f"✅ Completed job: {job_id}")
        return True
    
    def fail_job(self, job_id: int, error_message: str) -> bool:
        """Đánh dấu job thất bại"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        
        job.error_message = error_message
        
        # Nếu còn attempts, retry
        if job.attempts < job.max_attempts:
            job.status = JobStatus.RETRY
            logger.warning(f"🔄 Retrying job: {job_id} (attempt: {job.attempts}/{job.max_attempts})")
        else:
            job.status = JobStatus.FAILED
            logger.error(f"❌ Failed job: {job_id} (max attempts reached)")
        
        self.db.commit()
        return True
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """Lấy job theo ID"""
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def cleanup_old_jobs(self, days: int = 7):
        """Xóa jobs cũ (đã completed hoặc failed)"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted = self.db.query(Job).filter(
            and_(
                Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED]),
                Job.completed_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        logger.info(f"🧹 Cleaned up {deleted} old jobs")
        return deleted

