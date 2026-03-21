from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import Case, When
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.documents.models import Document as WagtailDocument
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import PreviewableMixin, Orderable, Page
from .forms import _FaqAdminForm
from .utils import get_video_file_path, get_video_thumbnail_path, get_document_path


class BlogIndexPage(Page):
    """Root page for the news/blog section managed with Wagtail."""

    intro = models.TextField("Introducción", blank=True)

    template = "utilidades/noticias/index.html"
    max_count = 1
    parent_page_types = ["wagtailcore.Page", "home.HomePage"]
    subpage_types = ["web.BlogPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]


class BlogPage(Page):
    """Article page with StreamField content, suitable for editor-reviewed submissions."""

    publication_date = models.DateField("Fecha", default=timezone.now)
    excerpt = models.TextField("Resumen", blank=True, max_length=320)
    author_name = models.CharField("Autor", max_length=120, blank=True)
    is_external_submission = models.BooleanField(
        "Envío externo",
        default=False,
        help_text="Marcar cuando la nota fue enviada por un colaborador externo.",
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Imagen destacada",
    )
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title", icon="title", label="Encabezado")),
            (
                "paragraph",
                blocks.RichTextBlock(
                    features=["h2", "h3", "bold", "italic", "link", "ol", "ul", "document-link"],
                    label="Párrafo",
                ),
            ),
            ("image", ImageChooserBlock(label="Imagen")),
            ("quote", blocks.BlockQuoteBlock(label="Cita")),
            ("embed", EmbedBlock(label="Contenido embebido")),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Contenido",
    )

    template = "utilidades/noticias/detail.html"
    parent_page_types = ["web.BlogIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("publication_date"),
        FieldPanel("excerpt"),
        FieldPanel("author_name"),
        FieldPanel("is_external_submission"),
        FieldPanel("cover_image"),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"

class important_date(PreviewableMixin, models.Model):
    """Editable timeline item for the home page."""

    title = models.CharField("Título", max_length=150, default="Selección Nacional")
    date_text = models.CharField(
        "Texto de la fecha", 
        max_length=200, 
        blank=True,
        help_text="Ej: 'Del 04 de mayo al 31 de agosto' o 'Hasta el 15 de septiembre'."
    )
    event_date = models.DateField(
        "Fecha para ordenar", 
        help_text="Fecha base usada internamente para ordenar cronológicamente."
    )
    description = models.TextField("Descripción")
    is_primary = models.BooleanField(
        "Fecha principal",
        default=True,
        help_text="Si está activa, se mostrará también en la página de inicio."
    )
    is_active = models.BooleanField("Activo", default=True, help_text="Activar o desactivar esta fecha")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("date_text"),
        FieldPanel("event_date"),
        FieldPanel("description"),
        FieldPanel("is_primary"),
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order", "event_date"]
        verbose_name = "Fecha importante"
        verbose_name_plural = "Fechas importantes"

    def __str__(self) -> str:
        return f"{self.title} ({self.event_date:%Y-%m-%d})"

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/important_date_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}
    
    
class frequently_ask_question(PreviewableMixin, models.Model):
    """Editable question and answer items for the home page."""

    base_form_class = _FaqAdminForm

    CATEGORY_SLUG_CHOICES = [
        ("participacion", "Participación y Equipos"),
        ("plataforma", "Plataforma Tecnológica"),
        ("entregables", "Entregables y Evaluación"),
    ]

    category_slug = models.SlugField(
        "Slug de categoría",
        max_length=50,
        choices=CATEGORY_SLUG_CHOICES,
        default="participacion",
        help_text="Identificador interno de la categoría (ej: participacion, plataforma, entregables)",
    )
    category = models.CharField("Categoría", max_length=150, choices=CATEGORY_SLUG_CHOICES)
    question  = models.TextField("Pregunta")
    answer = models.TextField("Respuesta")
    sort_order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True, help_text="Activar o desactivar esta pregunta")

    panels = [
        FieldPanel("category_slug"),
        FieldPanel("category"),
        FieldPanel("question"),
        FieldPanel("answer"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        ordering = [
            Case(
                When(category_slug='participacion', then=0),
                When(category_slug='plataforma', then=1),
                When(category_slug='entregables', then=2),
            ),
            'sort_order'
        ]
        verbose_name = "Pregunta frecuente"
        verbose_name_plural = "Preguntas frecuentes"

    def __str__(self) -> str:
        return f"{self.category}: {self.question}"

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/faq_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class background_item(PreviewableMixin, models.Model):
    """Editable timeline item for the JIC background/history section."""

    year_label = models.CharField("Año / Período", max_length=20)
    description = models.TextField("Descripción")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("year_label"),
        FieldPanel("description"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Antecedente"
        verbose_name_plural = "Antecedentes"

    def __str__(self) -> str:
        return self.year_label

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/background_item_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class jic_category(PreviewableMixin, models.Model):
    """Editable category item for the JIC categories section."""

    name = models.CharField("Nombre", max_length=150)
    description = models.TextField("Descripción")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Categoría JIC"
        verbose_name_plural = "Categorías JIC"

    def __str__(self) -> str:
        return self.name

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/jic_category_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class award(PreviewableMixin, models.Model):
    """Editable award/recognition item for the JIC recognitions section."""

    prize = models.CharField("Premio", max_length=200)
    year = models.CharField("Año", max_length=10)
    entity = models.CharField("Entidad", max_length=200)
    description = models.TextField("Descripción")
    sort_order = models.PositiveIntegerField("Orden", default=0)
    image = models.ImageField(
        "Logo del evento",
        upload_to="awards_logos/",
        null=True,
        blank=True,
        help_text="Logo a mostrar junto a la descripción"
    )

    panels = [
        FieldPanel("prize"),
        FieldPanel("year"),
        FieldPanel("entity"),
        FieldPanel("description"),
        FieldPanel("sort_order"),
        FieldPanel("image"),
    ]

    class Meta:
        ordering = ["sort_order", "year"]
        verbose_name = "Reconocimiento"
        verbose_name_plural = "Reconocimientos"

    def __str__(self) -> str:
        return f"{self.prize} ({self.year})"

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/award_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class event_intro(PreviewableMixin, models.Model):
    """Editable event introduction section with logo and descriptions - Singleton."""

    # Singleton pattern: always use the same primary key for the single instance
    _singleton_id = 1

    title = models.CharField(
        "Título principal",
        max_length=200,
        help_text="Ej: JIC Nacional"
    )
    main_description = models.TextField(
        "Descripción principal",
        help_text="Descripción del evento y contexto"
    )
    secondary_description = models.TextField(
        "Descripción secundaria",
        help_text="Información adicional o llamado a la acción"
    )
    framework_label = models.CharField(
        "Etiqueta de marco",
        max_length=100,
        default="En el marco de",
        help_text="Texto que precede al evento organizador"
    )
    framework_text = models.CharField(
        "Evento organizador",
        max_length=200,
        help_text="Ej: Congreso IESTEC"
    )
    logo_image = models.FileField(
        "Logo del evento",
        upload_to="event_logos/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'webp'])],
        help_text="Logo a mostrar junto a la descripción (Se aceptan PNG, JPG, SVG)"
    )
    logo_fallback_text = models.CharField(
        "Texto de respaldo para logo",
        max_length=50,
        default="Logo del evento",
        help_text="Texto a mostrar si la imagen no carga"
    )
    is_active = models.BooleanField(
        "Activo",
        default=True,
        help_text="Activar o desactivar esta sección"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("main_description"),
        FieldPanel("secondary_description"),
        FieldPanel("framework_label"),
        FieldPanel("framework_text"),
        FieldPanel("logo_image"),
        FieldPanel("logo_fallback_text"),
        FieldPanel("is_active"),
    ]

    class Meta:
        verbose_name = "Introducción del Evento"
        verbose_name_plural = "Introducción del Evento"

    def save(self, *args, **kwargs):
        """Override save to enforce singleton behavior - always use the same primary key."""
        self.pk = self._singleton_id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance."""
        pass

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=cls._singleton_id)
        return obj

    def __str__(self) -> str:
        return self.title

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/event_intro_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class coordinator(PreviewableMixin, models.Model):
    """National coordinator for JIC by university."""

    university_short_name = models.CharField("Sigla Universidad", max_length=20)
    name = models.CharField("Nombre del Coordinador", max_length=200)
    email = models.EmailField("Correo electrónico")
    photo = models.ImageField(
        "Foto del coordinador",
        upload_to="coordinators_photos/",
        null=True,
        blank=True,
        help_text="Foto de perfil del coordinador"
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    panels = [
        FieldPanel("university_short_name"),
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("photo"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Coordinador Nacional"
        verbose_name_plural = "Coordinadores Nacionales"

    def __str__(self) -> str:
        return f"{self.university_short_name} - {self.name}"

    @property
    def shortName(self):
        """Compatibility property for templates"""
        return self.university_short_name

    @property
    def coordinator(self):
        """Compatibility property for templates"""
        return self.name

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/coordinator_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class organizer_committee_member(PreviewableMixin, models.Model):
    """Member of the JIC organizing committee."""

    name = models.CharField("Nombre", max_length=200)
    role = models.CharField("Rol/Posición", max_length=200)
    institution = models.CharField("Institución", max_length=200)
    photo = models.ImageField(
        "Foto del miembro",
        upload_to="organizer_photos/",
        null=True,
        blank=True,
        help_text="Foto de perfil del miembro del comité"
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("institution"),
        FieldPanel("photo"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Miembro del Comité Organizador"
        verbose_name_plural = "Miembros del Comité Organizador"

    def __str__(self) -> str:
        return f"{self.name} - {self.role}"

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/organizer_committee_member_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}

    def get_dict(self):
        """Return as dict for template compatibility"""
        return {"name": self.name, "role": self.role, "institution": self.institution}


class selection_result(Orderable):
    """One category row within an institutional selection record."""

    CATEGORIES_CHOICES = [
        ("ingenieria", "Ingeniería"),
        ("ciencias_de_la_salud", "Ciencias de la Salud"),
        ("ciencias_naturales_y_exactas", "Ciencias Naturales y Exactas"),
        ("ciencias_sociales_y_humanisticas", "Ciencias Sociales y Humanísticas"),
    ]
    parent = ParentalKey(
        "selection_institutional",
        on_delete=models.CASCADE,
        related_name="results",
    )
    category = models.CharField("Categoría", max_length=150, choices=CATEGORIES_CHOICES)
    selected = models.PositiveIntegerField("Seleccionados")
    total = models.PositiveIntegerField("Total presentados")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("category"),
        FieldPanel("selected"),
        FieldPanel("total"),
        FieldPanel("sort_order"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Resultado por categoría"
        verbose_name_plural = "Resultados por categoría"

    def __str__(self) -> str:
        return f"{self.category}: {self.selected}/{self.total}"


class selection_document(Orderable):
    """Downloadable document linked to an institutional selection record."""

    parent = ParentalKey(
        "selection_institutional",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    label = models.CharField("Etiqueta", max_length=200)
    href = models.URLField("Enlace", help_text="URL pública del documento")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("label"),
        FieldPanel("href"),
        FieldPanel("sort_order"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self) -> str:
        return self.label


class selection_institutional(PreviewableMixin, ClusterableModel):
    """Institutional selection results per university per year."""

    STATUS_CHOICES = [
        ("completada", "Completada"),
        ("en_proceso", "En proceso"),
        ("pendiente", "Pendiente"),
    ]

    university = models.CharField("Universidad", max_length=300)
    short_name = models.CharField("Sigla", max_length=20)
    year = models.PositiveIntegerField("Año JIC")
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendiente",
    )
    is_active = models.BooleanField(
        "Activo",
        default=True,
        help_text="Si está desactivado, esta universidad no aparecerá en la página. Si todas están desactivadas, la página redirige a Resultados.",
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("university"),
        FieldPanel("short_name"),
        FieldPanel("year"),
        FieldPanel("status"),
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
        InlinePanel("results", label="Resultados por categoría"),
        InlinePanel("documents", label="Documentos descargables"),
    ]

    class Meta:
        ordering = ["sort_order", "university"]
        verbose_name = "Selección Institucional"
        verbose_name_plural = "Selecciones Institucionales"

    def __str__(self) -> str:
        return f"{self.short_name} {self.year} ({self.get_status_display()})"

    @property
    def shortName(self):
        return self.short_name

    def to_dict(self):
        """Normalize to the same dict structure used by the fallback."""
        return {
            "university": self.university,
            "shortName": self.short_name,
            "year": self.year,
            "status": self.status,
            "results": [
                {"category": r.category, "selected": r.selected, "total": r.total}
                for r in self.results.all().order_by("sort_order")
            ],
            "documents": [
                {"label": d.label, "href": d.href}
                for d in self.documents.all().order_by("sort_order")
            ],
        }

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/seleccion_institucional_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self, "seleccion": self.to_dict()}


class video(PreviewableMixin, models.Model):
    """Editable video file for multimedia resources."""

    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descripción", blank=True)
    video_file = models.FileField(
        "Archivo de video",
        upload_to=get_video_file_path,
        null=True,
        blank=True,
        help_text="Formatos soportados: MP4, WebM, Ogg (máx 500MB). Deja en blanco si usas YouTube."
    )
    youtube_url = models.URLField(
        "Enlace de YouTube",
        blank=True,
        help_text="Ej: https://www.youtube.com/watch?v=oispNb8t79o"
    )
    thumbnail = models.ImageField(
        "Miniatura",
        upload_to=get_video_thumbnail_path,
        null=True,
        blank=True,
        help_text="Imagen de previsualización para el video"
    )
    duration_seconds = models.PositiveIntegerField(
        "Duración (segundos)",
        null=True,
        blank=True,
        help_text="Duración total del video en segundos"
    )
    category = models.CharField(
        "Categoría",
        max_length=100,
        blank=True,
        help_text="Ej: Tutorial, Presentación, Promocional"
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField(
        "Activo",
        default=True,
        help_text="Activar o desactivar este video"
    )
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("video_file"),
        FieldPanel("youtube_url"),
        FieldPanel("thumbnail"),
        FieldPanel("duration_seconds"),
        FieldPanel("category"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        ordering = ["sort_order", "-created_at"]
        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self) -> str:
        return self.title

    def get_preview_thumbnail_url(self) -> str | None:
        if self.thumbnail and getattr(self.thumbnail, "url", None):
            return self.thumbnail.url

        if not self.youtube_url:
            return None

        try:
            parsed = urlparse(self.youtube_url)
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

    @property
    def preview_unavailable_reason(self) -> str:
        return (
            "En el panel de administración no siempre se permite incrustar reproductores externos "
            "(como YouTube) por políticas de seguridad/CSP."
        )

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/video_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class resource_document(PreviewableMixin, models.Model):
    """Editable document file for resources, organized by type and year."""

    DOC_TYPE_CHOICES = [
        ("lineamientos", "Lineamientos"),
        ("plantillas", "Plantillas"),
        ("memorias", "Memorias"),
        ("boletines", "Boletines"),
        ("actas", "Actas de Resultados"),
        ("otros", "Otros"),
    ]

    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descripción", blank=True)
    doc_type = models.CharField(
        "Tipo de documento",
        max_length=50,
        choices=DOC_TYPE_CHOICES,
        default="otros",
        help_text="Clasificación del documento"
    )
    document_file = models.FileField(
        "Archivo",
        upload_to=get_document_path,
        help_text="Formatos soportados: PDF, DOCX, XLS, etc."
    )
    year = models.PositiveIntegerField(
        "Año JIC",
        null=True,
        blank=True,
        help_text="Año al que corresponde el documento (ej: 2025, 2024)"
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField(
        "Activo",
        default=True,
        help_text="Activar o desactivar este documento"
    )
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("doc_type"),
        FieldPanel("document_file"),
        FieldPanel("year"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        ordering = ["-year", "doc_type", "sort_order"]
        verbose_name = "Documento de Recurso"
        verbose_name_plural = "Documentos de Recursos"

    def __str__(self) -> str:
        year_display = f"JIC {self.year}" if self.year else "Sin año"
        return f"{year_display} - {self.get_doc_type_display()}"
    
    def get_year_type_display(self) -> str:
        """Returns a readable combination of year and type for easier filtering."""
        year_display = f"JIC {self.year}" if self.year else "Sin año"
        return f"{year_display} - {self.get_doc_type_display()}"

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/resource_document_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class Document(WagtailDocument):
    """Custom Wagtail document model with activation toggle."""

    is_active = models.BooleanField("Activo", default=True)

    admin_form_fields = WagtailDocument.admin_form_fields + ("is_active",)


class Gallery(ClusterableModel):
    """
    Singleton gallery snippet to manage ordered images.
    Uses InlinePanel for drag-and-drop reordering of images.
    """
    _singleton_id = 1
    
    title = models.CharField("Título de la galería", max_length=150, default="Galería Principal")
    description = models.TextField("Descripción", blank=True, help_text="Descripción opcional de la galería.")
    
    def clean(self):
        # Prevent creating more than one instance
        if not self.pk and Gallery.objects.exists():
            raise ValidationError("Ya existe una galería creada. Solo se permite una galería principal.")
            
    def save(self, *args, **kwargs):
        self.pk = self._singleton_id
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        pass # Prevent deletion
        
    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        InlinePanel("gallery_images", label="Imágenes ordenables"),
    ]
    
    class Meta:
        verbose_name = "Galería de Fotos"
        verbose_name_plural = "Galería de Fotos"
        
    def __str__(self):
        return self.title


class GalleryImage(Orderable):
    gallery = ParentalKey(Gallery, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name="Imagen"
    )
    
    category = models.CharField("Año / Edición", max_length=100, blank=True, help_text="Año de la edición (Ej: 2024)")
    description = models.TextField("Descripción", blank=True, help_text="Descripción visible de la imagen")
    alt_text = models.CharField("Leyenda / Accesibilidad", max_length=255, blank=True, help_text="Texto alternativo para lectores de pantalla")
    
    panels = [
        FieldPanel("image"),
        FieldPanel("category"),
        FieldPanel("description"),
        FieldPanel("alt_text"),
    ]
    
    class Meta(Orderable.Meta):
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"


class title_section_image(Orderable):
    """Carousel image for the title/hero section."""
    
    parent = ParentalKey(
        "title_section",
        on_delete=models.CASCADE,
        related_name="carousel_images",
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name="Imagen del carrusel"
    )
    alt_text = models.CharField(
        "Texto alternativo",
        max_length=300,
        help_text="Descripción para accesibilidad"
    )
    
    panels = [
        FieldPanel("image"),
        FieldPanel("alt_text"),
    ]
    
    class Meta(Orderable.Meta):
        verbose_name = "Imagen del carrusel"
        verbose_name_plural = "Imágenes del carrusel"
        ordering = ["sort_order"]
    
    def __str__(self):
        return f"Imagen {self.sort_order + 1}"


class title_section_button(Orderable):
    """Action button for the title/hero section."""
    
    parent = ParentalKey(
        "title_section",
        on_delete=models.CASCADE,
        related_name="action_buttons",
    )
    label = models.CharField("Etiqueta del botón", max_length=100)
    url = models.CharField(
        "URL / Ruta",
        max_length=500,
        help_text="URL externa (ej: https://...) o ruta de Django (ej: nombre_vista)"
    )
    button_type = models.CharField(
        "Tipo de botón",
        max_length=20,
        choices=[
            ("primary", "Primario (Destacado)"),
            ("secondary", "Secundario"),
        ],
        default="primary"
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)
    
    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
        FieldPanel("button_type"),
        FieldPanel("sort_order"),
    ]
    
    class Meta(Orderable.Meta):
        verbose_name = "Botón de acción"
        verbose_name_plural = "Botones de acción"
        ordering = ["sort_order"]
    
    def __str__(self):
        return self.label


class title_section(PreviewableMixin, ClusterableModel):
    """Editable hero/title section with carousel for the home page."""
    
    title = models.CharField(
        "Título/Subtítulo",
        max_length=200,
        default="JIC Nacional",
        help_text="Texto mostrado en la etiqueta superior (ej: 'JIC Nacional {año}'), el año se calcula automáticamente y no debe incluirse aquí",
        editable=False,
    )
    description = models.TextField(
        "Descripción",
        default="Fomentando la investigación entre jóvenes universitarios a nivel nacional. Una iniciativa de la Secretaría Nacional de Ciencia, Tecnología e Innovación.",
        help_text="Párrafo descriptivo principal"
    )
    carousel_interval = models.PositiveIntegerField(
        "Intervalo del carrusel (ms)",
        default=8000,
        help_text="Milisegundos entre cambios automáticos (8000 = 8 segundos)"
    )
    is_active = models.BooleanField(
        "Activo",
        default=True,
        help_text="Mostrar u ocultar esta sección"
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)
    
    panels = [
        FieldPanel("title", read_only=True),
        FieldPanel("description"),
        FieldPanel("carousel_interval"),
        InlinePanel("carousel_images", label="Imágenes del carrusel", max_num=10),
        InlinePanel("action_buttons", label="Botones de acción", max_num=5),
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
    ]
    
    class Meta:
        verbose_name = "Sección de Título/Hero"
        verbose_name_plural = "Secciones de Título/Hero"
        ordering = ["sort_order"]
    
    def __str__(self):
        return f"Hero Section - {self.title}"
    
    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/title_section_preview.html"
    
    def get_preview_context(self, request, mode_name):
        return {"snippet": self}



class selection_national_result(Orderable):
    """One category row within a national selection record."""

    CATEGORIES_CHOICES = [
        ("ingenieria", "Ingeniería"),
        ("ciencias_de_la_salud", "Ciencias de la Salud"),
        ("ciencias_naturales_y_exactas", "Ciencias Naturales y Exactas"),
        ("ciencias_sociales_y_humanisticas", "Ciencias Sociales y Humanísticas"),
    ]
    parent = ParentalKey(
        "selection_national",
        on_delete=models.CASCADE,
        related_name="results",
    )
    category = models.CharField("Categoría", max_length=150, choices=CATEGORIES_CHOICES)
    participating_projects = models.PositiveIntegerField("Proyectos Participantes")
    winners = models.PositiveIntegerField("Ganadores")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("category"),
        FieldPanel("participating_projects"),
        FieldPanel("winners"),
        FieldPanel("sort_order"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Resultado Nacional por categoría"
        verbose_name_plural = "Resultados Nacionales por categoría"

    def __str__(self) -> str:
        return f"{self.category}: {self.winners} ganadores / {self.participating_projects} participantes"


class selection_national_document(Orderable):
    """Downloadable document linked to a national selection record."""

    parent = ParentalKey(
        "selection_national",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    label = models.CharField("Etiqueta", max_length=200)
    document_type = models.CharField("Tipo (ej: PDF, XLS)", max_length=50, default="PDF")
    href = models.URLField("Enlace", help_text="URL pública del documento")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("label"),
        FieldPanel("document_type"),
        FieldPanel("href"),
        FieldPanel("sort_order"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Documento Nacional"
        verbose_name_plural = "Documentos Nacionales"

    def __str__(self) -> str:
        return self.label


class selection_national(PreviewableMixin, ClusterableModel):
    """National selection results per year."""

    STATUS_CHOICES = [
        ("finalizada", "Finalizada"),
        ("en proceso", "En proceso"),
    ]

    year = models.PositiveIntegerField("Año JIC", unique=True)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=STATUS_CHOICES,
        default="en proceso",
    )
    total_projects = models.PositiveIntegerField("Total de Proyectos (Histórico)", default=0, help_text="Para datos históricos, si no se usan los resultados por categoría.")
    host_place = models.CharField(
        "Sede", 
        max_length=300, 
        blank=True, 
        null=True,
        help_text="Lugar donde se lleva a cabo el evento nacional (Opcional)"
    )
    universities_count = models.PositiveIntegerField("Universidades Participantes", default=5)
    is_active = models.BooleanField(
        "Activo",
        default=True,
        help_text="Activar para mostrar estos resultados nacionales en la página.",
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("year"),
        FieldPanel("status"),
        FieldPanel("total_projects"),
        FieldPanel("host_place"),
        FieldPanel("universities_count"),
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
        InlinePanel("results", label="Resultados por categoría"),
        InlinePanel("documents", label="Documentos descargables"),
    ]

    class Meta:
        ordering = ["-year", "sort_order"]
        verbose_name = "Selección Nacional"
        verbose_name_plural = "Selecciones Nacionales"

    def __str__(self) -> str:
        return f"JIC Nacional {self.year} ({self.get_status_display()})"

    @property
    def host_university(self):
        # Backward compatibility for templates/views still using the old key.
        return self.host_place

    def to_dict(self):
        """Normalize to a dict structure. Solo documentos reales (con href y tipo relevante)."""
        # Puedes ajustar los tipos permitidos aquí:
        tipos_permitidos = ["PDF", "Actas de Resultados", "acta", "actas"]
        def es_documento_real(doc):
            # Solo documentos con href no vacío y tipo relevante
            return bool(doc.href) and (
                doc.document_type.strip().lower() in [t.lower() for t in tipos_permitidos]
                or any(t.lower() in doc.document_type.strip().lower() for t in tipos_permitidos)
            )

        return {
            "year": self.year,
            "status": self.status,
            "totalProjects": self.total_projects,
            "universities": self.universities_count,
            "host_university": self.host_place,
            "results": [
                {
                    "category": r.category, 
                    "participating_projects": r.participating_projects, 
                    "winners": r.winners
                }
                for r in self.results.all().order_by("sort_order")
            ],
            "documents": [
                {"label": d.label, "type": d.document_type, "href": d.href}
                for d in self.documents.all().order_by("sort_order") if es_documento_real(d)
            ],
        }

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/seleccion_nacional_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self, "seleccion": self.to_dict()}


class consultant(models.Model):
    """Advisor/teacher for research projects."""

    name = models.CharField("Nombre", max_length=200)
    email = models.EmailField("Correo electrónico", blank=True)
    institution = models.CharField("Institución", max_length=255, blank=True)
    is_active = models.BooleanField("Activo", default=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("institution"),
        FieldPanel("is_active"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = "Asesor"
        verbose_name_plural = "Asesores"

    def __str__(self) -> str:
        return self.name


class project(PreviewableMixin, models.Model):
    """Research/investigation projects by students."""

    WINNER_CHOICES = [
        (0, "No ganador"),
        (1, "Primer lugar"),
        (2, "Segundo lugar"),
        (3, "Tercer lugar"),
    ]

    year = models.PositiveIntegerField("Año")
    title = models.CharField("Título", max_length=500)
    abstract = models.TextField("Resumen")
    advisor = models.ForeignKey(
        consultant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="investigations",
        verbose_name="Asesor",
    )
    university = models.CharField("Universidad", max_length=255)    
    university_short_name = models.CharField("Siglas", max_length=50, blank=True, null=True, help_text="Siglas de la Universidad")    
    category = models.CharField("Categoría", max_length=255)
    winner = models.PositiveSmallIntegerField(
        "Estado de Premio",
        choices=WINNER_CHOICES,
        default=0,
    )

    panels = [
        FieldPanel("year"),
        FieldPanel("title"),
        FieldPanel("abstract"),
        FieldPanel("advisor"),
        FieldPanel("university"),
        FieldPanel("university_short_name"),
        FieldPanel("category"),
        FieldPanel("winner"),
    ]

    class Meta:
        ordering = ["-year", "title"]
        verbose_name = "Investigación"
        verbose_name_plural = "Investigaciones"

    def __str__(self) -> str:
        return self.title

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/investigacion_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}
