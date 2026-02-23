"""
PowerPilot AI — Anomaly Repository
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.app.models.anomaly_model import AnomalyData
from backend.app.schemas.anomaly_schema import AnomalyDataCreate


class AnomalyRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_bulk(self, records: List[AnomalyDataCreate]) -> int:
        objects = [AnomalyData(**r.model_dump()) for r in records]
        self.db.bulk_save_objects(objects)
        self.db.commit()
        return len(objects)

    def get_all(self, limit: int = 1000) -> List[AnomalyData]:
        return (
            self.db.query(AnomalyData)
            .order_by(AnomalyData.timestamp)
            .limit(limit)
            .all()
        )

    def get_anomalies_only(self) -> List[AnomalyData]:
        return (
            self.db.query(AnomalyData)
            .filter(AnomalyData.is_anomaly == True)
            .order_by(AnomalyData.timestamp)
            .all()
        )

    def get_counts(self):
        total = self.db.query(func.count(AnomalyData.id)).scalar()
        anomalies = (
            self.db.query(func.count(AnomalyData.id))
            .filter(AnomalyData.is_anomaly == True)
            .scalar()
        )
        return total, anomalies

    def delete_all(self):
        self.db.query(AnomalyData).delete()
        self.db.commit()
