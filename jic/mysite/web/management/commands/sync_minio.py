from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from wagtail.images import get_image_model
from wagtail.documents import get_document_model
from web.models import (
    video,
    resource_document,
    award,
    event_intro,
    coordinator,
    organizer_committee_member,
    GalleryImage
)

Image = get_image_model()
Document = get_document_model()

class Command(BaseCommand):
    help = 'Synchronize MinIO deletions by removing database records pointing to non-existent files.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting MinIO synchronization check..."))
        
        # Configuration: List of (Model, [file_fields]) to check
        checks = [
            (video, ['video_file', 'thumbnail']),
            (resource_document, ['document_file']),
            (award, ['image']),
            (event_intro, ['logo_image']),
            (coordinator, ['photo']),
            (organizer_committee_member, ['photo']),
            (GalleryImage, ['image']),
            # Wagtail core models
            (Image, ['file']),
            (Document, ['file']),
        ]

        total_deleted = 0

        for model, fields in checks:
            model_name = model._meta.verbose_name
            self.stdout.write(f"Checking {model_name}...")
            
            deleted_count = 0
            # Iterate through all objects of the model
            for instance in model.objects.all():
                should_delete = False
                missing_files = []

                for field_name in fields:
                    field_value = getattr(instance, field_name, None)

                    # Resolve to a file name for both FileField values and related objects (e.g. wagtail image FK).
                    file_name = None
                    if field_value is not None:
                        if hasattr(field_value, "name"):
                            file_name = field_value.name
                        elif hasattr(field_value, "file") and getattr(field_value.file, "name", None):
                            file_name = field_value.file.name

                    # Skip if field is empty/null or does not point to a file.
                    if not file_name:
                        continue
                        
                    # Check if file exists in storage (MinIO)
                    if not default_storage.exists(file_name):
                        missing_files.append(file_name)
                        should_delete = True

                if should_delete:
                    try:
                        pk = instance.pk
                        title = str(instance)
                        instance.delete()
                        self.stdout.write(
                            self.style.WARNING(f"  [DELETED] {model_name} ID {pk} ('{title}') - Missing: {', '.join(missing_files)}")
                        )
                        deleted_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  [ERROR] Failed to delete {model_name} ID {instance.pk}: {e}")
                        )
            
            if deleted_count > 0:
                self.stdout.write(self.style.SUCCESS(f"-> Removed {deleted_count} orphan {model_name}(s)"))
            
            total_deleted += deleted_count

        self.stdout.write(self.style.MIGRATE_HEADING(f"Synchronization complete. Total records removed: {total_deleted}"))
