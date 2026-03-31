# Generated migration for normalizing project categories and universities to canonical forms

from django.db import migrations
import unicodedata


def normalize_text_key(raw_value):
    """Convert any text to normalized ASCII lowercase key for matching."""
    value = str(raw_value or "").strip().lower()
    value = unicodedata.normalize('NFD', value)
    value = ''.join(ch for ch in value if unicodedata.category(ch) != 'Mn')
    value = ''.join(ch if ch.isalnum() or ch.isspace() else ' ' for ch in value)
    return ' '.join(value.split())


CATEGORY_ALIASES = {
    "ingenieria": "Ingeniería",
    "ingenierias": "Ingeniería",
    "de la salud": "Ciencias de la Salud",
    "salud": "Ciencias de la Salud",
    "ciencias de la salud": "Ciencias de la Salud",
    "naturales y exactas": "Ciencias Naturales y Exactas",
    "ciencias naturales y exactas": "Ciencias Naturales y Exactas",
    "ciencias sociales": "Ciencias Sociales y Humanísticas",
    "sociales y humanisticas": "Ciencias Sociales y Humanísticas",
    "ciencias sociales y humanisticas": "Ciencias Sociales y Humanísticas",
    "0": "Ingeniería",
    "1": "Ciencias de la Salud",
    "2": "Ciencias Naturales y Exactas",
    "3": "Ciencias Sociales y Humanísticas",
}

CATEGORY_LABELS = {
    "Ingeniería": "Ingeniería",
    "Ciencias de la Salud": "Ciencias de la Salud",
    "Ciencias Naturales y Exactas": "Ciencias Naturales y Exactas",
    "Ciencias Sociales y Humanísticas": "Ciencias Sociales y Humanísticas",
}

OFFICIAL_UNIVERSITIES = [
    "Universidad Católica Santa María la Antigua",
    "Universidad Especializada de las Américas",
    "Universidad Internacional de Ciencia y Tecnología",
    "Universidad Latina de Panamá",
    "Universidad Marítima Internacional de Panamá",
    "Universidad Metropolitana de Educación, Ciencia y Tecnología",
    "Universidad Santander",
    "Universidad Tecnológica de Oteima",
    "Universidad Tecnológica de Panamá",
    "Universidad de Panamá",
]

UNIVERSITY_ALIASES = {
    "universidad catolica santa maria la antigua": "Universidad Católica Santa María la Antigua",
    "universidad catolica santa maria la antigua usma": "Universidad Católica Santa María la Antigua",
    "usma": "Universidad Católica Santa María la Antigua",
    "universidad tecnologica de panama": "Universidad Tecnológica de Panamá",
    "utp": "Universidad Tecnológica de Panamá",
    "universidad de panama": "Universidad de Panamá",
    "up": "Universidad de Panamá",
    "universidad metropolitana de educacion ciencia y tecnologia": "Universidad Metropolitana de Educación, Ciencia y Tecnología",
    "umecit": "Universidad Metropolitana de Educación, Ciencia y Tecnología",
    "universidad especializada de las americas": "Universidad Especializada de las Américas",
    "udelas": "Universidad Especializada de las Américas",
    "universidad internacional de ciencia y tecnologia": "Universidad Internacional de Ciencia y Tecnología",
    "unicyt": "Universidad Internacional de Ciencia y Tecnología",
    "universidad latina de panama": "Universidad Latina de Panamá",
    "ulat": "Universidad Latina de Panamá",
    "universidad maritima internacional de panama": "Universidad Marítima Internacional de Panamá",
    "umip": "Universidad Marítima Internacional de Panamá",
    "universidad santander": "Universidad Santander",
    "universidad tecnologica de oteima": "Universidad Tecnológica de Oteima",
}


def normalize_category(value):
    """Map category variants to canonical label."""
    if not value:
        return "Ingeniería"
    
    normalized_key = normalize_text_key(value)
    canonical = CATEGORY_ALIASES.get(normalized_key, value.strip())
    
    if canonical in CATEGORY_LABELS:
        return canonical
    
    return value.strip()


def normalize_university(value):
    """Map university name variants to canonical label."""
    if not value:
        return ""
    
    normalized_key = normalize_text_key(value)
    
    if normalized_key in UNIVERSITY_ALIASES:
        return UNIVERSITY_ALIASES[normalized_key]
    
    for official in OFFICIAL_UNIVERSITIES:
        if normalize_text_key(official) == normalized_key:
            return official
    
    return value.strip()


def normalize_projects(apps, schema_editor):
    """Forward: normalize all project categories and universities."""
    Project = apps.get_model('web', 'project')
    updated = 0
    
    for project_obj in Project.objects.all():
        old_category = project_obj.category
        old_university = project_obj.university
        
        project_obj.category = normalize_category(project_obj.category)
        project_obj.university = normalize_university(project_obj.university)
        
        if project_obj.category != old_category or project_obj.university != old_university:
            project_obj.save(update_fields=['category', 'university'])
            updated += 1
    
    print(f"✓ Normalized {updated} projects to canonical categories and universities")


def reverse_normalize_projects(apps, schema_editor):
    """Reverse: This is a data normalization; reversal not meaningful (no-op)."""
    print("ℹ Normalization cannot be reversibly undone; skipping reverse.")


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0043_download_documents_url_and_dropdown'),
    ]

    operations = [
        migrations.RunPython(normalize_projects, reverse_normalize_projects),
    ]
