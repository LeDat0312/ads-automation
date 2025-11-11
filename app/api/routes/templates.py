"""
Rule Templates API Routes
API endpoints cho rule templates system
"""
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.rule_template import RuleTemplate
from app.services.rule_template_service import (
    get_all_templates,
    apply_template,
    create_template_from_config,
    initialize_default_templates
)

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("/")
async def list_templates(
    campaign_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all rule templates"""
    try:
        templates = get_all_templates(campaign_type)
        return {
            "templates": templates,
            "total": len(templates)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get template by ID"""
    try:
        template = db.query(RuleTemplate).filter_by(id=template_id).first()
        if not template:
            return JSONResponse(
                status_code=404,
                content={"error": "Template not found"}
            )
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "campaign_type": template.campaign_type,
            "template_config": template.template_config,
            "usage_count": template.usage_count
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/{template_id}/apply")
async def apply_template_endpoint(
    template_id: int,
    account_id: str = Body(...),
    prefix: str = Body(...),
    custom_values: Optional[Dict[str, Any]] = Body(None),
    db: Session = Depends(get_db)
):
    """Apply template to account/prefix"""
    try:
        success = apply_template(template_id, account_id, prefix, custom_values)
        if success:
            return {
                "message": "Template applied successfully",
                "template_id": template_id,
                "account_id": account_id,
                "prefix": prefix
            }
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to apply template"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/")
async def create_template_endpoint(
    config: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create new template"""
    try:
        template_id = create_template_from_config(config)
        if template_id:
            return {
                "message": "Template created successfully",
                "template_id": template_id
            }
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to create template"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/initialize")
async def initialize_templates():
    """Initialize default templates (run once)"""
    try:
        initialize_default_templates()
        return {"message": "Default templates initialized successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

