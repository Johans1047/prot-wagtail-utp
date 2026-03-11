from django.shortcuts import render
from django.db.utils import OperationalError, ProgrammingError
from .viewsdata_types import *
from .viewsdata_fallback import *
from .models import *

def Inicio(request) -> render:
    try:
        important_dates = list(
            important_date.objects.filter(is_active=True).order_by("sort_order", "event_date")
        )
    except (OperationalError, ProgrammingError):
        # Keeps the home page functional before running migrations.
        important_dates = []

    if not important_dates:
        important_dates = important_dates_fallback()

    faqs: dict[str, FAQCategory] = {}
    try:
        db_faqs = frequently_ask_question.objects.filter(is_active=True)
        for faq in db_faqs:
            slug = faq.category_slug
            if slug not in faqs:
                faqs[slug] = FAQCategory(title=faq.category)
            faqs[slug].items.append(FAQItem(q=faq.question, a=faq.answer))
    except (OperationalError, ProgrammingError):
        pass

    if not faqs:
        faqs = faqs_fallback()
    
    winners_by_place = [
        {
            "place": 1,
            "place_label": "Primer Lugar",
            "winners": [
                {"title": "Sistema de monitoreo ambiental con IoT para la detección temprana de contaminantes", "university": "Universidad Tecnológica de Panamá", "category": "Ingeniería", "authors": "J. Pérez, M. Rodríguez"},
                {"title": "Análisis de biomarcadores en pacientes con diabetes tipo 2 en población panameña", "university": "Universidad de Panamá", "category": "Ciencias de la Salud", "authors": "M. García, L. Sánchez"},
                {"title": "Modelado matemático de ecosistemas costeros del Golfo de Panamá", "university": "Universidad Tecnológica de Panamá", "category": "Ciencias Naturales y Exactas", "authors": "A. López, C. Martínez"},
                {"title": "Impacto socioeconómico de la migración en comunidades rurales de Darién", "university": "Universidad de Panamá", "category": "Ciencias Sociales y Humanísticas", "authors": "R. Castillo, E. Vega"},
            ],
        },
        {
            "place": 2,
            "place_label": "Segundo Lugar",
            "winners": [
                {"title": "Desarrollo de materiales biodegradables a partir de residuos agrícolas", "university": "USMA", "category": "Ingeniería", "authors": "F. Morales, K. Chen"},
                {"title": "Evaluación de plantas medicinales nativas con propiedades antiinflamatorias", "university": "UNACHI", "category": "Ciencias de la Salud", "authors": "D. Herrera, P. Gutiérrez"},
                {"title": "Estudio de microplásticos en ríos de la cuenca del Canal de Panamá", "university": "Universidad Tecnológica de Panamá", "category": "Ciencias Naturales y Exactas", "authors": "S. Moreno, J. Batista"},
                {"title": "Preservación digital del patrimonio cultural Guna", "university": "Universidad Latina", "category": "Ciencias Sociales y Humanísticas", "authors": "M. Obaldia, L. Torres"},
            ],
        },
        {
            "place": 3,
            "place_label": "Tercer Lugar",
            "winners": [
                {"title": "Optimización de redes eléctricas mediante algoritmos de inteligencia artificial", "university": "Universidad Tecnológica de Panamá", "category": "Ingeniería", "authors": "H. Quintero, N. Salas"},
                {"title": "Factores de riesgo cardiovascular en jóvenes universitarios panameños", "university": "Universidad de Panamá", "category": "Ciencias de la Salud", "authors": "V. Arauz, B. Montenegro"},
                {"title": "Inventario de biodiversidad en manglares de Bocas del Toro", "university": "UNACHI", "category": "Ciencias Naturales y Exactas", "authors": "G. Santamaría, I. Pitti"},
                {"title": "Análisis lingüístico de lenguas criollas en la costa caribeña panameña", "university": "Universidad de Panamá", "category": "Ciencias Sociales y Humanísticas", "authors": "T. Williams, A. Brown"},
            ],
        },
    ]

    context = {
        'important_dates': important_dates,
        'faqs': faqs,
        'winners_by_place': winners_by_place,
    }
    
    return render(request, 'inicio/_index.html', context)

