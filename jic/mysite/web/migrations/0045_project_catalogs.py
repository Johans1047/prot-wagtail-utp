from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.text


def _get_or_create_ci(model, value, defaults=None):
    if not value:
        return None
    existing = model.objects.filter(name__iexact=value).first()
    if existing:
        updated = False
        if defaults:
            for key, default_value in defaults.items():
                if not getattr(existing, key, None) and default_value:
                    setattr(existing, key, default_value)
                    updated = True
            if updated:
                existing.save(update_fields=list(defaults.keys()))
        return existing
    return model.objects.create(name=value, **(defaults or {}))


def backfill_project_catalogs(apps, schema_editor):
    Project = apps.get_model("web", "project")
    ProjectCategory = apps.get_model("web", "project_category")
    ProjectUniversity = apps.get_model("web", "project_university")

    for item in Project.objects.all().only("id", "category", "university", "university_short_name"):
        category_obj = _get_or_create_ci(ProjectCategory, (item.category or "").strip())
        university_obj = _get_or_create_ci(
            ProjectUniversity,
            (item.university or "").strip(),
            defaults={"short_name": (item.university_short_name or "").strip() or None},
        )

        update_fields = []
        if category_obj and item.category_catalog_id != category_obj.id:
            item.category_catalog_id = category_obj.id
            update_fields.append("category_catalog_id")

        if university_obj and item.university_catalog_id != university_obj.id:
            item.university_catalog_id = university_obj.id
            update_fields.append("university_catalog_id")

        if update_fields:
            item.save(update_fields=update_fields)


def reverse_backfill_project_catalogs(apps, schema_editor):
    # Safe no-op: keeping catalog data is harmless and useful on rollback.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0044_normalize_project_categories_universities"),
    ]

    operations = [
        migrations.CreateModel(
            name="project_category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="Nombre")),
                ("is_active", models.BooleanField(default=True, verbose_name="Activo")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Orden")),
            ],
            options={
                "verbose_name": "Categoría de Proyecto",
                "verbose_name_plural": "Categorías de Proyecto",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="project_university",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Nombre")),
                ("short_name", models.CharField(blank=True, max_length=50, null=True, verbose_name="Siglas")),
                ("is_active", models.BooleanField(default=True, verbose_name="Activo")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Orden")),
            ],
            options={
                "verbose_name": "Universidad de Proyecto",
                "verbose_name_plural": "Universidades de Proyecto",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="project_category",
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower("name"), name="web_project_category_name_ci_unique"),
        ),
        migrations.AddConstraint(
            model_name="project_university",
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower("name"), name="web_project_university_name_ci_unique"),
        ),
        migrations.AddField(
            model_name="project",
            name="category_catalog",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="projects", to="web.project_category", verbose_name="Categoría (catálogo)"),
        ),
        migrations.AddField(
            model_name="project",
            name="university_catalog",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="projects", to="web.project_university", verbose_name="Universidad (catálogo)"),
        ),
        migrations.RunPython(backfill_project_catalogs, reverse_backfill_project_catalogs),
    ]
