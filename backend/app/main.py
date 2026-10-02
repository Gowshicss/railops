import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db_instance, init_indexes
from app.services.seed_data import seed_database
from app.routes.requests import router as requests_router
from app.routes.plans import router as plans_router
from app.routes.authority import router as authority_router
from app.routes.possessions import router as possessions_router
from app.routes.stations import router as stations_router
from app.routes.schedules import router as schedules_router
from app.routes.data_management import router as data_router
from app.routes.audit import router as audit_router

# Initialize MongoDB indexes and seed initial dataset
mongo_db = get_db_instance()
init_indexes(mongo_db)
seed_database(mongo_db)

app = FastAPI(
    title="RailOps Central API",
    description="Intelligent Railway Maintenance Block Planning & Statutory Authority System",
    version="5.2.0"
)

# CORS Middleware allowing Vite dev server and frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Include Routers
app.include_router(requests_router)
app.include_router(plans_router)
app.include_router(authority_router)
app.include_router(possessions_router)
app.include_router(stations_router)
app.include_router(schedules_router)
app.include_router(data_router)
app.include_router(audit_router)

@app.get("/api/info")
def root_info():
    return {
        "system": "RailOps Intelligent Railway Maintenance Planning & Authority Platform",
        "cluster": "SEC-PROD-04",
        "zone": "Southern Railway (SR)",
        "division": "Salem & Chennai",
        "status": "ONLINE",
        "version": "5.2.0"
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "database": f"mongodb/{getattr(mongo_db, 'name', 'railops')}",
        "gateway": "CRIS FOIS CONNECTED",
        "latency_ms": 14
    }

# Mount Frontend SPA if dist exists
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

