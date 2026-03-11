from django.db import migrations


def load_background_items(apps, schema_editor):
    BackgroundItem = apps.get_model("web", "background_item")
    items = [
        ("2002", "El Dr. Alexis Tejedor inicia el Salón de Iniciación Científica en el Centro Regional de Veraguas de la Universidad Tecnológica de Panamá.", 0),
        ("2015", "Se celebra la primera Jornada de Iniciación Científica a nivel institucional en la Universidad Tecnológica de Panamá.", 1),
        ("2016", "Firma de convenio con la Secretaría Nacional de Ciencia, Tecnología e Innovación. La JIC se nacionaliza en el marco del Congreso de la Asociación Panameña para el Avance de la Ciencia (APANAC).", 2),
        ("2017–2025", "La JIC se consolida como el principal evento de investigación juvenil a nivel nacional, con la participación de más de cinco universidades.", 3),
    ]
    for year_label, description, sort_order in items:
        BackgroundItem.objects.get_or_create(
            year_label=year_label,
            defaults={"description": description, "sort_order": sort_order},
        )


def load_jic_categories(apps, schema_editor):
    JicCategory = apps.get_model("web", "jic_category")
    items = [
        ("Ingeniería", "Proyectos de investigación en todas las ramas de la ingeniería: civil, mecánica, eléctrica, industrial, de sistemas, entre otras.", 0),
        ("Ciencias de la Salud", "Investigaciones en medicina, enfermería, odontología, farmacia y ciencias biomédicas.", 1),
        ("Ciencias Naturales y Exactas", "Proyectos en matemáticas, física, química, biología y ciencias ambientales.", 2),
        ("Ciencias Sociales y Humanísticas", "Estudios en sociología, psicología, educación, economía, derecho y humanidades.", 3),
        ("Tecnología e Informática", "Desarrollo de software, inteligencia artificial, ciberseguridad y sistemas de información.", 4),
        ("Agrociencias", "Investigaciones en agronomía, veterinaria, biotecnología agrícola y recursos naturales.", 5),
    ]
    for name, description, sort_order in items:
        JicCategory.objects.get_or_create(
            name=name,
            defaults={"description": description, "sort_order": sort_order},
        )


def load_awards(apps, schema_editor):
    Award = apps.get_model("web", "award")
    items = [
        ("Premio Nacional de Innovación Juvenil", "2024", "SENACYT", "Reconocimiento a la mejor iniciativa de divulgación científica estudiantil a nivel nacional.", 0),
        ("Mención de Honor APANAC", "2023", "APANAC", "Distinción por fomentar la investigación científica en universidades públicas panameñas.", 1),
        ("Premio a la Excelencia Académica", "2022", "Ministerio de Educación", "Otorgado por el impacto en la formación científica de jóvenes panameños.", 2),
        ("Reconocimiento a la Innovación Tecnológica", "2021", "Cámara de Comercio, Industrias y Agricultura de Panamá", "Reconocimiento a proyectos con mayor potencial de aplicación industrial y tecnológica.", 3),
        ("Premio Iberoamericano de Iniciación Científica", "2019", "OEI – Organización de Estados Iberoamericanos", "Distinción internacional por el modelo de jornada científica estudiantil replicable en Iberoamérica.", 4),
    ]
    for premio, year, entidad, descripcion, sort_order in items:
        Award.objects.get_or_create(
            premio=premio,
            year=year,
            defaults={"entidad": entidad, "descripcion": descripcion, "sort_order": sort_order},
        )


def load_important_dates(apps, schema_editor):
    ImportantDate = apps.get_model("web", "important_date")
    items = [
        ("Apertura de inscripciones", "2025-05-15", "Inicio del periodo de inscripción de proyectos en la plataforma JIC.", 0),
        ("Cierre de inscripciones", "2025-07-30", "Fecha límite para registrar proyectos de investigación.", 1),
        ("Selección institucional", "2025-08-20", "Evaluación y selección de proyectos a nivel de cada universidad.", 2),
        ("Selección nacional", "2025-09-15", "Evaluación nacional de los proyectos seleccionados por cada universidad.", 3),
        ("JIC Nacional 2025", "2025-10-24", "Celebración de la Jornada de Iniciación Científica a nivel nacional.", 4),
    ]
    for title, event_date, description, sort_order in items:
        ImportantDate.objects.get_or_create(
            title=title,
            defaults={
                "event_date": event_date,
                "description": description,
                "sort_order": sort_order,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0008_award_background_item_jic_category"),
    ]

    operations = [
        migrations.RunPython(load_background_items, migrations.RunPython.noop),
        migrations.RunPython(load_jic_categories, migrations.RunPython.noop),
        migrations.RunPython(load_awards, migrations.RunPython.noop),
        migrations.RunPython(load_important_dates, migrations.RunPython.noop),
    ]
