'''
one-off: load the existing CSV history into MongoDB
run from the project root with: python -m scripts.migrate_csv_to_mongo
'''
import pandas as pd
from pathlib import Path
from src.db import get_db, ensure_indexes
from src.file_manager import upsert_flights

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ensure_indexes()
#merged first, then upcoming, so the newer upcoming rows win on overlap
for name in ["HKIA_merged.csv", "HKIA_upcoming.csv"]:
    path = DATA_DIR / name
    if not path.exists() or path.stat().st_size == 0:
        print(f"Skipping {name}: missing or empty")
        continue
    df = pd.read_csv(path, header=0)
    df = df.drop_duplicates(subset=["flight_id", "flight_type"], keep="last")
    print(f"{name}: {len(df)} unique rows")
    upsert_flights(df, verbose=False)

print(f"flights collection now has {get_db().flights.count_documents({})} documents")
