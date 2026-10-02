from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.database import get_db

router = APIRouter(prefix="/api/schedules", tags=["Schedules"])

@router.get("/weekly")
def get_weekly_schedule(db: Database = Depends(get_db)):
    # Aggregates requests and plans into a Mon-Sun weekly schedule
    requests = list(db["maintenance_requests"].find({}, {"_id": 0}))
    recommended_plans = list(db["maintenance_plans"].find({"is_recommended": True}, {"_id": 0}))
    plans_by_req = {p.get("request_id"): p for p in recommended_plans}

    items = []
    for r in requests:
        plan = plans_by_req.get(r.get("request_id"))
        items.append({
            "request_id": r.get("request_id"),
            "station": r.get("station_code"),
            "department": r.get("department"),
            "segment": r.get("segment"),
            "track": r.get("track"),
            "maintenance_type": r.get("maintenance_type"),
            "requested_date": r.get("requested_date"),
            "requested_time": f"{r.get('requested_start_time')} - {r.get('requested_end_time')}",
            "planned_time": f"{plan.get('recommended_start_time')} - {plan.get('recommended_end_time')}" if plan else f"{r.get('requested_start_time')} - {r.get('requested_end_time')}",
            "duration": f"{r.get('duration_minutes')} min",
            "priority": r.get("priority"),
            "status": plan.get("status") if plan and plan.get("status") in ["APPROVED", "MODIFIED", "SCHEDULED", "COMPLETED"] else r.get("status"),
            "impact": plan.get("operational_impact") if plan else "EVALUATING"
        })
    return items

@router.get("/monthly")
def get_monthly_schedule(month: str = "2026-09", db: Database = Depends(get_db)):
    requests = list(db["maintenance_requests"].find({}, {"_id": 0}))
    all_plans = list(db["maintenance_plans"].find({}, {"_id": 0}))
    plans = {p.get("request_id"): p for p in all_plans}

    # Group activities by date
    days_data: Dict[str, List[Dict[str, Any]]] = {}
    for r in requests:
        dt = r.get("requested_date")
        if not dt:
            continue
        if dt not in days_data:
            days_data[dt] = []
        p = plans.get(r.get("request_id"))
        days_data[dt].append({
            "id": r.get("request_id"),
            "department": r.get("department"),
            "type": r.get("maintenance_type"),
            "location": r.get("segment"),
            "priority": r.get("priority"),
            "status": p.get("status") if p and p.get("status") in ["APPROVED", "MODIFIED", "SCHEDULED", "COMPLETED"] else r.get("status"),
            "time": f"{p.get('recommended_start_time') if p else r.get('requested_start_time')} - {p.get('recommended_end_time') if p else r.get('requested_end_time')}"
        })

    return {
        "month": month,
        "calendar_days": days_data
    }
