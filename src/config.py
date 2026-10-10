import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

'''
reads settings from .env locally, or from Heroku config vars in production
'''

load_dotenv() #looks for .env in the current directory; on Heroku, config vars are already in the environment

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "hkia")

HK_TZ = ZoneInfo("Asia/Hong_Kong")  #Heroku runs on UTC, so "today" must be computed in HK time

def hk_today():
    return datetime.now(HK_TZ).date()
