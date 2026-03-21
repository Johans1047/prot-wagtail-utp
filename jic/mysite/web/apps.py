from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'web'

    def ready(self):
        # Register signal handlers for automatic ImageField -> Wagtail image sync.
        from . import signals  # noqa: F401

        signals.register_imagefield_sync_signals()
