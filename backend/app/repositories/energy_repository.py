"""
PowerPilot AI — Energy Repository (DB access layer)
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional

from backend.app.models.energy_model import EnergyData
from backend.app.schemas.energy_schema import EnergyDataCreate


class EnergyRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_bulk(self, records: List[EnergyDataCreate]) -> int:
        """Insert multiple energy records efficiently"""
        objects = [
            EnergyData(**r.model_dump()) for r in records
        ]
        self.db.bulk_save_objects(objects)
        self.db.commit()
        return len(objects)

    def get_all(self, limit: int = 1000, offset: int = 0) -> List[EnergyData]:
        return (
            self.db.query(EnergyData)
            .order_by(EnergyData.timestamp)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_count(self) -> int:
        return self.db.query(func.count(EnergyData.id)).scalar()

    def get_by_date_range(self, start: datetime, end: datetime) -> List[EnergyData]:
        return (
            self.db.query(EnergyData)
            .filter(EnergyData.timestamp >= start, EnergyData.timestamp <= end)
            .order_by(EnergyData.timestamp)
            .all()
        )

    def get_recent(self, hours: int = 168) -> List[EnergyData]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.db.query(EnergyData)
            .filter(EnergyData.timestamp >= cutoff)
            .order_by(EnergyData.timestamp)
            .all()
        )

    def get_daily_stats(self) -> List[dict]:
        results = (
            self.db.query(
                func.date(EnergyData.timestamp).label("date"),
                func.sum(EnergyData.consumption_kwh).label("total_kwh"),
                func.avg(EnergyData.consumption_kwh).label("avg_kwh"),
                func.max(EnergyData.consumption_kwh).label("max_kwh"),
            )
            .group_by(func.date(EnergyData.timestamp))
            .order_by(func.date(EnergyData.timestamp))
            .all()
        )
        return [
            {"date": str(r.date), "total_kwh": r.total_kwh, "avg_kwh": r.avg_kwh, "max_kwh": r.max_kwh}
            for r in results
        ]

    def get_hourly_stats(self) -> List[dict]:
        results = (
            self.db.query(
                EnergyData.hour,
                func.avg(EnergyData.consumption_kwh).label("avg_kwh"),
            )
            .group_by(EnergyData.hour)
            .order_by(EnergyData.hour)
            .all()
        )
        return [{"hour": r.hour, "avg_kwh": r.avg_kwh} for r in results]

    def delete_all(self):
        self.db.query(EnergyData).delete()
        self.db.commit()
