from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.files.images import get_image_dimensions
from django.db.models import Case, When
from django.db.models.functions import Lower
from django.utils import timezone
import re
import unicodedata
from urllib.parse import urlparse, parse_qs
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.documents.models import Document as WagtailDocument
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import AbstractImage, AbstractRendition, Image as WagtailImage
from wagtail.models import PreviewableMixin, Orderable, Page
from .forms.forms import _FaqAdminForm
from .image_pipeline import optimize_and_apply_to_field_file
from .utils import get_video_file_path, get_video_thumbnail_path, get_document_path


IMAGE_MODEL = get_image_model_string()


class FrontendUsageMixin:
    """Shared admin metric: whether an item is expected to appear on frontend."""

    def frontend_usage_count(self) -> int:
        return 1 if getattr(self, "is_active", True) else 0

    frontend_usage_count.short_description = "Usos"


class AutoSortOrderMixin(models.Model):
    """Keep sort_order unique and compact when items are inserted, moved, or deleted."""

    sort_order_group_fields: tuple[str, ...] = ()

    class Meta:
        abstract = True

    def _group_filter(self, source=None) -> dict:
        instance = source or self
        return {field_name: getattr(instance, field_name) for field_name in self.sort_order_group_fields}

    def _group_queryset(self, source=None):
        return self.__class__.objects.filter(**self._group_filter(source=source))

    @staticmethod
    def _normalize_target_order(target_order, max_index: int) -> int:
        if target_order is None:
            return max_index
        return max(0, min(int(target_order), max_index))

    def _reindex_group(self, group_filter: dict, target_pk=None, target_order=None):
        base_ids = list(
            self.__class__.objects.filter(**group_filter)
            .exclude(pk=target_pk)
            .order_by("sort_order", "pk")
            .values_list("pk", flat=True)
        )

        if target_pk is not None:
            insert_at = self._normalize_target_order(target_order, len(base_ids))
            base_ids.insert(insert_at, target_pk)

        instances_by_pk = {
            obj.pk: obj
            for obj in self.__class__.objects.filter(pk__in=base_ids)
        }
        to_update = []
        for index, pk_value in enumerate(base_ids):
            obj = instances_by_pk.get(pk_value)
            if obj and obj.sort_order != index:
                obj.sort_order = index
                to_update.append(obj)
        if to_update:
            self.__class__.objects.bulk_update(to_update, ["sort_order"])

    def save(self, *args, **kwargs):
        old_instance = None
        if self.pk:
            old_instance = self.__class__.objects.filter(pk=self.pk).first()

        with transaction.atomic():
            old_group = self._group_filter(source=old_instance) if old_instance else None
            new_group = self._group_filter()
            requested_position = self.sort_order
            super().save(*args, **kwargs)

            if old_group and old_group != new_group:
                self._reindex_group(old_group)
            self._reindex_group(new_group, target_pk=self.pk, target_order=requested_position)
            self.refresh_from_db(fields=["sort_order"])

    def delete(self, *args, **kwargs):
        group_filter = self._group_filter()
        with transaction.atomic():
            result = super().delete(*args, **kwargs)
            self._reindex_group(group_filter)
            return result


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
        IMAGE_MODEL,
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

