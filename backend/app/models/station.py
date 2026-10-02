from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class Station:
    station_code: str
    station_name: str
    location: str
    zone: str = "SR"
    division: str = "Salem Division"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_maintenance_works: int = 0
    last_maintenance_date: Optional[str] = None
    departments_involved: str = "Engineering, TRD, S&T"
    current_status: str = "OPERATIONAL"

    def to_dict(self):
        return asdict(self)

@dataclass
class RailwaySection:
    section_id: str
    section_name: str
    from_station_code: str
    to_station_code: str
    km_start: float = 334.0
    km_end: float = 396.0
    line_type: str = "DOUBLE LINE"
    max_speed_kmh: int = 110
    electrified: str = "YES (25KV AC)"

    def to_dict(self):
        return asdict(self)

@dataclass
class TrackAsset:
    asset_id: str
    department: str
    dept_ref: str
    asset_type: str
    activity_description: str
    location: str
    station_code: str
    schedule_date: str
    priority: str = "HIGH"
    status: str = "UPCOMING"
    last_maintenance_date: Optional[str] = None
    condition_rating: str = "Good"

    def to_dict(self):
        return asdict(self)

@dataclass
class StationMaintenanceHistory:
    maintenance_id: str
    station_code: str
    station_name: str
    department: str
    maintenance_type: str
    date: str
    track: str = "Track 2"
    asset_id: Optional[str] = None
    year: int = 2026
    month: str = "September"
    start_time: str = "18:00"
    end_time: str = "20:00"
    duration_str: str = "2 hours"
    description: Optional[str] = None
    status: str = "Completed"
    crew_gang: str = "Gang #4"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return asdict(self)
