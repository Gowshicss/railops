from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from app.database import get_db
from app.schemas.plan_schemas import ActivePossessionResponse
from app.schemas.station_schemas import MaintenanceHistoryResponse, MaintenanceCompleteRequest
from app.services.possession_service import complete_maintenance_block

router = APIRouter(prefix="/api/possessions", tags=["Possessions"])

@router.get("/active", response_model=List[ActivePossessionResponse])
def get_active_possessions(db: Database = Depends(get_db)):
    return list(db["active_possessions"].find({}, {"_id": 0}).sort("created_at", -1))

@router.post("/complete", response_model=MaintenanceHistoryResponse)
def complete_possession(data: MaintenanceCompleteRequest, db: Database = Depends(get_db)):
    try:
        history_entry = complete_maintenance_block(
            db=db,
            block_id=data.block_id,
            station_code=data.station_code or "SA",
            actual_start=data.actual_start_time or "12:10",
            actual_end=data.actual_end_time or "13:40",
            work_summary=data.work_summary or "Track possession executed and certified clear.",
            crew_gang=data.crew_gang or "Gang #4"
        )
        return history_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
