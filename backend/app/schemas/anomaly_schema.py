"""
PowerPilot AI — Anomaly Pydantic Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class AnomalyDataCreate(BaseModel):
    timestamp: datetime
    consumption: float
    is_anomaly: bool
    anomaly_score: Optional[float] = None


class AnomalyDataResponse(BaseModel):
    id: int
    timestamp: datetime
    consumption: float
    is_anomaly: bool
    anomaly_score: Optional[float] = None

    model_config = {"from_attributes": True}


class AnomalyListResponse(BaseModel):
    total_records: int
    total_anomalies: int
    anomaly_rate: float
    anomalies: List[AnomalyDataResponse]
