"""
PowerPilot AI — Anomaly Service
Loads trained IsolationForest model, detects anomalies in energy data
"""
import os
import pickle
import numpy as np
import pandas as pd
from typing import List

from sqlalchemy.orm import Session
from backend.app.repositories.energy_repository import EnergyRepository
from backend.app.repositories.anomaly_repository import AnomalyRepository
from backend.app.schemas.anomaly_schema import AnomalyDataCreate, AnomalyListResponse, AnomalyDataResponse
from backend.app.core.config import settings


class AnomalyService:

    def __init__(self, db: Session):
        self.energy_repo = EnergyRepository(db)
        self.anomaly_repo = AnomalyRepository(db)
        self.model = self._load_model()

    def _load_model(self):
        path = settings.ANOMALY_MODEL_PATH
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
        return None

    def detect_and_store(self) -> AnomalyListResponse:
        """
        Run anomaly detection on all stored energy data and persist results.
        """
        all_data = self.energy_repo.get_all(limit=10000)
        if not all_data:
            return AnomalyListResponse(total_records=0, total_anomalies=0, anomaly_rate=0.0, anomalies=[])

        df = pd.DataFrame([{
            "timestamp": d.timestamp,
            "consumption_kwh": d.consumption_kwh,
            "hour": d.hour,
            "day": d.day,
            "month": d.month,
        } for d in all_data])

        features = df[["consumption_kwh", "hour", "day", "month"]].values

        if self.model is not None:
            scores = self.model.decision_function(features)
            predictions = self.model.predict(features)  # -1 = anomaly, 1 = normal
            is_anomaly = predictions == -1
        else:
            # Statistical fallback: z-score > 3 = anomaly
            mean = features[:, 0].mean()
            std = features[:, 0].std() or 1.0
            z_scores = np.abs((features[:, 0] - mean) / std)
            is_anomaly = z_scores > 3
            scores = -z_scores

        records = [
            AnomalyDataCreate(
                timestamp=df.iloc[i]["timestamp"],
                consumption=float(df.iloc[i]["consumption_kwh"]),
                is_anomaly=bool(is_anomaly[i]),
                anomaly_score=float(scores[i]),
            )
            for i in range(len(df))
        ]

        self.anomaly_repo.delete_all()
        self.anomaly_repo.create_bulk(records)

        total = len(records)
        anomalies_count = int(np.sum(is_anomaly))
        rate = round(anomalies_count / total * 100, 2) if total > 0 else 0.0

        anomaly_records = [r for r in records if r.is_anomaly]
        anomaly_responses = [
            AnomalyDataResponse(
                id=i,
                timestamp=r.timestamp,
                consumption=r.consumption,
                is_anomaly=r.is_anomaly,
                anomaly_score=r.anomaly_score,
            )
            for i, r in enumerate(anomaly_records, 1)
        ]

        return AnomalyListResponse(
            total_records=total,
            total_anomalies=anomalies_count,
            anomaly_rate=rate,
            anomalies=anomaly_responses,
        )

    def get_stored_anomalies(self) -> AnomalyListResponse:
        """Return previously detected anomalies from DB"""
        total, anomalies_count = self.anomaly_repo.get_counts()
        all_records = self.anomaly_repo.get_all()

        responses = [
            AnomalyDataResponse(
                id=r.id,
                timestamp=r.timestamp,
                consumption=r.consumption,
                is_anomaly=r.is_anomaly,
                anomaly_score=r.anomaly_score,
            )
            for r in all_records if r.is_anomaly
        ]

        rate = round(anomalies_count / total * 100, 2) if total > 0 else 0.0
        return AnomalyListResponse(
            total_records=total,
            total_anomalies=anomalies_count,
            anomaly_rate=rate,
            anomalies=responses,
        )