def Jic(request) -> render:
    try:
        background_items = list(background_item.objects.all())
    except (OperationalError, ProgrammingError):
        background_items = []
        
    if not background_items:
        background_items = background_items_fallback()

    try:
        jic_categories = list(jic_category.objects.all())
    except (OperationalError, ProgrammingError):
        jic_categories = []
        
    if not jic_categories:
        jic_categories = jic_categories_fallback()

    try:
        awards = list(award.objects.all())
    except (OperationalError, ProgrammingError):
        awards = []
        
    if not awards:
        awards = awards_fallback()

    organizations = [
        {
            "nombre": "Universidad Tecnológica de Panamá",
            "siglas": "UTP"
        }
    ]

    sponsors = [
        {
            "nombre": "Secretaría Nacional de Ciencia, Tecnología e Innovación",
            "siglas": "SENACYT"
        }
    ]

    coordinadores_nacionales = [
        {"shortName": "UTP", "coordinator": "Dr. Juan Pérez", "email": "jic.utp@utp.ac.pa"},
        {"shortName": "UP", "coordinator": "Dra. María Rodríguez", "email": "jic.up@up.ac.pa"},
        {"shortName": "USMA", "coordinator": "Mgtr. Carlos López", "email": "jic.usma@usma.ac.pa"},
        {"shortName": "UNACHI", "coordinator": "Dr. Roberto Gómez", "email": "jic.unachi@unachi.ac.pa"},
        {"shortName": "ULAT", "coordinator": "Mgtr. Ana Torres", "email": "jic.ulat@ulat.ac.pa"},
    ]

    comite_organizador = [
        {"name": "Dr. Luis Herrera", "role": "Director General", "institution": "UTP"},
        {"name": "Dra. Sandra Morales", "role": "Coordinación Académica", "institution": "SENACYT"},
        {"name": "Mgtr. Ricardo Vega", "role": "Coordinación Logística", "institution": "UTP"},
        {"name": "Ing. Patricia Salas", "role": "Coordinación Tecnológica", "institution": "UTP"},
    ]

    context = {
        'background_items': background_items,
        'jic_categories': jic_categories,
        'awards': awards,
        'organizations': organizations,
        'sponsors': sponsors,
        'coordinadores_nacionales': coordinadores_nacionales,
        'comite_organizador': comite_organizador,
    }
    return render(request, 'jic/_index.html', context)

def Participar(request) -> render:
    try:
        important_dates = list(
            important_date.objects.filter(is_active=True).order_by("sort_order", "event_date")
        )
    except (OperationalError, ProgrammingError):
        important_dates = []
    if not important_dates:
        important_dates = important_dates_fallback()

    resource_categories = [
        {
            "title": "Estudiantes",
            "description": "Informacion para participantes",
            "accent": "bg-primary/90 text-primary-foreground",
            "resources": [
                {
                    "label": "Lineamientos de participacion 2025",
                    "href": "https://iniciacioncientifica.utp.ac.pa/subida-de-documentos-para-docentes/",
                },
                {
                    "label": "Plantilla para articulos",
                    "href": "https://iniciacioncientifica.utp.ac.pa/instructivos-y-ejemplos-para-estudiantes/",
                },
                {"label": "Manual de usuario: Estudiante", "href": "#"},
                {
                    "label": "Recursos digitales",
                    "href": "https://iniciacioncientifica.utp.ac.pa/subida-de-documentos-para-docentes/",
                },
            ]
        },
        {
            "title": "Asesores",
            "description": "Informacion para asesores",
            "accent": "bg-secondary-foreground/65 text-primary-foreground",
            "resources": [
                {"label": "Lineamientos para asesores", "href": "#"},
                {
                    "label": "Rubricas de evaluacion",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/05/manual-proce-JIC.pdf",
                },
                {"label": "Manual de usuario: Asesor", "href": "#"},
            ]
        },
        {
            "title": "Evaluadores",
            "description": "Informacion para evaluadores",
            "accent": "bg-amber-400 text-secondary-foreground",
            "resources": [
                {
                    "label": "Rubricas de evaluacion",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/05/manual-proce-JIC.pdf",
                },
                {"label": "Procedimiento de evaluacion", "href": "#"},
                {"label": "Documentos de induccion", "href": "#"},
            ]
        },
    ]
    
    context = {
        'important_dates': important_dates,
        'resource_categories': resource_categories,
    }
    return render(request, 'participar/_index..html', context)

