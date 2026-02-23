"""
PowerPilot AI — Prediction Data SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from backend.app.core.database import Base


class PredictionData(Base):
    __tablename__ = "prediction_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    predicted_value = Column(Float, nullable=False)
    prediction_horizon = Column(Integer, default=1)  # hours ahead
    created_at = Column(DateTime, server_default=func.now())
