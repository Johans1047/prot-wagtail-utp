from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone
from datetime import date, datetime
import re
from urllib.parse import urlencode
from .data_types import *
from .data_fallback import *
from ..utils import get_recursos_gallery, get_recursos_videos, get_processed_projects
from ..models import *
from wagtail.images.models import Image
from wagtail.documents import get_document_model

Document = get_document_model()


def _to_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return timezone.localtime(value)

    if isinstance(value, date):
        naive_dt = datetime.combine(value, datetime.min.time())
        return timezone.make_aware(naive_dt, timezone.get_current_timezone())

    try:
        year_int = int(value)
        if 1900 <= year_int <= 3000:
            return timezone.make_aware(datetime(year_int, 1, 1), timezone.get_current_timezone())
    except (TypeError, ValueError):
        pass

    return None


def _get_field_value(item, field_name):
    if isinstance(item, dict):
        return item.get(field_name)
    return getattr(item, field_name, None)


def _iter_items(dataset):
    if dataset is None:
        return []
    if hasattr(dataset, "object_list"):
        return list(dataset.object_list)
    if isinstance(dataset, dict):
        return [dataset]
    if isinstance(dataset, (str, bytes)):
        return []
    try:
        return list(dataset)
    except TypeError:
        return [dataset]


def _get_last_data_update(*datasets, include_year=True):
    latest = None
    candidate_fields = ["updated_at", "created_at", "event_date", "publication_date"]
    if include_year:
        candidate_fields.append("year")

    for dataset in datasets:
        for item in _iter_items(dataset):
            for field in candidate_fields:
                candidate = _to_datetime(_get_field_value(item, field))
                if candidate is not None and (latest is None or candidate > latest):
                    latest = candidate

    return latest


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
            important_date.objects.filter(is_active=True, is_primary=True).order_by("sort_order", "event_date")
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
            .filter(is_active=True)
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

    show_national_coordinators = True
    try:
        nat_coords_section = national_coordinators_section.get_singleton()
        show_national_coordinators = bool(nat_coords_section.is_active)
    except (OperationalError, ProgrammingError):
        show_national_coordinators = True

    if show_national_coordinators:
        try:
            coordinadores_nacionales = list(coordinator.objects.filter(is_active=True).order_by("sort_order"))
        except (OperationalError, ProgrammingError):
            coordinadores_nacionales = []

        if not coordinadores_nacionales:
            coordinadores_nacionales = coordinators_fallback()
    else:
        coordinadores_nacionales = []

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
        'show_national_coordinators': show_national_coordinators,
        'coordinadores_nacionales': coordinadores_nacionales,
        'comite_organizador': comite_organizador,
        'last_data_update': _get_last_data_update(
            background_items,
            jic_categories,
            awards,
            coordinadores_nacionales,
            comite_organizador,
            include_year=False,
        ),
    }
    if not context['last_data_update'] or context['last_data_update'] > timezone.now():
        context['last_data_update'] = timezone.now()
    return render(request, 'jic/_index.html', context)

