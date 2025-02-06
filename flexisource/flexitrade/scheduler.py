from apscheduler.schedulers.background import BackgroundScheduler

from .tasks import local_csv_import_task


def schedule_csv_import():
    """This cron job get run every 1 minute"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(local_csv_import_task, "interval", minutes=1)
    print("\n\nBulk Order job started and will run every minute.")
    scheduler.start()
