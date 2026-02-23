# ⚡ PowerPilot AI

> **Smart Energy Intelligence & Optimization Platform**
> AI-powered system for energy consumption analysis, prediction, and anomaly detection.

---

## 🏗️ Architecture

```
PowerPilot/
├── backend/           # FastAPI REST API
│   └── app/
│       ├── api/v1/    # Endpoints: energy, prediction, anomaly
│       ├── core/      # Config & Database (SQLAlchemy + SQLite)
│       ├── models/    # SQLAlchemy ORM models
│       ├── schemas/   # Pydantic request/response schemas
│       ├── services/  # Business logic layer
│       └── repositories/  # DB access layer
├── frontend/          # Streamlit dashboard (futuristic UI)
│   ├── pages/         # Dashboard, Predictions, Anomaly, Analytics
│   ├── components/    # Particle background, animated UI
│   └── styles/        # CSS (glassmorphism, neon effects)
├── ml/                # ML pipeline
│   ├── pipeline.py    # Feature engineering utilities
│   ├── train.py       # Train RandomForest + IsolationForest
│   ├── predict.py     # CLI prediction inference
│   └── anomaly.py     # CLI anomaly detection
├── scripts/
│   └── generate_mock_data.py  # Realistic data generator
└── database/          # SQLite (auto-created)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 2. Generate Mock Data & Train Models

```bash
# Generate 2 years of hourly data
python scripts/generate_mock_data.py

# Train RandomForest (prediction) + IsolationForest (anomaly)
python ml/train.py
```

### 3. Start Backend (FastAPI)

```bash
cd e:\PowerPilot
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend available at: http://localhost:8000  
API docs: http://localhost:8000/docs

### 4. Start Frontend (Streamlit)

```bash
cd e:\PowerPilot\frontend
streamlit run app.py
```

Dashboard available at: http://localhost:8501

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload-csv` | Upload & process CSV |
| `GET` | `/api/v1/energy-data` | Get stored data |
| `GET` | `/api/v1/analysis` | Analysis & recommendations |
| `GET` | `/api/v1/predict?horizon=next_day` | ML predictions |
| `GET` | `/api/v1/anomalies` | Get anomaly results |
| `POST` | `/api/v1/anomalies/detect` | Run anomaly detection |

### Prediction Horizons
- `next_hour` — 1 hour ahead
- `next_day` — 24 hours ahead  
- `next_7_days` — 7-day forecast

---

## 📊 CSV Format

Your CSV must contain these columns:

```csv
timestamp,consumption_kwh
2024-01-01 00:00:00,2.345
2024-01-01 01:00:00,1.987
...
```

**Accepted timestamp column names:** `timestamp`, `datetime`, `date`, `time`  
**Accepted consumption column names:** `consumption_kwh`, `consumption`, `kwh`, `energy`, `usage`

---

## 🤖 ML Models

| Model | Algorithm | Purpose |
|-------|-----------|---------|
| Prediction | RandomForestRegressor (100 trees) | Forecast energy consumption |
| Anomaly | IsolationForest (contamination=2%) | Detect abnormal patterns |

**Features used for prediction:**
- Hour of day, Day of week, Month
- Weekend flag
- 24h rolling mean & std dev
- Lag-1h and Lag-24h values

---

## 🎨 UI Features

- 🌌 **tsParticles** — Animated neon particles with cursor interaction
- 💎 **Glassmorphism** — Frosted glass metric cards
- ✨ **Neon glows** — Orbitron font with animated text shadows
- 🌊 **Grid animations** — Moving background scanlines
- 📊 **Plotly** — Interactive energy charts with confidence bands

---

## 🐳 Docker

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:8501
