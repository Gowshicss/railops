from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.database import Database
from app.database import get_db
from app.schemas.station_schemas import StationResponse, MaintenanceHistoryResponse

router = APIRouter(prefix="/api/stations", tags=["Stations"])

@router.get("", response_model=List[StationResponse])
def get_stations(db: Database = Depends(get_db)):
    return list(db["stations"].find({}, {"_id": 0}).sort("station_name", 1))

@router.get("/network/sections")
def get_railway_sections(db: Database = Depends(get_db)):
    return list(db["railway_sections"].find({}, {"_id": 0}))

@router.get("/records/search", response_model=List[MaintenanceHistoryResponse])
def search_maintenance_history(
    q: Optional[str] = None,
    station: Optional[str] = None,
    department: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
    db: Database = Depends(get_db)
):
    query: dict = {}
    if station and station != "ALL":
        query["station_code"] = station.upper()
    if department and department != "ALL":
        query["department"] = {"$regex": department, "$options": "i"}
    if year:
        query["year"] = year
    if status and status != "ALL":
        query["status"] = {"$regex": f"^{status}$", "$options": "i"}
    if q:
        regex_q = {"$regex": q, "$options": "i"}
        query["$or"] = [
            {"maintenance_id": regex_q},
            {"station_name": regex_q},
            {"asset_id": regex_q},
            {"description": regex_q},
            {"maintenance_type": regex_q},
        ]
    return list(db["station_maintenance_history"].find(query, {"_id": 0}).sort([("year", -1), ("created_at", -1)]))

@router.get("/{station_code}", response_model=StationResponse)
def get_station(station_code: str, db: Database = Depends(get_db)):
    st = db["stations"].find_one({"station_code": station_code.upper()}, {"_id": 0})
    if not st:
        raise HTTPException(status_code=404, detail="Station not found")
    return st

@router.get("/{station_code}/history", response_model=List[MaintenanceHistoryResponse])
def get_station_history(station_code: str, db: Database = Depends(get_db)):
    return list(db["station_maintenance_history"].find(
        {"station_code": station_code.upper()},
        {"_id": 0}
    ).sort([("year", -1), ("created_at", -1)]))
