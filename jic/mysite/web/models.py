from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class ImportantDate(models.Model):
    """Editable timeline item for the home page."""

    title = models.CharField(max_length=150)
    event_date = models.DateField()
    description = models.TextField(blank=True)
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
