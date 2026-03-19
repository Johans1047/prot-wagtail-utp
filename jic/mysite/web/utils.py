import json
from django.urls import reverse
from django.utils import timezone
from wagtail.admin.menu import MenuItem
from django.core.paginator import Paginator
from django.db.utils import OperationalError, ProgrammingError
from wagtail.images.models import Image


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
    

def get_raw_projects_data() -> dict:
    return json.loads(
        """
        {
          "total": 13,
          "proyectos": [
            {
              "id": 606,
              "ano": 2024,
              "titulo": "Percepción, implicación y consecuencias del acoso escolar en instituciones educativas particulares y oficiales, en una muestra de docentes y estudiantes de distintas provincias de Panamá",
              "abstract": "El acoso escolar es una problemática cotidiana en el entorno educativo a nivel mundial. El objetivo de esta investigación fue analizar la percepción, implicación y consecuencias del acoso escolar en instituciones educativas, particulares y oficiales, en una muestra de docentes y estudiantes de distintas provincias de Panamá.",
              "asesor": "Abdel Alexander Solís Rodríguez",
              "contacto": "abdelsolis@gmail.com",
              "universidad": "Universidad Católica Santa María la Antigua",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 647,
              "ano": 2024,
              "titulo": "Densidad poblacional del mono tití panameño (Oedipomidas geoffroyi) en dos sitios del distrito de Chame, Panamá",
              "abstract": "El mono tití panameño (Oedipomidas geoffroyi) es considerado tolerante a perturbaciones antropogénica. Sin embargo, la última evaluación del estado de conservación lo consideran Casi Amenazado.",
              "asesor": "Pedro G Méndez Carvajal",
              "contacto": "giprimatologia.up@gmail.com",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 633,
              "ano": 2024,
              "titulo": "Uso de los sentidos por Alouatta coibensis en la evaluación/aceptación de frutos de Spondias mombin en Isla Coiba, Panamá",
              "abstract": "Los frutos de jobo (Spondias mombin) han sido reportados frecuentemente en la dieta del mono aullador (Alouatta sp.), usando sus sentidos para evaluar de manera efectiva la palatabilidad a estos frutos.",
              "asesor": "Karol M. Gutiérrez Pineda",
              "contacto": "gutierrezpinedakm@gmail.com",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 629,
              "ano": 2024,
              "titulo": "Identificación molecular de filogrupos y patotipos de cepas de Escherichia coli resistentes a los aminoglucósidos aisladas de aguas residuales y naturales en la Ciudad de Panamá.",
              "abstract": "El crecimiento poblacional, la urbanización, el cambio climático y la creciente demanda de agua han llevado a la degradación de muchas fuentes hídricas.",
              "asesor": "Jordi Querol",
              "contacto": "jordi.querol@up.ac.pa",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias de la Salud"
            },
            {
              "id": 610,
              "ano": 2024,
              "titulo": "Restauración del parque recreacional de Buena Vista",
              "abstract": "El Parque Recreacional de Buena Vista en Tocumen, Panamá, ha experimentado un deterioro significativo en su infraestructura, afectando la calidad de vida de la comunidad.",
              "asesor": "Maricela Ivonne Rodríguez C",
              "contacto": "mrodriguez@unicyt.net",
              "universidad": "Universidad Internacional de Ciencia y Tecnología",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 617,
              "ano": 2024,
              "titulo": "Aplicación y Efectividad de las Leyes de Protección de Afluentes Primarios en Los Algarrobos, Veraguas.",
              "abstract": "Panamá es un país rico en biodiversidad y recursos naturales, uno de éstos son los recursos hídricos.",
              "asesor": "Zoila Chilan",
              "contacto": "zchilan16@gmail.com",
              "universidad": "Universidad Metropolitana de Educación, Ciencia y Tecnología",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 420,
              "ano": 2024,
              "titulo": "Valoración de la capacidad antioxidante del puam (Muntingia calabura) y su potencial como alimento funcional",
              "abstract": "El árbol Muntingia calabura (puam) es de gran abundancia y accesibilidad en la República de Panamá.",
              "asesor": "Jhonny Correa",
              "contacto": "jhonny.correa@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 247,
              "ano": 2024,
              "titulo": "Impacto de campos electromagnéticos en el crecimiento de plantas: Un estudio experimental",
              "abstract": "Cuando la semilla se encuentra en un proceso germinativo, existen muchas condiciones fundamentales.",
              "asesor": "Hector Vergara",
              "contacto": "hector.vergara@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 388,
              "ano": 2024,
              "titulo": "Prototipo de una aplicación móvil para el reconocimiento, diagnóstico y sugerencias de tratamiento para melanomas",
              "abstract": "El cáncer de piel es causado por células cancerosas en tejidos de la piel.",
              "asesor": "Mariluz Centella",
              "contacto": "mariluz.centella@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ingeniería"
            },
            {
              "id": 476,
              "ano": 2024,
              "titulo": "Desarrollo de estrategias para potenciar el crecimiento de emprendimientos estudiantiles de la Universidad Tecnológica de Panamá",
              "abstract": "Este artículo aborda el impacto de factores como la asignatura Formación de Emprendedores y el uso de los servicios de la DGTC.",
              "asesor": "Enith González",
              "contacto": "enith.gonzalez@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 626,
              "ano": 2024,
              "titulo": "Biodiversidad Vegetal del Parque Nacional Camino de Cruces",
              "abstract": "Este proyecto se enfoca en obtener información biológica descriptiva sobre las especies vegetales presentes en el área protegida Parque Nacional Camino de Cruces.",
              "asesor": "Carlos Patricio Guerra Torres",
              "contacto": "guerrcarlos@gmail.com",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 302,
              "ano": 2024,
              "titulo": "Propuesta de un índice técnico de caminabilidad (ICM) para microentornos educativos: diagnóstico de los alrededores del Campus Víctor Levi Sasso",
              "abstract": "Este estudio propone un Índice Técnico de Caminabilidad (ICM) para evaluar microentornos educativos, tomando como caso de estudio el Campus Víctor Levi Sasso.",
              "asesor": "Analissa Icaza",
              "contacto": "analissa.icaza@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 332,
              "ano": 2024,
              "titulo": "Modelo metodológico para la evaluación de agua y saneamiento con soluciones a corto plazo para comunidades emergentes: Caso de Calle 50 y La Isla en la Cuenca del Río Mocambo",
              "abstract": "El agua es un recurso esencial y un derecho humano; este estudio evalúa soluciones a corto plazo para comunidades emergentes.",
              "asesor": "Viccelda María Domínguez de Franco",
              "contacto": "viccelda.dominguez@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ingeniería"
            },
            {
              "id": 411,
              "ano": 2024,
              "titulo": "Desarrollo de un adaptador electrónico basado en LoRaWAN para la medición remota de agua en dispositivos tradicionales",
              "abstract": "Con el objetivo de lograr un mundo más interconectado, se diseñó un prototipo para medir consumo de agua y transmitirlo por LoRaWAN.",
              "asesor": "Héctor Poveda",
              "contacto": "hector.poveda@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ingeniería"
            }
          ]
        }
        """
    )


def get_processed_projects() -> list[dict]:
    projects_payload = get_raw_projects_data()
    return [
        {
            "id": project["id"],
            "title": project["titulo"],
            "university": project["universidad"],
            "category": project["categoria"],
            "year": project["ano"],
            "contact": project["contacto"],
            "advisor": project["asesor"],
            "winner": project.get("winner", False),
            "abstract": project["abstract"],
        }
        for project in projects_payload["proyectos"]
    ]


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

