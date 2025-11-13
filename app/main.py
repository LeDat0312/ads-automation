"""
FastAPI Main Application
Entry point cho Facebook Ads Automation System
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import get_settings, init_db
from app.services.automation import run_automation, test_run_automation
from app.services.telegram_bot import send_telegram_message_safe
from app.services.webhook_setup import setup_webhook
from app.api.routes import dashboard, templates, templates_ui, rules, rules_ui, rules_ui_v2, telegram, accounts_prefixes, logic_7days_config

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

# Include routes
app.include_router(dashboard.router)
app.include_router(templates.router)
app.include_router(templates_ui.router)
app.include_router(rules.router)
app.include_router(rules_ui.router)
app.include_router(rules_ui_v2.router)
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Facebook Ads Automation System",
        "status": "running",
        "version": "1.0.0"
    }


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

