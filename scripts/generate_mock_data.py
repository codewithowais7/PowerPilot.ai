"""
PowerPilot AI — Mock Data Generator
Generates realistic hourly electricity consumption data for training and testing.
Output: data/mock_energy_data.csv
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ─── Configuration ───────────────────────────────────────────────────────────
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31, 23, 0, 0)
np.random.seed(42)

print("🔧 Generating mock energy data...")

# ─── Time range ───────────────────────────────────────────────────────────────
timestamps = pd.date_range(start=START_DATE, end=END_DATE, freq="h")
n = len(timestamps)

# ─── Base consumption (kWh) ───────────────────────────────────────────────────
base = 2.5  # base residential load

# Hour of day factor (morning and evening peaks)
def hour_factor(hour):
    if 6 <= hour < 9:      return 1.6  # morning
    elif 9 <= hour < 17:   return 1.2  # daytime
    elif 17 <= hour < 21:  return 1.8  # evening peak
    elif 21 <= hour < 23:  return 1.3  # night
    else:                  return 0.7  # late night / early morning

# Month factor (summer & winter peaks)
def month_factor(month):
    peak_months = {12: 1.4, 1: 1.4, 2: 1.3, 6: 1.3, 7: 1.5, 8: 1.4}
    return peak_months.get(month, 1.0)

hour_factors = np.array([hour_factor(ts.hour) for ts in timestamps])
month_factors = np.array([month_factor(ts.month) for ts in timestamps])
weekday_factors = np.where(timestamps.weekday >= 5, 0.85, 1.0)  # weekend lower

# Smooth trend (gradual growth)
trend = 1.0 + np.linspace(0, 0.1, n)

# Gaussian noise
noise = np.random.normal(0, 0.2, n)

consumption = base * hour_factors * month_factors * weekday_factors * trend + noise
consumption = np.clip(consumption, 0.1, None)

# ─── Inject anomalies (~2%) ───────────────────────────────────────────────────
anomaly_indices = np.random.choice(n, size=int(n * 0.02), replace=False)
for idx in anomaly_indices:
    if np.random.rand() > 0.5:
        consumption[idx] *= np.random.uniform(3.5, 6.0)   # spike
    else:
        consumption[idx] *= np.random.uniform(0.05, 0.15)  # dropout

# ─── Build DataFrame ─────────────────────────────────────────────────────────
df = pd.DataFrame({
    "timestamp": timestamps,
    "consumption_kwh": np.round(consumption, 3),
})

# ─── Save ─────────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
output_path = "data/mock_energy_data.csv"
df.to_csv(output_path, index=False)

print(f"✅ Generated {len(df):,} records → {output_path}")
print(f"   Date range : {df['timestamp'].min()} → {df['timestamp'].max()}")
print(f"   Avg kWh/hr : {df['consumption_kwh'].mean():.3f}")
print(f"   Anomalies  : {len(anomaly_indices)} injected (~{len(anomaly_indices)/n*100:.1f}%)")
print(f"\n📄 Sample:\n{df.head(5).to_string(index=False)}")
