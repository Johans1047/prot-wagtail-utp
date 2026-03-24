from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'web'

    @staticmethod
    def _patch_collections_translation() -> None:
        # Wagtail es locale contains a typo for "collections" -> "coleciones".
        # Patch gettext resolution at runtime so admin breadcrumbs show correctly.
        from django.utils.translation import trans_real

        if getattr(trans_real, "_jic_collections_patch_applied", False):
            return

        original_gettext = trans_real.DjangoTranslation.gettext

        def _patched_gettext(self, message):
            value = original_gettext(self, message)
            language = getattr(self, "_DjangoTranslation__language", "")
            if message == "collections" and language in {"es", "es_419"} and value == "coleciones":
                return "colecciones"
            return value

        trans_real.DjangoTranslation.gettext = _patched_gettext
        trans_real._jic_collections_patch_applied = True

    def ready(self):
        # Register signal handlers for automatic ImageField -> Wagtail image sync.
        from . import signals  # noqa: F401

        self._patch_collections_translation()
        signals.register_imagefield_sync_signals()
        signals.register_collection_visibility_signal()
