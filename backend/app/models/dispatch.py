from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class DownstreamDispatch:
    block_id: str
    unit_order: int
    unit_name: str
    recipient_role: str
    sent_timestamp: str
    status: str = "SENT"
    acknowledged_by: Optional[str] = None
    acknowledged_time: Optional[str] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return asdict(self)

@dataclass
class ActivePossession:
    block_id: str
    section: str
    department: str
    start_time: str
    end_time: str
    trains_affected: int = 0
    status: str = "ACTIVE"
    remaining_display: str = "00:28:14"
    total_seconds_duration: int = 5400
    elapsed_seconds: int = 1800
    resource_gang: str = "Gang #4"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return asdict(self)
