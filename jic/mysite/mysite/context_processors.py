from django.conf import settings
from django.urls import reverse

def debug(request):
    return {'debug': settings.DEBUG}

def nav_items(request):
    return {
        "nav_items": [
            {"url": reverse('Inicio'), "label": "Inicio"},
            {"url": reverse('Jic'), "label": "JIC"},
            {"url": reverse('Participar'), "label": "Participar"},
            {"url": reverse('Proyectos'), "label": "Proyectos"},
            {"url": reverse('Resultados'), "label": "Resultados"},
            {"url": reverse('Recursos'), "label": "Recursos"},
            {"url": reverse('Contacto'), "label": "Contacto"},
        ]
    }
