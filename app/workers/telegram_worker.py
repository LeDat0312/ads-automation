"""
Telegram Worker
Xử lý jobs từ queue (các lệnh nặng)
"""
import logging
import time
import sys
from app.services.job_queue import JobQueue, JobStatus
from app.services.command_processor import CommandProcessor, HEAVY_COMMANDS
from app.services.telegram_bot import send_message
from app.core.config import get_settings
from app.core.database import get_db_session

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_job(job):
    """Xử lý một job"""
    job_queue = JobQueue()
    settings = get_settings()
    processor = CommandProcessor()
    
    try:
        payload = job.payload
        command = payload.get('command')
        chat_id = payload.get('chat_id')
        message_id = payload.get('message_id')
        
        if not command or command not in HEAVY_COMMANDS:
            job_queue.fail_job(job.id, f"Unknown command: {command}")
            return
        
        # Gọi handler tương ứng
        handler_name = HEAVY_COMMANDS[command]
        handler = getattr(processor, handler_name, None)
        
        if not handler:
            job_queue.fail_job(job.id, f"Handler not found: {handler_name}")
            return
        
        # Xử lý command
        response = handler(payload)
        
        # Gửi response
        if response:
            send_message(
                chat_id,
                response,
                settings.TELEGRAM_BOT_TOKEN,
                reply_to_message_id=message_id
            )
        
        # Mark job as completed
        job_queue.complete_job(job.id)
        logger.info(f"✅ Processed job {job.id}: {command}")
        
    except Exception as e:
        logger.error(f"❌ Error processing job {job.id}: {e}")
        job_queue.fail_job(job.id, str(e))


def worker_loop(worker_id: str = "worker-1"):
    """Main worker loop"""
    logger.info(f"🚀 Starting Telegram worker: {worker_id}")
    job_queue = JobQueue()
    
    while True:
        try:
            # Lấy job tiếp theo
            job = job_queue.get_next_job(worker_id)
            
            if job:
                process_job(job)
            else:
                # Không có job, đợi 1 giây
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info(f"🛑 Stopping worker: {worker_id}")
            break
        except Exception as e:
            logger.error(f"❌ Worker error: {e}")
            time.sleep(5)  # Đợi 5 giây trước khi retry


if __name__ == "__main__":
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker-1"
    worker_loop(worker_id)

