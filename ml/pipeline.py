"""
PowerPilot AI — ML Pipeline Utilities
Shared feature engineering and data loading functions
"""
import os
import pickle
import numpy as np
import pandas as pd
from typing import Tuple


# ─── Feature Engineering ─────────────────────────────────────────────────────

def build_features(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build feature matrix and target vector from energy DataFrame.
    
    Expects columns: timestamp, consumption_kwh
    Returns: (X, y)
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Time features
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["week"] = df["timestamp"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = (df["day"] >= 5).astype(int)

    # Rolling stats (window = 24 hours)
    df["rolling_mean_24"] = df["consumption_kwh"].rolling(window=24, min_periods=1).mean()
    df["rolling_std_24"] = df["consumption_kwh"].rolling(window=24, min_periods=1).std().fillna(0)

    # Lag features
    df["lag_1h"] = df["consumption_kwh"].shift(1).fillna(df["consumption_kwh"].mean())
    df["lag_24h"] = df["consumption_kwh"].shift(24).fillna(df["consumption_kwh"].mean())

    feature_cols = [
        "hour", "day", "month", "is_weekend",
        "rolling_mean_24", "rolling_std_24",
        "lag_1h", "lag_24h",
    ]

    X = df[feature_cols].values
    y = df["consumption_kwh"].values

    return X, y


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.lower().strip() for c in df.columns]
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["consumption_kwh"] = pd.to_numeric(df["consumption_kwh"], errors="coerce")
    df = df.dropna(subset=["consumption_kwh"])
    df = df[df["consumption_kwh"] >= 0]
    return df


def save_model(model, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"  💾 Model saved → {path}")


def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)
