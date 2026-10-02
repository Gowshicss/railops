from datetime import datetime
from typing import Dict, Any
from pymongo.database import Database
from app.models.plan import PlanDecision, PlanModification
from app.models.dispatch import DownstreamDispatch, ActivePossession
from app.models.audit import AuditLog
from app.database import get_next_sequence

def send_plan_to_authority(db: Database, plan_id: str) -> Dict[str, Any]:
    plan = db["maintenance_plans"].find_one({"plan_id": plan_id}, {"_id": 0})
    if not plan:
        raise ValueError("Plan not found")
    
    db["maintenance_plans"].update_one(
        {"plan_id": plan_id},
        {"$set": {"status": "SENT FOR APPROVAL", "updated_at": datetime.utcnow()}}
    )
    plan["status"] = "SENT FOR APPROVAL"

    db["maintenance_requests"].update_one(
        {"request_id": plan["request_id"]},
        {"$set": {"status": "SENT FOR APPROVAL", "updated_at": datetime.utcnow()}}
    )

    audit = AuditLog(
        id=get_next_sequence(db, "audit_logs"),
        user="Central Operations Officer",
        role="PLANNER",
        action="Plan Sent to Authority",
        entity_type="PLAN",
        entity_id=plan_id,
        previous_status="GENERATED",
        new_status="SENT FOR APPROVAL",
        comments="Forwarded to Chief Controller for statutory sign-off"
    ).to_dict()
    db["audit_logs"].insert_one(audit)
    return plan

