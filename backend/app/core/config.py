"""
PowerPilot AI — Core Configuration
"""
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    APP_NAME: str = "PowerPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./database/energy.db"

    # ML Model paths
    PREDICTION_MODEL_PATH: str = "ml/models/prediction_model.pkl"
    ANOMALY_MODEL_PATH: str = "ml/models/anomaly_model.pkl"

    # API
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