def Proyectos(request) -> render:
    # Datos de ejemplo de proyectos
    all_projects = [
        {
            "year": 2024,
            "title": "Sistema de monitoreo ambiental con IoT",
            "university": "UTP",
            "category": "Ingeniería",
            "contact": "proyecto1@utp.ac.pa",
            "advisor": "Dr. Carlos Méndez",
            "abstract": "Desarrollo de un sistema de monitoreo ambiental basado en sensores IoT para la detección temprana de contaminantes en zonas industriales de la provincia de Panamá.",
            "place": 1,
            "winner": True,
        },
        {
            "year": 2024,
            "title": "Análisis de biomarcadores en diabetes",
            "university": "UP",
            "category": "Ciencias de la Salud",
            "contact": "proyecto2@up.ac.pa",
            "advisor": "Dra. Rosa Jiménez",
            "abstract": "Estudio de biomarcadores séricos en pacientes con diabetes tipo 2 en la población panameña, buscando indicadores tempranos de complicaciones renales.",
            "place": 2,
            "winner": True,
        },
        {
            "year": 2023,
            "title": "Modelado matemático de ecosistemas",
            "university": "UTP",
            "category": "Ciencias Naturales",
            "contact": "proyecto3@utp.ac.pa",
            "advisor": "Dr. Federico Ríos",
            "abstract": "Modelado computacional de la dinámica de ecosistemas costeros del Golfo de Panamá utilizando ecuaciones diferenciales y simulación numérica.",
            "place": None,
            "winner": False,
        },
        {
            "year": 2023,
            "title": "Plataforma de educación digital",
            "university": "UNIANDES",
            "category": "Tecnología",
            "contact": "proyecto4@uniandes.ac.pa",
            "advisor": "Mgtr. Ana Valdés",
            "abstract": "Diseño e implementación de una plataforma de educación digital adaptativa para comunidades rurales con acceso limitado a internet en Panamá.",
            "place": None,
            "winner": False,
        },
        {
            "year": 2022,
            "title": "Estudio de aguas residuales",
            "university": "UTP",
            "category": "Ingeniería Ambiental",
            "contact": "proyecto5@utp.ac.pa",
            "advisor": "Dr. Héctor Sandoval",
            "abstract": "Evaluación de técnicas de fitorremediación para el tratamiento de aguas residuales industriales en la cuenca del Canal de Panamá.",
            "place": 1,
            "winner": True,
        },
    ]
    
    # Obtener parámetros de filtro
    tab = request.GET.get('tab', 'all')
    search = request.GET.get('search', '')
    year_filter = request.GET.get('year', 'all')
    category_filter = request.GET.get('category', 'all')
    
    # Filtrar proyectos
    filtered = all_projects
    
    if tab == 'winners':
        filtered = [p for p in filtered if p['winner']]
    
    if search:
        search_lower = search.lower()
        filtered = [p for p in filtered if search_lower in p['title'].lower() or search_lower in p['university'].lower()]
    
    if year_filter != 'all':
        try:
            year_filter_int = int(year_filter)
            filtered = [p for p in filtered if p['year'] == year_filter_int]
        except ValueError:
            pass
    
    if category_filter != 'all':
        filtered = [p for p in filtered if p['category'] == category_filter]
    
    # Obtener lista de años únicos
    years = sorted(set(p['year'] for p in all_projects), reverse=True)
    
    # Obtener opciones de categorías únicas
    categories_options = [
        {"value": "all", "label": "Todas las categorías"},
    ]
    for category in sorted(set(p['category'] for p in all_projects)):
        categories_options.append({"value": category, "label": category})
    
    try:
        schedule_dates = list(
            important_date.objects.filter(is_active=True).order_by("sort_order", "event_date")
        )
    except (OperationalError, ProgrammingError):
        schedule_dates = []
    if not schedule_dates:
        schedule_dates = important_dates_fallback()

    context = {
        'filtered': filtered,
        'tab': tab,
        'search': search,
        'year_filter': year_filter,
        'category_filter': category_filter,
        'years': years,
        'categories_options': categories_options,
        'important_dates': schedule_dates,
    }
    return render(request, 'proyectos/_index.html', context)

