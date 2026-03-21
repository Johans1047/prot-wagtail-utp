from django.db import migrations, models
import django.db.models.deletion


def create_visibility_for_existing_documents(apps, schema_editor):
    Document = apps.get_model("wagtaildocs", "Document")
    DocumentVisibility = apps.get_model("web", "document_visibility")

    for doc in Document.objects.all().iterator():
        DocumentVisibility.objects.get_or_create(
            document_id=doc.id,
            defaults={"is_active": True},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("wagtaildocs", "0001_initial"),
        ("web", "0024_important_date_is_primary"),
    ]

    operations = [
        migrations.CreateModel(
            name="document_visibility",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True, verbose_name="Activo")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Última actualización")),
                (
                    "document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="visibility",
                        to="wagtaildocs.document",
                        verbose_name="Documento",
                    ),
                ),
            ],
            options={
                "verbose_name": "Estado de documento",
                "verbose_name_plural": "Estados de documentos",
                "ordering": ["document__title"],
            },
        ),
        migrations.RunPython(create_visibility_for_existing_documents, noop_reverse),
    ]
