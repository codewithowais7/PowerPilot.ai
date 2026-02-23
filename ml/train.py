"""
PowerPilot AI — Model Training Script
Trains RandomForestRegressor (prediction) + IsolationForest (anomaly detection)
Run from project root: python ml/train.py
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Ensure project root in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.pipeline import build_features, load_csv, save_model

DATA_PATH = "data/mock_energy_data.csv"
PRED_MODEL_PATH = "ml/models/prediction_model.pkl"
ANOM_MODEL_PATH = "ml/models/anomaly_model.pkl"


def train_prediction_model(df: pd.DataFrame):
    print("\n🤖 Training Prediction Model (RandomForestRegressor)...")

    X, y = build_features(df)

    # Train/test split (80/20, time-ordered)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"  📈 MAE  : {mae:.4f} kWh")
    print(f"  📈 R²   : {r2:.4f}")
    print(f"  📈 Accuracy (approx): {round(r2 * 100, 2)}%")

    save_model(model, PRED_MODEL_PATH)
    return model, r2


def train_anomaly_model(df: pd.DataFrame):
    print("\n🚨 Training Anomaly Detection Model (IsolationForest)...")

    features = ["consumption_kwh", "hour", "day", "month"]
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month

    X = df[features].values

    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,  # ~2% anomaly rate
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)

    predictions = model.predict(X)
    n_anomalies = (predictions == -1).sum()
    print(f"  🔍 Detected {n_anomalies} anomalies out of {len(X)} samples ({n_anomalies/len(X)*100:.2f}%)")

    save_model(model, ANOM_MODEL_PATH)
    return model


def main():
    print("=" * 50)
    print("  PowerPilot AI — Model Training")
    print("=" * 50)

    # Load data
    if not os.path.exists(DATA_PATH):
        print(f"❌ Data file not found: {DATA_PATH}")
        print("   Run: python scripts/generate_mock_data.py first")
        sys.exit(1)

    print(f"\n📂 Loading data from {DATA_PATH}...")
    df = load_csv(DATA_PATH)
    print(f"  ✅ {len(df):,} records loaded")

    os.makedirs("ml/models", exist_ok=True)

    # Train models
    pred_model, r2 = train_prediction_model(df)
    anom_model = train_anomaly_model(df)

    print("\n" + "=" * 50)
    print("✅ Training complete!")
    print(f"   Prediction model → {PRED_MODEL_PATH}")
    print(f"   Anomaly model    → {ANOM_MODEL_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    main()
