from django.core.management.base import BaseCommand
from web.models import background_item  # ajusta el import según tu app


BACKGROUND_DATA = [
    {
        "year_label": "2002",
        "description": (
            "El Dr. Alexis Tejedor inicia el Salón de Iniciación Científica en el "
            "Centro Regional de Veraguas de la Universidad Tecnológica de Panamá."
        ),
        "sort_order": 10,
    },
    {
        "year_label": "2015",
        "description": (
            "Se celebra la primera Jornada de Iniciación Científica a nivel "
            "institucional en la Universidad Tecnológica de Panamá (JIC-UTP)."
        ),
        "sort_order": 20,
    },
    {
        "year_label": "2016",
        "description": (
            "Firma de convenio con la Secretaría Nacional de Ciencia, Tecnología e "
            "Innovación. La JIC se nacionaliza en el marco del Congreso de la "
            "Asociación Panameña para el Avance de la Ciencia (APANAC). "
            "Se celebra la JIC Nacional I."
        ),
        "sort_order": 30,
    },
    {
        "year_label": "2019",
        "description": (
            "Aumento de presupuesto para la JIC-UTP, fortaleciendo su capacidad "
            "operativa y de difusión científica."
        ),
        "sort_order": 40,
    },
    {
        "year_label": "2020",
        "description": (
            "Ante la pandemia, la JIC-UTP VI se realiza en formato completamente "
            "virtual, marcando un hito en la adaptación tecnológica del evento."
        ),
        "sort_order": 50,
    },
    {
        "year_label": "2021",
        "description": (
            "Firma de Convenio de Cooperación para la JIC Nacional V, consolidando "
            "alianzas interinstitucionales para la investigación juvenil."
        ),
        "sort_order": 60,
    },
    {
        "year_label": "2022",
        "description": (
            "Firma del Convenio de Cooperación para la JIC Nacional 2022–2023, "
            "asegurando continuidad y crecimiento del evento a nivel nacional."
        ),
        "sort_order": 70,
    },
    {
        "year_label": "2024",
        "description": (
            "Firma del Convenio de Cooperación para la JIC Nacional 2024–2025, "
            "reafirmando el compromiso de las instituciones participantes."
        ),
        "sort_order": 80,
    },
    {
        "year_label": "2025",
        "description": (
            "Se celebran simultáneamente la JIC-UTP XI y la JIC Nacional IX, "
            "consolidando el evento como el principal foro de investigación "
            "juvenil a nivel nacional, con la participación de más de cinco "
            "universidades."
        ),
        "sort_order": 90,
    },
]


class Command(BaseCommand):
    help = "Populates (or repopulates) the background_item table with JIC history data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Delete all existing records before inserting (default: False).",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted_count, _ = background_item.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Deleted {deleted_count} existing record(s).")
            )

        created = 0
        updated = 0

        for entry in BACKGROUND_DATA:
            obj, was_created = background_item.objects.update_or_create(
                year_label=entry["year_label"],
                defaults={
                    "description": entry["description"],
                    "sort_order": entry["sort_order"],
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created} record(s) created, {updated} record(s) updated."
            )
        )