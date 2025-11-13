"""
API Routes cho quản lý Accounts và Prefixes
Cho phép thêm/sửa/xóa accounts và prefixes động
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.account_prefix import Account, Prefix

router = APIRouter(prefix="/api/accounts-prefixes", tags=["accounts_prefixes"])


# Schemas
class AccountCreate(BaseModel):
    account_id: str
    account_name: Optional[str] = None
    enabled: bool = True
    description: Optional[str] = None


class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class AccountResponse(BaseModel):
    id: int
    account_id: str
    account_name: Optional[str]
    enabled: bool
    description: Optional[str]
    
    class Config:
        from_attributes = True


class PrefixCreate(BaseModel):
    prefix: str
    prefix_name: Optional[str] = None
    enabled: bool = True
    description: Optional[str] = None


class PrefixUpdate(BaseModel):
    prefix_name: Optional[str] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class PrefixResponse(BaseModel):
    id: int
    prefix: str
    prefix_name: Optional[str]
    enabled: bool
    description: Optional[str]
    
    class Config:
        from_attributes = True


# Account endpoints
@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(enabled: Optional[bool] = None, db: Session = Depends(get_db)):
    """Lấy danh sách accounts"""
    query = db.query(Account)
    if enabled is not None:
        query = query.filter(Account.enabled == enabled)
    return query.order_by(Account.account_id).all()


@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    """Tạo account mới"""
    # Check duplicate
    existing = db.query(Account).filter(Account.account_id == account_data.account_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Account {account_data.account_id} đã tồn tại")
    
    account = Account(**account_data.dict())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/accounts/{account_id}", response_model=AccountResponse)
def update_account(account_id: str, account_data: AccountUpdate, db: Session = Depends(get_db)):
    """Cập nhật account"""
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for key, value in account_data.dict(exclude_unset=True).items():
        setattr(account, key, value)
    
    db.commit()
    db.refresh(account)
    return account


@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: str, db: Session = Depends(get_db)):
    """Xóa account"""
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(account)
    db.commit()
    return None


# Prefix endpoints
@router.get("/prefixes", response_model=List[PrefixResponse])
def list_prefixes(enabled: Optional[bool] = None, db: Session = Depends(get_db)):
    """Lấy danh sách prefixes"""
    query = db.query(Prefix)
    if enabled is not None:
        query = query.filter(Prefix.enabled == enabled)
    return query.order_by(Prefix.prefix).all()


@router.post("/prefixes", response_model=PrefixResponse, status_code=201)
def create_prefix(prefix_data: PrefixCreate, db: Session = Depends(get_db)):
    """Tạo prefix mới"""
    # Check duplicate
    existing = db.query(Prefix).filter(Prefix.prefix == prefix_data.prefix).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Prefix {prefix_data.prefix} đã tồn tại")
    
    prefix = Prefix(**prefix_data.dict())
    db.add(prefix)
    db.commit()
    db.refresh(prefix)
    return prefix


@router.put("/prefixes/{prefix}", response_model=PrefixResponse)
def update_prefix(prefix: str, prefix_data: PrefixUpdate, db: Session = Depends(get_db)):
    """Cập nhật prefix"""
    prefix_obj = db.query(Prefix).filter(Prefix.prefix == prefix).first()
    if not prefix_obj:
        raise HTTPException(status_code=404, detail="Prefix not found")
    
    for key, value in prefix_data.dict(exclude_unset=True).items():
        setattr(prefix_obj, key, value)
    
    db.commit()
    db.refresh(prefix_obj)
    return prefix_obj


@router.delete("/prefixes/{prefix}", status_code=204)
def delete_prefix(prefix: str, db: Session = Depends(get_db)):
    """Xóa prefix"""
    prefix_obj = db.query(Prefix).filter(Prefix.prefix == prefix).first()
    if not prefix_obj:
        raise HTTPException(status_code=404, detail="Prefix not found")
    
    db.delete(prefix_obj)
    db.commit()
    return None

