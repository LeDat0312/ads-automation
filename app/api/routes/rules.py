"""
API Routes cho Logic Rules Management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.logic_rule import (
    LogicRuleCreate,
    LogicRuleUpdate,
    LogicRuleResponse,
    LogicRuleListResponse
)
from app.services.rule_manager import RuleManager

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("/", response_model=LogicRuleListResponse)
def list_rules(
    folder: Optional[str] = Query(None, description="Filter by folder"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    prefix: Optional[str] = Query(None, description="Filter by prefix"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    status: Optional[str] = Query(None, description="Filter by status (DRAFT, LIVE, PAUSED)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List tất cả rules với filters"""
    manager = RuleManager(db)
    rules = manager.list_rules(folder, account_id, prefix, enabled, status, skip, limit)
    total = manager.count_rules(folder, enabled, status)
    
    return LogicRuleListResponse(
        total=total,
        rules=[LogicRuleResponse.from_orm(rule) for rule in rules]
    )


@router.post("/", response_model=LogicRuleResponse, status_code=201)
def create_rule(rule_data: LogicRuleCreate, db: Session = Depends(get_db)):
    """Tạo rule mới"""
    try:
        manager = RuleManager(db)
        rule = manager.create_rule(rule_data)
        return LogicRuleResponse.from_orm(rule)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating rule: {e}", exc_info=True)
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{rule_id}", response_model=LogicRuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết rule"""
    manager = RuleManager(db)
    rule = manager.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return LogicRuleResponse.from_orm(rule)


@router.put("/{rule_id}", response_model=LogicRuleResponse)
def update_rule(
    rule_id: int,
    rule_data: LogicRuleUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật rule"""
    manager = RuleManager(db)
    rule = manager.update_rule(rule_id, rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return LogicRuleResponse.from_orm(rule)


@router.delete("/{rule_id}", status_code=204)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Xóa rule"""
    manager = RuleManager(db)
    success = manager.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return None


@router.post("/{rule_id}/toggle", response_model=LogicRuleResponse)
def toggle_rule(rule_id: int, db: Session = Depends(get_db)):
    """Bật/tắt rule"""
    manager = RuleManager(db)
    rule = manager.toggle_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return LogicRuleResponse.from_orm(rule)


@router.get("/folder/{folder_name}", response_model=List[LogicRuleResponse])
def get_rules_by_folder(folder_name: str, db: Session = Depends(get_db)):
    """Lấy tất cả rules trong folder"""
    manager = RuleManager(db)
    rules = manager.get_rules_by_folder(folder_name)
    return [LogicRuleResponse.from_orm(rule) for rule in rules]

