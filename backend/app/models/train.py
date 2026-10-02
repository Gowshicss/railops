from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Train:
    train_number: str
    train_name: str
    train_type: str = "SUPERFAST EXPRESS"
    origin: str = "MAS"
    destination: str = "CBE"
    corridor: str = "South Corridor"
    priority: int = 1
    goods_train_indicator: bool = False

    def to_dict(self):
        return asdict(self)

@dataclass
class TrainSchedule:
    train_number: str
    section_id: str
    station_code: str
    scheduled_arrival: str
    scheduled_departure: str
    direction: str = "DOWN"
    route_line: str = "MAIN LINE"
    id: Optional[int] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class TrainMovement:
    train_number: str
    current_section: str
    status: str = "ON TIME"
    delay_minutes: int = 0
    current_speed: int = 95
    last_reported_time: str = "11:32:00"
    id: Optional[int] = None

    def to_dict(self):
        return asdict(self)
