from django.db import models
from django.db.models import Case, When
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import PreviewableMixin, Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from .forms import _FaqAdminForm


class important_date(PreviewableMixin, models.Model):
    """Editable timeline item for the home page."""

    title = models.CharField("Título", max_length=150)
    event_date = models.DateField("Fecha del evento")
    description = models.TextField("Descripción")
    is_active = models.BooleanField("Activo", default=True, help_text="Activar o desactivar esta fecha")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("event_date"),
        FieldPanel("description"),
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
        return "web/previews/important_date_preview.html"

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
        return "web/previews/faq_preview.html"

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
        return "web/previews/background_item_preview.html"

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
        return "web/previews/jic_category_preview.html"

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
        return "web/previews/award_preview.html"

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
    logo_image = models.ImageField(
        "Logo del evento",
        upload_to="event_logos/",
        null=True,
        blank=True,
        help_text="Logo a mostrar junto a la descripción"
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
        verbose_name = "Intro del Evento"
        verbose_name_plural = "Intro del Evento"

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
        return "web/previews/event_intro_preview.html"

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
        return "web/previews/coordinator_preview.html"

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
        return "web/previews/organizer_committee_member_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self}

    def get_dict(self):
        """Return as dict for template compatibility"""
        return {"name": self.name, "role": self.role, "institution": self.institution}


class seleccion_result(Orderable):
    """One category row within an institutional selection record."""

    parent = ParentalKey(
        "seleccion_institucional",
        on_delete=models.CASCADE,
        related_name="results",
    )
    category = models.CharField("Categoría", max_length=150)
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


class seleccion_document(Orderable):
    """Downloadable document linked to an institutional selection record."""

    parent = ParentalKey(
        "seleccion_institucional",
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


class seleccion_institucional(PreviewableMixin, ClusterableModel):
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
        return "web/previews/seleccion_institucional_preview.html"

    def get_preview_context(self, request, mode_name):
        return {"snippet": self, "seleccion": self.to_dict()}

