import json
import logging
import time
import unicodedata
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from wagtail.admin.menu import MenuItem
from django.core.paginator import Paginator
from django.db.models import Q
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

OFFICIAL_UNIVERSITIES = [
    'Universidad Católica Santa María la Antigua',
    'Universidad Especializada de las Américas',
    'Universidad Internacional de Ciencia y Tecnología',
    'Universidad Latina de Panamá',
    'Universidad Marítima Internacional de Panamá',
    'Universidad Metropolitana de Educación, Ciencia y Tecnología',
    'Universidad Santander',
    'Universidad Tecnológica de Oteima',
    'Universidad Tecnológica de Panamá',
    'Universidad de Panamá',
]


def _normalize_text_key(value: str | None) -> str:
    text = (value or '').strip().lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    text = ''.join(ch if ch.isalnum() or ch.isspace() else ' ' for ch in text)
    return ' '.join(text.split())


def _normalize_university_name(value: str | None) -> str:
    raw_text = (value or '').strip()
    if not raw_text:
        return ''

    official_by_key = {_normalize_text_key(name): name for name in OFFICIAL_UNIVERSITIES}
    aliases = {
        'universidad catolica santa maria la antigua': 'Universidad Católica Santa María la Antigua',
        'universidad catolica santa maria la antigua usma': 'Universidad Católica Santa María la Antigua',
        'usma': 'Universidad Católica Santa María la Antigua',
        'universidad tecnologica de panama': 'Universidad Tecnológica de Panamá',
        'utp': 'Universidad Tecnológica de Panamá',
        'universidad de panama': 'Universidad de Panamá',
        'up': 'Universidad de Panamá',
        'universidad metropolitana de educacion ciencia y tecnologia': 'Universidad Metropolitana de Educación, Ciencia y Tecnología',
        'umecit': 'Universidad Metropolitana de Educación, Ciencia y Tecnología',
        'universidad especializada de las americas': 'Universidad Especializada de las Américas',
        'udelas': 'Universidad Especializada de las Américas',
        'universidad internacional de ciencia y tecnologia': 'Universidad Internacional de Ciencia y Tecnología',
        'unicyt': 'Universidad Internacional de Ciencia y Tecnología',
        'universidad latina de panama': 'Universidad Latina de Panamá',
        'ulat': 'Universidad Latina de Panamá',
        'universidad maritima internacional de panama': 'Universidad Marítima Internacional de Panamá',
        'umip': 'Universidad Marítima Internacional de Panamá',
        'universidad santander': 'Universidad Santander',
        'universidad tecnologica de oteima': 'Universidad Tecnológica de Oteima',
    }

    key = _normalize_text_key(raw_text)
    if key in aliases:
        return aliases[key]
    if key in official_by_key:
        return official_by_key[key]
    return raw_text


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
                            "titulo": "Sistema de monitoreo ambiental con IoT",
                            "ano": "2025",
                            "universidad": "Universidad Tecnologica de Panama",
                            "siglas": "UTP",
                            "resumen": "Desarrollo de sensores IoT para medir calidad del aire y emitir alertas tempranas en tiempo real.",
                            "categoria": "Ingenieria",
                            "premio": "Primer Lugar",
                            "asesor": "Carlos Mendoza",
                            "email": "carlos.mendoza@utp.ac.pa",
                            "institucion": "Facultad de Ingenieria Electrica",
                            "activo": 1,
                            "estudiantes": ["Andrés Fuentes", "Valeria Ríos", "Miguel Herrera"],
                            "keywords": ["IoT", "calidad del aire", "sensores", "alertas tempranas", "monitoreo"]
            },
            {
                            "id": 2,
                            "titulo": "Gemelo digital para mantenimiento predictivo industrial",
                            "ano": "2025",
                            "universidad": "Universidad de Panama",
                            "siglas": "UP",
                            "resumen": "Plataforma de analitica para anticipar fallas en maquinaria critica mediante series temporales.",
                            "categoria": "Ingenieria",
                            "premio": "Segundo Lugar",
                            "asesor": "Maria Garcia",
                            "email": "maria.garcia@up.ac.pa",
                            "institucion": "Facultad de Ingenieria",
                            "activo": 1,
                            "estudiantes": ["Camila Núñez", "Sebastián Mora", "Lucía Pinto"],
                            "keywords": ["gemelo digital", "mantenimiento predictivo", "series temporales", "analítica industrial"]
            },
            {
                            "id": 3,
                            "titulo": "Materiales biodegradables con residuos agricolas",
                            "ano": "2025",
                            "universidad": "Universidad Autonoma de Chiriqui",
                            "siglas": "UNACHI",
                            "resumen": "Creacion de biopolimeros para empaques sostenibles aprovechando subproductos agroindustriales.",
                            "categoria": "Ingenieria",
                            "premio": "Tercer Lugar",
                            "asesor": "Diana Herrera",
                            "email": "diana.herrera@unachi.ac.pa",
                            "institucion": "Laboratorio de Innovacion Sostenible",
                            "activo": 1,
                            "estudiantes": ["Daniela Salas", "Jorge Quirós", "Fernanda Leal"],
                            "keywords": ["biopolímeros", "empaques sostenibles", "residuos agrícolas", "agroindustria", "economía circular"]
            },
            {
                            "id": 4,
                            "titulo": "Analisis de biomarcadores en diabetes tipo 2",
                            "ano": "2025",
                            "universidad": "Universidad Latina de Panama",
                            "siglas": "ULAT",
                            "resumen": "Estudio de biomarcadores clinicos asociados a progresion de diabetes tipo 2 en poblacion universitaria.",
                            "categoria": "Ciencias de la Salud",
                            "premio": "Primer Lugar",
                            "asesor": "Roberto Castillo",
                            "email": "roberto.castillo@ulatina.edu.pa",
                            "institucion": "Facultad de Medicina",
                            "activo": 1,
                            "estudiantes": ["Andrea Villar", "Tomás Espino", "Natalia Cruz"],
                            "keywords": ["biomarcadores", "diabetes tipo 2", "población universitaria", "diagnóstico clínico"]
            },
            {
                            "id": 5,
                            "titulo": "Prediccion de brotes de dengue con ML",
                            "ano": "2025",
                            "universidad": "Universidad Catolica Santa Maria La Antigua",
                            "siglas": "USMA",
                            "resumen": "Modelo predictivo con datos climaticos y epidemiologicos para apoyar decisiones de salud publica.",
                            "categoria": "Ciencias de la Salud",
                            "premio": "Segundo Lugar",
                            "asesor": "Fernando Morales",
                            "email": "fernando.morales@usma.ac.pa",
                            "institucion": "Centro de Analitica en Salud",
                            "activo": 1,
                            "estudiantes": ["Ricardo Blanco", "Sofía Arias", "Manuel Delgado"],
                            "keywords": ["dengue", "machine learning", "epidemiología", "salud pública", "predicción"]
            },
            {
                            "id": 6,
                            "titulo": "Plantas medicinales con actividad antiinflamatoria",
                            "ano": "2025",
                            "universidad": "Universidad Especializada de las Americas",
                            "siglas": "UDELAS",
                            "resumen": "Caracterizacion fitoquimica y pruebas in vitro de especies nativas con potencial terapeutico.",
                            "categoria": "Ciencias de la Salud",
                            "premio": "Tercer Lugar",
                            "asesor": "Patricia Solis",
                            "email": "patricia.solis@udelas.ac.pa",
                            "institucion": "Instituto de Investigacion Biomedica",
                            "activo": 1,
                            "estudiantes": ["Isabela Mora", "Carlos Rivas", "Alejandra Vega"],
                            "keywords": ["fitoquímica", "plantas medicinales", "antiinflamatorio", "especies nativas", "in vitro"]
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


def _normalize_string_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]

    return []


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
            advisor_name = (item.get("advisor1") or item.get("advisor") or item.get("advisor2") or "").strip()
            advisor_email = (item.get("contact") or "").strip()
            institution = (item.get("institution") or item.get("university") or "").strip()
            advisor_obj = None

            if advisor_name:
                # Match consultant by name case-insensitively to avoid duplicate advisors.
                advisor_obj = consultant.objects.filter(name__iexact=advisor_name).first()
                if advisor_obj:
                    advisor_obj.name = advisor_name
                    advisor_obj.email = advisor_email
                    advisor_obj.institution = institution
                    advisor_obj.is_active = True
                    advisor_obj.save(update_fields=["name", "email", "institution", "is_active"])
                else:
                    advisor_obj = consultant.objects.create(
                        name=advisor_name,
                        email=advisor_email,
                        institution=institution,
                        is_active=True,
                    )

            title = (item.get("title") or "").strip()
            year = int(item.get("year") or 0)
            university = _normalize_university_name((item.get("university") or "").strip())
            if not title or not year or not university:
                continue

            existing_project = project.objects.filter(title__iexact=title, year=year).first()
            if existing_project:
                existing_project.title = title
                existing_project.abstract = (item.get("abstract") or "").strip()
                existing_project.advisor = advisor_obj
                existing_project.university = university
                existing_project.university_short_name = (item.get("university_short_name") or "").strip() or None
                existing_project.category = (item.get("category") or "").strip()
                existing_project.winner = winner_map.get(int(item.get("winner") or 0), 0)
                existing_project.save(update_fields=[
                    "title",
                    "abstract",
                    "advisor",
                    "university",
                    "university_short_name",
                    "category",
                    "winner",
                ])
            else:
                project.objects.create(
                    title=title,
                    year=year,
                    abstract=(item.get("abstract") or "").strip(),
                    advisor=advisor_obj,
                    university=university,
                    university_short_name=(item.get("university_short_name") or "").strip() or None,
                    category=(item.get("category") or "").strip(),
                    winner=winner_map.get(int(item.get("winner") or 0), 0),
                )
    except (OperationalError, ProgrammingError, Exception) as exc:
        logger.warning("Could not auto-sync API projects to DB: %s", exc)


