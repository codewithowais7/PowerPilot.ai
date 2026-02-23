"""
PowerPilot AI — Prediction Pydantic Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class PredictionRequest(BaseModel):
    horizon: str = "next_hour"  # next_hour | next_day | next_7_days


class PredictionPoint(BaseModel):
    timestamp: datetime
    predicted_value: float


class PredictionResponse(BaseModel):
    horizon: str
    predictions: List[PredictionPoint]
    model_accuracy: Optional[float] = None


class PredictionDataCreate(BaseModel):
    timestamp: datetime
    predicted_value: float
    prediction_horizon: int = 1


class PredictionDataResponse(BaseModel):
    id: int
    timestamp: datetime
    predicted_value: float
    prediction_horizon: int

    model_config = {"from_attributes": True}
