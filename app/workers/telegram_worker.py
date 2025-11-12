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


def process_job(job_id: int):
    """Xử lý một job"""
    # Create new session for processing
    db = get_db_session()
    job_queue = JobQueue(db=db)
    settings = get_settings()
    processor = CommandProcessor()
    
    try:
        # Get job from database
        job = job_queue.get_job(job_id)
        if not job:
            logger.error(f"❌ Job {job_id} not found")
            return
        
        # Kiểm tra job status - nếu không phải PROCESSING thì bỏ qua
        if job.status != JobStatus.PROCESSING:
            logger.warning(f"⚠️ Job {job_id} status is {job.status}, not PROCESSING. Skipping.")
            return
        
        payload = job.payload
        job_type = job.job_type
        
        # Xử lý job type: send_message
        if job_type == 'send_message':
            chat_id = payload.get('chat_id')
            text = payload.get('text')
            reply_to_message_id = payload.get('reply_to_message_id')
            
            if not chat_id or not text:
                job_queue.fail_job(job.id, "Missing chat_id or text")
                return
            
            # Gửi message
            send_message(
                chat_id,
                text,
                settings.TELEGRAM_BOT_TOKEN,
                reply_to_message_id=reply_to_message_id
            )
            
            job_queue.complete_job(job.id)
            logger.info(f"✅ Processed send_message job {job.id}")
            return
        
        # Xử lý job type: telegram_command
        if job_type == 'telegram_command':
            command = payload.get('cmd') or payload.get('command')
            chat_id = payload.get('chat_id')
            message_id = payload.get('message_id')
            
            if not command:
                job_queue.fail_job(job.id, "Missing command")
                return
            
            if command not in HEAVY_COMMANDS:
                job_queue.fail_job(job.id, f"Unknown command: {command}")
                return
            
            # Gọi handler tương ứng
            handler_name = HEAVY_COMMANDS[command]
            handler = getattr(processor, handler_name, None)
            
            if not handler:
                job_queue.fail_job(job.id, f"Handler not found: {handler_name}")
                return
            
            # Xử lý command với error handling
            try:
                response = handler(payload)
                
                # Gửi response (chỉ nếu handler không edit message - trả về None)
                if response:
                    send_message(
                        chat_id,
                        response,
                        settings.TELEGRAM_BOT_TOKEN,
                        reply_to_message_id=message_id
                    )
                else:
                    # Handler đã edit message, không cần gửi thêm
                    logger.info(f"✅ Handler đã edit message cho command {command}, không gửi thêm")
                
                job_queue.complete_job(job.id)
                logger.info(f"✅ Processed telegram_command job {job.id}: {command}")
            except Exception as handler_error:
                # Gửi lỗi chi tiết về Telegram
                error_msg = f"❌ **LỖI khi xử lý lệnh `{command}`:**\n\n`{str(handler_error)}`"
                logger.error(f"❌ Error in handler {handler_name}: {handler_error}", exc_info=True)
                try:
                    send_message(
                        chat_id,
                        error_msg,
                        settings.TELEGRAM_BOT_TOKEN,
                        reply_to_message_id=message_id
                    )
                except:
                    pass
                job_queue.fail_job(job.id, str(handler_error))
            return
        
        # Unknown job type
        job_queue.fail_job(job.id, f"Unknown job type: {job_type}")
        
    except Exception as e:
        logger.error(f"❌ Error processing job {job_id}: {e}", exc_info=True)
        try:
            job_queue.fail_job(job_id, str(e))
        except:
            pass
    finally:
        db.close()


def worker_loop(worker_id: str = "worker-1"):
    """Main worker loop"""
    logger.info(f"🚀 Starting Telegram worker: {worker_id}")
    
    while True:
        db = None
        try:
            # Create new session for getting job
            db = get_db_session()
            job_queue = JobQueue(db=db)
            
            # Lấy job tiếp theo
            job = job_queue.get_next_job(worker_id)
            
            if job:
                job_id = job.id
                db.close()  # Close session before processing
                db = None
                
                # Process job (will create its own session)
                process_job(job_id)
            else:
                # Không có job, đợi 1 giây
                if db:
                    db.close()
                    db = None
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info(f"🛑 Stopping worker: {worker_id}")
            break
        except Exception as e:
            logger.error(f"❌ Worker error: {e}", exc_info=True)
            if db:
                try:
                    db.close()
                except:
                    pass
                db = None
            time.sleep(5)  # Đợi 5 giây trước khi retry


if __name__ == "__main__":
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker-1"
    worker_loop(worker_id)

