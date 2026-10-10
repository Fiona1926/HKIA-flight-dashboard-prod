import pandas as pd
import logging
from datetime import datetime, timezone
from pymongo import UpdateOne
from src.db import get_db

'''
load_previous_snapshot() - read previous status of the given flights from MongoDB
upsert_flights() - insert/update flights in the flights collection (replaces HKIA_merged.csv + HKIA_upcoming.csv)
append_changes() - record newly delayed/cancelled flights in the status_changes collection
'''

logging.basicConfig(level=logging.INFO)

def _print_df(title, df):
    print("=" * 40)
    print(title)
    print("=" * 40)
    with pd.option_context(
        'display.max_columns', None,       # Show all columns
        'display.width', None,              # Auto-detect console width
        'display.max_colwidth', None,       # Show full content of each cell
        'display.max_rows', None            # Show all rows (or set a limit e.g., 20)
    ):
        print(df)

def _to_records(df):
    """DataFrame -> list of dicts with NaN converted to None (MongoDB can't store NaN meaningfully)."""
    return df.astype(object).where(pd.notna(df), None).to_dict("records")

def load_previous_snapshot(flight_ids):       #this one to compare, any updated status
    """
    Return {flight_id: status} for the given flights as currently stored, empty dict if none yet.
    """
    cursor = get_db().flights.find(
        {"flight_id": {"$in": list(flight_ids)}},
        {"_id": 0, "flight_id": 1, "status": 1},
    )
    return {doc["flight_id"]: doc.get("status") for doc in cursor}

def upsert_flights(flights_df, verbose=True):
    """Insert new flights and update existing ones, keyed on (flight_id, flight_type)."""
    if flights_df.empty:
        logging.warning("Skipping upsert: DataFrame is empty.")
        return
    now = datetime.now(timezone.utc)
    ops = [
        UpdateOne(
            {"flight_id": rec["flight_id"], "flight_type": rec["flight_type"]},
            {"$set": {**rec, "fetched_at": now}},
            upsert=True,
        )
        for rec in _to_records(flights_df)
    ]
    result = get_db().flights.bulk_write(ops, ordered=False)
    logging.info(f"Upserted flights: {result.upserted_count} new, {result.modified_count} updated.")
    if not verbose:
        return

    _print_df("Current flights snapshot:", flights_df)
    _print_df("Delayed/cancelled flights snapshot :",
              flights_df[flights_df["status"].fillna("").str.lower().isin(["delayed", "cancelled"])])

def append_changes(new_change_records):     #receive list of row dicts with newly delayed/cancelled status
    if not new_change_records:
        return

    df_new = pd.DataFrame(new_change_records)
    now = datetime.now(timezone.utc)
    docs = [{**rec, "detected_at": now} for rec in _to_records(df_new)]
    try:
        get_db().status_changes.insert_many(docs)
    except Exception as e: #catch the exception as e
        logging.error(f"Failed to write status_changes: {e}")
        return

    _print_df("Newly fetch delayed/cancelled flight status:", df_new)
