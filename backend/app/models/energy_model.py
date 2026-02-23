"""
PowerPilot AI — Energy Data SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, Float, DateTime, Boolean, String
from sqlalchemy.sql import func
from backend.app.core.database import Base


class EnergyData(Base):
    __tablename__ = "energy_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    consumption_kwh = Column(Float, nullable=False)
    hour = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    is_weekend = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
