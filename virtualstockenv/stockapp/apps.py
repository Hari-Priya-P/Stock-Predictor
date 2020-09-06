from django.apps import AppConfig


class StockAppConfig(AppConfig):
    name = 'stockapp'

    def ready(self):
        from stockupdate import updater
        updater.start()