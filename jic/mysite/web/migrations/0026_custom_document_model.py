from django.db import migrations, models
import django.db.models.deletion


def backfill_custom_document(apps, schema_editor):
    BaseDocument = apps.get_model("wagtaildocs", "Document")
    CustomDocument = apps.get_model("web", "Document")
    DocumentVisibility = apps.get_model("web", "document_visibility")

    base_table = BaseDocument._meta.db_table
    custom_table = CustomDocument._meta.db_table
    visibility_table = DocumentVisibility._meta.db_table

    qn = schema_editor.quote_name

    # Insert missing child rows linked to existing wagtaildocs_document rows.
    # This avoids ORM save() on the child model, which can try to re-create the parent row.
    schema_editor.execute(
        f"""
        INSERT INTO {qn(custom_table)} (document_ptr_id, is_active)
        SELECT d.id, COALESCE(v.is_active, TRUE)
        FROM {qn(base_table)} d
        LEFT JOIN {qn(visibility_table)} v ON v.document_id = d.id
        WHERE NOT EXISTS (
            SELECT 1
            FROM {qn(custom_table)} cd
            WHERE cd.document_ptr_id = d.id
        )
        """
    )

    # Preserve explicit visibility values for rows that already existed in the child table.
    schema_editor.execute(
        f"""
        UPDATE {qn(custom_table)} cd
        SET is_active = v.is_active
        FROM {qn(visibility_table)} v
        WHERE cd.document_ptr_id = v.document_id
        """
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0025_document_visibility"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "document_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtaildocs.document",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Activo")),
            ],
            bases=("wagtaildocs.document",),
        ),
        migrations.RunPython(backfill_custom_document, noop_reverse),
        migrations.DeleteModel(
            name="document_visibility",
        ),
    ]
