"""
PowerPilot AI — Prediction API Routes
GET /predict
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.prediction_service import PredictionService
from backend.app.schemas.prediction_schema import PredictionResponse

router = APIRouter()


@router.get("/predict", response_model=PredictionResponse, summary="Get energy predictions")
def predict(
    horizon: str = Query("next_hour", enum=["next_hour", "next_day", "next_7_days"]),
    db: Session = Depends(get_db),
):
    """
    Predict future energy consumption.
    - **next_hour**: Predict next 1 hour
    - **next_day**: Predict next 24 hours
    - **next_7_days**: Predict next 7 days (42 data points, 4h interval)
    """
    service = PredictionService(db)
    return service.predict(horizon=horizon)
