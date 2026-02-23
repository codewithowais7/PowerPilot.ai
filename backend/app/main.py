"""
PowerPilot AI — FastAPI Application Entry Point
"""
import os
import sys

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.v1 import energy, prediction, anomaly

# ─── App Instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="🔋 AI-powered Smart Energy Intelligence and Optimization Platform",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    os.makedirs("database", exist_ok=True)
    os.makedirs("ml/models", exist_ok=True)
    init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started")
    print("📊 Database initialized")


# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(energy.router, prefix=settings.API_V1_PREFIX, tags=["Energy Data"])
app.include_router(prediction.router, prefix=settings.API_V1_PREFIX, tags=["Predictions"])
app.include_router(anomaly.router, prefix=settings.API_V1_PREFIX, tags=["Anomaly Detection"])


# ─── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ─── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
