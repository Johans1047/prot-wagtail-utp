from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

@register_snippet
class important_date(models.Model):
    """Editable timeline item for the home page."""

    title = models.CharField(max_length=150)
    event_date = models.DateField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

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
    
@register_snippet
class frequently_ask_question(models.Model):
    """Editable question and answer items for the home page."""

    category_slug = models.SlugField(
        max_length=50,
        default="general",
        help_text="Identificador interno de la categoría (ej: participacion, plataforma, entregables)",
    )
    category = models.CharField(max_length=150)
    question  = models.TextField()
    answer = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [
        FieldPanel("category_slug"),
        FieldPanel("category"),
        FieldPanel("question"),
        FieldPanel("answer"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        ordering = ["category_slug", "sort_order"]
        verbose_name = "Pregunta frecuente"
        verbose_name_plural = "Preguntas frecuentes"

    def __str__(self) -> str:
        return f"{self.category}: {self.question}"