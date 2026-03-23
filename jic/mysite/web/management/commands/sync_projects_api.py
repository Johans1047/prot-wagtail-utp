from django.core.management.base import BaseCommand

from web.utils import sync_projects_from_api


class Command(BaseCommand):
    help = "Synchronize projects from API payload into local DB tables."

    def handle(self, *args, **options):
        projects = sync_projects_from_api()
        self.stdout.write(
            self.style.SUCCESS(
                f"Projects payload normalized: {len(projects)}. Sync process executed."
            )
        )
