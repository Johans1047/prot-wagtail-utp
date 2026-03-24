"""
Management command to fix database integrity errors related to renditions.
Removes orphaned renditions and resets sequences.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from wagtail.images import get_image_model


class Command(BaseCommand):
    help = 'Fix rendition integrity errors by removing orphaned renditions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=True,
            help='Show what would be deleted without actually deleting (default: True)',
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            dest='execute',
            help='Actually fix the issues (be careful!)',
        )

    def handle(self, *args, **options):
        Image = get_image_model()
        dry_run = options['dry_run'] and not options['execute']

        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS(f"  FIX RENDITION INTEGRITY"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}\n"))
        self.stdout.write(f"Mode: {'DRY RUN (simulating)' if dry_run else 'EXECUTING'}\n")

        # Find orphaned renditions
        with connection.cursor() as cursor:
            # Get count of renditions with missing images
            cursor.execute("""
                SELECT COUNT(*)
                FROM wagtailimages_rendition r
                WHERE NOT EXISTS (
                    SELECT 1 FROM wagtailimages_image i 
                    WHERE i.id = r.image_id
                )
            """)
            orphaned_count = cursor.fetchone()[0]
            self.stdout.write(f"Found {orphaned_count} orphaned renditions")

            if orphaned_count > 0:
                if dry_run:
                    self.stdout.write(f"[DRY RUN] Would delete {orphaned_count} orphaned renditions")
                else:
                    self.stdout.write(f"Deleting orphaned renditions...")
                    cursor.execute("""
                        DELETE FROM wagtailimages_rendition
                        WHERE NOT EXISTS (
                            SELECT 1 FROM wagtailimages_image i 
                            WHERE i.id = image_id
                        )
                    """)
                    self.stdout.write(self.style.SUCCESS(f"✓ Deleted {orphaned_count} orphaned renditions"))

        # Reset sequences
        if not dry_run:
            self.stdout.write("\nResetting database sequences...")
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT setval(pg_get_serial_sequence('wagtailimages_rendition', 'id'), 
                                   COALESCE((SELECT MAX(id) FROM wagtailimages_rendition), 1))
                """)
            self.stdout.write(self.style.SUCCESS("✓ Sequences reset"))

        self.stdout.write(f"\n{'='*70}")
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"This was a DRY RUN. To actually fix, run with --execute flag."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("✓ Integrity check completed!"))
        self.stdout.write(f"{'='*70}\n")
