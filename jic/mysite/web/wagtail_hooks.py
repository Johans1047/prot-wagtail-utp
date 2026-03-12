from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import (
    important_date,
    frequently_ask_question,
    background_item,
    jic_category,
    award,
    event_intro,
    coordinator,
    organizer_committee_member,
    seleccion_institucional,
)


# ─── Inicio ──────────────────────────────────────────────────────────

class ImportantDateViewSet(SnippetViewSet):
    model = important_date
    menu_label = "Fechas importantes"
    icon = "date"
    list_display = ("title", "event_date", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")


class FrequentlyAskQuestionViewSet(SnippetViewSet):
    model = frequently_ask_question
    menu_label = "Preguntas frecuentes"
    icon = "help"
    list_display = ("category", "question", "sort_order", "is_active")
    list_filter = ("category_slug", "is_active")
    search_fields = ("category", "question", "answer")


class EventIntroViewSet(SnippetViewSet):
    model = event_intro
    menu_label = "Intro del evento"
    icon = "doc-full"
    list_display = ("title", "is_active")


class InicioGroup(SnippetViewSetGroup):
    menu_label = "Inicio"
    menu_icon = "home"
    menu_order = 100
    items = (ImportantDateViewSet, FrequentlyAskQuestionViewSet, EventIntroViewSet)


# ─── JIC ─────────────────────────────────────────────────────────────

class BackgroundItemViewSet(SnippetViewSet):
    model = background_item
    menu_label = "Antecedentes"
    icon = "history"
    list_display = ("year_label", "sort_order")
    search_fields = ("year_label", "description")


class JicCategoryViewSet(SnippetViewSet):
    model = jic_category
    menu_label = "Categorías"
    icon = "folder-open-inverse"
    list_display = ("name", "sort_order")
    search_fields = ("name", "description")


class AwardViewSet(SnippetViewSet):
    model = award
    menu_label = "Reconocimientos"
    icon = "pick"
    list_display = ("prize", "year", "entity", "sort_order")
    search_fields = ("prize", "entity", "description")


class CoordinatorViewSet(SnippetViewSet):
    model = coordinator
    menu_label = "Coordinadores"
    icon = "user"
    list_display = ("university_short_name", "name", "email", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "university_short_name")


class OrganizerCommitteeViewSet(SnippetViewSet):
    model = organizer_committee_member
    menu_label = "Comité organizador"
    icon = "group"
    list_display = ("name", "role", "institution", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "role", "institution")


class JicGroup(SnippetViewSetGroup):
    menu_label = "JIC"
    menu_icon = "clipboard-list"
    menu_order = 101
    items = (
        BackgroundItemViewSet,
        JicCategoryViewSet,
        AwardViewSet,
        CoordinatorViewSet,
        OrganizerCommitteeViewSet,
    )


# ─── Resultados ──────────────────────────────────────────────────────

class SeleccionInstitucionalViewSet(SnippetViewSet):
    model = seleccion_institucional
    menu_label = "Selecciones institucionales"
    icon = "list-ul"
    list_display = ("university", "short_name", "year", "status", "is_active", "sort_order")
    list_filter = ("status", "is_active", "year")
    search_fields = ("university", "short_name")


class ResultadosGroup(SnippetViewSetGroup):
    menu_label = "Resultados"
    menu_icon = "success"
    menu_order = 102
    items = (SeleccionInstitucionalViewSet,)


# ─── Register all groups ─────────────────────────────────────────────

register_snippet(InicioGroup)
register_snippet(JicGroup)
register_snippet(ResultadosGroup)
