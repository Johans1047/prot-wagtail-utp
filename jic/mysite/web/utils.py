import json
import logging
import time
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from wagtail.admin.menu import MenuItem
from django.core.paginator import Paginator
from django.db.utils import OperationalError, ProgrammingError
from wagtail.images import get_image_model
from wagtail.images.models import Image


logger = logging.getLogger(__name__)


class WagtailDocWrapper:
    def __init__(self, doc):
        self.title = doc.title
        self.description = ""
        self.year = ""
        self.url = doc.url
        self.document_file = type('obj', (object,), {'url': doc.url})
        self.is_wagtail_doc = True
        
        tags = [t.lower() for t in doc.tags.names()]
        title_lower = (doc.title or "").lower()

        if any(t in tags for t in ["boletin", "boletines"]) or "boletin" in title_lower:
            self.doc_type = 'boletines'
            self.doc_type_title = 'Boletín'
        elif any(t in tags for t in ["memoria", "memorias"]) or "memoria" in title_lower:
            self.doc_type = 'memorias'
            self.doc_type_title = 'Memoria'
        elif any(t in tags for t in ["manual", "manuales"]) or "manual" in title_lower:
            self.doc_type = 'manuales'
            self.doc_type_title = 'Manual'
        elif any(t in tags for t in ["lineamiento", "lineamientos"]) or "lineamiento" in title_lower:
            self.doc_type = 'lineamientos'
            self.doc_type_title = 'Lineamiento'
        elif any(t in tags for t in ["plantilla", "plantillas", "plantilla de articulo", "plantillas de articulos"]) or "plantilla" in title_lower:
            self.doc_type = 'plantillas'
            self.doc_type_title = 'Plantilla'
        elif any(t in tags for t in ["acta", "actas", "acta de resultados"]) or "acta" in title_lower:
            self.doc_type = 'actas'
            self.doc_type_title = 'Acta de Resultados'
        else:
            self.doc_type = 'otros'
            self.doc_type_title = 'Documento'
    
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


# In-process cache to avoid repeated slow API timeouts on every request.
_PROJECTS_CACHE: dict[str, object] = {
    "data": None,
    "expires_at": 0.0,
    "last_error_at": 0.0,
}


def _resolve_image_url(image_obj) -> str | None:
    if not image_obj:
        return None

    # Supports both Django ImageField (image.url) and Wagtail FK image (image.file.url).
    try:
        if getattr(image_obj, "url", None):
            return image_obj.url
    except Exception:
        pass

    try:
        file_obj = getattr(image_obj, "file", None)
        if file_obj and getattr(file_obj, "url", None):
            return file_obj.url
    except Exception:
        pass

    return None


def _youtube_thumbnail_from_url(youtube_url: str | None) -> str | None:
    if not youtube_url:
        return None

    try:
        parsed = urlparse(youtube_url)
        host = (parsed.netloc or "").lower()

        if "youtu.be" in host:
            video_id = parsed.path.strip("/")
        else:
            video_id = parse_qs(parsed.query).get("v", [""])[0]
            if not video_id and "/shorts/" in parsed.path:
                video_id = parsed.path.split("/shorts/")[-1].split("/")[0]

        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    except Exception:
        return None

    return None


def _get_wagtail_rendition_url(image_obj, filter_spec: str) -> str | None:
    if not image_obj:
        return None

    try:
        rendition = image_obj.get_rendition(filter_spec)
        if rendition and getattr(rendition, "url", None):
            return rendition.url
    except Exception:
        return None

    return None


def _get_synced_imagefield_rendition_url(instance, field_name: str, filter_spec: str) -> str | None:
    field_file = getattr(instance, field_name, None)
    if not field_file or not getattr(field_file, "name", ""):
        return None

    # Titles are synced in signals.py with this deterministic prefix.
    key_prefix = f"[auto-sync:{instance._meta.label_lower}:{instance.pk}:{field_name}] "

    try:
        image_model = get_image_model()
        synced_image = image_model.objects.filter(title__startswith=key_prefix).first()
    except Exception:
        synced_image = None

    if not synced_image:
        return None

    return _get_wagtail_rendition_url(synced_image, filter_spec)


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