def _get_projects_from_database() -> list[dict]:
    """Return normalized projects from local DB (project + consultant)."""
    try:
        from .models import project
    except Exception as e:
        logger.warning("Could not import project model: %s", e)
        return []

    try:
        rows = project.objects.select_related("advisor").all().order_by("-year", "title")
        row_count = rows.count()
        logger.debug("Database query returned %d project rows", row_count)
    except (OperationalError, ProgrammingError) as e:
        logger.warning("Database error fetching projects: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error fetching projects from database: %s", e, exc_info=True)
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
        university = _normalize_university_name((p.university or "").strip())
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
                "advisor1": (advisor_name or "").strip(),
                "advisor2": "",
                "advisor": (advisor_name or "").strip(),
                "winner": int(p.winner or 0),
                "winner_label": winner_label_map.get(int(p.winner or 0), ""),
                "abstract": (p.abstract or "").strip(),
                "institution": (advisor_institution or university or "").strip(),
                "students": [],
                "keywords": [],
            }
        )

    logger.debug("Normalized %d projects from database", len(normalized_projects))
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
        university = _normalize_university_name((project.get("universidad") or project.get("university") or "").strip())
        university_display = f"{university} ({university_short_name})" if university_short_name else university
        advisor1 = (project.get("asesor1") or project.get("advisor1") or project.get("asesor") or project.get("advisor") or "").strip()
        advisor2 = (project.get("asesor2") or project.get("advisor2") or "").strip()
        advisor = advisor1 or advisor2

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
                "advisor1": advisor1,
                "advisor2": advisor2,
                "advisor": advisor,
                "winner": winner_level,
                "winner_label": winner_label,
                "abstract": (project.get("resumen") or project.get("abstract") or "").strip(),
                "institution": (project.get("institucion") or "").strip(),
                "students": _normalize_string_list(project.get("estudiantes", project.get("students"))),
                "keywords": _normalize_string_list(project.get("keywords", project.get("palabras_clave"))),
            }
        )

    normalized_projects.sort(key=lambda p: (p["year"], p["title"]), reverse=True)
    return normalized_projects


