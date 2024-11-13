from django.apps import AppConfig


class SolutionsAppConfig(AppConfig):
    name = "solutions"

    def ready(self):
        # Hook up the signals
        import solutions.signals
