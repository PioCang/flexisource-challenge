"""File for cron tasks"""
from .views.trade import PlaceBulkTrade


def local_csv_import_task():
    PlaceBulkTrade().process_from_local_file()