class important_date(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
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
    
    
class frequently_ask_question(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
    """Editable question and answer items for the home page."""

    base_form_class = _FaqAdminForm

    CATEGORY_SLUG_CHOICES = [
        ("participacion", "Participación y Equipos"),
        ("plataforma", "Plataforma Tecnológica"),
        ("entregables", "Entregables y Evaluación"),
    ]
    CATEGORY_LABELS = dict(CATEGORY_SLUG_CHOICES)
    CATEGORY_ALIASES = {
        "participacion": "participacion",
        "participacion_y_equipos": "participacion",
        "plataforma": "plataforma",
        "plataforma_tecnologica": "plataforma",
        "entregable": "entregables",
        "entregables": "entregables",
        "entregables_y_evaluacion": "entregables",
    }
    sort_order_group_fields = ("category_slug",)

    category_slug = models.SlugField(
        "Categoría",
        max_length=50,
        choices=CATEGORY_SLUG_CHOICES,
        default="participacion",
        help_text="Selecciona la categoría para esta pregunta",
    )
    category = models.CharField(
        "Etiqueta de categoría",
        max_length=150,
        choices=CATEGORY_SLUG_CHOICES,
        help_text="La etiqueta se sincroniza automáticamente con la categoría seleccionada",
    )
    question  = models.TextField("Pregunta")
    answer = models.TextField("Respuesta")
    sort_order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True, help_text="Activar o desactivar esta pregunta")

    panels = [
        FieldPanel("category_slug"),
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

    @classmethod
    def normalize_category_slug(cls, value) -> str:
        normalized = unicodedata.normalize("NFKD", str(value or "").strip().lower())
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        normalized = normalized.replace("-", "_").replace(" ", "_")
        normalized = "_".join(part for part in normalized.split("_") if part)
        normalized = cls.CATEGORY_ALIASES.get(normalized, normalized)
        if normalized not in cls.CATEGORY_LABELS:
            return "participacion"
        return normalized

    def save(self, *args, **kwargs):
        canonical_slug = self.normalize_category_slug(self.category_slug or self.category)
        self.category_slug = canonical_slug
        self.category = canonical_slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.get_category_slug_display()}: {self.question}"

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/faq_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class background_item(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
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


class jic_category(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
    """Editable category item for the JIC categories section."""

    name = models.CharField("Nombre", max_length=150)
    description = models.TextField("Descripción")
    image = models.ImageField(
        "Ícono",
        upload_to="category_icons/",
        null=True,
        blank=True,
        help_text="Imagen opcional para representar visualmente la categoría.",
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("image"),
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


class award(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
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


class event_intro(FrontendUsageMixin, PreviewableMixin, models.Model):
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
        blank=True,
        help_text="Texto que precede al evento organizador"
    )
    framework_text = models.CharField(
        "Evento organizador",
        max_length=200,
        blank=True,
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
        blank=True,
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


class site_content_settings(FrontendUsageMixin, models.Model):
    """Singleton editable settings for recurring frontend copy and external links."""

    _singleton_id = 1

    platform_url = models.URLField(
        "URL de Plataforma JIC",
        default="https://jic.utp.ac.pa",
        help_text="Enlace usado por los botones y accesos de Plataforma JIC.",
    )
    quick_section_title = models.CharField(
        "Título de accesos rápidos",
        max_length=120,
        default="Accesos rápidos",
    )
    quick_section_description = models.CharField(
        "Descripción de accesos rápidos",
        max_length=240,
        default="Todo lo que necesitas para la JIC en un solo lugar",
    )
    faq_section_title = models.CharField(
        "Título de preguntas frecuentes",
        max_length=120,
        default="Preguntas Frecuentes",
    )
    faq_section_description = models.CharField(
        "Descripción de preguntas frecuentes",
        max_length=240,
        default="Todo lo que necesitas saber sobre la Jornada de Iniciación Científica",
    )
    ridda_url = models.URLField(
        "URL de RIDDA",
        default="https://ridda2.utp.ac.pa",
        help_text="Enlace por defecto para referencias al repositorio institucional.",
    )
    categories_reference_url = models.URLField(
        "URL de referencia para categorías",
        default="https://ridda2.utp.ac.pa",
        help_text="Enlace alternativo cuando no exista documento etiquetado para categorías.",
    )

    panels = [
        FieldPanel("platform_url"),
        FieldPanel("quick_section_title"),
        FieldPanel("quick_section_description"),
        FieldPanel("faq_section_title"),
        FieldPanel("faq_section_description"),
        FieldPanel("ridda_url"),
        FieldPanel("categories_reference_url"),
    ]

    class Meta:
        verbose_name = "Configuración de Contenido del Sitio"
        verbose_name_plural = "Configuración de Contenido del Sitio"

    def save(self, *args, **kwargs):
        self.pk = self._singleton_id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_singleton(cls):
        obj, _created = cls.objects.get_or_create(pk=cls._singleton_id)
        return obj

    def __str__(self) -> str:
        return "Configuración del sitio"


class national_coordinators_section(FrontendUsageMixin, PreviewableMixin, models.Model):
    """Control de visibilidad para la sección de Coordinadores Nacionales - Singleton."""

    _singleton_id = 1

    title = models.CharField(
        "Título de la sección",
        max_length=200,
        default="Coordinadores Nacionales",
        help_text="Título que se muestra en la sección"
    )
    description = models.TextField(
        "Descripción",
        default="Representantes de cada universidad participante en la JIC.",
        help_text="Descripción breve de la sección"
    )
    is_active = models.BooleanField(
        "Mostrar sección",
        default=True,
        help_text="Activar o desactivar la sección completa de Coordinadores Nacionales"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("is_active"),
    ]

    class Meta:
        verbose_name = "Sección de Coordinadores Nacionales"
        verbose_name_plural = "Sección de Coordinadores Nacionales"

    def save(self, *args, **kwargs):
        """Enforce singleton behavior."""
        self.pk = self._singleton_id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of singleton."""
        pass

    @classmethod
    def get_singleton(cls):
        obj, created = cls.objects.get_or_create(pk=cls._singleton_id)
        return obj

    def __str__(self) -> str:
        return self.title


class coordinator(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
    """National coordinator for JIC by university."""

    university_short_name = models.CharField("Sigla Universidad", max_length=20)
    name = models.CharField("Nombre del Coordinador", max_length=200)
    email = models.EmailField("Correo electrónico")
    url = models.URLField("Sitio web de la Universidad", blank=True, help_text="URL opcional de la Universidad")
    college_logo = models.ImageField(
        "Logo de la Universidad",
        upload_to="university_logos/",
        null=True,
        blank=True,
        help_text="Logo de la Universidad"
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)
    is_active = models.BooleanField("Activo", default=True)

    panels = [
        FieldPanel("university_short_name"),
        FieldPanel("name"),
        FieldPanel("email"),
        FieldPanel("url"),
        FieldPanel("college_logo"),
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


class organizer_committee_member(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
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
    label = models.CharField("Nombre", help_text="Nombre con que se muestra el documento", max_length=200)
    href = models.URLField(
        "URL pública",
        blank=True,
        help_text="Enlace público del documento (opcional si eliges un documento del dropdown)",
    )
    document = models.ForeignKey(
        "wagtaildocs.Document",
        on_delete=models.CASCADE,
        verbose_name="Documento",
        help_text="Documento guardado en la biblioteca de documentos",
        null=True,
        blank=True,
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("label"),
        FieldPanel("href"),
        FieldPanel("document"),
        FieldPanel("sort_order"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self) -> str:
        return self.label


class selection_institutional(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, ClusterableModel):
    """Institutional selection results per university per year."""

    university = models.CharField("Universidad", max_length=300)
    short_name = models.CharField("Sigla", max_length=20)
    year = models.PositiveIntegerField("Año JIC")
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
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
        InlinePanel("results", label="Resultados por categoría"),
        InlinePanel("documents", label="Documentos descargables"),
    ]

    class Meta:
        ordering = ["sort_order", "-year", "university"]
        verbose_name = "Selección Institucional"
        verbose_name_plural = "Selecciones Institucionales"

    def __str__(self) -> str:
        return f"{self.short_name} {self.year}"

    @property
    def shortName(self):
        return self.short_name

    @staticmethod
    def format_category_display(category_str) -> str:
        """Convert category slug to display name (e.g., 'ciencias_de_la_salud' -> 'Ciencias de la Salud')."""
        category_map = {
            "ingenieria": "Ingeniería",
            "ciencias_de_la_salud": "Ciencias de la Salud",
            "ciencias_naturales_y_exactas": "Ciencias Naturales y Exactas",
            "ciencias_sociales_y_humanisticas": "Ciencias Sociales y Humanísticas",
        }
        return category_map.get(str(category_str).lower(), str(category_str).title())

    def to_dict(self):
        """Normalize to the same dict structure used by the fallback."""
        return {
            "university": self.university,
            "shortName": self.short_name,
            "year": self.year,
            "results": [
                {
                    "category": self.format_category_display(r.category),
                    "selected": r.selected,
                    "total": r.total
                }
                for r in self.results.all().order_by("sort_order")
            ],
            "documents": [
                {
                    "label": d.label,
                    "url": (d.document.url if d.document else d.href),
                    "filename": (d.document.filename if d.document else ""),
                    "title": (d.document.title if d.document else d.label),
                }
                for d in self.documents.all().order_by("sort_order")
                if (d.document or d.href)
            ],
        }

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/seleccion_institucional_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self, "seleccion": self.to_dict()}


class video(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
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


class resource_document(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
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

    CANONICAL_TAG_ALIASES = {
        "lineamiento": "lineamiento",
        "lineamientos": "lineamiento",
        "manual": "manual",
        "manuales": "manual",
        "memoria": "memoria",
        "memorias": "memoria",
        "ganador": "ganadores",
        "ganadores": "ganadores",
        "estudiante": "estudiante",
        "estudiantes": "estudiante",
        "imprenta": "imprenta",
        "boletin": "boletin",
        "boletines": "boletin",
    }

    @classmethod
    def _normalize_tag(cls, value: str) -> str:
        text = unicodedata.normalize("NFKD", str(value or "").strip().lower())
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"\s+", " ", text)
        return cls.CANONICAL_TAG_ALIASES.get(text, text)

    def _infer_tags_from_title(self) -> set[str]:
        title_key = self._normalize_tag(self.title or "")
        inferred = set()

        for keyword, canonical in self.CANONICAL_TAG_ALIASES.items():
            if keyword in title_key:
                inferred.add(canonical)

        years_in_title = re.findall(r"\b(19\d{2}|20\d{2})\b", self.title or "")
        inferred.update(years_in_title)
        return inferred

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        current_tags = {self._normalize_tag(tag) for tag in self.tags.names()}
        inferred_tags = self._infer_tags_from_title()

        tags_to_add = sorted(inferred_tags.difference(current_tags))
        if tags_to_add:
            self.tags.add(*tags_to_add)


class CustomImage(AbstractImage):
    admin_form_fields = WagtailImage.admin_form_fields

    def save(self, *args, **kwargs):
        field_file = getattr(self, "file", None)
        if field_file and getattr(field_file, "name", "") and not getattr(self, "_compression_in_progress", False):
            self._compression_in_progress = True
            try:
                result = optimize_and_apply_to_field_file(field_file)
                if result:
                    self.file_size = result.final_size
                    if result.replace_file and result.width and result.height:
                        self.width = result.width
                        self.height = result.height
            finally:
                self._compression_in_progress = False

        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name="renditions")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, "width", None) is None or getattr(self, "height", None) is None:
            width = getattr(self, "width", None)
            height = getattr(self, "height", None)

            if self.file:
                try:
                    if hasattr(self.file, "seek"):
                        self.file.seek(0)
                    w, h = get_image_dimensions(self.file)
                    width = width or w
                    height = height or h
                    if hasattr(self.file, "seek"):
                        self.file.seek(0)
                except Exception:
                    pass

            if (not width or not height) and getattr(self, "filter_spec", ""):
                import re
                match = re.search(r"(\d+)x(\d+)", self.filter_spec)
                if match:
                    width = width or int(match.group(1))
                    height = height or int(match.group(2))

            if (not width or not height) and getattr(self, "image", None):
                width = width or getattr(self.image, "width", None)
                height = height or getattr(self.image, "height", None)

            self.width = width or 1
            self.height = height or 1

    def save(self, *args, **kwargs):
        if self.width and self.height:
            return super().save(*args, **kwargs)

        width, height = None, None

        if self.file:
            try:
                if hasattr(self.file, "seek"):
                    self.file.seek(0)
                width, height = get_image_dimensions(self.file)
                if hasattr(self.file, "seek"):
                    self.file.seek(0)
            except Exception:
                pass

        if (not width or not height) and getattr(self, "filter_spec", ""):
            import re

            match = re.search(r"(\d+)x(\d+)", self.filter_spec)
            if match:
                width = width or int(match.group(1))
                height = height or int(match.group(2))

        if (not width or not height) and getattr(self, "image", None):
            width = width or getattr(self.image, "width", None)
            height = height or getattr(self.image, "height", None)

        self.width = width or 1
        self.height = height or 1
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class Gallery(FrontendUsageMixin, ClusterableModel):
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
        IMAGE_MODEL,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name="Imagen"
    )
    collection = models.ForeignKey(
        "wagtailcore.Collection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Colección",
        help_text="Opcional: mover la imagen a una colección específica al guardar.",
    )
    
    category = models.CharField("Año / Edición", max_length=100, blank=True, help_text="Año de la edición (Ej: 2024)")
    year = models.PositiveIntegerField(
        "Año",
        null=True,
        blank=True,
        help_text="Año para ordenar y filtrar en la galería (ej: 2024).",
    )
    description = models.TextField("Descripción", blank=True, help_text="Descripción visible de la imagen")
    alt_text = models.CharField("Leyenda / Accesibilidad", max_length=255, blank=True, help_text="Texto alternativo para lectores de pantalla")
    
    panels = [
        FieldPanel("image"),
        FieldPanel("collection"),
        FieldPanel("category"),
        FieldPanel("year"),
        FieldPanel("description"),
        FieldPanel("alt_text"),
    ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.collection_id or not self.image_id:
            return

        image_obj = self.image
        if image_obj.collection_id != self.collection_id:
            image_obj.collection_id = self.collection_id
            image_obj.save(update_fields=["collection"])
    
    class Meta(Orderable.Meta):
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
        # Keep inline saves compatible with modelcluster, which expects string keys.
        ordering = ["sort_order", "-pk"]


class CollectionResourceVisibility(models.Model):
    collection = models.OneToOneField(
        "wagtailcore.Collection",
        on_delete=models.CASCADE,
        related_name="resource_visibility",
        verbose_name="Colección",
    )
    is_visible_in_resources = models.BooleanField(
        "Visible en galería de Recursos",
        default=True,
        help_text="Controla si esta colección de Wagtail aparece en la pestaña Galería de Recursos.",
    )

    class Meta:
        verbose_name = "Visibilidad de colección en Recursos"
        verbose_name_plural = "Visibilidad de colecciones en Recursos"

    def __str__(self):
        state = "Visible" if self.is_visible_in_resources else "Oculta"
        return f"{self.collection.name} ({state})"


class title_section_image(Orderable):
    """Carousel image for the title/hero section."""
    
    parent = ParentalKey(
        "title_section",
        on_delete=models.CASCADE,
        related_name="carousel_images",
    )
    image = models.ForeignKey(
        IMAGE_MODEL,
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


class title_section(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, ClusterableModel):
    """Editable hero/title section with carousel for the home page."""
    
    title = models.CharField(
        "Título/Subtítulo",
        max_length=200,
        default="JIC Nacional",
        help_text="Texto mostrado en la etiqueta superior (ej: 'JIC Nacional {año}'), el año se calcula automáticamente y no debe incluirse aquí",
        editable=True,
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
        FieldPanel("title", read_only=False),
        FieldPanel("description"),
        FieldPanel("carousel_interval"),
        InlinePanel("carousel_images", label="Imágenes del carrusel", max_num=10),
        InlinePanel("action_buttons", label="Botones de acción", max_num=2),
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
    label = models.CharField("Nombre", help_text="Nombre con que se muestra el documento", max_length=200)
    document_type = models.CharField("Tipo (ej: PDF, XLS)", max_length=50, default="PDF")
    document = models.ForeignKey(
        "wagtaildocs.Document",
        on_delete=models.CASCADE,
        verbose_name="Documento",
        help_text="Documento guardado en la biblioteca de documentos",
        null=True,
        blank=True,
    )
    href = models.URLField(
        "URL pública",
        blank=True,
        help_text="Enlace público del documento (opcional si eliges un documento del dropdown)",
    )
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("label"),
        FieldPanel("document_type"),
        FieldPanel("document"),
        FieldPanel("href"),
        FieldPanel("sort_order"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Documento Nacional"
        verbose_name_plural = "Documentos Nacionales"

    def __str__(self) -> str:
        return self.label


class selection_national(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, ClusterableModel):
    """National selection results per year."""

    year = models.PositiveIntegerField("Año JIC", unique=True)
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
        return f"JIC Nacional {self.year}"

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
            resolved_url = doc.document.url if doc.document else doc.href
            return bool(resolved_url) and (
                doc.document_type.strip().lower() in [t.lower() for t in tipos_permitidos]
                or any(t.lower() in doc.document_type.strip().lower() for t in tipos_permitidos)
            )

        return {
            "year": self.year,
            "totalProjects": self.total_projects,
            "universities": self.universities_count,
            "host_university": self.host_place,
            "results": [
                {
                    "category": r.category, 
                    "category_display": r.get_category_display(),
                    "participating_projects": r.participating_projects, 
                    "winners": r.winners
                }
                for r in self.results.all().order_by("sort_order")
            ],
            "documents": [
                {
                    "label": d.label,
                    "type": d.document_type,
                    "href": (d.document.url if d.document else d.href),
                }
                for d in self.documents.all().order_by("sort_order") if es_documento_real(d)
            ],
        }

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/seleccion_nacional_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self, "seleccion": self.to_dict()}


class consultant(FrontendUsageMixin, models.Model):
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
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="web_consultant_name_ci_unique",
            )
        ]

    def __str__(self) -> str:
        return self.name


class project_category(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
    """Editable catalog of project categories used by investigations."""

    name = models.CharField("Nombre", max_length=150)
    is_active = models.BooleanField("Activo", default=True)
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Categoría de Proyecto"
        verbose_name_plural = "Categorías de Proyecto"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="web_project_category_name_ci_unique",
            )
        ]

    def __str__(self) -> str:
        return self.name

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/jic_category_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class project_university(AutoSortOrderMixin, FrontendUsageMixin, PreviewableMixin, models.Model):
    """Editable catalog of universities used by investigations."""

    name = models.CharField("Nombre", max_length=255)
    short_name = models.CharField("Siglas", max_length=50, blank=True, null=True)
    is_active = models.BooleanField("Activo", default=True)
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("short_name"),
        FieldPanel("is_active"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Universidad de Proyecto"
        verbose_name_plural = "Universidades de Proyecto"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="web_project_university_name_ci_unique",
            )
        ]

    def __str__(self) -> str:
        if self.short_name:
            return f"{self.name} ({self.short_name})"
        return self.name

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/coordinator_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}


class project(FrontendUsageMixin, PreviewableMixin, models.Model):
    """Research/investigation projects by students with canonical category and university names."""

    # Winner status choices
    WINNER_CHOICES = [
        (0, "No ganador"),
        (1, "Primer lugar"),
        (2, "Segundo lugar"),
        (3, "Tercer lugar"),
    ]

    # Canonical project categories with aliases for robust filtering
    CATEGORY_CHOICES = [
        ("Ingeniería", "Ingeniería"),
        ("Ciencias de la Salud", "Ciencias de la Salud"),
        ("Ciencias Naturales y Exactas", "Ciencias Naturales y Exactas"),
        ("Ciencias Sociales y Humanísticas", "Ciencias Sociales y Humanísticas"),
    ]
    CATEGORY_LABELS = dict(CATEGORY_CHOICES)
    CATEGORY_ALIASES = {
        # Lowercase versions
        "ingenieria": "Ingeniería",
        "ingenierias": "Ingeniería",
        # Salud variants
        "de la salud": "Ciencias de la Salud",
        "salud": "Ciencias de la Salud",
        "ciencias de la salud": "Ciencias de la Salud",
        # Naturales y exactas
        "naturales y exactas": "Ciencias Naturales y Exactas",
        "ciencias naturales y exactas": "Ciencias Naturales y Exactas",
        # Sociales y humanísticas
        "ciencias sociales": "Ciencias Sociales y Humanísticas",
        "sociales y humanisticas": "Ciencias Sociales y Humanísticas",
        "ciencias sociales y humanisticas": "Ciencias Sociales y Humanísticas",
        # Index numbers (from legacy imports)
        "0": "Ingeniería",
        "1": "Ciencias de la Salud",
        "2": "Ciencias Naturales y Exactas",
        "3": "Ciencias Sociales y Humanísticas",
    }

    # Official university names with aliases for robust filtering
    OFFICIAL_UNIVERSITIES = [
        "Universidad Católica Santa María la Antigua",
        "Universidad Especializada de las Américas",
        "Universidad Internacional de Ciencia y Tecnología",
        "Universidad Latina de Panamá",
        "Universidad Marítima Internacional de Panamá",
        "Universidad Metropolitana de Educación, Ciencia y Tecnología",
        "Universidad Santander",
        "Universidad Tecnológica de Oteima",
        "Universidad Tecnológica de Panamá",
        "Universidad de Panamá",
    ]
    UNIVERSITY_ALIASES = {
        # USMA variants
        "universidad catolica santa maria la antigua": "Universidad Católica Santa María la Antigua",
        "universidad catolica santa maria la antigua usma": "Universidad Católica Santa María la Antigua",
        "usma": "Universidad Católica Santa María la Antigua",
        # UTP variants
        "universidad tecnologica de panama": "Universidad Tecnológica de Panamá",
        "utp": "Universidad Tecnológica de Panamá",
        # UP variants
        "universidad de panama": "Universidad de Panamá",
        "up": "Universidad de Panamá",
        # UMECIT variants
        "universidad metropolitana de educacion ciencia y tecnologia": "Universidad Metropolitana de Educación, Ciencia y Tecnología",
        "umecit": "Universidad Metropolitana de Educación, Ciencia y Tecnología",
        # Udelas variants
        "universidad especializada de las americas": "Universidad Especializada de las Américas",
        "udelas": "Universidad Especializada de las Américas",
        # Others
        "universidad internacional de ciencia y tecnologia": "Universidad Internacional de Ciencia y Tecnología",
        "unicyt": "Universidad Internacional de Ciencia y Tecnología",
        "universidad latina de panama": "Universidad Latina de Panamá",
        "ulat": "Universidad Latina de Panamá",
        "universidad maritima internacional de panama": "Universidad Marítima Internacional de Panamá",
        "umip": "Universidad Marítima Internacional de Panamá",
        "universidad santander": "Universidad Santander",
        "universidad tecnologica de oteima": "Universidad Tecnológica de Oteima",
    }

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
    university_catalog = models.ForeignKey(
        "project_university",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="Universidad (catálogo)",
    )
    university = models.CharField(
        "Universidad",
        max_length=255,
        help_text="Se normaliza automáticamente a nombres canónicos (mayúsculas, acentos, etc.)",
    )
    university_short_name = models.CharField(
        "Siglas",
        max_length=50,
        blank=True,
        null=True,
        help_text="Siglas de la Universidad",
    )
    category_catalog = models.ForeignKey(
        "project_category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="Categoría (catálogo)",
    )
    category = models.CharField(
        "Categoría",
        max_length=255,
        help_text="Se normaliza automáticamente a nombres canónicos (Ingeniería, Ciencias de la Salud, etc.)",
    )
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
        FieldPanel("university_catalog"),
        FieldPanel("university_short_name"),
        FieldPanel("category_catalog"),
        FieldPanel("winner"),
    ]

    class Meta:
        ordering = ["-year", "title"]
        verbose_name = "Investigación"
        verbose_name_plural = "Investigaciones"
        constraints = [
            models.UniqueConstraint(
                Lower("title"),
                models.F("year"),
                name="web_project_title_year_ci_unique",
            )
        ]

    @staticmethod
    def _normalize_text_key(raw_value) -> str:
        """Convert any text to normalized ASCII lowercase key for matching (strips accents, punctuation)."""
        value = str(raw_value or "").strip().lower()
        value = unicodedata.normalize('NFD', value)
        value = ''.join(ch for ch in value if unicodedata.category(ch) != 'Mn')  # Remove diacritics
        value = ''.join(ch if ch.isalnum() or ch.isspace() else ' ' for ch in value)
        return ' '.join(value.split())

    @classmethod
    def normalize_category(cls, value) -> str:
        """Map category variants to canonical label (e.g., 'ingenieria' -> 'Ingeniería')."""
        if not value:
            return "Ingeniería"  # default
        
        normalized_key = cls._normalize_text_key(value)
        canonical = cls.CATEGORY_ALIASES.get(normalized_key, value.strip())
        
        # If result is in official labels, return it; otherwise return original
        if canonical in cls.CATEGORY_LABELS:
            return canonical
        
        return value.strip()

    @classmethod
    def normalize_university(cls, value) -> str:
        """Map university name variants to canonical label."""
        if not value:
            return ""
        
        normalized_key = cls._normalize_text_key(value)
        
        # First check aliases (handles abbreviations + variants)
        if normalized_key in cls.UNIVERSITY_ALIASES:
            return cls.UNIVERSITY_ALIASES[normalized_key]
        
        # Check if input matches any official university (after normalization)
        for official in cls.OFFICIAL_UNIVERSITIES:
            if cls._normalize_text_key(official) == normalized_key:
                return official
        
        # Return original value if no canonical match found (first-seen behavior)
        return value.strip()

    def save(self, *args, **kwargs):
        # Keep text fields synchronized for templates/services that still consume raw strings.
        normalized_category = self.normalize_category(self.category)
        normalized_university = self.normalize_university(self.university)

        if self.category_catalog:
            normalized_category = self.category_catalog.name
        elif normalized_category:
            existing_category = project_category.objects.filter(name__iexact=normalized_category).first()
            if existing_category:
                self.category_catalog = existing_category
            else:
                self.category_catalog = project_category.objects.create(name=normalized_category)

        if self.university_catalog:
            normalized_university = self.university_catalog.name
            if not self.university_short_name:
                self.university_short_name = self.university_catalog.short_name
        elif normalized_university:
            existing_university = project_university.objects.filter(name__iexact=normalized_university).first()
            if existing_university:
                self.university_catalog = existing_university
            else:
                self.university_catalog = project_university.objects.create(name=normalized_university)

        self.category = normalized_category
        self.university = normalized_university

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    def get_preview_template(self, request, mode_name):
        return "utilidades/previews/investigacion_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}
