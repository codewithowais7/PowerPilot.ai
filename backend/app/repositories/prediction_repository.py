"""
PowerPilot AI — Prediction Repository
"""
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.app.models.prediction_model import PredictionData
from backend.app.schemas.prediction_schema import PredictionDataCreate


class PredictionRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_bulk(self, records: List[PredictionDataCreate]) -> int:
        objects = [PredictionData(**r.model_dump()) for r in records]
        self.db.bulk_save_objects(objects)
        self.db.commit()
        return len(objects)

    def get_all(self, limit: int = 500) -> List[PredictionData]:
        return (
            self.db.query(PredictionData)
            .order_by(PredictionData.timestamp)
            .limit(limit)
            .all()
        )

    def get_by_horizon(self, horizon: int, limit: int = 500) -> List[PredictionData]:
        return (
            self.db.query(PredictionData)
            .filter(PredictionData.prediction_horizon == horizon)
            .order_by(PredictionData.timestamp)
            .limit(limit)
            .all()
        )

    def delete_all(self):
        self.db.query(PredictionData).delete()
        self.db.commit()
