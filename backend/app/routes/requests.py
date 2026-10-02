from typing import List, Optional
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from app.database import get_db, get_next_sequence, clean_doc
from app.models.request import MaintenanceRequest
from app.models.audit import AuditLog
from app.schemas.request_schemas import RequestCreate, RequestResponse
from app.schemas.station_schemas import TrackAssetResponse

router = APIRouter(prefix="/api/requests", tags=["Requests"])

@router.get("", response_model=List[RequestResponse])
def get_requests(
    department: Optional[str] = None,
    status: Optional[str] = None,
    db: Database = Depends(get_db)
):
    query = {}
    if department and department != "ALL":
        query["department"] = {"$regex": department, "$options": "i"}
    if status:
        query["status"] = status
    docs = list(db["maintenance_requests"].find(query, {"_id": 0}).sort("created_at", -1))
    return docs

@router.post("", response_model=RequestResponse)
def create_request(data: RequestCreate, db: Database = Depends(get_db)):
    req_num = random.randint(145, 999)
    req_id = f"BR-2026-0{req_num}"
    
    # Check conflict flag heuristically
    conflict_flag = "PENDING"
    conflict_summary = "Awaiting central intelligence scheduling analysis"
    if "11:30" in data.requested_start_time or "14:00" in data.requested_start_time:
        conflict_flag = "CONFLICT DETECTED"
        conflict_summary = "Corridor slot overlaps scheduled passenger train running"

    new_req = MaintenanceRequest(
        request_id=req_id,
        department=data.department,
        dept_ref=data.dept_ref or "TMS",
        station_code=data.station_code,
        zone=data.zone or "SR",
        segment=data.segment,
        track=data.track or "UP LINE",
        asset_id=data.asset_id,
        maintenance_type=data.maintenance_type,
        description=data.description,
        requested_date=data.requested_date,
        requested_start_time=data.requested_start_time,
        requested_end_time=data.requested_end_time,
        duration_minutes=data.duration_minutes or 90,
        priority=data.priority or "HIGH",
        urgency=data.urgency or "High",
        asset_criticality=data.asset_criticality or "Tier-1",
        reason=data.reason,
        status="SUBMITTED",
        conflict_flag=conflict_flag,
        conflict_summary=conflict_summary
    ).to_dict()
    db["maintenance_requests"].insert_one(new_req)

    audit = AuditLog(
        id=get_next_sequence(db, "audit_logs"),
        user=f"{data.department} Supervisor",
        role="ENGINEERING" if "eng" in data.department.lower() else "OPERATOR",
        action="Request Created",
        entity_type="REQUEST",
        entity_id=req_id,
        previous_status=None,
        new_status="SUBMITTED",
        comments=f"Maintenance requisition submitted for {data.segment}"
    ).to_dict()
    db["audit_logs"].insert_one(audit)

    new_req.pop("_id", None)
    return new_req

@router.get("/{request_id}", response_model=RequestResponse)
def get_request(request_id: str, db: Database = Depends(get_db)):
    req = db["maintenance_requests"].find_one({"request_id": request_id}, {"_id": 0})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req

@router.get("/assets/inventory", response_model=List[TrackAssetResponse])
def get_assets_inventory(
    dept_ref: Optional[str] = None,
    status: Optional[str] = None,
    db: Database = Depends(get_db)
):
    query = {}
    if dept_ref and dept_ref != "ALL":
        query["dept_ref"] = dept_ref
    if status and status != "ALL":
        query["status"] = status
    return list(db["track_assets"].find(query, {"_id": 0}))