def _build_project_match_keys(item: dict) -> tuple[tuple, tuple, tuple]:
    project_id = int(item.get("id") or 0)
    year = int(item.get("year") or 0)
    title = (item.get("title") or "").strip().lower()
    university = _normalize_university_name(item.get("university") or "").lower()

    by_id = (project_id,)
    by_title_year_university = (title, year, university)
    by_title_year = (title, year)
    return by_id, by_title_year_university, by_title_year


def _enrich_projects_with_api_fields(base_projects: list[dict]) -> list[dict]:
    if not base_projects:
        return base_projects

    api_projects = sync_projects_from_api()
    if not api_projects:
        return base_projects

    by_id: dict[tuple, dict] = {}
    by_tyu: dict[tuple, dict] = {}
    by_ty: dict[tuple, dict] = {}

    for api_item in api_projects:
        key_id, key_tyu, key_ty = _build_project_match_keys(api_item)
        if key_id[0] > 0:
            by_id[key_id] = api_item
        if key_tyu[0] and key_tyu[1] > 0:
            by_tyu[key_tyu] = api_item
        if key_ty[0] and key_ty[1] > 0:
            by_ty[key_ty] = api_item

    enriched = []
    for item in base_projects:
        key_id, key_tyu, key_ty = _build_project_match_keys(item)

        match = None
        if key_id[0] > 0:
            match = by_id.get(key_id)
        if not match:
            match = by_tyu.get(key_tyu)
        if not match:
            match = by_ty.get(key_ty)

        if match:
            merged = dict(item)
            merged["students"] = match.get("students") or item.get("students") or []
            merged["keywords"] = match.get("keywords") or item.get("keywords") or []
            enriched.append(merged)
        else:
            enriched.append(item)

    return enriched


