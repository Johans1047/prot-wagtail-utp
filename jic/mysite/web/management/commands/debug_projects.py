from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


class Command(BaseCommand):
    help = "Debug projects and consultant data in database"

    def handle(self, *args, **options):
        try:
            # Import models
            from web.models import project, consultant
            
            # Check if tables exist and have data
            projects_count = project.objects.count()
            consultants_count = consultant.objects.count()
            
            self.stdout.write(self.style.SUCCESS(f"✓ Projects table: {projects_count} records"))
            self.stdout.write(self.style.SUCCESS(f"✓ Consultants table: {consultants_count} records"))
            
            if projects_count > 0:
                self.stdout.write("\n📋 Sample projects:")
                for p in project.objects.all()[:3]:
                    advisor_name = p.advisor.name if p.advisor else "NO ADVISOR"
                    self.stdout.write(f"  ID: {p.id} | {p.title} | Advisor: {advisor_name}")
            
            if consultants_count > 0:
                self.stdout.write("\n👤 Sample consultants:")
                for c in consultant.objects.all()[:3]:
                    self.stdout.write(f"  ID: {c.id} | {c.name} | Email: {c.email}")
            
            # Now test _get_projects_from_database()
            self.stdout.write("\n" + "="*60)
            self.stdout.write("Testing _get_projects_from_database()...")
            self.stdout.write("="*60)
            
            from web.utils import _get_projects_from_database
            result = _get_projects_from_database()
            
            self.stdout.write(self.style.SUCCESS(f"✓ Returned: {len(result)} projects"))
            if result:
                self.stdout.write("\n📋 First project from function:")
                p = result[0]
                self.stdout.write(f"  Title: {p['title']}")
                self.stdout.write(f"  Advisor: {p['advisor']}")
                self.stdout.write(f"  Contact: {p['contact']}")
            
        except (OperationalError, ProgrammingError) as e:
            self.stdout.write(self.style.ERROR(f"✗ Database Error: {e}"))
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"✗ Import Error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Unexpected Error: {e}"))
            import traceback
            traceback.print_exc()
