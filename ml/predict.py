"""
PowerPilot AI — Prediction Inference Script
Run standalone predictions from command line.
Usage: python ml/predict.py --horizon next_day
"""
import os
import sys
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.pipeline import load_model, load_csv, build_features

PRED_MODEL_PATH = "ml/models/prediction_model.pkl"


def predict(horizon: str = "next_hour", data_path: str = "data/mock_energy_data.csv"):
    print(f"\n🔮 Running prediction: {horizon}")

    if not os.path.exists(PRED_MODEL_PATH):
        print("❌ Model not trained yet. Run: python ml/train.py")
        return

    model = load_model(PRED_MODEL_PATH)

    if os.path.exists(data_path):
        df = load_csv(data_path)
        values = df["consumption_kwh"].values
    else:
        print("⚠️  No data file. Using synthetic baseline.")
        values = np.array([2.5] * 48)

    # Rolling stats from recent data
    window = min(24, len(values))
    rolling_mean = float(np.mean(values[-window:]))
    rolling_std = float(np.std(values[-window:]) or 0.5)
    lag_1 = float(values[-1])
    lag_24 = float(values[-24]) if len(values) >= 24 else lag_1

    base_ts = datetime.now().replace(minute=0, second=0, microsecond=0)

    if horizon == "next_hour":
        steps = [base_ts + timedelta(hours=1)]
    elif horizon == "next_day":
        steps = [base_ts + timedelta(hours=i) for i in range(1, 25)]
    else:  # next_7_days
        steps = [base_ts + timedelta(hours=i) for i in range(1, 24 * 7 + 1, 4)]

    print(f"\n{'Timestamp':<25} {'Predicted kWh':>15}")
    print("-" * 42)

    for ts in steps:
        X = np.array([[
            ts.hour,
            ts.weekday(),
            ts.month,
            1 if ts.weekday() >= 5 else 0,
            rolling_mean,
            rolling_std,
            lag_1,
            lag_24,
        ]])
        pred = max(0.0, float(model.predict(X)[0]))
        print(f"{ts.strftime('%Y-%m-%d %H:%M'):<25} {pred:>15.3f}")
        rolling_mean = rolling_mean * 0.97 + pred * 0.03
        lag_1 = pred


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PowerPilot AI — Prediction")
    parser.add_argument("--horizon", choices=["next_hour", "next_day", "next_7_days"], default="next_hour")
    args = parser.parse_args()
    predict(args.horizon)
