from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from app.database import get_db
from app.schemas.plan_schemas import (
    PlanResponse,
    PlanApproveRequest,
    PlanModifyRequest,
    PlanRejectRequest,
    DecisionResponse,
    DispatchResponse
)
from app.services.approval_service import approve_plan, modify_plan, reject_plan

router = APIRouter(prefix="/api/authority", tags=["Authority"])

@router.get("/pending", response_model=List[PlanResponse])
def get_pending_authority_plans(db: Database = Depends(get_db)):
    return list(db["maintenance_plans"].find(
        {"status": {"$in": ["SENT FOR APPROVAL", "GENERATED"]}},
        {"_id": 0}
    ))

@router.post("/approve", response_model=PlanResponse)
def approve_plan_route(data: PlanApproveRequest, db: Database = Depends(get_db)):
    try:
        plan = approve_plan(
            db=db,
            plan_id=data.plan_id,
            authority_user=data.authority_user or "Chief Controller",
            officer_id=data.officer_id or "CO MAS 4091",
            comments=data.comments or ""
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/modify", response_model=PlanResponse)
def modify_plan_route(data: PlanModifyRequest, db: Database = Depends(get_db)):
    try:
        plan = modify_plan(
            db=db,
            plan_id=data.plan_id,
            modified_date=data.modified_date,
            modified_start_time=data.modified_start_time,
            modified_end_time=data.modified_end_time,
            modified_duration=data.modified_duration,
            modified_track=data.modified_track,
            modified_priority=data.modified_priority,
            operational_notes=data.operational_notes or "",
            modified_by=data.modified_by or "Chief Controller"
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/reject", response_model=PlanResponse)
def reject_plan_route(data: PlanRejectRequest, db: Database = Depends(get_db)):
    try:
        plan = reject_plan(
            db=db,
            plan_id=data.plan_id,
            rejection_reason=data.rejection_reason,
            comments=data.comments or "",
            authority_user=data.authority_user or "Chief Controller",
            officer_id=data.officer_id or "CO MAS 4091"
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/dispatches/{block_id}", response_model=List[DispatchResponse])
def get_block_dispatches(block_id: str, db: Database = Depends(get_db)):
    return list(db["downstream_dispatches"].find(
        {"block_id": block_id},
        {"_id": 0}
    ).sort("unit_order", 1))

@router.get("/decisions", response_model=List[DecisionResponse])
def get_decisions_history(
    decision: Optional[str] = None,
    db: Database = Depends(get_db)
):
    query = {}
    if decision and decision != "ALL":
        query["decision"] = decision
    return list(db["plan_decisions"].find(query, {"_id": 0}).sort("id", -1))
