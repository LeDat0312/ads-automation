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
from app.api.routes import dashboard, templates, templates_ui, rules, telegram

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
app.include_router(telegram.router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"🚨 Error initializing database: {e}")


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

