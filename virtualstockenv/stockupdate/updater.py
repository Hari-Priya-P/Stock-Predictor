from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from stockupdate import data_collection
from stockapp import thresholds

def start():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(data_collection.get_real, trigger='cron', hour = '10-15', minute = '0-59', second = '0', day_of_week = '0-4')
    scheduler.add_job(data_collection.get_hist, trigger='cron', hour='17', minute='0', second='0', day_of_week='0-4')
    scheduler.add_job(thresholds.check_thresholds, trigger='cron', hour = '10-15', minute = '0-59', second = '0', day_of_week = '0-4')
    scheduler.start()

