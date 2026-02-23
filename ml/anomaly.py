"""
PowerPilot AI — Anomaly Detection Script
Run standalone anomaly detection from command line.
Usage: python ml/anomaly.py
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.pipeline import load_model, load_csv

ANOM_MODEL_PATH = "ml/models/anomaly_model.pkl"


def detect_anomalies(data_path: str = "data/mock_energy_data.csv"):
    print("\n🚨 Running Anomaly Detection...")

    if not os.path.exists(ANOM_MODEL_PATH):
        print("❌ Anomaly model not trained yet. Run: python ml/train.py")
        return

    if not os.path.exists(data_path):
        print(f"❌ Data not found: {data_path}")
        return

    model = load_model(ANOM_MODEL_PATH)
    df = load_csv(data_path)
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month

    features = df[["consumption_kwh", "hour", "day", "month"]].values
    predictions = model.predict(features)   # -1 = anomaly, 1 = normal
    scores = model.decision_function(features)

    df["is_anomaly"] = predictions == -1
    df["anomaly_score"] = scores

    n_anomalies = df["is_anomaly"].sum()
    total = len(df)
    rate = n_anomalies / total * 100

    print(f"\n📊 Results: {n_anomalies} anomalies out of {total:,} records ({rate:.2f}%)")
    print(f"\n{'Timestamp':<25} {'Consumption':>12} {'Score':>10} {'Anomaly':>10}")
    print("-" * 62)

    anomalies = df[df["is_anomaly"]].head(20)
    for _, row in anomalies.iterrows():
        ts = str(row["timestamp"])[:19]
        print(f"{ts:<25} {row['consumption_kwh']:>12.3f} {row['anomaly_score']:>10.4f}   {'⚠️ YES':>8}")

    if len(anomalies) < n_anomalies:
        print(f"  ... and {n_anomalies - len(anomalies)} more anomalies")


if __name__ == "__main__":
    detect_anomalies()
