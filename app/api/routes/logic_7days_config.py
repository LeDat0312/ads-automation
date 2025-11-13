"""
API Routes cho Logic 7 Days Config
CRUD operations cho cấu hình logic lọc 7 ngày
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.logic_7days_config import Logic7DaysConfig
from pydantic import BaseModel

router = APIRouter(prefix="/api/logic-7days-config", tags=["logic-7days-config"])


class Logic7DaysConfigCreate(BaseModel):
    account_id: Optional[str] = None
    prefix: Optional[str] = None
    spend_threshold: float = 100000.0
    gia_data_threshold: float = 0.0  # 0 = dùng từ SL_2_GIA_DATA
    cost_per_purchase_keep_threshold: float = 150000.0
    days: int = 7
    enabled: bool = True


class Logic7DaysConfigUpdate(BaseModel):
    account_id: Optional[str] = None
    prefix: Optional[str] = None
    spend_threshold: Optional[float] = None
    gia_data_threshold: Optional[float] = None
    cost_per_purchase_keep_threshold: Optional[float] = None
    days: Optional[int] = None
    enabled: Optional[bool] = None


class Logic7DaysConfigResponse(BaseModel):
    id: int
    account_id: Optional[str]
    prefix: Optional[str]
    spend_threshold: float
    gia_data_threshold: float
    cost_per_purchase_keep_threshold: float
    days: int
    enabled: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=Logic7DaysConfigResponse, status_code=status.HTTP_201_CREATED)
def create_config(config: Logic7DaysConfigCreate, db: Session = Depends(get_db)):
    """Tạo config mới"""
    # Kiểm tra xem đã có config cho account_id + prefix chưa
    existing = db.query(Logic7DaysConfig).filter(
        Logic7DaysConfig.account_id == config.account_id,
        Logic7DaysConfig.prefix == config.prefix
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Config đã tồn tại cho account_id và prefix này")
    
    new_config = Logic7DaysConfig(**config.dict())
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return new_config


@router.get("/", response_model=List[Logic7DaysConfigResponse])
def read_configs(
    account_id: Optional[str] = None,
    prefix: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lấy danh sách configs"""
    query = db.query(Logic7DaysConfig)
    
    if account_id:
        query = query.filter(Logic7DaysConfig.account_id == account_id)
    if prefix:
        query = query.filter(Logic7DaysConfig.prefix == prefix)
    
    configs = query.offset(skip).limit(limit).all()
    return configs


@router.get("/{config_id}", response_model=Logic7DaysConfigResponse)
def read_config(config_id: int, db: Session = Depends(get_db)):
    """Lấy config theo ID"""
    config = db.query(Logic7DaysConfig).filter(Logic7DaysConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config không tồn tại")
    return config


@router.put("/{config_id}", response_model=Logic7DaysConfigResponse)
def update_config(
    config_id: int,
    config_update: Logic7DaysConfigUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật config"""
    config = db.query(Logic7DaysConfig).filter(Logic7DaysConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config không tồn tại")
    
    update_data = config_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(config_id: int, db: Session = Depends(get_db)):
    """Xóa config"""
    config = db.query(Logic7DaysConfig).filter(Logic7DaysConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config không tồn tại")
    
    db.delete(config)
    db.commit()
    return None