def _is_truthy(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _auto_sync_projects_to_database(normalized_projects: list[dict]) -> None:
    """Persist normalized API projects into local project/consultant tables."""
    auto_sync_enabled = _is_truthy(getattr(settings, "JIC_PROJECTS_AUTO_SYNC_DB", True))
    if not auto_sync_enabled or not normalized_projects:
        return

    try:
        from .models import consultant, project
    except Exception:
        return

    winner_map = {0: 0, 1: 1, 2: 2, 3: 3}

    try:
        for item in normalized_projects:
            advisor_name = (item.get("advisor") or "").strip()
            advisor_email = (item.get("contact") or "").strip()
            institution = (item.get("institution") or item.get("university") or "").strip()
            advisor_obj = None

            if advisor_name:
                advisor_obj, _ = consultant.objects.update_or_create(
                    name=advisor_name,
                    defaults={
                        "email": advisor_email,
                        "institution": institution,
                        "is_active": True,
                    },
                )

            title = (item.get("title") or "").strip()
            year = int(item.get("year") or 0)
            university = (item.get("university") or "").strip()
            if not title or not year or not university:
                continue

            project.objects.update_or_create(
                title=title,
                year=year,
                defaults={
                    "abstract": (item.get("abstract") or "").strip(),
                    "advisor": advisor_obj,
                    "university": university,
                    "university_short_name": (item.get("university_short_name") or "").strip() or None,
                    "category": (item.get("category") or "").strip(),
                    "winner": winner_map.get(int(item.get("winner") or 0), 0),
                },
            )
    except (OperationalError, ProgrammingError, Exception) as exc:
        logger.warning("Could not auto-sync API projects to DB: %s", exc)


def _get_projects_from_database() -> list[dict]:
    """Return normalized projects from local DB (project + consultant)."""
    try:
        from .models import project
    except Exception:
        return []

    try:
        rows = project.objects.select_related("advisor").all().order_by("-year", "title")
    except (OperationalError, ProgrammingError, Exception):
        return []

    winner_label_map = {
        0: "",
        1: "Primer Lugar",
        2: "Segundo Lugar",
        3: "Tercer Lugar",
    }

    normalized_projects = []
    for p in rows:
        advisor_name = p.advisor.name if p.advisor else ""
        advisor_email = p.advisor.email if p.advisor else ""
        advisor_institution = p.advisor.institution if p.advisor else ""
        short_name = (p.university_short_name or "").strip()
        university = (p.university or "").strip()
        university_display = f"{university} ({short_name})" if short_name else university

        normalized_projects.append(
            {
                "id": int(p.id),
                "title": (p.title or "").strip(),
                "university": university,
                "university_short_name": short_name,
                "university_display": university_display,
                "category": (p.category or "").strip(),
                "year": int(p.year or 0),
                "contact": (advisor_email or "").strip(),
                "advisor": (advisor_name or "").strip(),
                "winner": int(p.winner or 0),
                "winner_label": winner_label_map.get(int(p.winner or 0), ""),
                "abstract": (p.abstract or "").strip(),
                "institution": (advisor_institution or university or "").strip(),
            }
        )

    return normalized_projects


def _normalize_projects_payload(projects_payload: dict) -> list[dict]:
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


def sync_projects_from_api() -> list[dict]:
    """Fetch projects from API/fallback payload and persist them to local DB when enabled."""
    projects_payload = get_raw_projects_data()
    normalized_projects = _normalize_projects_payload(projects_payload)
    _auto_sync_projects_to_database(normalized_projects)
    return normalized_projects


def get_processed_projects() -> list[dict]:
    # Priority order: local DB (imported/admin data) -> external API -> in-code fallback.
    projects_from_db = _get_projects_from_database()
    if projects_from_db:
        return projects_from_db

    normalized_projects = sync_projects_from_api()
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
                thumb_src = (
                    _get_wagtail_rendition_url(item.image, "fill-600x600|jpegquality-75")
                    or item.image.file.url
                )
                lightbox_src = (
                    _get_wagtail_rendition_url(item.image, "max-1800x1800|jpegquality-82")
                    or item.image.file.url
                )

                gallery_images.append({
                    'obj': item.image,
                    'src': thumb_src,
                    'full_src': lightbox_src,
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
                thumb_src = (
                    _get_wagtail_rendition_url(img, "fill-600x600|jpegquality-75")
                    or img.file.url
                )
                lightbox_src = (
                    _get_wagtail_rendition_url(img, "max-1800x1800|jpegquality-82")
                    or img.file.url
                )

                gallery_images.append({
                    'obj': img,
                    'src': thumb_src,
                    'full_src': lightbox_src,
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
            thumb_rendition_url = _get_synced_imagefield_rendition_url(v, 'thumbnail', 'fill-640x360|jpegquality-75')
            poster_rendition_url = _get_synced_imagefield_rendition_url(v, 'thumbnail', 'max-1280x720|jpegquality-82')

            thumb_url = (
                thumb_rendition_url
                or _resolve_image_url(v.thumbnail)
                or _youtube_thumbnail_from_url(v.youtube_url)
                or '/static/images/hero-jic.jpg'
            )
            poster_url = (
                poster_rendition_url
                or _resolve_image_url(v.thumbnail)
                or thumb_url
            )
            video_url = v.youtube_url if v.youtube_url else (v.video_file.url if v.video_file else '#')
            videos.append({
                'title': v.title,
                'thumbnail': thumb_url,
                'poster': poster_url,
                'url': video_url,
                'description': v.description,
            })
    except (OperationalError, ProgrammingError, Exception) as exc:
        logger.warning("Could not load videos from DB: %s", exc)
        
    if not videos:
        videos = fallback_videos

    if tab == 'videos':
        paginator = Paginator(videos, 12)
        page_obj_vid = paginator.get_page(request.GET.get('page', 1))
        videos = page_obj_vid.object_list
        
    return videos, page_obj_vid