def sync_projects_from_api() -> list[dict]:
    """Fetch projects from API/fallback payload and persist them to local DB when enabled."""
    projects_payload = get_raw_projects_data()
    normalized_projects = _normalize_projects_payload(projects_payload)
    _auto_sync_projects_to_database(normalized_projects)
    return normalized_projects


def get_processed_projects() -> list[dict]:
    # Optional API-first mode for environments that must always reflect external API.
    if _is_truthy(getattr(settings, "JIC_PROJECTS_PREFER_API", False)):
        logger.info("JIC_PROJECTS_PREFER_API enabled, syncing from API")
        api_projects = sync_projects_from_api()
        if api_projects:
            logger.info("API returned %d projects", len(api_projects))
            return api_projects
        logger.warning("API returned no projects, falling back")

    # Default priority order: local DB (imported/admin data) -> external API -> in-code fallback.
    logger.debug("Attempting to fetch projects from local database")
    projects_from_db = _get_projects_from_database()
    if projects_from_db:
        logger.info("Local database returned %d projects", len(projects_from_db))
        enriched = _enrich_projects_with_api_fields(projects_from_db)
        logger.info("After API enrichment: %d projects", len(enriched))
        return enriched
    
    logger.warning("No projects in local database, syncing from API")
    normalized_projects = sync_projects_from_api()
    if normalized_projects:
        logger.info("API sync returned %d projects", len(normalized_projects))
    else:
        logger.warning("API returned no projects, will use in-code fallback")
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


