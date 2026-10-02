import random
from datetime import datetime
from typing import Dict, Any
from pymongo.database import Database
from app.models.station import StationMaintenanceHistory
from app.models.audit import AuditLog
from app.database import get_next_sequence

def complete_maintenance_block(db: Database, block_id: str, station_code: str = "SA",
                               actual_start: str = "12:10", actual_end: str = "13:40",
                               work_summary: str = "Track inspection and destressing completed successfully",
                               crew_gang: str = "Gang #4") -> Dict[str, Any]:
    db["active_possessions"].update_one(
        {"block_id": block_id},
        {"$set": {"status": "COMPLETED", "remaining_display": "00:00:00"}}
    )

    req = db["maintenance_requests"].find_one({"request_id": block_id}, {"_id": 0})
    if req:
        db["maintenance_requests"].update_one(
            {"request_id": block_id},
            {"$set": {"status": "COMPLETED", "updated_at": datetime.utcnow()}}
        )
        station_code = req.get("station_code") or station_code

    db["maintenance_plans"].update_many(
        {"request_id": block_id},
        {"$set": {"status": "COMPLETED", "updated_at": datetime.utcnow()}}
    )

    # Fetch station details
    station = db["stations"].find_one({"station_code": station_code}, {"_id": 0})
    station_name = station["station_name"] if station else "Salem Junction"

    now = datetime.now()
    mnt_id = f"MNT-{random.randint(10485, 19999)}"

    # Add to Station Maintenance History
    history_entry = StationMaintenanceHistory(
        maintenance_id=mnt_id,
        station_code=station_code,
        station_name=station_name,
        department=req.get("department", "Engineering") if req else "Engineering",
        asset_id=req.get("asset_id", "TMS-002") if req else "TMS-002",
        track=req.get("track", "Track 2") if req else "Track 2",
        maintenance_type=req.get("maintenance_type", "Thermit Weld Repair & Destressing") if req else "Thermit Weld Repair & Destressing",
        date=now.strftime("%d %b %Y"),
        year=now.year,
        month=now.strftime("%B"),
        start_time=actual_start,
        end_time=actual_end,
        duration_str="1 hr 30 min",
        description=work_summary,
        status="Completed",
        crew_gang=crew_gang
    ).to_dict()
    db["station_maintenance_history"].insert_one(history_entry)

    # Increment station total works
    db["stations"].update_one(
        {"station_code": station_code},
        {
            "$inc": {"total_maintenance_works": 1},
            "$set": {"last_maintenance_date": now.strftime("%d %b %Y")}
        }
    )

    audit = AuditLog(
        id=get_next_sequence(db, "audit_logs"),
        user="Site Supervisor",
        role="ENGINEERING",
        action="Maintenance Completed",
        entity_type="POSSESSION",
        entity_id=block_id,
        previous_status="ACTIVE",
        new_status="COMPLETED",
        comments=f"Track possession released. Logged in Station History as {mnt_id}"
    ).to_dict()
    db["audit_logs"].insert_one(audit)

    history_entry.pop("_id", None)
    return history_entry
