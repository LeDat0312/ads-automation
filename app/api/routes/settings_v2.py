# -*- coding: utf-8 -*-
"""
Enhanced Settings API Routes v2
Với advanced filtering, batch operations, export, health checks
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import json

from app.core.database import get_db
from app.models.user import User
from app.models.account_prefix import Account, Prefix
from app.api.routes.auth import get_current_user_optional
from app.schemas.account_response import (
    AccountFilterRequest,
    EnhancedAccountResponse,
    PaginatedAccountResponse,
    AccountBulkUpdateRequest,
    AccountBulkDeleteRequest,
)
from app.schemas.prefix_response import (
    PrefixFilterRequest,
    EnhancedPrefixResponse,
    PaginatedPrefixResponse,
    PrefixMatchTestRequest,
    PatternTestResult,
    PrefixCreateRequest,
    PrefixAutoSuggestRequest,
    PrefixBulkOperationRequest,
)
from app.services.account_manager import (
    AccountFilterService,
    AccountHealthService,
    AccountBatchService,
    AccountExportService,
)
from app.services.prefix_manager import (
    PrefixFilterService,
    PrefixPatternService,
    PrefixAutoSuggestService,
    PrefixCampaignService,
    PrefixBatchService,
)

router = APIRouter(prefix="/settings/v2", tags=["settings-v2"])


# ===== ACCOUNT ENDPOINTS =====

@router.post("/accounts/filter", response_model=PaginatedAccountResponse)
def filter_accounts(
    filter_req: AccountFilterRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Filter, search, sort accounts with pagination
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        accounts, total = AccountFilterService.apply_filters(
            db, current_user.id, filter_req
        )
        
        # Build enhanced responses
        responses = []
        for account in accounts:
            # Get basic response
            account_dict = {
                "id": account.id,
                "account_id": account.account_id,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "status": account.status,
                "enabled": account.enabled,
                "timezone": account.timezone,
                "currency": account.currency,
                "last_30_days_spend": account.last_30_days_spend,
                "created_at": account.created_at,
                "updated_at": account.updated_at,
            }
            
            # Add health check
            health = AccountHealthService.check_account_health(account)
            account_dict["health"] = health
            
            # Add spending trend
            spending_trend = AccountHealthService.calculate_spending_trend(account, db)
            account_dict["spending_trend"] = spending_trend
            
            # Add campaign stats
            campaign_stats = AccountHealthService.build_campaign_stats(account, db)
            account_dict["campaign_stats"] = campaign_stats
            
            # Add linked prefixes
            prefixes = AccountFilterService.get_account_prefixes(db, account.id)
            account_dict["linked_prefixes"] = prefixes
            
            # Add other fields
            account_dict["last_synced"] = account.updated_at
            account_dict["token_valid"] = True  # TODO: check from token service
            account_dict["token_expires_at"] = None  # TODO: get from token
            account_dict["notes"] = account.description
            account_dict["metadata"] = None
            account_dict["last_modified_by"] = None
            account_dict["last_modified_at"] = account.updated_at
            
            responses.append(EnhancedAccountResponse(**account_dict))
        
        total_pages = (total + filter_req.page_size - 1) // filter_req.page_size
        
        return PaginatedAccountResponse(
            items=responses,
            total=total,
            page=filter_req.page,
            page_size=filter_req.page_size,
            total_pages=total_pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/batch-update")
def batch_update_accounts(
    req: AccountBulkUpdateRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Batch update multiple accounts"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        updated = AccountBatchService.bulk_update(
            db, current_user.id, req.account_ids, req.updates
        )
        return {
            "success": True,
            "message": f"Updated {updated} accounts",
            "count": updated
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/batch-delete")
def batch_delete_accounts(
    req: AccountBulkDeleteRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Batch delete multiple accounts"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not req.confirm:
        raise HTTPException(status_code=400, detail="Please confirm deletion")
    
    try:
        deleted = AccountBatchService.bulk_delete(
            db, current_user.id, req.account_ids
        )
        return {
            "success": True,
            "message": f"Deleted {deleted} accounts",
            "count": deleted
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/batch-enable")
def batch_enable_accounts(
    account_ids: List[int] = Query(...),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Batch enable accounts"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        updated = AccountBatchService.bulk_enable(db, current_user.id, account_ids)
        return {"success": True, "count": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/batch-disable")
def batch_disable_accounts(
    account_ids: List[int] = Query(...),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Batch disable accounts"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        updated = AccountBatchService.bulk_disable(db, current_user.id, account_ids)
        return {"success": True, "count": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/export/csv")
def export_accounts_csv(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Export all accounts as CSV"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        accounts = db.query(Account).filter(
            Account.user_id == current_user.id
        ).all()
        
        csv_content = AccountExportService.export_to_csv(accounts)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=accounts.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/export/json")
def export_accounts_json(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Export all accounts as JSON"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        accounts = db.query(Account).filter(
            Account.user_id == current_user.id
        ).all()
        
        data = AccountExportService.export_to_json(accounts, db)
        
        return {
            "success": True,
            "count": len(accounts),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== PREFIX ENDPOINTS =====

@router.post("/prefixes/filter", response_model=PaginatedPrefixResponse)
def filter_prefixes(
    filter_req: PrefixFilterRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Filter and search prefixes"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        prefixes, total = PrefixFilterService.apply_filters(
            db, current_user.id, filter_req
        )
        
        # Build enhanced responses
        responses = []
        for prefix in prefixes:
            coverage = PrefixCampaignService.get_prefix_coverage(db, prefix)
            
            response = EnhancedPrefixResponse(
                id=prefix.id,
                prefix=prefix.prefix,
                prefix_name=prefix.prefix_name,
                enabled=prefix.enabled,
                pattern_type="EXACT",  # TODO: get from enhanced model
                pattern=prefix.prefix,
                category="OTHER",  # TODO: get from enhanced model
                color=None,  # TODO: get from enhanced model
                icon=None,  # TODO: get from enhanced model
                total_accounts_linked=coverage["linked_accounts"],
                total_campaigns_matched=coverage["total_campaigns"],
                active_campaigns=coverage["active_campaigns"],
                last_used=prefix.updated_at,
                matched_campaigns=[],
                description=prefix.description,
                test_strings=[],
                metadata=None,
                created_at=prefix.created_at,
                updated_at=prefix.updated_at,
            )
            responses.append(response)
        
        total_pages = (total + filter_req.page_size - 1) // filter_req.page_size
        
        return PaginatedPrefixResponse(
            items=responses,
            total=total,
            page=filter_req.page,
            page_size=filter_req.page_size,
            total_pages=total_pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prefixes/test-pattern", response_model=PatternTestResult)
def test_prefix_pattern(
    req: PrefixMatchTestRequest,
    current_user: User = Depends(get_current_user_optional),
):
    """Test prefix pattern matching"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        result = PrefixPatternService.test_pattern(
            req.pattern,
            req.pattern_type,
            req.test_strings
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prefixes/validate-regex")
def validate_regex(
    pattern: str = Query(...),
    current_user: User = Depends(get_current_user_optional),
):
    """Validate regex pattern"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    is_valid, error = PrefixPatternService.validate_regex_pattern(pattern)
    
    return {
        "valid": is_valid,
        "error": error if not is_valid else None
    }


@router.post("/prefixes/auto-suggest")
def auto_suggest_prefixes(
    req: PrefixAutoSuggestRequest,
    current_user: User = Depends(get_current_user_optional),
):
    """Auto-suggest prefixes from campaign names"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        suggestions = PrefixAutoSuggestService.extract_prefixes_from_campaigns(
            req.campaigns,
            min_frequency=req.min_frequency
        )
        
        # Also detect naming pattern
        campaign_names = [c.get("campaign_name", "") for c in req.campaigns]
        pattern_info = PrefixAutoSuggestService.detect_naming_pattern(campaign_names)
        
        return {
            "suggestions": suggestions,
            "naming_pattern": pattern_info,
            "total_campaigns": len(req.campaigns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prefixes/batch-enable")
def batch_enable_prefixes(
    prefix_ids: List[int] = Query(...),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Batch enable prefixes"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        updated = PrefixBatchService.bulk_enable(db, current_user.id, prefix_ids)
        return {"success": True, "count": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prefixes/batch-disable")
def batch_disable_prefixes(
    prefix_ids: List[int] = Query(...),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Batch disable prefixes"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        updated = PrefixBatchService.bulk_disable(db, current_user.id, prefix_ids)
        return {"success": True, "count": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prefixes/batch-delete")
def batch_delete_prefixes(
    req: PrefixBulkOperationRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Batch delete prefixes"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not req.confirm or req.operation != "delete":
        raise HTTPException(status_code=400, detail="Please confirm deletion")
    
    try:
        deleted = PrefixBatchService.bulk_delete(db, current_user.id, req.prefix_ids)
        return {"success": True, "count": deleted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
