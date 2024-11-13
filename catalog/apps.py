from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"

    def ready(self):
        """This code will run after app is initialized"""
        # TODO EX2: This is a good place to make sure signals are imported
