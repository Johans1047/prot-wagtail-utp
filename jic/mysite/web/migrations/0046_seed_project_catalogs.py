from django.db import migrations


DEFAULT_PROJECT_CATEGORIES = [
    "Ingeniería",
    "Ciencias de la Salud",
    "Ciencias Naturales y Exactas",
    "Ciencias Sociales y Humanísticas",
]

DEFAULT_PROJECT_UNIVERSITIES = [
    ("Universidad Católica Santa María la Antigua", "USMA"),
    ("Universidad Especializada de las Américas", "UDELAS"),
    ("Universidad Internacional de Ciencia y Tecnología", "UNICYT"),
    ("Universidad Latina de Panamá", "ULAT"),
    ("Universidad Marítima Internacional de Panamá", "UMIP"),
    ("Universidad Metropolitana de Educación, Ciencia y Tecnología", "UMECIT"),
    ("Universidad Santander", ""),
    ("Universidad Tecnológica de Oteima", "UTO"),
    ("Universidad Tecnológica de Panamá", "UTP"),
    ("Universidad de Panamá", "UP"),
]


def _get_or_create_ci(model, name, defaults=None):
    item = model.objects.filter(name__iexact=name).first()
    if item:
        if defaults:
            changed = False
            for key, value in defaults.items():
                if not getattr(item, key, None) and value:
                    setattr(item, key, value)
                    changed = True
            if changed:
                item.save(update_fields=list(defaults.keys()))
        return item
    return model.objects.create(name=name, **(defaults or {}))


def seed_project_catalogs(apps, schema_editor):
    ProjectCategory = apps.get_model("web", "project_category")
    ProjectUniversity = apps.get_model("web", "project_university")

    for index, category_name in enumerate(DEFAULT_PROJECT_CATEGORIES):
        category = _get_or_create_ci(ProjectCategory, category_name)
        if category.sort_order != index:
            category.sort_order = index
            category.save(update_fields=["sort_order"])

    for index, (university_name, short_name) in enumerate(DEFAULT_PROJECT_UNIVERSITIES):
        university = _get_or_create_ci(
            ProjectUniversity,
            university_name,
            defaults={"short_name": short_name or None},
        )
        updates = []
        if university.sort_order != index:
            university.sort_order = index
            updates.append("sort_order")
        if short_name and not university.short_name:
            university.short_name = short_name
            updates.append("short_name")
        if updates:
            university.save(update_fields=updates)


def reverse_seed_project_catalogs(apps, schema_editor):
    # Keep catalog records on rollback to avoid deleting user-managed data.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0045_project_catalogs"),
    ]

    operations = [
        migrations.RunPython(seed_project_catalogs, reverse_seed_project_catalogs),
    ]
