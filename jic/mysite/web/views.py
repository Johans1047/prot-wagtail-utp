from django.shortcuts import render
from django.db.utils import OperationalError, ProgrammingError
from .viewsdata_types import *
from .viewsdata_fallback import *
from .models import *

def Inicio(request):
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
    
    context = {
        'important_dates': important_dates,
        'faqs': faqs,
    }
    
    return render(request, 'inicio/_index.html', context)

def Jic(request):
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

    context = {
        'background_items': background_items,
        'jic_categories': jic_categories,
        'awards': awards,
        'organizations': organizations,
        'sponsors': sponsors,
    }
    return render(request, 'jic/_index.html', context)

def Participar(request):
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

def Proyectos(request):
    # Datos de ejemplo de proyectos
    all_projects = [
        {
            "year": 2024,
            "title": "Sistema de monitoreo ambiental con IoT",
            "university": "UTP",
            "category": "Ingeniería",
            "contact": "proyecto1@utp.ac.pa",
            "winner": True,
        },
        {
            "year": 2024,
            "title": "Análisis de biomarcadores en diabetes",
            "university": "UP",
            "category": "Ciencias de la Salud",
            "contact": "proyecto2@up.ac.pa",
            "winner": True,
        },
        {
            "year": 2023,
            "title": "Modelado matemático de ecosistemas",
            "university": "UTP",
            "category": "Ciencias Naturales",
            "contact": "proyecto3@utp.ac.pa",
            "winner": False,
        },
        {
            "year": 2023,
            "title": "Plataforma de educación digital",
            "university": "UNIANDES",
            "category": "Tecnología",
            "contact": "proyecto4@uniandes.ac.pa",
            "winner": False,
        },
        {
            "year": 2022,
            "title": "Estudio de aguas residuales",
            "university": "UTP",
            "category": "Ingeniería Ambiental",
            "contact": "proyecto5@utp.ac.pa",
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

def Resultados(request):
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

def Recursos(request):
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

def Contacto(request):
    
    return render(request, 'contacto/_index.html')