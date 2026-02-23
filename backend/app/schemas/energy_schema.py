"""
PowerPilot AI — Energy Pydantic Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class EnergyDataBase(BaseModel):
    timestamp: datetime
    consumption_kwh: float
    hour: int
    day: int
    month: int
    is_weekend: bool


class EnergyDataCreate(EnergyDataBase):
    pass


class EnergyDataResponse(EnergyDataBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EnergyDataList(BaseModel):
    total: int
    data: List[EnergyDataResponse]


class AnalysisResponse(BaseModel):
    daily_usage: float
    weekly_usage: float
    monthly_usage: float
    yearly_usage: float
    peak_hours: List[int]
    low_usage_hours: List[int]
    trend: str
    recommendations: List[str]
