from apscheduler.schedulers.background import BackgroundScheduler

from .views.trade import PlaceBulkTrade


def schedule_csv_import():
    """This cron job get run every 1 minute"""
    PlaceBulkTrade.process_from_local_file()

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        PlaceBulkTrade.process_from_local_file, "interval", minutes=1
    )
    scheduler.start()
