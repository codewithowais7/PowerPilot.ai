"""
PowerPilot AI — Energy Service (Business Logic)
Handles: CSV upload, data cleaning, feature engineering, analysis
"""
import io
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session

from backend.app.repositories.energy_repository import EnergyRepository
from backend.app.schemas.energy_schema import EnergyDataCreate, AnalysisResponse


class EnergyService:

    def __init__(self, db: Session):
        self.repo = EnergyRepository(db)

    # ─── CSV Processing ────────────────────────────────────────────────────────

    def process_csv(self, file_content: bytes) -> Tuple[int, str]:
        """
        Parse, clean, feature-engineer, and store CSV energy data.
        Expected CSV columns: timestamp, consumption_kwh
        Returns (records_saved, message)
        """
        try:
            df = pd.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"Cannot parse CSV: {e}")

        # Normalize column names
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

        # Find timestamp column
        ts_col = None
        for candidate in ["timestamp", "datetime", "date", "time"]:
            if candidate in df.columns:
                ts_col = candidate
                break
        if ts_col is None:
            raise ValueError("CSV must contain a 'timestamp' or 'datetime' column")

        # Find consumption column
        kw_col = None
        for candidate in ["consumption_kwh", "consumption", "kwh", "energy", "usage"]:
            if candidate in df.columns:
                kw_col = candidate
                break
        if kw_col is None:
            raise ValueError("CSV must contain a consumption column (consumption_kwh, kwh, etc.)")

        df = df[[ts_col, kw_col]].copy()
        df.columns = ["timestamp", "consumption_kwh"]

        # Parse timestamps
        df["timestamp"] = pd.to_datetime(df["timestamp"], infer_datetime_format=True, errors="coerce")
        df = df.dropna(subset=["timestamp"])

        # Remove duplicates
        df = df.drop_duplicates(subset=["timestamp"])

        # Handle missing consumption values
        df["consumption_kwh"] = pd.to_numeric(df["consumption_kwh"], errors="coerce")
        df["consumption_kwh"] = df["consumption_kwh"].fillna(df["consumption_kwh"].median())

        # Remove negative values
        df = df[df["consumption_kwh"] >= 0]

        # Feature engineering
        df["hour"] = df["timestamp"].dt.hour
        df["day"] = df["timestamp"].dt.dayofweek
        df["month"] = df["timestamp"].dt.month
        df["is_weekend"] = df["day"].isin([5, 6])

        df = df.sort_values("timestamp").reset_index(drop=True)

        # Build schema objects
        records = [
            EnergyDataCreate(
                timestamp=row["timestamp"],
                consumption_kwh=float(row["consumption_kwh"]),
                hour=int(row["hour"]),
                day=int(row["day"]),
                month=int(row["month"]),
                is_weekend=bool(row["is_weekend"]),
            )
            for _, row in df.iterrows()
        ]

        saved = self.repo.create_bulk(records)
        return saved, f"Successfully processed and stored {saved} records"

    # ─── Data Retrieval ────────────────────────────────────────────────────────

    def get_all_data(self, limit: int = 1000):
        return self.repo.get_all(limit=limit)

    def get_count(self):
        return self.repo.get_count()

    # ─── Analysis Engine ───────────────────────────────────────────────────────

    def get_analysis(self) -> AnalysisResponse:
        all_data = self.repo.get_all(limit=10000)
        if not all_data:
            return AnalysisResponse(
                daily_usage=0, weekly_usage=0, monthly_usage=0, yearly_usage=0,
                peak_hours=[], low_usage_hours=[], trend="No data",
                recommendations=["Upload energy data to get started"]
            )

        df = pd.DataFrame([{
            "timestamp": d.timestamp,
            "consumption_kwh": d.consumption_kwh,
            "hour": d.hour,
            "day": d.day,
            "month": d.month,
            "is_weekend": d.is_weekend,
        } for d in all_data])

        # Aggregate stats
        hourly = df.groupby("hour")["consumption_kwh"].mean()
        daily_usage = float(df["consumption_kwh"].sum() / max(df["timestamp"].dt.date.nunique(), 1))
        weekly_usage = daily_usage * 7
        monthly_usage = daily_usage * 30
        yearly_usage = daily_usage * 365

        # Peak / low hours
        peak_hours = hourly.nlargest(3).index.tolist()
        low_usage_hours = hourly.nsmallest(3).index.tolist()

        # Trend (rolling mean slope)
        daily_sums = df.groupby(df["timestamp"].dt.date)["consumption_kwh"].sum().reset_index()
        if len(daily_sums) >= 3:
            first_half = daily_sums["consumption_kwh"].iloc[:len(daily_sums)//2].mean()
            second_half = daily_sums["consumption_kwh"].iloc[len(daily_sums)//2:].mean()
            if second_half > first_half * 1.05:
                trend = "Increasing ↑"
            elif second_half < first_half * 0.95:
                trend = "Decreasing ↓"
            else:
                trend = "Stable →"
        else:
            trend = "Insufficient data"

        # Recommendations
        recommendations = self._generate_recommendations(peak_hours, hourly, df)

        return AnalysisResponse(
            daily_usage=round(daily_usage, 2),
            weekly_usage=round(weekly_usage, 2),
            monthly_usage=round(monthly_usage, 2),
            yearly_usage=round(yearly_usage, 2),
            peak_hours=peak_hours,
            low_usage_hours=low_usage_hours,
            trend=trend,
            recommendations=recommendations,
        )

    def _generate_recommendations(self, peak_hours, hourly, df) -> List[str]:
        recs = []

        if peak_hours:
            peak_str = ", ".join([f"{h}:00" for h in peak_hours])
            recs.append(
                f"⚡ High usage detected at {peak_str}. Shift heavy loads to off-peak hours."
            )

        avg_weekend = df[df["is_weekend"] == True]["consumption_kwh"].mean() if df["is_weekend"].any() else 0
        avg_weekday = df[df["is_weekend"] == False]["consumption_kwh"].mean() if (~df["is_weekend"]).any() else 0
        if avg_weekend > avg_weekday * 1.1:
            recs.append("🏠 Weekend usage is significantly higher. Review home appliance usage on weekends.")

        if hourly.max() > hourly.mean() * 2:
            recs.append("📊 Energy usage is uneven across hours. Consider spreading load more evenly.")

        monthly_avg = df.groupby("month")["consumption_kwh"].mean()
        if not monthly_avg.empty:
            peak_month = monthly_avg.idxmax()
            recs.append(
                f"📅 Month {peak_month} has the highest consumption. Check heating/cooling systems."
            )

        recs.append("💡 Consider switching to LED lighting and smart power strips to reduce standby power.")
        recs.append("🔋 Installing a smart meter can help track real-time consumption and reduce waste.")

        return recs
