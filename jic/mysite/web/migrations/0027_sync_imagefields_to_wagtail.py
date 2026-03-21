from pathlib import Path

from django.db import migrations


def _sync_key(instance, field_name: str) -> str:
    return f"auto-sync:{instance._meta.label_lower}:{instance.pk}:{field_name}"


def _sync_title(instance, field_name: str, source_name: str) -> str:
    key = _sync_key(instance, field_name)
    return f"[{key}] {Path(source_name).name}"


def _sync_instance_field(instance, field_name: str, image_model):
    field_file = getattr(instance, field_name, None)
    if not field_file or not getattr(field_file, "name", ""):
        return

    if not field_file.storage.exists(field_file.name):
        return

    key_prefix = f"[{_sync_key(instance, field_name)}] "
    desired_title = _sync_title(instance, field_name, field_file.name)
    existing = image_model.objects.filter(title__startswith=key_prefix).first()

    if existing and existing.title == desired_title:
        return

    image_obj = existing or image_model(title=desired_title)

    image_obj.file = field_file.name

    image_obj.title = desired_title
    image_obj.save()


def backfill_image_fields_to_wagtail(apps, schema_editor):
    image_model = apps.get_model("wagtailimages", "Image")

    source_map = [
        ("web", "award", "image"),
        ("web", "coordinator", "photo"),
        ("web", "organizer_committee_member", "photo"),
        ("web", "video", "thumbnail"),
    ]

    for app_label, model_name, field_name in source_map:
        model = apps.get_model(app_label, model_name)
        queryset = model.objects.exclude(**{f"{field_name}__isnull": True}).exclude(**{field_name: ""})

        for instance in queryset.iterator(chunk_size=200):
            _sync_instance_field(instance, field_name, image_model)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0026_custom_document_model"),
    ]

    operations = [
        migrations.RunPython(backfill_image_fields_to_wagtail, noop_reverse),
    ]
