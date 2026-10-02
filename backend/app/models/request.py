from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class MaintenanceRequest:
    request_id: str
    department: str
    station_code: str
    segment: str
    maintenance_type: str
    requested_date: str
    requested_start_time: str
    requested_end_time: str
    dept_ref: str = "TMS"
    zone: str = "SR"
    track: str = "UP LINE"
    asset_id: Optional[str] = None
    description: Optional[str] = ""
    duration_minutes: int = 90
    priority: str = "HIGH"
    urgency: str = "High"
    asset_criticality: str = "Tier-1"
    reason: Optional[str] = ""
    status: str = "SUBMITTED"
    conflict_flag: str = "PENDING"
    conflict_summary: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return asdict(self)
