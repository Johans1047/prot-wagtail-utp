from pathlib import Path

from django.apps import apps
from django.core.files.base import File
from django.db import models
from django.db.models.signals import post_save, pre_save
from wagtail.images import get_image_model
from wagtail.images.models import AbstractRendition

from .image_pipeline import optimize_and_apply_to_field_file


def _sync_key(instance, field_name: str) -> str:
    return f"auto-sync:{instance._meta.label_lower}:{instance.pk}:{field_name}"


def _sync_title(instance, field_name: str, source_name: str) -> str:
    key = _sync_key(instance, field_name)
    return f"[{key}] {Path(source_name).name}"


def _sync_image_field(instance, field_name: str) -> None:
    field_file = getattr(instance, field_name, None)
    if not field_file or not getattr(field_file, "name", ""):
        return

    if not field_file.storage.exists(field_file.name):
        return

    image_model = get_image_model()
    key_prefix = f"[{_sync_key(instance, field_name)}] "
    desired_title = _sync_title(instance, field_name, field_file.name)
    existing = image_model.objects.filter(title__startswith=key_prefix).first()

    if existing and existing.title == desired_title:
        return

    image_obj = existing or image_model(title=desired_title)

    with field_file.open("rb") as source_file:
        image_obj.file.save(Path(field_file.name).name, File(source_file), save=False)

    image_obj.title = desired_title
    image_obj.save()


def sync_instance_image_fields(sender, instance, **kwargs) -> None:
    for field in sender._meta.fields:
        if isinstance(field, models.ImageField):
            _sync_image_field(instance, field.name)


def compress_model_image_fields(sender, instance, **kwargs) -> None:
    for field in sender._meta.fields:
        if not isinstance(field, models.ImageField):
            continue

        field_file = getattr(instance, field.name, None)
        if not field_file or not getattr(field_file, "name", ""):
            continue

        if getattr(field_file, "_committed", True):
            continue

        optimize_and_apply_to_field_file(field_file)


def register_imagefield_sync_signals() -> None:
    app_config = apps.get_app_config("web")
    image_model = get_image_model()
    
    for model in app_config.get_models():
        if model is image_model or issubclass(model, AbstractRendition):
            continue

        image_fields = [field for field in model._meta.fields if isinstance(field, models.ImageField)]
        if not image_fields:
            continue

        dispatch_uid = f"web.sync_imagefield_to_wagtail.{model._meta.label_lower}"
        pre_save.connect(compress_model_image_fields, sender=model, dispatch_uid=f"{dispatch_uid}.compress")
        post_save.connect(sync_instance_image_fields, sender=model, dispatch_uid=dispatch_uid)