def approve_plan(db: Database, plan_id: str, authority_user: str = "Chief Controller", officer_id: str = "CO MAS 4091", comments: str = "") -> Dict[str, Any]:
    plan = db["maintenance_plans"].find_one({"plan_id": plan_id}, {"_id": 0})
    if not plan:
        raise ValueError("Plan not found")

    now = datetime.now()
    date_str = now.strftime("%d %b %Y")
    time_str = now.strftime("%H:%M:%S")

    db["maintenance_plans"].update_one(
        {"plan_id": plan_id},
        {"$set": {"status": "APPROVED", "updated_at": datetime.utcnow()}}
    )
    plan["status"] = "APPROVED"

    db["maintenance_requests"].update_one(
        {"request_id": plan["request_id"]},
        {"$set": {"status": "SCHEDULED", "updated_at": datetime.utcnow()}}
    )

    # Record Decision
    dec_id = get_next_sequence(db, "plan_decisions")
    decision = PlanDecision(
        id=dec_id,
        plan_id=plan["plan_id"],
        request_id=plan["request_id"],
        decision="ACCEPTED",
        authority_user=authority_user,
        officer_id=officer_id,
        decision_date=date_str,
        decision_time=time_str,
        comments=comments or "Statutory sanction granted under G&SR rules Chapter IV.",
        rejection_reason=None
    ).to_dict()
    db["plan_decisions"].insert_one(decision)

    # Trigger Instantaneous Downstream Dispatch to 6 Operational Units
    units = [
        (1, "1. ENGINEERING DEPT", "SSE / Permanent Way (Salem)", f"{now.strftime('%H:%M')}:02", "SENT"),
        (2, "2. SIGNAL & TELECOM", "Section Controller (S&T)", f"{now.strftime('%H:%M')}:04", "SENT"),
        (3, "3. ELECTRICAL (OHE)", "Traction Power Controller (TPC)", f"{now.strftime('%H:%M')}:05", "SENT"),
        (4, "4. TRAFFIC CONTROL", "Chief Train Controller (CTC)", f"{now.strftime('%H:%M')}:06", "SENT"),
        (5, "5. DIVISION CONTROL", "DRM Operations Cell", f"{now.strftime('%H:%M')}:08", "SENT"),
        (6, "6. MAINTENANCE CREW", "Gang #4 Supervisor (Field Terminal)", f"{now.strftime('%H:%M')}:10", "ACKNOWLEDGED"),
    ]

    # Clear old dispatches for this block if any
    db["downstream_dispatches"].delete_many({"block_id": plan["request_id"]})

    for order, name, role, timestamp, st in units:
        d_id = get_next_sequence(db, "downstream_dispatches")
        disp = DownstreamDispatch(
            id=d_id,
            block_id=plan["request_id"],
            unit_order=order,
            unit_name=name,
            recipient_role=role,
            sent_timestamp=timestamp,
            status=st,
            acknowledged_by="Field Terminal #4" if st == "ACKNOWLEDGED" else None,
            acknowledged_time=timestamp if st == "ACKNOWLEDGED" else None
        ).to_dict()
        db["downstream_dispatches"].insert_one(disp)

    # Upsert in Active Possession Register
    db["active_possessions"].update_one(
        {"block_id": plan["request_id"]},
        {"$set": {
            "section": plan["segment"],
            "department": plan["department"].upper(),
            "start_time": plan["recommended_start_time"],
            "end_time": plan["recommended_end_time"],
            "trains_affected": plan.get("conflicts_detected", 0),
            "status": "ON SCHEDULE",
            "remaining_display": "START IN 00:38",
            "total_seconds_duration": plan.get("duration_minutes", 90) * 60,
            "elapsed_seconds": 0,
            "resource_gang": plan.get("resource_gang", "Gang #4"),
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

    audit = AuditLog(
        id=get_next_sequence(db, "audit_logs"),
        user=authority_user,
        role="CHIEF_CONTROLLER",
        action="Plan Approved",
        entity_type="PLAN",
        entity_id=plan_id,
        previous_status="SENT FOR APPROVAL",
        new_status="APPROVED",
        comments=f"Statutory sign-off confirmed by {authority_user} ({officer_id}). Dispatches routed."
    ).to_dict()
    db["audit_logs"].insert_one(audit)

    return plan

def modify_plan(db: Database, plan_id: str, modified_date: str, modified_start_time: str, modified_end_time: str,
                modified_duration: int, modified_track: str, modified_priority: str, operational_notes: str,
                modified_by: str = "Chief Controller") -> Dict[str, Any]:
    plan = db["maintenance_plans"].find_one({"plan_id": plan_id}, {"_id": 0})
    if not plan:
        raise ValueError("Plan not found")

    now = datetime.now()
    date_str = now.strftime("%d %b %Y")
    time_str = now.strftime("%H:%M:%S")

    # Record Modification record
    mod_id = get_next_sequence(db, "plan_modifications")
    mod = PlanModification(
        id=mod_id,
        plan_id=plan["plan_id"],
        request_id=plan["request_id"],
        original_date=plan["recommended_date"],
        original_start_time=plan["recommended_start_time"],
        original_end_time=plan["recommended_end_time"],
        original_duration=plan["duration_minutes"],
        original_track=plan.get("track", "MAIN"),
        modified_date=modified_date,
        modified_start_time=modified_start_time,
        modified_end_time=modified_end_time,
        modified_duration=modified_duration,
        modified_track=modified_track,
        modified_priority=modified_priority,
        operational_notes=operational_notes,
        modified_by=modified_by
    ).to_dict()
    db["plan_modifications"].insert_one(mod)

    # Update plan values
    plan["recommended_date"] = modified_date
    plan["recommended_start_time"] = modified_start_time
    plan["recommended_end_time"] = modified_end_time
    plan["duration_minutes"] = modified_duration
    plan["track"] = modified_track
    plan["priority"] = modified_priority
    plan["status"] = "MODIFIED"

    db["maintenance_plans"].update_one(
        {"plan_id": plan_id},
        {"$set": {
            "recommended_date": modified_date,
            "recommended_start_time": modified_start_time,
            "recommended_end_time": modified_end_time,
            "duration_minutes": modified_duration,
            "track": modified_track,
            "priority": modified_priority,
            "status": "MODIFIED",
            "updated_at": datetime.utcnow()
        }}
    )

    db["maintenance_requests"].update_one(
        {"request_id": plan["request_id"]},
        {"$set": {"status": "MODIFIED", "updated_at": datetime.utcnow()}}
    )

    dec_id = get_next_sequence(db, "plan_decisions")
    decision = PlanDecision(
        id=dec_id,
        plan_id=plan["plan_id"],
        request_id=plan["request_id"],
        decision="MODIFIED",
        authority_user=modified_by,
        officer_id="CO MAS 4091",
        decision_date=date_str,
        decision_time=time_str,
        comments=operational_notes,
        rejection_reason=None
    ).to_dict()
    db["plan_decisions"].insert_one(decision)

    audit = AuditLog(
        id=get_next_sequence(db, "audit_logs"),
        user=modified_by,
        role="CHIEF_CONTROLLER",
        action="Plan Modified",
        entity_type="PLAN",
        entity_id=plan_id,
        previous_status="SENT FOR APPROVAL",
        new_status="MODIFIED",
        comments=f"Slot revised to {modified_start_time}-{modified_end_time}. Notes: {operational_notes}"
    ).to_dict()
    db["audit_logs"].insert_one(audit)

    return plan

def reject_plan(db: Database, plan_id: str, rejection_reason: str, comments: str, authority_user: str = "Chief Controller", officer_id: str = "CO MAS 4091") -> Dict[str, Any]:
    plan = db["maintenance_plans"].find_one({"plan_id": plan_id}, {"_id": 0})
    if not plan:
        raise ValueError("Plan not found")

    now = datetime.now()
    date_str = now.strftime("%d %b %Y")
    time_str = now.strftime("%H:%M:%S")

    plan["status"] = "REJECTED"
    db["maintenance_plans"].update_one(
        {"plan_id": plan_id},
        {"$set": {"status": "REJECTED", "updated_at": datetime.utcnow()}}
    )

    db["maintenance_requests"].update_one(
        {"request_id": plan["request_id"]},
        {"$set": {"status": "REJECTED", "updated_at": datetime.utcnow()}}
    )

    dec_id = get_next_sequence(db, "plan_decisions")
    decision = PlanDecision(
        id=dec_id,
        plan_id=plan["plan_id"],
        request_id=plan["request_id"],
        decision="REJECTED",
        authority_user=authority_user,
        officer_id=officer_id,
        decision_date=date_str,
        decision_time=time_str,
        comments=comments,
        rejection_reason=rejection_reason
    ).to_dict()
    db["plan_decisions"].insert_one(decision)

    audit = AuditLog(
        id=get_next_sequence(db, "audit_logs"),
        user=authority_user,
        role="CHIEF_CONTROLLER",
        action="Plan Rejected",
        entity_type="PLAN",
        entity_id=plan_id,
        previous_status="SENT FOR APPROVAL",
        new_status="REJECTED",
        comments=f"Rejection: {rejection_reason}. Comments: {comments}"
    ).to_dict()
    db["audit_logs"].insert_one(audit)

    return plan
