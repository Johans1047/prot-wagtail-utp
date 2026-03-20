import json
import logging
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from wagtail.admin.menu import MenuItem
from django.core.paginator import Paginator
from django.db.utils import OperationalError, ProgrammingError
from wagtail.images.models import Image


logger = logging.getLogger(__name__)


# In-process cache to avoid repeated slow API timeouts on every request.
_PROJECTS_CACHE: dict[str, object] = {
    "data": None,
    "expires_at": 0.0,
    "last_error_at": 0.0,
}


class WagtailDocWrapper:
    def __init__(self, doc):
        self.title = doc.title
        self.description = ""
        self.year = ""
        self.url = doc.url
        self.document_file = type('obj', (object,), {'url': doc.url})
        self.is_wagtail_doc = True
        
        tags = [t.lower() for t in doc.tags.names()]
        if 'boletin' in tags or 'boletines' in tags:
            self.doc_type = 'boletines'
        elif 'memoria' in tags or 'memorias' in tags:
            self.doc_type = 'memorias'
        else:
            self.doc_type = 'otros'
    
    def get_doc_type_display(self):
        return "Documento PDF"
                

class LazyMenuItem(MenuItem):
    def __init__(self, label, url_name, **kwargs):
        self._url_name = url_name
        super().__init__(label, "#", **kwargs)

    @property
    def url(self):
        try:
            return reverse(self._url_name)
        except Exception:
            return "#"

    @url.setter
    def url(self, value):
        pass
    

def _get_mock_projects_data() -> dict:
    return json.loads(
        """
        {
                    "total": 6,
                    "ganadores_historicos": [
            {
                            "id": 1,
                            "titulo": "Sistema de monitoreo ambiental con IoT para la detección temprana de contaminantes",
                            "ano": "2024",
                            "universidad": "Universidad Tecnológica de Panamá",
                            "siglas": "UTP",
                            "resumen": "Desarrollo de una red de sensores IoT para monitoreo de calidad del aire y alertas tempranas en zonas urbanas.",
                            "categoria": "Ingeniería",
                            "premio": "Primer Lugar",
                            "asesor": "Juan Pérez",
                            "email": "juan.perez@utp.ac.pa",
                            "institucion": "Universidad Tecnológica de Panamá",
                            "activo": 1
            },
            {
                            "id": 2,
                            "titulo": "Análisis de biomarcadores en pacientes con diabetes tipo 2 en población panameña",
                            "ano": "2024",
                            "universidad": "Universidad de Panamá",
                            "siglas": "UP",
                            "resumen": "Evaluación clínica de biomarcadores asociados a progresión de diabetes tipo 2 en cohortes universitarias.",
                            "categoria": "Ciencias de la Salud",
                            "premio": "Primer Lugar",
                            "asesor": "María García",
                            "email": "maria.garcia@up.ac.pa",
                            "institucion": "Universidad de Panamá",
                            "activo": 1
            },
            {
                            "id": 3,
                            "titulo": "Modelado matemático de ecosistemas costeros del Golfo de Panamá",
                            "ano": "2024",
                            "universidad": "Universidad Tecnológica de Panamá",
                            "siglas": "UTP",
                            "resumen": "Se propone un modelo de dinámica de poblaciones para analizar resiliencia ecológica en ecosistemas costeros.",
                            "categoria": "Ciencias Naturales y Exactas",
                            "premio": "Segundo Lugar",
                            "asesor": "Ana López",
                            "email": "ana.lopez@utp.ac.pa",
                            "institucion": "Universidad Tecnológica de Panamá",
                            "activo": 1
            },
            {
                            "id": 4,
                            "titulo": "Impacto socioeconómico de la migración en comunidades rurales de Darién",
                            "ano": "2024",
                            "universidad": "Universidad Latina de Panamá",
                            "siglas": "ULAT",
                            "resumen": "Estudio mixto sobre movilidad humana, empleo y acceso a servicios en comunidades de alta vulnerabilidad.",
                            "categoria": "Ciencias Sociales y Humanísticas",
                            "premio": "Segundo Lugar",
                            "asesor": "Roberto Castillo",
                            "email": "roberto.castillo@ulatina.edu.pa",
                            "institucion": "Universidad Latina de Panamá",
                            "activo": 1
            },
            {
                            "id": 5,
                            "titulo": "Desarrollo de materiales biodegradables a partir de residuos agrícolas",
                            "ano": "2023",
                            "universidad": "Universidad Católica Santa María la Antigua",
                            "siglas": "USMA",
                            "resumen": "Investigación de compuestos biodegradables para empaque sostenible usando subproductos agroindustriales.",
                            "categoria": "Ingeniería",
                            "premio": "Tercer Lugar",
                            "asesor": "Fernando Morales",
                            "email": "fmorales@usma.ac.pa",
                            "institucion": "Universidad Católica Santa María la Antigua",
                            "activo": 1
            },
            {
                            "id": 6,
                            "titulo": "Evaluación de plantas medicinales nativas con propiedades antiinflamatorias",
                            "ano": "2023",
                            "universidad": "Universidad Autónoma de Chiriquí",
                            "siglas": "UNACHI",
                            "resumen": "Caracterización fitoquímica y pruebas preliminares de actividad antiinflamatoria in vitro.",
                            "categoria": "Ciencias de la Salud",
                            "premio": "Tercer Lugar",
                            "asesor": "Diana Herrera",
                            "email": "dherrera@unachi.ac.pa",
                            "institucion": "Universidad Autónoma de Chiriquí",
                            "activo": 1
            }
          ]
        }
        """
    )


