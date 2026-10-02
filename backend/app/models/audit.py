from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class AuditLog:
    action: str
    entity_id: str
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user: str = "System"
    role: str = "OPERATOR"
    entity_type: str = "REQUEST"
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    comments: Optional[str] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class DataSource:
    source_id: str
    source_name: str
    source_type: str
    file_name: Optional[str] = None
    source_url: Optional[str] = None
    imported_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)
    description: Optional[str] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class DataImportLog:
    import_id: str
    filename: str
    source_type: str = "CSV"
    import_time: datetime = field(default_factory=datetime.utcnow)
    total_rows: int = 0
    successful_rows: int = 0
    failed_rows: int = 0
    duplicate_rows: int = 0
    warnings: int = 0
    errors: int = 0
    status: str = "Completed"
    notes: Optional[str] = None

    def to_dict(self):
        return asdict(self)
