"""
PowerPilot AI — Anomaly Detection API Routes
GET /anomalies, POST /anomalies/detect
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.anomaly_service import AnomalyService
from backend.app.schemas.anomaly_schema import AnomalyListResponse

router = APIRouter()


@router.get("/anomalies", response_model=AnomalyListResponse, summary="Get stored anomaly results")
def get_anomalies(db: Session = Depends(get_db)):
    """Return previously detected anomalies from the database."""
    service = AnomalyService(db)
    return service.get_stored_anomalies()


@router.post("/anomalies/detect", response_model=AnomalyListResponse, summary="Run anomaly detection")
def detect_anomalies(db: Session = Depends(get_db)):
    """
    Run IsolationForest anomaly detection on all stored energy data.
    Results are persisted to database and returned.
    """
    service = AnomalyService(db)
    return service.detect_and_store()
