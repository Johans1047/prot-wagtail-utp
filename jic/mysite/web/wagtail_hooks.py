from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem, SubmenuMenuItem, Menu
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.images.models import Image
from wagtail.documents.models import Document

from .models import (
    important_date,
    frequently_ask_question,
    background_item,
    jic_category,
    award,
    event_intro,
    coordinator,
    organizer_committee_member,
    selection_institutional,
    video,
    resource_document,
    Gallery,
)


# ─── Home ─────────────────────────────────────────────────────────────

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
    model = selection_institutional
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


# ─── Recursos ────────────────────────────────────────────────────────

class VideoViewSet(SnippetViewSet):
    model = video
    menu_label = "Videos"
    icon = "media"
    list_display = ("title", "category", "sort_order", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description", "category")


class ResourceDocumentViewSet(SnippetViewSet):
    model = resource_document
    menu_label = "Documentos de Recursos"
    icon = "doc-full"
    list_display = ("title", "doc_type", "year", "sort_order", "is_active")
    list_filter = ("doc_type", "year", "is_active")
    search_fields = ("title", "description")


class GalleryViewSet(SnippetViewSet):
    model = Gallery
    menu_label = "Galería Ordenable"
    icon = "image"
    list_display = ("title",)
    search_fields = ("title",)


@hooks.register("register_admin_menu_item")
def register_recursos_menu():
    recursos_menu = Menu(items=[
        MenuItem("Imágenes", reverse("wagtailimages:index"), icon_name="image"),
        MenuItem("Galería Ordenable", reverse("wagtailsnippets_web_gallery:list"), icon_name="image"),
        MenuItem("Documentos", reverse("wagtaildocs:index"), icon_name="doc-full"),
        MenuItem("Videos", reverse("wagtailsnippets_web_video:list"), icon_name="media"),
    ])
    
    return SubmenuMenuItem("Recursos", recursos_menu, icon_name="folder-open-inverse", order=103)

@hooks.register("construct_main_menu")
def hide_original_menus(request, menu_items):
    """Hide the original top-level items so they only appear inside Resources."""
    hidden_items = ['images', 'documents']
    menu_items[:] = [item for item in menu_items if item.name not in hidden_items]


# ─── Register all groups ─────────────────────────────────────────────

register_snippet(InicioGroup)
register_snippet(JicGroup)
register_snippet(ResultadosGroup)
register_snippet(VideoViewSet)
register_snippet(ResourceDocumentViewSet)
register_snippet(GalleryViewSet)
