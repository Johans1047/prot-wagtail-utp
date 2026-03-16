from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.utils import OperationalError, ProgrammingError
from urllib.parse import urlencode
from .data_types import *
from .data_fallback import *
from ..models import *
from wagtail.images.models import Image
from ..utils import get_processed_projects


def Inicio(request) -> render:
    try:
        ts = title_section.objects.filter(is_active=True).order_by('sort_order').first()
    except (OperationalError, ProgrammingError):
        ts = None
        
    if not ts:
        ts = title_section_fallback()

    try:
        _event_intro = list(
            event_intro.objects.filter(is_active=True)
        )
    except (OperationalError, ProgrammingError):
        _event_intro = []

    if not _event_intro:
        _event_intro = [event_intro_fallback()]
        
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
    
    winners_filters = urlencode({
        'tab': ['all', 'winners'],
        'year': 'all',
        'category': 'all',
        'university': 'all'
    }, doseq=True)

    context = {
        'title_section': ts,
        'introductions': _event_intro,
        'important_dates': important_dates,
        'faqs': faqs,
        'winners_by_place': winners_by_place,
        'winners_filters': winners_filters,
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

    try:
        coordinadores_nacionales = list(coordinator.objects.filter(is_active=True).order_by("sort_order"))
    except (OperationalError, ProgrammingError):
        coordinadores_nacionales = []
        
    if not coordinadores_nacionales:
        coordinadores_nacionales = coordinators_fallback()

    try:
        comite_organizador = list(organizer_committee_member.objects.filter(is_active=True).order_by("sort_order"))
    except (OperationalError, ProgrammingError):
        comite_organizador = []
        
    if not comite_organizador:
        comite_organizador = organizer_committee_members_fallback()

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

def JicCoordinadores(request) -> render:
    try:
        coordinadores_nacionales = list(coordinator.objects.filter(is_active=True).order_by("sort_order"))
    except (OperationalError, ProgrammingError):
        coordinadores_nacionales = []

    if not coordinadores_nacionales:
        coordinadores_nacionales = coordinators_fallback()

    try:
        comite_organizador = list(organizer_committee_member.objects.filter(is_active=True).order_by("sort_order"))
    except (OperationalError, ProgrammingError):
        comite_organizador = []

    if not comite_organizador:
        comite_organizador = organizer_committee_members_fallback()

    context = {
        'coordinadores_nacionales': coordinadores_nacionales,
        'comite_organizador': comite_organizador,
    }
    return render(request, 'jic/coordinadores/_index.html', context)

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
        {
            "title": "Coordinadores",
            "description": "Informacion para coordinadores institucionales",
            "accent": "bg-secondary-foreground/65 text-primary-foreground",
            "resources": [
                {"label": "Guia de coordinadores", "href": "#"},
                {"label": "Cronograma de actividades", "href": "#"},
                {"label": "Plantillas administrativas", "href": "#"},
                {"label": "Contacto de soporte", "href": "mailto:jornada.cientifica@utp.ac.pa"},
            ]
        },
    ]
    
    context = {
        'important_dates': important_dates,
        'resource_categories': resource_categories,
    }
    return render(request, 'participar/_index..html', context)

def Proyectos(request) -> render:
    all_projects = get_processed_projects()

    tab = request.GET.get('tab', 'all')
    search = request.GET.get('search', '').strip()
    year_filter = request.GET.get('year', 'all')
    category_filter = request.GET.get('category', 'all')
    university_filter = request.GET.get('university', 'all')

    filtered = all_projects

    if tab == 'winners':
        filtered = [p for p in filtered if p['winner']]

    if search:
        search_lower = search.lower()
        filtered = [
            p for p in filtered
            if search_lower in p['title'].lower() or search_lower in p['university'].lower()
        ]

    if year_filter != 'all':
        try:
            year_filter_int = int(year_filter)
            filtered = [p for p in filtered if p['year'] == year_filter_int]
        except ValueError:
            pass

    if category_filter != 'all':
        filtered = [p for p in filtered if p['category'] == category_filter]

    if university_filter != 'all':
        filtered = [p for p in filtered if p['university'] == university_filter]

    years = sorted(set(p['year'] for p in all_projects), reverse=True)

    categories_options = [
        {"value": "all", "label": "Todas las categorías"},
    ]
    for category in sorted(set(p['category'] for p in all_projects)):
        categories_options.append({"value": category, "label": category})

    universities_options = [
        {"value": "all", "label": "Todas las universidades"},
    ]
    for uni in sorted(set(p['university'] for p in all_projects)):
        universities_options.append({"value": uni, "label": uni})

    paginator = Paginator(filtered, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    query_params = request.GET.copy()
    query_params.pop('page', None)
    page_query = query_params.urlencode()

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
        'page_obj': page_obj,
        'tab': tab,
        'search': search,
        'year_filter': year_filter,
        'category_filter': category_filter,
        'university_filter': university_filter,
        'years': years,
        'categories_options': categories_options,
        'universities_options': universities_options,
        'page_query': page_query,
        'important_dates': schedule_dates,
    }
    return render(request, 'proyectos/_index.html', context)

