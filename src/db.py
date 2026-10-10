from functools import lru_cache
from pymongo import MongoClient, ASCENDING
from src.config import MONGODB_URI, MONGODB_DB

'''
get_db() - shared MongoDB connection (one client per process)
ensure_indexes() - unique key on flights so re-runs update instead of duplicate
'''

@lru_cache(maxsize=1)
def get_db():
    if not MONGODB_URI:
        raise RuntimeError("MONGODB_URI is not set (add it to .env or Heroku config vars)")
    return MongoClient(MONGODB_URI)[MONGODB_DB]

def ensure_indexes():
    db = get_db()
    db.flights.create_index([("flight_id", ASCENDING), ("flight_type", ASCENDING)], unique=True)
    db.flights.create_index("date")
    db.status_changes.create_index("detected_at")