def get_raw_projects_data() -> dict:
    api_url = getattr(settings, "JIC_PROJECTS_API_URL", "").strip()
    timeout = int(getattr(settings, "JIC_PROJECTS_API_TIMEOUT", 8))
    cache_ttl = int(getattr(settings, "JIC_PROJECTS_CACHE_TTL", 300))
    retry_after_error = int(getattr(settings, "JIC_PROJECTS_RETRY_AFTER_ERROR", 60))
    now = time.monotonic()

    if not api_url:
        return _get_mock_projects_data()

    cached_data = _PROJECTS_CACHE.get("data")
    expires_at = float(_PROJECTS_CACHE.get("expires_at", 0.0) or 0.0)
    last_error_at = float(_PROJECTS_CACHE.get("last_error_at", 0.0) or 0.0)

    if cached_data is not None and now < expires_at:
        return cached_data

    # Circuit breaker: after a recent failure, serve cached data immediately.
    if cached_data is not None and (now - last_error_at) < retry_after_error:
        return cached_data

    request = Request(api_url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            data = json.loads(payload)
            if isinstance(data, dict):
                _PROJECTS_CACHE["data"] = data
                _PROJECTS_CACHE["expires_at"] = now + max(cache_ttl, 30)
                _PROJECTS_CACHE["last_error_at"] = 0.0
                return data

            logger.warning("Projects API returned a non-dict payload. Falling back to mock data.")
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        _PROJECTS_CACHE["last_error_at"] = now
        logger.warning("Could not fetch projects from API %s: %s", api_url, exc)

    if cached_data is not None:
        return cached_data

    fallback_data = _get_mock_projects_data()
    _PROJECTS_CACHE["data"] = fallback_data
    _PROJECTS_CACHE["expires_at"] = now + max(cache_ttl, 30)
    return fallback_data


def _parse_year(value) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _parse_winner(value) -> tuple[int, str]:
    if value is None:
        return 0, ""

    # New API sends textual prizes ("Primer Lugar"), old payload used numeric winner.
    normalized = str(value).strip().lower()

    if normalized in {"1", "primer lugar", "primer", "primero", "1er lugar"}:
        return 1, "Primer Lugar"
    if normalized in {"2", "segundo lugar", "segundo", "2do lugar"}:
        return 2, "Segundo Lugar"
    if normalized in {"3", "tercer lugar", "tercero", "3er lugar"}:
        return 3, "Tercer Lugar"

    return 0, ""


def get_processed_projects() -> list[dict]:
    projects_payload = get_raw_projects_data()
    raw_projects = projects_payload.get("ganadores_historicos") or projects_payload.get("proyectos") or []

    normalized_projects = []
    for project in raw_projects:
        is_active = int(project.get("activo", 1)) == 1 if str(project.get("activo", "")).strip() != "" else True
        if not is_active:
            continue

        winner_level, winner_label = _parse_winner(project.get("premio", project.get("winner", 0)))
        university_short_name = (project.get("siglas") or project.get("university_short_name") or "").strip()
        university = (project.get("universidad") or project.get("university") or "").strip()
        university_display = f"{university} ({university_short_name})" if university_short_name else university

        normalized_projects.append(
            {
                "id": int(project.get("id", 0)),
                "title": (project.get("titulo") or project.get("title") or "").strip(),
                "university": university,
                "university_short_name": university_short_name,
                "university_display": university_display,
                "category": (project.get("categoria") or project.get("category") or "").strip(),
                "year": _parse_year(project.get("ano", project.get("año", project.get("year")))),
                "contact": (project.get("email") or project.get("contacto") or "").strip(),
                "advisor": (project.get("asesor") or project.get("advisor") or "").strip(),
                "winner": winner_level,
                "winner_label": winner_label,
                "abstract": (project.get("resumen") or project.get("abstract") or "").strip(),
                "institution": (project.get("institucion") or "").strip(),
            }
        )

    normalized_projects.sort(key=lambda p: (p["year"], p["title"]), reverse=True)
    return normalized_projects


def get_gallery_image_path(instance, filename) -> str:
    """
    Generate path for gallery images: galeria/{year}/{filename}
    Example: galeria/2025/photo_abc123.jpg
    """
    year = timezone.now().year
    return f"galeria/{year}/{filename}"


def get_video_file_path(instance, filename) -> str:
    """
    Generate path for video files: videos/{year}/{filename}
    Example: videos/2025/tutorial_abc123.mp4
    """
    year = timezone.now().year
    return f"videos/{year}/{filename}"


def get_video_thumbnail_path(instance, filename) -> str:
    """
    Generate path for video thumbnails: video_thumbnails/{year}/{filename}
    Example: video_thumbnails/2025/thumb_abc123.jpg
    """
    year = timezone.now().year
    return f"video_thumbnails/{year}/{filename}"


def get_document_path(instance, filename) -> str:
    """
    Generate path for documents: documentos/{doc_type}/{year}/{filename}
    Example: documentos/lineamientos/2025/lineamientos_jic.pdf
    """
    year = timezone.now().year
    doc_type = getattr(instance, 'doc_type', 'otros').lower()
    return f"documentos/{doc_type}/{year}/{filename}"


def get_recursos_gallery(request, tab, current_img_cat, fallback_images) -> tuple[list[dict], list[str], Paginator.page]: #Paginator.page | None
    from .models import Gallery
    gallery_images = []
    gallery_categories = ['General']
    page_obj_gall = None
    
    try:
        gallery = Gallery.objects.prefetch_related('gallery_images__image__tags').first()
        
        if gallery and gallery.gallery_images.exists():
            gallery_images_qs = gallery.gallery_images.select_related('image').order_by('-image__created_at')
            gallery_categories = list(set(gallery_images_qs.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True)))
            gallery_categories = sorted(gallery_categories, reverse=True)
            if not gallery_categories:
                gallery_categories = ['General']
            
            if current_img_cat != 'all':
                gallery_images_qs = gallery_images_qs.filter(category=current_img_cat)
            
            if tab == 'galeria':
                paginator = Paginator(gallery_images_qs, 24)
                page_obj_gall = paginator.get_page(request.GET.get('page', 1))
                page_items = page_obj_gall.object_list
            else:
                page_items = gallery_images_qs[:24]

            for item in page_items:
                category = item.category if item.category else 'General'
                description = item.description if hasattr(item, 'description') and item.description else ''
                if not description and hasattr(item.image, 'description') and item.image.description:
                     description = item.image.description
                     
                alt_text = item.alt_text if hasattr(item, 'alt_text') and item.alt_text else item.image.title

                gallery_images.append({
                    'obj': item.image,
                    'src': item.image.file.url,
                    'full_src': item.image.file.url,
                    'alt': alt_text,
                    'title': item.image.title,
                    'description': description,
                    'category': category,
                })
        else:
            db_images = list(Image.objects.all().order_by('-created_at')[:24])
            if tab == 'galeria':
                paginator = Paginator(Image.objects.all().order_by('-created_at'), 24)
                page_obj_gall = paginator.get_page(request.GET.get('page', 1))
                db_images = list(page_obj_gall.object_list)
            
            for img in db_images:
                gallery_images.append({
                    'obj': img,
                    'src': img.file.url,
                    'full_src': img.file.url,
                    'alt': img.title,
                    'title': img.title,
                    'description': img.get_title() if hasattr(img, 'get_title') else '',
                    'category': 'General',
                })

    except (OperationalError, ProgrammingError, Exception) as e:
        print(f'Error loading gallery: {e}')
        
    if not gallery_images:
        gallery_images = fallback_images
        gallery_categories = sorted(list(set(img['category'] for img in gallery_images)), reverse=True)
        if current_img_cat != 'all':
            gallery_images = [img for img in gallery_images if img['category'] == current_img_cat]
            
        if tab == 'galeria':
            paginator = Paginator(gallery_images, 24)
            page_obj_gall = paginator.get_page(request.GET.get('page', 1))
            gallery_images = page_obj_gall.object_list

    return gallery_images, gallery_categories, page_obj_gall

def get_recursos_videos(request, tab, fallback_videos) -> tuple[list[dict], Paginator.page]: #Paginator.page | None
    from .models import video
    from django.core.paginator import Paginator
    from django.db.utils import OperationalError, ProgrammingError
    videos = []
    page_obj_vid = None
    
    try:
        db_videos = video.objects.filter(is_active=True).order_by('sort_order', '-created_at')
        for v in db_videos:
            thumb_url = v.thumbnail.url if v.thumbnail else '/static/images/hero-jic.jpg'
            video_url = v.youtube_url if v.youtube_url else (v.video_file.url if v.video_file else '#')
            videos.append({
                'title': v.title,
                'thumbnail': thumb_url,
                'url': video_url,
                'description': v.description,
            })
    except (OperationalError, ProgrammingError, Exception):
        pass
        
    if not videos:
        videos = fallback_videos

    if tab == 'videos':
        paginator = Paginator(videos, 12)
        page_obj_vid = paginator.get_page(request.GET.get('page', 1))
        videos = page_obj_vid.object_list
        
    return videos, page_obj_vid

