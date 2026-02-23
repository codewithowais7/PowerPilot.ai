"""
PowerPilot AI — Anomaly Data SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, Float, DateTime, Boolean
from sqlalchemy.sql import func
from backend.app.core.database import Base


class AnomalyData(Base):
    __tablename__ = "anomaly_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    consumption = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
