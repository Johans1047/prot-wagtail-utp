from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from datetime import date
from urllib.parse import urlencode
from .data_types import *
from .data_fallback import *
from ..utils import get_recursos_gallery, get_recursos_videos, get_processed_projects
from ..models import *
from wagtail.images.models import Image
from wagtail.documents.models import Document


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

    lineamientos_docs = []
    try:
        lineamientos_docs = list(
            Document.objects.filter(
                Q(tags__name__icontains="lineamiento")
                | Q(title__icontains="lineamiento")
            )
            .distinct()
            .order_by("-created_at")
        )
    except (OperationalError, ProgrammingError):
        lineamientos_docs = []
    
    all_projects = get_processed_projects()
    winner_projects = [p for p in all_projects if p.get("winner", 0) > 0]

    today = date.today()
    # Before November, show previous year's winners; from November onward, prefer current year.
    target_winners_year = today.year - 1 if today.month < 11 else today.year
    latest_winners = [p for p in winner_projects if p.get("year", 0) == target_winners_year]

    if latest_winners:
        latest_winners_year = target_winners_year
    else:
        latest_winners_year = max((p.get("year", 0) for p in winner_projects), default=0)
        latest_winners = [p for p in winner_projects if p.get("year", 0) == latest_winners_year]

    winners_by_place = []
    for place, label in [(1, "Primer Lugar"), (2, "Segundo Lugar"), (3, "Tercer Lugar")]:
        winners_in_place = [
            {
                "title": p["title"],
                "university": p.get("university_display") or p.get("university") or "-",
                "category": p.get("category") or "Sin categoría",
                "authors": p.get("advisor") or "Asesor no registrado",
            }
            for p in latest_winners
            if p.get("winner") == place
        ]

        winners_by_place.append(
            {
                "place": place,
                "place_label": label,
                "winners": winners_in_place,
            }
        )
    
    winners_filters = urlencode({
        'tab': 'winners',
        'year': 'all',
        'category': 'all',
        'university': 'all'
    })

    context = {
        'title_section': ts,
        'introductions': _event_intro,
        'important_dates': important_dates,
        'faqs': faqs,
        'lineamientos_docs': lineamientos_docs,
        'lineamiento_destacado': lineamientos_docs[0] if lineamientos_docs else None,
        'winners_by_place': winners_by_place,
        'latest_winners_year': latest_winners_year,
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

    role_definitions = [
        {
            "title": "Estudiantes",
            "description": "Informacion para participantes",
            "accent": "bg-primary/90 text-primary-foreground",
            "tags": ["estudiante", "estudiantes"],
        },
        {
            "title": "Asesores",
            "description": "Informacion para asesores",
            "accent": "bg-secondary-foreground/65 text-primary-foreground",
            "tags": ["asesor", "asesores"],
        },
        {
            "title": "Evaluadores",
            "description": "Informacion para evaluadores",
            "accent": "bg-amber-400 text-secondary-foreground",
            "tags": ["evaluador", "evaluadores"],
        },
        {
            "title": "Coordinadores",
            "description": "Informacion para coordinadores institucionales",
            "accent": "bg-secondary-foreground/65 text-primary-foreground",
            "tags": ["coordinador", "coordinadores"],
        },
    ]

    resource_categories = []
    for role in role_definitions:
        documents_qs = (
            Document.objects.filter(tags__name__in=role["tags"])
            .distinct()
            .order_by("title")
        )
        resources = [{"label": doc.title, "href": doc.url} for doc in documents_qs]

        resource_categories.append(
            {
                "title": role["title"],
                "description": role["description"],
                "accent": role["accent"],
                "resources": resources,
            }
        )
    
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
        filtered = [p for p in filtered if p.get('winner', 0) > 0]

    if search:
        search_lower = search.lower()
        filtered = [
            p for p in filtered
            if search_lower in p['title'].lower()
            or search_lower in p['university'].lower()
            or search_lower in (p.get('university_short_name') or '').lower()
            or search_lower in (p.get('advisor') or '').lower()
            or search_lower in (p.get('category') or '').lower()
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

    years = sorted(set(p['year'] for p in all_projects if p.get('year')), reverse=True)

    categories_options = [
        {"value": "all", "label": "Todas las categorías"},
    ]
    for category in sorted(set(p['category'] for p in all_projects if p.get('category'))):
        categories_options.append({"value": category, "label": category})

    universities_options = [
        {"value": "all", "label": "Todas las universidades"},
    ]
    for uni in sorted(set(p['university'] for p in all_projects if p.get('university'))):
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


def Noticias(request) -> render:
    noticias_qs = BlogPage.objects.live().public().order_by("-publication_date", "-first_published_at")
    paginator = Paginator(noticias_qs, 9)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    context = {
        "page_obj": page_obj,
        "noticias": page_obj.object_list,
    }
    return render(request, "utilidades/noticias/index.html", context)


def NoticiaDetalle(request, slug: str) -> render:
    noticia = get_object_or_404(BlogPage.objects.live().public(), slug=slug)
    relacionadas = (
        BlogPage.objects.live()
        .public()
        .exclude(id=noticia.id)
        .order_by("-publication_date", "-first_published_at")[:3]
    )

    context = {
        "page": noticia,
        "relacionadas": relacionadas,
    }
    return render(request, "utilidades/noticias/detail.html", context)

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
    
    # 1. Documents By Edition
    # documents_by_edition_list = documents_by_edition_fallback() # Removed fallback
    
    excluded_tags = ['manual', 'boletin', 'memoria', 'plantilla de articulo', 'plantilla_articulo', 'manuales', 'boletines', 'memorias', 'plantillas de articulos']
    
    all_docs = Document.objects.exclude(tags__name__in=excluded_tags)
    
    # Also exclude by title for documents that might be missing tags
    all_docs = all_docs.exclude(title__icontains='manual')
    all_docs = all_docs.exclude(title__icontains='boletin')
    all_docs = all_docs.exclude(title__icontains='memoria')
    all_docs = all_docs.exclude(title__icontains='plantilla')
    
    all_docs = all_docs.distinct()
    
    docs_by_year = {}
    
    for doc in all_docs:
        # Find year tag
        years_found = set()
        for tag in doc.tags.names():
            # Check for year (4 digits, starts with 20)
            if tag.isdigit() and len(tag) == 4 and tag.startswith('20'):
                try:
                    years_found.add(int(tag))
                except ValueError:
                    continue
        
        if years_found:
            for year in years_found:
                if year not in docs_by_year:
                    docs_by_year[year] = []
                
                docs_by_year[year].append({
                    'label': doc.title,
                    'href': doc.url
                })
    
    documents_by_edition_list = [{"year": year, "docs": docs} for year, docs in docs_by_year.items()]
    documents_by_edition_list.sort(key=lambda x: x['year'], reverse=True)
    
    paginator_docs = Paginator(documents_by_edition_list, 5) # 5 editions per page
    documents_by_edition = paginator_docs.get_page(request.GET.get('page', 1))

    # 2. Bulletins and Memories
    if tab == 'boletines':
        boletines_list = Document.objects.filter(tags__name='boletin').order_by('-created_at')
        paginator_b = Paginator(boletines_list, 6)
        boletines = paginator_b.get_page(request.GET.get('page', 1))
    else:
        boletines = []

    if tab == 'memorias':
        memorias_list = Document.objects.filter(tags__name='memoria').order_by('-created_at')
        paginator_m = Paginator(memorias_list, 6)
        memorias = paginator_m.get_page(request.GET.get('page', 1))
    else:
        memorias = []
    
    # 3. Gallery
    current_img_cat = request.GET.get('img_cat', 'all')
    gallery_images, gallery_categories, page_obj_gall = get_recursos_gallery(
        request, tab, current_img_cat, gallery_images_fallback()
    )
    
    # 4. Videos
    videos, page_obj_vid = get_recursos_videos(
        request, tab, videos_fallback()
    )

    page_obj = None
    if tab == 'videos':
        page_obj = page_obj_vid
    elif tab == 'galeria':
        page_obj = page_obj_gall

    query_params = request.GET.copy()
    query_params.pop('page', None)
    page_query = query_params.urlencode()
    
    context = {
        'tab': tab,
        'documents_by_edition': documents_by_edition,
        'boletines': boletines,
        'memorias': memorias,
        'gallery_images': gallery_images,
        'categories': gallery_categories,
        'current_img_cat': current_img_cat,
        'videos': videos,
        'page_obj': page_obj,
        'page_query': f'tab=galeria&img_cat={current_img_cat}' if tab == 'galeria' else '',
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