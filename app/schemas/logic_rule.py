"""
Pydantic Schemas cho LogicRule
Validation và serialization
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class Condition(BaseModel):
    """Single condition"""
    metric: str  # "spend", "cpl", "roas", "leads", etc.
    timeframe: str  # "today", "last_3days", "last_7days", "yesterday"
    operator: str  # ">", "<", ">=", "<=", "==", "!="
    value: Union[float, int, Dict[str, Any]]  # Số hoặc {multiplier, base_metric, base_timeframe}
    
    @validator('operator')
    def validate_operator(cls, v):
        allowed = [">", "<", ">=", "<=", "==", "!="]
        if v not in allowed:
            raise ValueError(f"Operator must be one of {allowed}")
        return v


class ConditionsGroup(BaseModel):
    """Group of conditions with AND/OR logic"""
    AND: Optional[List[Condition]] = None
    OR: Optional[List[Condition]] = None
    
    @validator('*', pre=True)
    def validate_conditions(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("Conditions must be a list")
        return v


class LogicRuleCreate(BaseModel):
    """Schema để tạo rule mới"""
    name: str = Field(..., min_length=1, max_length=200)
    folder: Optional[str] = Field(default="General", max_length=100)
    account_ids: List[str] = Field(default_factory=list)  # [] = all accounts
    prefixes: Optional[List[Optional[str]]] = Field(default_factory=list)  # [null] = all prefixes
    conditions: ConditionsGroup
    action: str = Field(..., min_length=1)  # "INCREASE_BUDGET", "DECREASE_BUDGET", "PAUSE", "RESUME"
    action_params: Dict[str, Any] = Field(default_factory=dict)
    schedule: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    status: str = Field(default="DRAFT")  # "DRAFT", "LIVE", "PAUSED"
    description: Optional[str] = None
    
    @validator('action')
    def validate_action(cls, v):
        allowed = ["INCREASE_BUDGET", "DECREASE_BUDGET", "PAUSE", "RESUME", "DUPLICATE_CAMPAIGN"]
        if v.upper() not in allowed:
            raise ValueError(f"Action must be one of {allowed}")
        return v.upper()
    
    @validator('status')
    def validate_status(cls, v):
        allowed = ["DRAFT", "LIVE", "PAUSED"]
        if v.upper() not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v.upper()


class LogicRuleUpdate(BaseModel):
    """Schema để cập nhật rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    folder: Optional[str] = Field(None, max_length=100)
    account_ids: Optional[List[str]] = None
    prefixes: Optional[List[Optional[str]]] = None
    conditions: Optional[ConditionsGroup] = None
    action: Optional[str] = None
    action_params: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    status: Optional[str] = None
    description: Optional[str] = None
    
    @validator('action')
    def validate_action(cls, v):
        if v is None:
            return v
        allowed = ["INCREASE_BUDGET", "DECREASE_BUDGET", "PAUSE", "RESUME", "DUPLICATE_CAMPAIGN"]
        if v.upper() not in allowed:
            raise ValueError(f"Action must be one of {allowed}")
        return v.upper()
    
    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        allowed = ["DRAFT", "LIVE", "PAUSED"]
        if v.upper() not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v.upper()


class LogicRuleResponse(BaseModel):
    """Schema để trả về rule"""
    id: int
    name: str
    folder: str
    account_ids: List[str]
    prefixes: List[Optional[str]]
    conditions: Dict[str, Any]
    action: str
    action_params: Dict[str, Any]
    schedule: Dict[str, Any]
    filters: Dict[str, Any]
    enabled: bool
    status: str
    created_at: datetime
    updated_at: datetime
    version: int
    description: Optional[str] = None
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class LogicRuleListResponse(BaseModel):
    """Schema để list rules"""
    total: int
    rules: List[LogicRuleResponse]