def Resultados(request) -> render:
    # Datos históricos de ediciones anteriores
    historical_results = [
        {
            "year": 2024,
            "totalProjects": 47,
            "universities": 5,
            "documents": [
                {
                    "label": "Acta de resultados",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/12/acta-jic-2024.pdf",
                },
                {
                    "label": "Listado de ganadores",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/12/ganadores-jic-2024.pdf",
                },
            ]
        },
        {
            "year": 2023,
            "totalProjects": 42,
            "universities": 5,
            "documents": [
                {
                    "label": "Acta de resultados",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2023/12/acta-jic-2023.pdf",
                },
                {
                    "label": "Listado de ganadores",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2023/12/ganadores-jic-2023.pdf",
                },
                {
                    "label": "Fotografías del evento",
                    "type": "ZIP",
                    "href": "https://iniciacioncientifica.utp.ac.pa/galeria-jic-2023/",
                },
            ]
        },
        {
            "year": 2022,
            "totalProjects": 38,
            "universities": 4,
            "documents": [
                {
                    "label": "Acta de resultados",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2022/11/acta-jic-2022.pdf",
                },
                {
                    "label": "Listado de ganadores",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2022/11/ganadores-jic-2022.pdf",
                },
            ]
        },
    ]
    
    context = {
        'historical_results': historical_results,
    }
    return render(request, 'resultados/_index.html', context)

