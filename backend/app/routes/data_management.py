from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File
from pymongo.database import Database
from app.database import get_db
from app.models.audit import DataImportLog
from app.schemas.data_schemas import DataSourceResponse, DataImportLogResponse, QualityReportItem

router = APIRouter(prefix="/api/data", tags=["Data Management"])

@router.get("/sources", response_model=List[DataSourceResponse])
def get_data_sources(db: Database = Depends(get_db)):
    return list(db["data_sources"].find({}, {"_id": 0}))

@router.get("/import-logs", response_model=List[DataImportLogResponse])
def get_import_logs(db: Database = Depends(get_db)):
    return list(db["data_import_logs"].find({}, {"_id": 0}).sort("import_time", -1))

@router.get("/inventory")
def get_dataset_inventory():
    return [
        {
            "dataset": "Indian Railway Stations & Route Master (Southern Railway)",
            "source": "CRIS / National Train Enquiry System (NTES)",
            "rows": 8,
            "important_columns": "station_code, station_name, zone, division, latitude, longitude",
            "type": "STATIC / SEEDED"
        },
        {
            "dataset": "Corridor Section Geometry & Line Configuration",
            "source": "Southern Railway Headquarters (Chennai)",
            "rows": 7,
            "important_columns": "section_id, from_station, to_station, km_start, km_end, max_speed",
            "type": "STATIC / SEEDED"
        },
        {
            "dataset": "Track Maintenance Assets & Defect Register (TMS)",
            "source": "Track Management System (TMS)",
            "rows": 7,
            "important_columns": "asset_id, dept_ref, activity_description, location, priority, status",
            "type": "INTERNAL OPERATIONAL"
        },
        {
            "dataset": "COA Passenger & Goods Train Operational Schedules",
            "source": "Control Office Application (COA Gateway)",
            "rows": 3,
            "important_columns": "train_number, train_name, train_type, corridor, priority, scheduled_timings",
            "type": "REAL-TIME READY / COA"
        },
        {
            "dataset": "Historical Maintenance & Possession Records",
            "source": "Division Maintenance History Archive",
            "rows": 9,
            "important_columns": "maintenance_id, date, station, department, asset, duration, status",
            "type": "HISTORICAL ARCHIVE"
        }
    ]

@router.get("/quality-report", response_model=List[QualityReportItem])
def get_quality_report():
    return [
        QualityReportItem(
            dataset_name="TMS Track Assets & Flaw Registry",
            source_type="CSV (Internal TMS)",
            total_records=1420,
            valid_records=1418,
            missing_fields_count=2,
            duplicate_records_count=0,
            quality_score_pct=99.86,
            status="PASSED / OPERATIONAL"
        ),
        QualityReportItem(
            dataset_name="COA Train Schedules & Timings",
            source_type="JSON (COA API)",
            total_records=850,
            valid_records=850,
            missing_fields_count=0,
            duplicate_records_count=0,
            quality_score_pct=100.0,
            status="PASSED / VALIDATED"
        ),
        QualityReportItem(
            dataset_name="Station Master & Coordinates Register",
            source_type="CSV (GIS)",
            total_records=340,
            valid_records=338,
            missing_fields_count=2,
            duplicate_records_count=0,
            quality_score_pct=99.41,
            status="PASSED"
        ),
        QualityReportItem(
            dataset_name="Historical Block Decisions Archive",
            source_type="CSV (BDMS)",
            total_records=1200,
            valid_records=1195,
            missing_fields_count=5,
            duplicate_records_count=0,
            quality_score_pct=99.58,
            status="PASSED"
        ),
    ]

@router.post("/simulate-import")
def simulate_import(dataset_name: str, db: Database = Depends(get_db)):
    now = datetime.now()
    imp_id = f"IMP-2026-{now.strftime('%H%M%S')}"
    new_log = DataImportLog(
        import_id=imp_id,
        filename=dataset_name or "external_dataset.csv",
        source_type="CSV",
        total_rows=250,
        successful_rows=248,
        failed_rows=2,
        duplicate_rows=0,
        warnings=2,
        errors=0,
        status="Completed with warnings",
        notes="Imported via standardized RailOps ETL pipeline; schema fields mapped to internal model."
    ).to_dict()
    db["data_import_logs"].insert_one(new_log)
    new_log.pop("_id", None)
    return new_log
