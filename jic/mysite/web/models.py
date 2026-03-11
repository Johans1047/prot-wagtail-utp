from django.db import models
from django.db.models import Case, When
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .forms import _FaqAdminForm


@register_snippet
class important_date(models.Model):
    """Editable timeline item for the home page."""

    title = models.CharField("Título", max_length=150)
    event_date = models.DateField("Fecha del evento")
    description = models.TextField("Descripción")
    is_active = models.BooleanField("Activo", default=True)
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
    
    
class frequently_ask_question(models.Model):
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
    is_active = models.BooleanField("Activo", default=True)

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


class FrequentlyAskQuestionViewSet(SnippetViewSet):
    model = frequently_ask_question
    menu_label = "Preguntas frecuentes"
    icon = "help"
    list_display = ("category", "question", "sort_order", "is_active")
    list_filter = ("category_slug", "is_active")
    search_fields = ("category", "question", "answer")


register_snippet(FrequentlyAskQuestionViewSet)


@register_snippet
class background_item(models.Model):
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


@register_snippet
class jic_category(models.Model):
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


@register_snippet
class award(models.Model):
    """Editable award/recognition item for the JIC recognitions section."""

    prize = models.CharField("Premio", max_length=200)
    year = models.CharField("Año", max_length=10)
    entity = models.CharField("Entidad", max_length=200)
    description = models.TextField("Descripción")
    sort_order = models.PositiveIntegerField("Orden", default=0)

    panels = [
        FieldPanel("prize"),
        FieldPanel("year"),
        FieldPanel("entity"),
        FieldPanel("description"),
        FieldPanel("sort_order"),
    ]

    class Meta:
        ordering = ["sort_order", "year"]
        verbose_name = "Reconocimiento"
        verbose_name_plural = "Reconocimientos"

    def __str__(self) -> str:
        return f"{self.prize} ({self.year})"


