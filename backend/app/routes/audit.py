from typing import List
from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.database import get_db
from app.schemas.data_schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(db: Database = Depends(get_db)):
    return list(db["audit_logs"].find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
