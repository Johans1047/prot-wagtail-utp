from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from web.image_pipeline import optimize_and_apply_to_field_file
from web.models import CustomImage


class Command(BaseCommand):
    help = "Recompress existing Wagtail images using the same upload pipeline."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of images to process (0 = all).",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all images, not only those above max final size.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be processed without saving changes.",
        )

    def handle(self, *args, **options):
        max_final_size = int(getattr(settings, "IMAGE_MAX_FINAL_SIZE", 5 * 1024 * 1024))
        process_all = bool(options["all"])
        dry_run = bool(options["dry_run"])
        limit = int(options["limit"] or 0)

        scanned = 0
        processed = 0
        replaced = 0
        failed = 0
        skipped = 0

        queryset = CustomImage.objects.order_by("id")

        for image in queryset.iterator():
            if limit and processed >= limit:
                break

            field_file = getattr(image, "file", None)
            if not field_file or not getattr(field_file, "name", ""):
                skipped += 1
                continue

            try:
                original_size = int(field_file.size)
            except Exception:
                skipped += 1
                continue

            scanned += 1

            if not process_all and original_size <= max_final_size:
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"[DRY-RUN] id={image.id} size={original_size} name={field_file.name}"
                )
                processed += 1
                continue

            try:
                result = optimize_and_apply_to_field_file(field_file)
            except ValidationError as exc:
                failed += 1
                self.stdout.write(self.style.ERROR(f"[ERROR] id={image.id}: {exc}"))
                continue
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.ERROR(f"[ERROR] id={image.id}: {exc}"))
                continue

            if not result:
                skipped += 1
                continue

            update_fields = ["file_size"]
            image.file_size = result.final_size

            if result.width and result.height:
                image.width = result.width
                image.height = result.height
                update_fields.extend(["width", "height"])

            if result.replace_file:
                replaced += 1
                update_fields.append("file")

            image._compression_in_progress = True
            try:
                image.save(update_fields=list(dict.fromkeys(update_fields)))
            finally:
                image._compression_in_progress = False

            processed += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"[OK] id={image.id} {original_size} -> {result.final_size} bytes ({image.file.name})"
                )
            )

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Recompression summary"))
        self.stdout.write(f"Scanned:   {scanned}")
        self.stdout.write(f"Processed: {processed}")
        self.stdout.write(f"Replaced:  {replaced}")
        self.stdout.write(f"Skipped:   {skipped}")
        self.stdout.write(f"Failed:    {failed}")
