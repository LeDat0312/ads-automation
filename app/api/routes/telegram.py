"""
Telegram Webhook API
Webhook siêu nhẹ - chỉ xác thực và enqueue job
"""
import logging
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from fastapi.responses import Response
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import get_settings
from app.models.telegram_update import TelegramUpdate
from app.services.job_queue import JobQueue, JobPriority
from app.services.command_processor import CommandProcessor, LIGHT_COMMANDS, HEAVY_COMMANDS
from app.services.telegram_bot import parse_command, send_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/telegram", tags=["telegram"])


def verify_webhook_secret(request: Request, x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    """Xác thực webhook secret token"""
    settings = get_settings()
    expected_secret = settings.TELEGRAM_WEBHOOK_SECRET
    
    if not x_telegram_bot_api_secret_token or x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    
    return True


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_webhook_secret)
):
    """
    Telegram webhook endpoint - SIÊU NHẸ
    Chỉ xác thực, check idempotency, và enqueue job
    Trả 200 OK ngay (< 1s)
    """
    try:
        update = await request.json()
        update_id = update.get('update_id')
        
        if not update_id:
            return Response(status_code=200)  # Trả 200 OK ngay
        
        # Check idempotency - Kiểm tra xem update_id đã được xử lý chưa
        existing_update = db.query(TelegramUpdate).filter(
            TelegramUpdate.update_id == update_id
        ).first()
        
        if existing_update:
            # Update đã tồn tại (duplicate) - bỏ qua
            logger.info(f"⏭️ Duplicate update {update_id}, skipping")
            return Response(status_code=200)  # Trả 200 OK ngay
        
        # Tạo record mới để đánh dấu đã nhận update này
        telegram_update = TelegramUpdate(
            update_id=update_id,
            chat_id=str(update.get('message', {}).get('chat', {}).get('id', '')),
            user_id=str(update.get('message', {}).get('from', {}).get('id', '')),
            processed=False
        )
        db.add(telegram_update)
        db.commit()
        
        # Parse command
        parsed = parse_command(update)
        if not parsed:
            # Không phải command, bỏ qua
            return Response(status_code=200)
        
        cmd = parsed.get('cmd')
        chat_id = parsed.get('chat_id')
        message_id = parsed.get('message_id')
        settings = get_settings()
        
        # Lệnh nhẹ - xử lý inline và gửi trực tiếp (KHÔNG enqueue job)
        if cmd in LIGHT_COMMANDS:
            processor = CommandProcessor()
            try:
                handler_name = LIGHT_COMMANDS[cmd]
                handler = getattr(processor, handler_name, None)
                if handler:
                    response = handler(parsed)
                    if response:
                        # Gửi trực tiếp, không enqueue job để tránh duplicate
                        send_message(
                            chat_id,
                            response,
                            settings.TELEGRAM_BOT_TOKEN,
                            reply_to_message_id=message_id
                        )
            except Exception as e:
                logger.error(f"❌ Error handling light command {cmd}: {e}")
        
        # Lệnh nặng - enqueue job
        elif cmd in HEAVY_COMMANDS:
            job_queue = JobQueue(db=db)
            try:
                # Gửi "Đang xử lý..." ngay và lưu message_id để edit sau
                success, result = send_message(
                    chat_id,
                    "⏳ Đang xử lý...",
                    settings.TELEGRAM_BOT_TOKEN,
                    reply_to_message_id=message_id
                )
                
                # Lấy message_id từ response (nếu có)
                progress_message_id = None
                if success and isinstance(result, int):
                    progress_message_id = result
                
                # Enqueue job với progress_message_id
                parsed['progress_message_id'] = progress_message_id
                job_queue.enqueue_job(
                    job_type='telegram_command',
                    payload=parsed,
                    priority=JobPriority.LOW,
                    chat_id=chat_id,
                    user_id=parsed.get('user_id')
                )
            except Exception as e:
                logger.error(f"❌ Error enqueueing job: {e}")
        
        # Lệnh không tồn tại - thông báo lỗi
        else:
            send_message(
                chat_id,
                f"❌ **Lệnh không hợp lệ**\n\nLệnh `{cmd}` không tồn tại.\n\nVui lòng sử dụng lệnh `/help` để xem danh sách lệnh có sẵn.",
                settings.TELEGRAM_BOT_TOKEN,
                reply_to_message_id=message_id
            )
        
        # Mark update as processed
        telegram_update.processed = True
        db.commit()
        
        # Trả 200 OK ngay (< 1s)
        return Response(status_code=200)
        
    except Exception as e:
        logger.error(f"🚨 Webhook error: {e}")
        # Vẫn trả 200 OK để Telegram không retry
        return Response(status_code=200)


@router.get("/health")
async def telegram_health():
    """Health check cho Telegram webhook"""
    return {"status": "ok", "service": "telegram_webhook"}


@router.get("/webhook")
async def telegram_webhook_get():
    """GET endpoint cho webhook - chỉ để test, Telegram chỉ dùng POST"""
    return {
        "status": "ok",
        "message": "Telegram webhook endpoint. Use POST method to send updates.",
        "endpoint": "/api/telegram/webhook",
        "method": "POST"
    }

