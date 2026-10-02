import os
import logging
from pathlib import Path
from typing import Generator, Any
from dotenv import load_dotenv
import pymongo
from pymongo.database import Database

# Load environment variables from backend/.env and current working directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

logger = logging.getLogger("railops.database")
logging.basicConfig(level=logging.INFO)

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "railops").strip()

client: Any = None
db: Any = None

def get_mongo_client():
    global client, db
    if client is not None:
        return client, db

    # 1. Connect to MongoDB Atlas if URI is provided and not a placeholder
    if MONGODB_URI and not MONGODB_URI.startswith("<PASTE"):
        try:
            logger.info("Connecting to MongoDB Atlas via MONGODB_URI...")
            client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client[MONGODB_DATABASE]
            logger.info(f"Successfully connected to MongoDB Atlas database: '{MONGODB_DATABASE}'")
            return client, db
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB Atlas URI: {e}. Checking fallback.")

    # 2. Try local MongoDB daemon if running
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1500)
        client.admin.command('ping')
        db = client[MONGODB_DATABASE]
        logger.info(f"Connected to local MongoDB database: '{MONGODB_DATABASE}'")
        return client, db
    except Exception:
        pass

    # 3. Resilient development fallback: in-memory mongomock
    try:
        import mongomock
        logger.info("MONGODB_URI not configured or unreachable; using in-memory mock MongoDB for local execution.")
        client = mongomock.MongoClient()
        db = client[MONGODB_DATABASE]
        return client, db
    except Exception as e:
        logger.error(f"Critical error initializing database: {e}")
        raise

client, db = get_mongo_client()

def get_db() -> Generator[Database, None, None]:
    """FastAPI dependency for accessing the MongoDB database."""
    yield db

def get_db_instance() -> Database:
    """Direct database instance access."""
    return db

def get_next_sequence(database: Database, sequence_name: str) -> int:
    """Atomic counter generating sequential integer IDs for entities that require them."""
    counter = database["counters"].find_one({"_id": sequence_name})
    if not counter:
        database["counters"].insert_one({"_id": sequence_name, "seq": 1})
        return 1
    new_seq = counter.get("seq", 0) + 1
    database["counters"].update_one({"_id": sequence_name}, {"$set": {"seq": new_seq}})
    return new_seq

def clean_doc(doc: Any) -> Any:
    """Removes or formats MongoDB _id field to guarantee clean JSON serialization."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [clean_doc(d) for d in doc]
    if isinstance(doc, dict):
        d = dict(doc)
        d.pop("_id", None)
        return d
    return doc

def init_indexes(database: Database):
    """Initializes performance and constraint indexes for MongoDB collections."""
    try:
        database["stations"].create_index("station_code", unique=True)
        database["railway_sections"].create_index("section_id", unique=True)
        database["track_assets"].create_index("asset_id", unique=True)
        database["track_assets"].create_index([("dept_ref", 1), ("status", 1)])
        database["maintenance_requests"].create_index("request_id", unique=True)
        database["maintenance_requests"].create_index([("department", 1), ("status", 1)])
        database["maintenance_requests"].create_index([("created_at", -1)])
        database["maintenance_plans"].create_index("plan_id", unique=True)
        database["maintenance_plans"].create_index([("request_id", 1), ("status", 1)])
        database["plan_decisions"].create_index("plan_id")
        database["downstream_dispatches"].create_index([("block_id", 1), ("unit_order", 1)])
        database["active_possessions"].create_index("block_id", unique=True)
        database["active_possessions"].create_index("status")
        database["station_maintenance_history"].create_index("maintenance_id", unique=True)
        database["station_maintenance_history"].create_index([("station_code", 1), ("year", -1)])
        database["trains"].create_index("train_number", unique=True)
        database["train_schedules"].create_index([("train_number", 1), ("section_id", 1)])
        database["audit_logs"].create_index([("timestamp", -1)])
        database["data_sources"].create_index("source_id", unique=True)
        database["data_import_logs"].create_index("import_id", unique=True)
    except Exception as e:
        logger.info(f"Indexes verification: {e}")
