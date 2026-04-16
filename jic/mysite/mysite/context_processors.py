from django.conf import settings
from django.urls import reverse
from django.db.utils import OperationalError, ProgrammingError

def debug(request):
    return {'debug': settings.DEBUG}

def nav_items(request):
    return {
        "nav_items": [
            {"url": reverse('Inicio'), "label": "Inicio"},
            {"url": reverse('AcercaDe'), "label": "Acerca de"},
            {"url": reverse('Participar'), "label": "Participar"},
            {"url": reverse('Proyectos'), "label": "Proyectos"},
            {"url": reverse('Resultados'), "label": "Resultados"},
            {"url": reverse('Recursos'), "label": "Recursos"},
            {"url": reverse('Contacto'), "label": "Contacto"},
        ]
    }


def site_content(request):
    defaults = {
        "platform_url": "https://jic.utp.ac.pa",
        "quick_section_title": "Accesos rápidos",
        "quick_section_description": "Todo lo que necesitas para la JIC en un solo lugar",
        "faq_section_title": "Preguntas Frecuentes",
        "faq_section_description": "Todo lo que necesitas saber sobre la Jornada de Iniciación Científica",
        "ridda_url": "https://ridda2.utp.ac.pa",
        "categories_reference_url": "https://ridda2.utp.ac.pa",
    }

    try:
        from web.models import site_content_settings

        data = site_content_settings.get_singleton()
        return {
            "site_content": {
                "platform_url": data.platform_url or defaults["platform_url"],
                "quick_section_title": data.quick_section_title or defaults["quick_section_title"],
                "quick_section_description": data.quick_section_description or defaults["quick_section_description"],
                "faq_section_title": data.faq_section_title or defaults["faq_section_title"],
                "faq_section_description": data.faq_section_description or defaults["faq_section_description"],
                "ridda_url": data.ridda_url or defaults["ridda_url"],
                "categories_reference_url": data.categories_reference_url or defaults["categories_reference_url"],
            }
        }
    except (OperationalError, ProgrammingError):
        return {"site_content": defaults}
    except Exception:
        return {"site_content": defaults}
