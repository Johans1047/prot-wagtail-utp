from pathlib import Path

from django.apps import apps
from django.core.files.base import File
from django.db import models
from django.db.models.signals import post_save, pre_save
from wagtail.images import get_image_model
from wagtail.images.models import AbstractRendition
from wagtail.models import Collection

from .image_pipeline import optimize_and_apply_to_field_file
from .models import BlogPage, CollectionResourceVisibility


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


def sync_collection_resources_visibility(sender, instance, **kwargs) -> None:
    pending = getattr(instance, "_resource_visibility_pending", None)
    if pending is None:
        return

    CollectionResourceVisibility.objects.update_or_create(
        collection=instance,
        defaults={"is_visible_in_resources": bool(pending)},
    )


def register_collection_visibility_signal() -> None:
    post_save.connect(
        sync_collection_resources_visibility,
        sender=Collection,
        dispatch_uid="web.collection_resources_visibility.sync",
    )


def _get_or_create_child_collection(parent, name: str) -> Collection:
    child = parent.get_children().filter(name=name).first()
    if child:
        return child
    return parent.add_child(instance=Collection(name=name))


def _ensure_news_images_collection() -> Collection:
    root_collection = Collection.get_first_root_node()
    photos_collection = _get_or_create_child_collection(root_collection, "Fotos")

    news_collection = photos_collection.get_children().filter(name="Noticias").first()
    if news_collection:
        return news_collection

    legacy_news_collection = Collection.objects.filter(name="Noticias").exclude(pk=photos_collection.pk).first()
    if legacy_news_collection:
        legacy_news_collection.move(photos_collection, pos="last-child")
        return legacy_news_collection

    return _get_or_create_child_collection(photos_collection, "Noticias")


def _extract_news_image_ids(page: BlogPage) -> set[int]:
    image_ids = set()

    if page.cover_image_id:
        image_ids.add(page.cover_image_id)

    body_stream = getattr(page, "body", None)
    if not body_stream:
        return image_ids

    for block in body_stream:
        if getattr(block, "block_type", "") != "image":
            continue

        image_obj = getattr(block, "value", None)
        image_id = getattr(image_obj, "id", None)
        if image_id:
            image_ids.add(image_id)

    return image_ids


def _collect_referenced_news_image_ids() -> set[int]:
    referenced_ids = set()
    for page in BlogPage.objects.live():
        referenced_ids.update(_extract_news_image_ids(page))
    return referenced_ids


def sync_news_page_images_collection(sender, instance, **kwargs) -> None:
    news_collection = _ensure_news_images_collection()
    parent_collection = news_collection.get_parent() or Collection.get_first_root_node()
    image_model = get_image_model()

    current_page_image_ids = _extract_news_image_ids(instance)
    if current_page_image_ids:
        images = image_model.objects.filter(id__in=current_page_image_ids).exclude(collection=news_collection)

        for image in images:
            image.collection = news_collection
            image.save(update_fields=["collection"])

    referenced_ids = _collect_referenced_news_image_ids()
    orphaned_news_images = image_model.objects.filter(collection=news_collection)
    if referenced_ids:
        orphaned_news_images = orphaned_news_images.exclude(id__in=referenced_ids)

    for image in orphaned_news_images:
        image.collection = parent_collection
        image.save(update_fields=["collection"])


def register_news_image_collection_signal() -> None:
    post_save.connect(
        sync_news_page_images_collection,
        sender=BlogPage,
        dispatch_uid="web.blogpage.news_images_collection.sync",
    )
