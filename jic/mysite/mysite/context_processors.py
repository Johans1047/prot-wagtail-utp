from django.conf import settings

def debug(request):
    return {'debug': settings.DEBUG}

def nav_items(request):
    return {
        "nav_items": [
            {"url": "/", "label": "Inicio"},
            {"url": "/jic/", "label": "JIC"},
            {"url": "/participar/", "label": "Participar"},
            {"url": "/proyectos/", "label": "Proyectos"},
            {"url": "/resultados/", "label": "Resultados"},
            {"url": "/recursos/", "label": "Recursos"},
            {"url": "/contacto/", "label": "Contacto"},
        ]
    }
