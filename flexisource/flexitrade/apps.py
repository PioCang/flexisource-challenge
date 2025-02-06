from django.apps import AppConfig


class FlexitradeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "flexitrade"

    def ready(self):
        """Override ready hook. Runs after server is ready

        Reference:
        https://medium.com/@kevin.michael.horan/scheduling-tasks-in-django-with
        -the-advanced-python-scheduler-663f17e868e6
        """
        from .scheduler import schedule_csv_import

        schedule_csv_import()