def Recursos(request) -> render:
    tab = request.GET.get('tab', 'docs')
    
    documents_by_edition = [
        {
            "year": 2025,
            "docs": [
                {"label": "Lineamientos JIC 2025", "href": "https://iniciacioncientifica.utp.ac.pa/lineamientos-2025/"},
                {"label": "Informe de participacion institucional", "href": "#"},
                {"label": "Folleto JIC 2025", "href": "#"},
            ],
        },
        {
            "year": 2024,
            "docs": [
                {"label": "Lineamientos JIC 2024", "href": "https://iniciacioncientifica.utp.ac.pa/lineamientos-2024/"},
                {"label": "Programa final JIC 2024", "href": "#"},
                {"label": "Preguntas frecuentes 2024", "href": "#"},
                {"label": "Folleto JIC 2024", "href": "#"},
            ],
        },
        {
            "year": 2023,
            "docs": [
                {"label": "Lineamientos JIC 2023", "href": "#"},
                {"label": "Programa final JIC 2023", "href": "#"},
            ],
        },
    ]
    
    boletines = [
        {
            "title": "Boletin JIC 2024 - Momentos destacados",
            "description": "Ganadores, pasantias otorgadas y mejores momentos de la JIC Nacional 2024.",
            "href": "#",
        },
        {
            "title": "Boletin JIC 2023 - Resumen anual",
            "description": "Resumen de la edición 2023 con proyectos ganadores y estadisticas.",
            "href": "#",
        },
        {
            "title": "Boletin JIC 2022 - Innovacion juvenil",
            "description": "Destacados y logros de la edición 2022.",
            "href": "#",
        },
    ]
    
    memorias = [
        {
            "title": "Memorias JIC 2024",
            "description": "Publicaciones completas y documentacion de la edición 2024.",
            "href": "#",
        },
        {
            "title": "Memorias JIC 2023",
            "description": "Compendio de articulos e investigaciones presentadas en 2023.",
            "href": "#",
        },
        {
            "title": "Memorias JIC 2022",
            "description": "Documentacion integral de la edición 2022.",
            "href": "#",
        },
    ]
    
    gallery_images = [
        {"src": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=500&h=500&fit=crop", "alt": "Investigadores en laboratorio", "category": "Investigación"},
        {"src": "https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=500&h=500&fit=crop", "alt": "Presentación de proyecto", "category": "Presentaciones"},
        {"src": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=500&h=500&fit=crop", "alt": "Equipo científico", "category": "Investigación"},
        {"src": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&h=500&fit=crop", "alt": "Conferencia científica", "category": "Eventos"},
        {"src": "https://images.unsplash.com/photo-1516534775068-bb57b6439066?w=500&h=500&fit=crop", "alt": "Investigadores colaborando", "category": "Investigación"},
        {"src": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=500&h=500&fit=crop", "alt": "Presentación en auditorio", "category": "Presentaciones"},
        {"src": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&h=500&fit=crop", "alt": "Evento científico", "category": "Eventos"},
        {"src": "https://images.unsplash.com/photo-1537128191892-8ac93e876401?w=500&h=500&fit=crop", "alt": "Trabajo en equipo", "category": "Investigación"},
    ]
    
    videos = [
        {
            "title": "Video promocional JIC Nacional",
            "thumbnail": "/static/images/hero-jic.jpg",
            "url": "https://www.youtube.com/watch?v=oispNb8t79o",
            "description": "Conoce la JIC Nacional, el evento de investigacion mas importante para jovenes en Panama.",
        },
        {
            "title": "¿Cómo preparar tu proyecto de investigación?",
            "thumbnail": "/static/images/categories-science.jpg",
            "url": "https://www.youtube.com/watch?v=7VAMa-C7wG0",
            "description": "Conoce la JIC Nacional, el evento de investigacion mas importante para jovenes en Panama.",
        },
        {
            "title": "Inducción a la JIC 2024",
            "thumbnail": "/static/images/hero-jic.jpg",
            "url": "https://youtu.be/zxKc3FreHTQ?si=CORhb6r9ZoPpMf9d",
            "description": "Recursos sobre cómo presentar tu proyecto en la JIC.",
        },
    ]
    
    context = {
        'tab': tab,
        'documents_by_edition': documents_by_edition,
        'boletines': boletines,
        'memorias': memorias,
        'gallery_images': gallery_images,
        'gallery_categories': sorted(set(img['category'] for img in gallery_images)),
        'videos': videos,
    }
    return render(request, 'recursos/_index.html', context)

def Selecciones(request) -> render:
    selecciones = [
        {
            "university": "Universidad Tecnológica de Panamá",
            "shortName": "UTP",
            "year": 2025,
            "status": "completada",
            "results": [
                {"category": "Ingeniería", "selected": 8, "total": 24},
                {"category": "Ciencias de la Salud", "selected": 4, "total": 12},
                {"category": "Ciencias Naturales y Exactas", "selected": 5, "total": 18},
                {"category": "Ciencias Sociales y Humanísticas", "selected": 3, "total": 10},
            ],
            "documents": [
                {"label": "Acta de resultados UTP 2025", "href": "#"},
                {"label": "Lista de proyectos seleccionados", "href": "#"},
            ],
        },
        {
            "university": "Universidad de Panamá",
            "shortName": "UP",
            "year": 2025,
            "status": "completada",
            "results": [
                {"category": "Ingeniería", "selected": 5, "total": 15},
                {"category": "Ciencias de la Salud", "selected": 6, "total": 20},
                {"category": "Ciencias Naturales y Exactas", "selected": 4, "total": 14},
                {"category": "Ciencias Sociales y Humanísticas", "selected": 5, "total": 16},
            ],
            "documents": [
                {"label": "Acta de resultados UP 2025", "href": "#"},
            ],
        },
        {
            "university": "Universidad Santa María La Antigua",
            "shortName": "USMA",
            "year": 2025,
            "status": "en_proceso",
            "results": [],
            "documents": [],
        },
        {
            "university": "Universidad Autónoma de Chiriquí",
            "shortName": "UNACHI",
            "year": 2025,
            "status": "pendiente",
            "results": [],
            "documents": [],
        },
        {
            "university": "Universidad Latina de Panamá",
            "shortName": "ULAT",
            "year": 2025,
            "status": "pendiente",
            "results": [],
            "documents": [],
        },
    ]
    return render(request, 'resultados/selecciones/_index.html', {"selecciones": selecciones})

def Contacto(request) -> render:
    
    return render(request, 'contacto/_index.html')