def _sanitize_alt_text(filename_or_title: str) -> str:
    """
    Convert filename or title into accessible alt text.
    Removes file extensions, cleans special characters, and provides fallback.
    
    Examples:
    - "2025.10.01 JIC GRAN FINAL - JIC GRAN FINAL (93).jpg" → "Evento JIC 2025"
    - "image_2025_award.png" → "Premiación JIC"
    - "photo.jpg" → "Imagen del evento"
    """
    if not filename_or_title:
        return "Imagen del evento"
    
    import re
    
    text = str(filename_or_title).strip()
    
    # Remove file extensions
    text = re.sub(r'\.\w+$', '', text)
    
    # Remove obvious duplicate halves around hyphen, e.g. "JIC GRAN FINAL - JIC GRAN FINAL"
    if " - " in text:
        left, right = text.split(" - ", 1)
        if left.strip().lower() == right.strip().lower():
            text = left.strip()
    
    # Remove file hashes and technical suffixes (e.g., "(93)", "abc123")
    text = re.sub(r'\s*\(\d+\)\s*', ' ', text)
    text = re.sub(r'\s*[a-f0-9]{8,}\s*', ' ', text)
    
    # Clean up dates in format YYYY.MM.DD or YYYY-MM-DD
    text = re.sub(r'\d{4}[.\-]\d{2}[.\-]\d{2}\s*', '', text)
    
    # Replace underscores and extra spaces
    text = text.replace('_', ' ').strip()
    text = re.sub(r'\s+', ' ', text)
    
    # If the source still looks like a technical filename, return a safe generic alt.
    looks_like_filename = bool(
        re.search(r"\b(img|dsc|pxl|whatsapp|screenshot|image)\b", text, re.IGNORECASE)
        or re.search(r"\d{2,}", text)
        or re.search(r"\b[jJ][pP][eE]?[gG]\b|\b[pP][nN][gG]\b|\b[wW][eE][bB][pP]\b", text)
    )

    # If we have meaningful cleaned text, use it.
    if len(text) > 8 and not looks_like_filename:
        return text
    
    # Default fallback based on context
    return "Fotografia del evento JIC"


def get_recursos_gallery(request, tab, current_img_cat, fallback_images) -> tuple[list[dict], list[str], Paginator.page]: #Paginator.page | None
    from .models import Gallery
    gallery_images = []
    gallery_categories = ['General']
    page_obj_gall = None
    gallery_is_configured = False
    
    try:
        gallery = Gallery.objects.prefetch_related('gallery_images__image__tags').first()
        
        if gallery and gallery.gallery_images.exists():
            gallery_is_configured = True
            gallery_images_qs = (
                gallery.gallery_images
                .select_related('image')
                .order_by('-image__created_at')
            )
            gallery_images_qs = gallery_images_qs.filter(
                Q(image__collection__resource_visibility__is_visible_in_resources=True)
                | Q(image__collection__resource_visibility__isnull=True)
            )

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
                     
                raw_alt = item.alt_text if hasattr(item, 'alt_text') and item.alt_text else ''
                if not raw_alt:
                    raw_alt = description if description else item.image.title
                alt_text = _sanitize_alt_text(raw_alt)
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

                raw_alt = img.title
                if hasattr(img, 'description') and img.description:
                    raw_alt = img.description

                gallery_images.append({
                    'obj': img,
                    'src': thumb_src,
                    'full_src': lightbox_src,
                    'alt': _sanitize_alt_text(raw_alt),
                    'title': img.title,
                    'description': img.get_title() if hasattr(img, 'get_title') else '',
                    'category': 'General',
                })

    except (OperationalError, ProgrammingError, Exception) as e:
        print(f'Error loading gallery: {e}')
        
    if not gallery_images and not gallery_is_configured:
        gallery_images = []
        for img in fallback_images:
            raw_alt = img.get('alt') or img.get('description') or img.get('title') or ''
            normalized = dict(img)
            normalized['alt'] = _sanitize_alt_text(raw_alt)
            gallery_images.append(normalized)
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

# Photo collection name in Wagtail to identify gallery images.
PHOTO_COLLECTION_ROOT_NAME = "Fotos"
def _is_photo_collection(collection):
    """
    Verify if the given Wagtail collection is the designated photo collection or a descendant of it, based on the collection name.
    """
    if collection.name == PHOTO_COLLECTION_ROOT_NAME:
        return True
    
    # Check if it is a descendant of the photo collection root
    parent = collection.get_parent()
    while parent:
        if parent.name == PHOTO_COLLECTION_ROOT_NAME:
            return True
        parent = parent.get_parent()
    
    return False
