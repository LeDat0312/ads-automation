"""
FastAPI Main Application
Entry point cho Facebook Ads Automation System
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging

from app.core.config import get_settings, init_db
from app.services.automation import run_automation, test_run_automation
from app.services.telegram_bot import send_telegram_message_safe
from app.services.webhook_setup import setup_webhook
from app.api.routes import dashboard, templates, templates_ui, rules, rules_ui, rules_ui_v2, telegram, accounts_prefixes
from app.api.routes import logic_7days_config, rules_ui_birch, auth, home, settings
from fastapi.staticfiles import StaticFiles
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Facebook Ads Automation System")

# CORS middleware để frontend có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for favicon
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routes - Auth và Home phải được include trước
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(home.router)  # Home page - phải include trước để handle "/"
app.include_router(settings.router)  # Settings page - quản lý token, accounts, prefixes
app.include_router(dashboard.router)
app.include_router(templates.router)
app.include_router(templates_ui.router)
app.include_router(rules.router)
app.include_router(rules_ui.router)
app.include_router(rules_ui_v2.router)
app.include_router(rules_ui_birch.router)  # New Birch-style UI
app.include_router(telegram.router)
app.include_router(accounts_prefixes.router)
app.include_router(logic_7days_config.router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and setup webhook on startup"""
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"🚨 Error initializing database: {e}")
    
    # Setup Telegram webhook với drop_pending_updates
    try:
        settings = get_settings()
        if settings.WEBHOOK_URL and settings.TELEGRAM_BOT_TOKEN:
            success = await setup_webhook(drop_pending=True)
            if success:
                logger.info("✅ Telegram webhook setup successfully")
            else:
                logger.warning("⚠️ Failed to setup Telegram webhook")
        else:
            logger.warning("⚠️ WEBHOOK_URL or TELEGRAM_BOT_TOKEN not configured, skipping webhook setup")
    except Exception as e:
        logger.error(f"🚨 Error setting up webhook: {e}")


# Root endpoint "/" được handle bởi home.router
# Đã chuyển sang app/api/routes/home.py để có giao diện đẹp hơn


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/automation/run")
async def run_automation_endpoint():
    """Run automation (trong khung giờ cho phép)"""
    try:
        settings = get_settings()
        is_valid, error_msg = settings.validate()
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={"error": error_msg}
            )
        
        run_automation()
        return {"message": "Automation started", "status": "success"}
    except Exception as e:
        logger.error(f"🚨 Error running automation: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/automation/test")
async def test_automation_endpoint():
    """Test automation (bỏ qua khung giờ)"""
    try:
        settings = get_settings()
        is_valid, error_msg = settings.validate()
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={"error": error_msg}
            )
        
        test_run_automation()
        return {"message": "Test automation started", "status": "success"}
    except Exception as e:
        logger.error(f"🚨 Error running test automation: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/automation/run-7days")
async def run_7days_automation_endpoint(
    account_id: Optional[str] = None,
    prefix: Optional[str] = None
):
    """Run 7 days filter automation"""
    try:
        from app.services.automation_7days import run_7days_filter_automation
        
        account_ids = [account_id] if account_id else None
        prefixes = [prefix] if prefix else None
        
        result = run_7days_filter_automation(account_ids=account_ids, prefixes=prefixes)
        
        if result.get('success'):
            return {
                "message": "7 days filter automation completed",
                "status": "success",
                "result": result
            }
        else:
            return JSONResponse(
                status_code=500,
                content={"error": result.get('error', 'Unknown error')}
            )
    except Exception as e:
        logger.error(f"🚨 Error running 7days filter: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


from fastapi.responses import StreamingResponse
import json as json_lib
import asyncio
from typing import AsyncGenerator


async def stream_automation_logs(automation_func, *args, **kwargs) -> AsyncGenerator[str, None]:
    """Stream automation logs as JSON lines"""
    import logging
    import sys
    from io import StringIO
    
    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)
    
    # Get automation logger
    automation_logger = logging.getLogger('app.services.automation')
    automation_logger.addHandler(handler)
    
    try:
        # Send start message
        yield json_lib.dumps({"type": "log", "message": "🚀 Bắt đầu chạy automation...", "level": "info"}) + "\n"
        
        # Run automation in background thread
        import threading
        result = {"success": False, "error": None}
        
        def run_automation():
            try:
                automation_result = automation_func(*args, **kwargs)
                result.update(automation_result if isinstance(automation_result, dict) else {"success": True, "result": automation_result})
            except Exception as e:
                result.update({"success": False, "error": str(e)})
        
        thread = threading.Thread(target=run_automation, daemon=True)
        thread.start()
        
        # Poll for logs and completion
        while thread.is_alive():
            # Read captured logs
            log_content = log_capture.getvalue()
            if log_content:
                log_capture.seek(0)
                log_capture.truncate(0)
                for line in log_content.strip().split('\n'):
                    if line.strip():
                        yield json_lib.dumps({"type": "log", "message": line, "level": "info"}) + "\n"
            
            await asyncio.sleep(0.5)
        
        # Send completion message
        if result.get('success'):
            yield json_lib.dumps({"type": "complete", "result": result}) + "\n"
        else:
            yield json_lib.dumps({"type": "error", "message": result.get('error', 'Unknown error')}) + "\n"
            
    finally:
        automation_logger.removeHandler(handler)


@app.post("/api/automation/run-web")
async def run_automation_web():
    """Run automation with streaming logs for web UI"""
    from app.services.automation import run_automation
    return StreamingResponse(
        stream_automation_logs(run_automation),
        media_type="application/x-ndjson"
    )


@app.post("/api/automation/test-web")
async def test_automation_web():
    """Test automation (skip time window) with streaming logs for web UI"""
    from app.services.automation import test_run_automation
    return StreamingResponse(
        stream_automation_logs(test_run_automation),
        media_type="application/x-ndjson"
    )


@app.post("/api/automation/run-7days-web")
async def run_7days_automation_web():
    """Run 7 days filter automation with streaming logs for web UI"""
    from app.services.automation_7days import run_7days_filter_automation
    return StreamingResponse(
        stream_automation_logs(run_7days_filter_automation),
        media_type="application/x-ndjson"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

