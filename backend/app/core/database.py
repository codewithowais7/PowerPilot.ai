"""
PowerPilot AI — Database Setup (SQLAlchemy + SQLite)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ensure database directory exists
os.makedirs("database", exist_ok=True)

DATABASE_URL = "sqlite:///./database/energy.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize all tables"""
    from backend.app.models import energy_model, prediction_model, anomaly_model  # noqa: F401
    Base.metadata.create_all(bind=engine)
