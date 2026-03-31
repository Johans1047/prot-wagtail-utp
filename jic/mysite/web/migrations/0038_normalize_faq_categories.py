from django.db import migrations
import unicodedata


CANONICAL_CHOICES = {"participacion", "plataforma", "entregables"}
CATEGORY_ALIASES = {
    "participacion": "participacion",
    "participacion_y_equipos": "participacion",
    "plataforma": "plataforma",
    "plataforma_tecnologica": "plataforma",
    "entregable": "entregables",
    "entregables": "entregables",
    "entregables_y_evaluacion": "entregables",
}


def _normalize(value):
    normalized = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.replace("-", "_").replace(" ", "_")
    normalized = "_".join(part for part in normalized.split("_") if part)
    normalized = CATEGORY_ALIASES.get(normalized, normalized)
    if normalized not in CANONICAL_CHOICES:
        return "participacion"
    return normalized


def normalize_faq_categories(apps, schema_editor):
    FAQ = apps.get_model("web", "frequently_ask_question")

    for faq in FAQ.objects.all().iterator():
        canonical_slug = _normalize(getattr(faq, "category_slug", None) or getattr(faq, "category", None))
        updates = {}

        if faq.category_slug != canonical_slug:
            updates["category_slug"] = canonical_slug
        if faq.category != canonical_slug:
            updates["category"] = canonical_slug

        if updates:
            FAQ.objects.filter(pk=faq.pk).update(**updates)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0037_remove_coordinator_photo_coordinator_college_logo_and_more"),
    ]

    operations = [
        migrations.RunPython(normalize_faq_categories, reverse_noop),
    ]
