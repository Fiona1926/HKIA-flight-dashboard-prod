import logging
import sys
import time
from datetime import timedelta
from src.config import hk_today
from src.db import ensure_indexes
from src.main import run

'''
daily job for (replaces scripts/dailyfetch.sh)
fetches HK yesterday -> today + 2 days, for cargo arrivals and departures
run with: python -m src.daily_job
'''

logging.basicConfig(level=logging.INFO)

#(cargo, arrival) flag combinations
FLAG_COMBOS = [
    ("true", "true"),
    ("true", "false"),
]

def main():
    ensure_indexes()
    today = hk_today()
    start, end = today - timedelta(days=1), today + timedelta(days=2)
    logging.info(f"Starting daily fetch from {start} to {end}")

    failures = 0
    current = start
    while current <= end:
        for cargo, arrival in FLAG_COMBOS:
            logging.info(f"Running for {current} with cargo={cargo} arrival={arrival}")
            if run(current, cargo, arrival):
                logging.info(f"Successfully processed {current} (cargo={cargo}, arrival={arrival})")
            else:
                failures += 1
                logging.error(f"Failed to process {current} (cargo={cargo}, arrival={arrival})")
            time.sleep(1)   #brief pause between API calls
        current += timedelta(days=1)

    logging.info(f"Daily fetch completed with {failures} failure(s).")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
