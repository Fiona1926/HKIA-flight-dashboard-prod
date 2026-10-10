import logging
import argparse #testing to fetch specific date 
from datetime import datetime
#import all functions from different modules
from src.api_client import fetch_flights
from src.config import hk_today
from src.data_processor import process_flights
from src.file_manager import upsert_flights, append_changes

logging.basicConfig(level=logging.INFO) #basic logging from different libraries

def run(target_date=None, cargo='true', arrival='false'):   

    '''
    by default, cargo departure today (HK time)
    returns True on success, False otherwise
    '''
    if target_date is None:
        target_date = hk_today()

    logging.info("Starting flight data extraction...")
    try:
        flights = fetch_flights(target_date, cargo, arrival) #change to fetch_arrival_flights() for arrivals
        if not flights:     #raise a warning if no response from API
            logging.warning("No flights returned from API.")
            return False

        full_df, changes = process_flights(flights)     #full df and newly status changes, utilized load_previous_snapshot

        upsert_flights(full_df)               #past and upcoming flights live in one collection, updated in place
        append_changes(changes)               #record only newly changed status flights, say new cancellation or delayed

        logging.info(f"Saved {len(full_df)} flights; {len(changes)} new delayed/cancelled flights.")
        return True
    except Exception as e:
        logging.error(f"Run failed: {e}")
        return False
'''
if date is specified fetch API from that specific date
else fetch API from today
'''
if __name__ == "__main__":      #this shall be the main program 
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (defaults to today)')
    parser.add_argument('--cargo', type= str,choices= ['true','false'], default='true')
    parser.add_argument('--arrival', type= str,  choices= ['true','false'], default='false')
    args = parser.parse_args()

    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()   
    else: 
        target_date = hk_today()

    run(target_date, args.cargo, args.arrival)