def ProyectoDetalle(request, project_id: int) -> render:
    projects = get_processed_projects()
    project = next((p for p in projects if p["id"] == int(project_id)), None)
    
    if not project:
         # Debug info to understand why it's not found
         available_ids = [p["id"] for p in projects]
         raise Http404(f"Proyecto no encontrado. Buscando ID: {project_id} (tipo {type(project_id)}). IDs disponibles: {available_ids}")
         
    return render(request, 'proyectos/detail.html', {'project': project})

def Resultados(request) -> render:
    from ..models import selection_national

    # Obtain results from the database, prefetching related documents and results
    # Only active national selections that have year <= current year or whatever logic
    qs = selection_national.objects.filter(is_active=True).prefetch_related("results", "documents").order_by("-year")

    historical_results_db = [sn.to_dict() for sn in qs]

    # Datos históricos de ediciones anteriores (Fallback)
    historical_results_fallback = [
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
        'historical_results': historical_results_db if historical_results_db else historical_results_fallback,
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
    
    
    try:
        # Try to get the ordered gallery snippet first
        gallery = Gallery.objects.first()
        gallery_images = []
        
        if gallery and gallery.gallery_images.exists():
            for item in gallery.gallery_images.all():
                if item.image:
                    gallery_images.append({
                        "src": item.image.file.url,
                        "alt": item.image.title,
                        "category": item.caption if item.caption else "General",
                    })
        else:
            # Fallback to fetching latest images if no gallery snippet exists or it's empty
            db_images = Image.objects.all().order_by('-created_at').prefetch_related('tags')#[:24]
            for img in db_images:
                # Use the first tag as category, default to "General"
                category = "General"
                tags = img.tags.all()
                if tags:
                    category = tags[0].name.title()
                    
                gallery_images.append({
                    "src": img.file.url,
                    "alt": img.title,
                    "category": category,
                })
    except (OperationalError, ProgrammingError, Exception):
        # Fallback if DB not ready or empty
        gallery_images = []
    
    if not gallery_images:
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
    
    gallery_categories = sorted(set(img['category'] for img in gallery_images))
    
    if tab == 'galeria':
        paginator = Paginator(gallery_images, 24)
        page_obj = paginator.get_page(request.GET.get('page', 1))
        gallery_images = page_obj
    
    try:
        db_videos = video.objects.filter(is_active=True).order_by("sort_order", "-created_at")
        videos = []
        for v in db_videos:
            thumb_url = v.thumbnail.url if v.thumbnail else "/static/images/hero-jic.jpg"
            video_url = v.video_file.url if v.video_file else "#"
            videos.append({
                "title": v.title,
                "thumbnail": thumb_url,
                "url": video_url,
                "description": v.description,
            })
    except (OperationalError, ProgrammingError, Exception):
        videos = []
        
    if not videos:
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
                "title": "Guía de Investigación Científica",
                "thumbnail": "/static/images/hero-jic.jpg",
                "url": "https://youtu.be/bP2KW-TbApc?si=nW7pLA7U0spGEPsH",
                "description": "Tutorial completo sobre metodología y pasos para realizar investigación científica.",
            },
            {
                "title": "Inducción a la JIC 2024",
                "thumbnail": "/static/images/hero-jic.jpg",
                "url": "https://youtu.be/zxKc3FreHTQ?si=CORhb6r9ZoPpMf9d",
                "description": "Recursos sobre cómo presentar tu proyecto en la JIC.",
            },
            {
                "title": "Prueba de Video Interno",
                "thumbnail": "/static/images/hero-jic.jpg",
                "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "description": "Este es un video de prueba (mp4) para verificar el reproductor interno en el modal.",
            },
        ]

    page_obj = None # Default value
    
    if tab == 'videos':
        paginator = Paginator(videos, 12)
        page_obj = paginator.get_page(request.GET.get('page', 1))
        videos = page_obj
    elif tab == 'galeria':
        # Already paginated above, grab the page_obj from gallery_images
        page_obj = gallery_images

    query_params = request.GET.copy()
    query_params.pop('page', None)
    page_query = query_params.urlencode()
    
    context = {
        'tab': tab,
        'documents_by_edition': documents_by_edition,
        'boletines': boletines,
        'memorias': memorias,
        'gallery_images': gallery_images,
        'gallery_categories': gallery_categories,
        'videos': videos,
        'page_obj': page_obj,
        'page_query': page_query, 
    }
    return render(request, 'recursos/_index.html', context)

def Selecciones(request) -> render:
    try:
        all_selecciones = list(
            selection_institutional.objects.prefetch_related("results", "documents").order_by("sort_order", "university")
        )
    except (OperationalError, ProgrammingError):
        # DB error — redirect with message
        messages.warning(
            request,
            "No se pudo cargar la información de selecciones institucionales. Por favor, intenta más tarde.",
        )
        return redirect("Resultados")

    if not all_selecciones:
        # No records exist — redirect with message
        messages.info(
            request,
            "Las selecciones institucionales no están disponibles en este momento.",
        )
        return redirect("Resultados")

    # Filter to only active records
    active = [s for s in all_selecciones if s.is_active]
    if not active:
        # All records exist but all are inactive — redirect with message
        messages.info(
            request,
            "Las selecciones institucionales no están disponibles en este momento.",
        )
        return redirect("Resultados")

    selecciones = [s.to_dict() for s in active]
    return render(request, "resultados/selecciones/_index.html", {"selecciones": selecciones})

def Contacto(request) -> render:
    
    return render(request, 'contacto/_index.html')