"""
PowerPilot AI — Energy API Routes
POST /upload-csv, GET /energy-data, GET /analysis
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.energy_service import EnergyService
from backend.app.schemas.energy_schema import EnergyDataList, EnergyDataResponse, AnalysisResponse

router = APIRouter()


@router.post("/upload-csv", summary="Upload CSV energy data")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    service = EnergyService(db)

    try:
        saved, message = service.process_csv(content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"status": "success", "records_saved": saved, "message": message}


@router.get("/energy-data", summary="Get stored energy data")
def get_energy_data(
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    service = EnergyService(db)
    data = service.get_all_data(limit=limit)
    count = service.get_count()

    return {
        "total": count,
        "returned": len(data),
        "data": [
            {
                "id": d.id,
                "timestamp": d.timestamp.isoformat(),
                "consumption_kwh": d.consumption_kwh,
                "hour": d.hour,
                "day": d.day,
                "month": d.month,
                "is_weekend": d.is_weekend,
            }
            for d in data
        ],
    }


@router.get("/analysis", response_model=AnalysisResponse, summary="Get energy analysis and recommendations")
def get_analysis(db: Session = Depends(get_db)):
    service = EnergyService(db)
    return service.get_analysis()
