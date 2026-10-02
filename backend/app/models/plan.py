from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class MaintenancePlan:
    plan_id: str
    plan_code: str
    request_id: str
    department: str
    station_code: str
    segment: str
    maintenance_type: str
    requested_date: str
    requested_start_time: str
    requested_end_time: str
    recommended_date: str
    recommended_start_time: str
    recommended_end_time: str
    zone: str = "SR"
    track: str = "MAIN"
    duration_minutes: int = 90
    priority: str = "HIGH"
    risk_level: str = "LOW"
    operational_impact: str = "ACCEPTABLE SLA"
    reason_for_recommendation: Optional[str] = None
    conflicts_detected: int = 0
    delay_impact_min: int = 18
    resource_util_pct: int = 84
    recovered_trains: int = 3
    resource_gang: str = "GANG #4 & TAMP"
    is_recommended: bool = True
    tier_resolution: str = "TIER-1 RESOLUTION"
    status: str = "GENERATED"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return asdict(self)

@dataclass
class PlanDecision:
    plan_id: str
    request_id: str
    decision: str
    decision_date: str
    decision_time: str
    authority_user: str = "Chief Controller"
    officer_id: str = "CO MAS 4091"
    comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return asdict(self)

@dataclass
class PlanModification:
    plan_id: str
    request_id: str
    original_date: str
    original_start_time: str
    original_end_time: str
    original_duration: int
    original_track: str
    modified_date: str
    modified_start_time: str
    modified_end_time: str
    modified_duration: int
    modified_track: str
    modified_priority: str
    operational_notes: Optional[str] = None
    modified_by: str = "Chief Controller"
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return asdict(self)
