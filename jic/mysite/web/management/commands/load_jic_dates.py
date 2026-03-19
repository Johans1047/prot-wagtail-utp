from django.core.management.base import BaseCommand
from datetime import date
from web.models import important_date

class Command(BaseCommand):
    help = 'Puebla la base de datos con las fechas importantes de la JIC 2026'

    def handle(self, *args, **kwargs):
        self.stdout.write("Borrando fechas anteriores...")
        important_date.objects.all().delete()

        dates_data = [
            # --- Selección Institucional ---
            {
                "title": "Inscripción de participantes en Plataforma JIC",
                "date_text": "Del 04 de mayo al 31 de agosto de 2026",
                "event_date": date(2026, 5, 4),
                "description": "Si el coordinador IES utiliza otro sistema, deberá entregar la información según plantilla.",
                "sort_order": 1
            },
            {
                "title": "Registro de artículos de los participantes",
                "date_text": "Del 04 de mayo al 15 de septiembre 2026",
                "event_date": date(2026, 5, 5),
                "description": "De tener problemas con la entrega, remitir a jic.soporte@utp.ac.pa.",
                "sort_order": 2
            },
            {
                "title": "Selección de los participantes para la JIC Nacional",
                "date_text": "A más tardar el 17 de agosto de 2026",
                "event_date": date(2026, 8, 17),
                "description": "El proceso de evaluación para la selección será realizado por cada IES.",
                "sort_order": 3
            },
            {
                "title": "Entrega de acta, informe y registro de estudiantes",
                "date_text": "Hasta el 18 de agosto de 2026",
                "event_date": date(2026, 8, 18),
                "description": "Acta de evaluación, informe general de la participación y los proyectos seleccionados (Excel u opciones en plataforma).",
                "sort_order": 4
            },

            # --- Selección Nacional ---
            {
                "title": "Logística de hospedaje a estudiantes del interior",
                "date_text": "Entre 1 de julio y 3 de octubre de 2026",
                "event_date": date(2026, 7, 1),
                "description": "La Dirección Nacional de Investigación de la UTP es responsable según cuota.",
                "sort_order": 5
            },
            {
                "title": "Inscripción al Congreso Nacional de Ciencia (APANAC)",
                "date_text": "Del 20 de agosto al 4 de septiembre de 2026",
                "event_date": date(2026, 8, 20),
                "description": "Estudiantes y un asesor de cada proyecto seleccionado.",
                "sort_order": 6
            },
            {
                "title": "Envío de artículo final, póster y vídeo (YouTube)",
                "date_text": "Hasta el 15 de septiembre de 2026",
                "event_date": date(2026, 9, 15),
                "description": "Posterior a la fecha se realizará la evaluación de plagio y entrega a SENACYT.",
                "sort_order": 7
            },
            {
                "title": "Revisión de artículos (plagio, afiliaciones, póster)",
                "date_text": "Entre el 16 y el 24 de septiembre de 2026",
                "event_date": date(2026, 9, 16),
                "description": "Realizado por la Dirección Nacional de Investigación de la UTP.",
                "sort_order": 8
            },
            {
                "title": "Entrega de documentación a la SENACYT",
                "date_text": "25 de septiembre de 2026",
                "event_date": date(2026, 9, 25),
                "description": "La Dirección Nacional de Investigación entrega videos, artículos y pósteres.",
                "sort_order": 9
            },
            {
                "title": "Evaluación de los participantes por parte de SENACYT",
                "date_text": "Entre 12 al 16 de octubre de 2026",
                "event_date": date(2026, 10, 12),
                "description": "La evaluación se realiza con los vídeos, artículos y pósteres digitales sin autoría.",
                "sort_order": 10
            },
            {
                "title": "Exhibición de pósteres (IESTEC 2026)",
                "date_text": "Del 21 al 23 de octubre de 2026",
                "event_date": date(2026, 10, 21),
                "description": "Presentación de pósteres impresos a la comunidad científica en la UTP.",
                "sort_order": 11
            },
            {
                "title": "Selección de los equipos ganadores",
                "date_text": "Del 21 al 23 de octubre de 2026",
                "event_date": date(2026, 10, 22),
                "description": "Selección de los ganadores de la JIC Nacional.",
                "sort_order": 12
            },

            # --- Premiación e Internacional ---
            {
                "title": "Entrega de Premiación a los Ganadores (Gala Científica)",
                "date_text": "20 de noviembre de 2026",
                "event_date": date(2026, 11, 20),
                "description": "En la Universidad Tecnológica de Panamá (UTP)",
                "sort_order": 13
            },
            {
                "title": "Escogencia de actividad científica internacional",
                "date_text": "Entre 1 de diciembre 2026 a 30 de abril 2027",
                "event_date": date(2026, 12, 1),
                "description": "Congreso, capacitación, taller o pasantía.",
                "sort_order": 14
            },
            {
                "title": "Participación en actividad científica",
                "date_text": "Hasta el 31 de julio de 2027",
                "event_date": date(2027, 7, 31),
                "description": "Sujeta a fecha de la actividad escogida.",
                "sort_order": 15
            }
        ]

        for data in dates_data:
            important_date.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(f'¡Se cargaron {len(dates_data)} fechas exitosamente!'))