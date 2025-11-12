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
        db = self._get_db()
        should_close = self._db is None
        
        try:
            # Check rate limit per chat
            if chat_id and priority == JobPriority.LOW:
                if self._is_rate_limited(chat_id, db):
                    raise ValueError(f"Rate limit: Too many jobs for chat {chat_id}")
            
            # Check duplicate job - tránh tạo job trùng cho cùng command và chat_id
            if job_type == 'telegram_command' and chat_id:
                command = payload.get('command') or payload.get('cmd')
                
                if command:
                    # Query jobs và filter trong Python (vì JSON query phức tạp)
                    existing_jobs = db.query(Job).filter(
                        and_(
                            Job.job_type == job_type,
                            Job.chat_id == chat_id,
                            Job.status.in_([JobStatus.PENDING, JobStatus.PROCESSING])
                        )
                    ).all()
                    
                    # Check payload trong Python - nếu cùng command thì bỏ qua
                    for existing_job in existing_jobs:
                        job_command = existing_job.payload.get('command') or existing_job.payload.get('cmd')
                        
                        # Nếu cùng command, bỏ qua (tránh duplicate)
                        if job_command == command:
                            logger.warning(f"⏭️ Duplicate job skipped: {command} for chat {chat_id} (existing job: {existing_job.id}, status: {existing_job.status})")
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
            
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"✅ Enqueued job: {job.id} (type: {job_type}, priority: {priority})")
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error enqueueing job: {e}")
            raise
        finally:
            if should_close:
                db.close()
    
    def _is_rate_limited(self, chat_id: str, db: Session = None) -> bool:
        """Kiểm tra rate limit cho chat_id"""
        if db is None:
            db = self._get_db()
        
        rate_limit_seconds = self.settings.JOB_RATE_LIMIT_SECONDS
        cutoff_time = datetime.now() - timedelta(seconds=rate_limit_seconds)
        
        # Đếm số jobs đã xử lý trong khoảng thời gian
        count = db.query(Job).filter(
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
        Sử dụng SELECT FOR UPDATE để tránh race condition
        """
        db = self._get_db()
        should_close = self._db is None
        
        try:
            # Dùng SELECT FOR UPDATE để lock row và tránh race condition
            # Chỉ lấy job PENDING hoặc RETRY, lock row để tránh 2 workers cùng lấy
            job = db.query(Job).filter(
                Job.status.in_([JobStatus.PENDING, JobStatus.RETRY])
            ).order_by(
                Job.priority.desc(),  # HIGH trước
                Job.created_at.asc()  # Cũ nhất trước
            ).with_for_update(skip_locked=True).first()  # Lock row, skip nếu đã bị lock
            
            if job:
                # Mark as PROCESSING - đảm bảo không có worker khác lấy được
                job.status = JobStatus.PROCESSING
                job.started_at = datetime.now()
                job.attempts = (job.attempts or 0) + 1
                db.commit()
                db.refresh(job)
                logger.info(f"🔧 Processing job: {job.id} (type: {job.job_type}, attempt: {job.attempts}, worker: {worker_id})")
                # Store job_id before closing session
                job_id = job.id
            
            return job
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error getting next job: {e}")
            raise
        finally:
            if should_close:
                db.close()
    
    def complete_job(self, job_id: int) -> bool:
        """Đánh dấu job hoàn thành"""
        db = self._get_db()
        should_close = self._db is None
        
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            db.commit()
            logger.info(f"✅ Completed job: {job_id}")
            return True
        finally:
            if should_close:
                db.close()
    
    def fail_job(self, job_id: int, error_message: str) -> bool:
        """Đánh dấu job thất bại"""
        db = self._get_db()
        should_close = self._db is None
        
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
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
            
            db.commit()
            return True
        finally:
            if should_close:
                db.close()
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """Lấy job theo ID"""
        db = self._get_db()
        should_close = self._db is None
        
        try:
            return db.query(Job).filter(Job.id == job_id).first()
        finally:
            if should_close:
                db.close()
    
    def cleanup_old_jobs(self, days: int = 7):
        """Xóa jobs cũ (đã completed hoặc failed)"""
        db = self._get_db()
        should_close = self._db is None
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            deleted = db.query(Job).filter(
                and_(
                    Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED]),
                    Job.completed_at < cutoff_date
                )
            ).delete()
            
            db.commit()
            logger.info(f"🧹 Cleaned up {deleted} old jobs")
            return deleted
        finally:
            if should_close:
                db.close()

