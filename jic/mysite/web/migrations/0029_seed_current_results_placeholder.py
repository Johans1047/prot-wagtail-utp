from django.db import migrations
from django.utils import timezone


def seed_current_results_placeholder(apps, schema_editor):
    SelectionNational = apps.get_model("web", "selection_national")
    SelectionNationalDocument = apps.get_model("web", "selection_national_document")

    current_year = timezone.now().year

    current_result, _ = SelectionNational.objects.get_or_create(
        year=current_year,
        defaults={
            "status": "en_proceso",
            "total_projects": 0,
            "universities_count": 0,
            "is_active": True,
            "sort_order": 0,
        },
    )

    has_documents = SelectionNationalDocument.objects.filter(parent=current_result).exists()
    if not has_documents:
        SelectionNationalDocument.objects.create(
            parent=current_result,
            label=f"Documento provisional de resultados JIC {current_year}",
            document_type="PDF",
            href="https://iniciacioncientifica.utp.ac.pa/",
            sort_order=0,
        )


def reverse_seed_current_results_placeholder(apps, schema_editor):
    SelectionNational = apps.get_model("web", "selection_national")
    SelectionNationalDocument = apps.get_model("web", "selection_national_document")

    current_year = timezone.now().year
    try:
        current_result = SelectionNational.objects.get(year=current_year)
    except SelectionNational.DoesNotExist:
        return

    SelectionNationalDocument.objects.filter(
        parent=current_result,
        label=f"Documento provisional de resultados JIC {current_year}",
        href="https://iniciacioncientifica.utp.ac.pa/",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0028_alter_document_options"),
    ]

    operations = [
        migrations.RunPython(seed_current_results_placeholder, reverse_seed_current_results_placeholder),
    ]