def JicCoordinadores(request) -> render:
    show_national_coordinators = True
    try:
        nat_coords_section = national_coordinators_section.get_singleton()
        show_national_coordinators = bool(nat_coords_section.is_active)
    except (OperationalError, ProgrammingError):
        show_national_coordinators = True

    if show_national_coordinators:
        try:
            coordinadores_nacionales = list(coordinator.objects.filter(is_active=True).order_by("sort_order"))
        except (OperationalError, ProgrammingError):
            coordinadores_nacionales = []

        if not coordinadores_nacionales:
            coordinadores_nacionales = coordinators_fallback()
    else:
        coordinadores_nacionales = []

    try:
        comite_organizador = list(organizer_committee_member.objects.filter(is_active=True).order_by("sort_order"))
    except (OperationalError, ProgrammingError):
        comite_organizador = []

    if not comite_organizador:
        comite_organizador = organizer_committee_members_fallback()

    last_data_update = _get_last_data_update(coordinadores_nacionales, comite_organizador, include_year=False)
    if not last_data_update or last_data_update > timezone.now():
        last_data_update = timezone.now()

    context = {
        'show_national_coordinators': show_national_coordinators,
        'coordinadores_nacionales': coordinadores_nacionales,
        'comite_organizador': comite_organizador,
        'last_data_update': last_data_update,
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
    loaded_documents = []
    for role in role_definitions:
        try:
            documents_qs = (
                Document.objects.filter(tags__name__in=role["tags"])
                .filter(is_active=True)
                .distinct()
                .order_by("title")
            )
            loaded_documents.extend(list(documents_qs))
            resources = [{"label": doc.title, "href": doc.url} for doc in documents_qs]
        except (OperationalError, ProgrammingError):
            resources = []

        resource_categories.append(
            {
                "title": role["title"],
                "description": role["description"],
                "accent": role["accent"],
                "resources": resources,
            }
        )
    
    last_data_update = _get_last_data_update(important_dates, loaded_documents) or timezone.now()
    if last_data_update > timezone.now():
        last_data_update = timezone.now()

    context = {
        'important_dates': important_dates,
        'resource_categories': resource_categories,
        'last_data_update': last_data_update,
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
    universities_index = {
        p["university"]: (p.get("university_display") or p["university"])
        for p in all_projects
        if p.get("university")
    }
    for uni in sorted(universities_index):
        universities_options.append({"value": uni, "label": universities_index[uni]})

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
        'last_data_update': _get_last_data_update(filtered, schedule_dates),
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
         
    return render(
        request,
        'proyectos/detail.html',
        {
            'project': project,
            'last_data_update': _get_last_data_update(project),
        },
    )

def Resultados(request) -> render:
    from ..models import selection_national

    def _is_results_doc(doc_like) -> bool:
        label = (doc_like.get("label") or doc_like.get("title") or "").lower()
        doc_type = (doc_like.get("type") or "").lower()
        href = doc_like.get("href")
        if not href:
            return False
        return any(token in label for token in ["ganador", "acta"]) or any(
            token in doc_type for token in ["pdf", "acta"]
        )

    current_year = timezone.now().year

    # 1) Resultados nacionales desde BD
    national_qs = (
        selection_national.objects.filter(is_active=True)
        .prefetch_related("results", "documents")
        .order_by("-year")
    )
    historical_results_db = [sn.to_dict() for sn in national_qs]

    # 2) Fallback para anios historicos sin registro en BD
    historical_results_fallback = [
        {"year": 2024, "totalProjects": 47, "universities": 5},
        {"year": 2023, "totalProjects": 42, "universities": 5},
        {"year": 2022, "totalProjects": 38, "universities": 4},
    ]

    # 3) Documentos por anio (misma fuente de Recursos), filtrando solo ganadores/acta
    excluded_tags = [
        "manual",
        "boletin",
        "memoria",
        "plantilla de articulo",
        "plantilla_articulo",
        "manuales",
        "boletines",
        "memorias",
        "plantillas de articulos",
    ]
    docs_qs = Document.objects.filter(is_active=True).exclude(tags__name__in=excluded_tags)
    docs_qs = docs_qs.exclude(title__icontains="manual")
    docs_qs = docs_qs.exclude(title__icontains="boletin")
    docs_qs = docs_qs.exclude(title__icontains="memoria")
    docs_qs = docs_qs.exclude(title__icontains="plantilla")
    docs_qs = docs_qs.distinct()

    docs_by_year = {}
    for doc in docs_qs:
        tag_names = {tag.strip().lower() for tag in doc.tags.names()}
        candidate_doc = {
            "label": doc.title,
            "type": "PDF",
            "href": doc.url,
            "tags": tag_names,
        }
        if not _is_results_doc(candidate_doc):
            continue

        years_found = set()
        for tag in doc.tags.names():
            if tag.isdigit() and len(tag) == 4 and tag.startswith("20"):
                try:
                    years_found.add(int(tag))
                except ValueError:
                    continue

        if not years_found:
            title_match = re.search(r"(20\d{2})", doc.title or "")
            if title_match:
                years_found.add(int(title_match.group(1)))

        if not years_found and getattr(doc, "created_at", None):
            years_found.add(doc.created_at.year)

        for year in years_found:
            docs_by_year.setdefault(year, [])
            docs_by_year[year].append(candidate_doc)

    # 4) Unificar resultados por anio (BD tiene prioridad sobre fallback)
    results_by_year = {
        item["year"]: dict(item)
        for item in historical_results_fallback
        if item.get("year")
    }
    for item in historical_results_db:
        year = item.get("year")
        if year:
            results_by_year[year] = dict(item)

    # Incluir anos que existen en Documentos aunque no tengan registro en selection_national.
    for year in docs_by_year.keys():
        if year and year not in results_by_year:
            results_by_year[year] = {
                "year": year,
                "status": "finalizada",
                "totalProjects": 0,
                "universities": 0,
                "results": [],
                "documents": [],
            }

    # 5) Sincronizar documentos: primero los de Recursos, si no hay usar los del registro
    for year, result_item in results_by_year.items():
        resource_docs = docs_by_year.get(year, [])
        db_docs = [d for d in (result_item.get("documents") or []) if _is_results_doc(d)]
        chosen_docs = resource_docs if resource_docs else db_docs

        if year == current_year:
            current_year_tag = str(current_year)
            chosen_docs = [
                d
                for d in chosen_docs
                if current_year_tag in {str(t).strip().lower() for t in d.get("tags", [])}
                and {"ganador", "ganadores"}.intersection(
                    {str(t).strip().lower() for t in d.get("tags", [])}
                )
            ]

        seen_hrefs = set()
        dedup_docs = []
        for doc_item in chosen_docs:
            href = doc_item.get("href")
            if not href or href in seen_hrefs:
                continue
            seen_hrefs.add(href)
            safe_doc = {k: v for k, v in doc_item.items() if k != "tags"}
            dedup_docs.append(safe_doc)

        result_item["documents"] = dedup_docs

    normalized_results = sorted(results_by_year.values(), key=lambda x: x.get("year", 0), reverse=True)
    current_result = next((r for r in normalized_results if r.get("year") == current_year), None)
    historical_results = [r for r in normalized_results if r.get("year") != current_year]

    paginator_historical = Paginator(historical_results, 3)
    page_obj = paginator_historical.get_page(request.GET.get("page", 1))

    last_data_update = _get_last_data_update(national_qs, docs_qs, include_year=False)
    if not last_data_update or last_data_update > timezone.now():
        last_data_update = timezone.now()

    context = {
        "current_year": current_year,
        "current_result": current_result,
        "historical_results": list(page_obj.object_list),
        "page_obj": page_obj,
        "page_query": "",
        "last_data_update": last_data_update,
    }
    return render(request, "resultados/_index.html", context)

def Recursos(request) -> render:
    tab = request.GET.get('tab', 'docs')
    
    # 1. Documents By Edition
    # documents_by_edition_list = documents_by_edition_fallback() # Removed fallback
    
    excluded_tags = ['manual', 'boletin', 'memoria', 'plantilla de articulo', 'plantilla_articulo', 'manuales', 'boletines', 'memorias', 'plantillas de articulos']
    
    all_docs = Document.objects.filter(is_active=True).exclude(tags__name__in=excluded_tags)
    
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

        if not years_found:
            title_match = re.search(r"(20\d{2})", doc.title or "")
            if title_match:
                years_found.add(int(title_match.group(1)))

        if not years_found and getattr(doc, "created_at", None):
            years_found.add(doc.created_at.year)

        if not years_found:
            years_found.add(0)
        
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
        boletines_list = Document.objects.filter(is_active=True, tags__name='boletin').order_by('-created_at')
        paginator_b = Paginator(boletines_list, 6)
        boletines = paginator_b.get_page(request.GET.get('page', 1))
    else:
        boletines = []

    if tab == 'memorias':
        memorias_list = Document.objects.filter(is_active=True, tags__name='memoria').order_by('-created_at')
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
        'last_data_update': _get_last_data_update(all_docs, boletines, memorias),
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
    return render(
        request,
        "resultados/selecciones/_index.html",
        {
            "selecciones": selecciones,
            "last_data_update": _get_last_data_update(active),
        },
    )

def Contacto(request) -> render:
    
    return render(request, 'contacto/_index.html')