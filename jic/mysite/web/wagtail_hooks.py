from django.urls import reverse, path
from django.utils.html import format_html
from django.templatetags.static import static
from django.db.models import Q
from collections import OrderedDict
from wagtail import hooks
from wagtail.admin.menu import MenuItem, SubmenuMenuItem, Menu
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.images.models import Image
from wagtail.documents.models import Document
from .policies import SingletonPermissionPolicy
from .utils import LazyMenuItem
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
    selection_national,
    video,
    resource_document,
    Gallery,
    title_section,
    consultant,
    project,
)
from .views.import_data_view import import_view


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


class TitleSectionViewSet(SnippetViewSet):
    model = title_section
    menu_label = "Sección Hero/Título"
    icon = "image"
    list_display = ("title", "carousel_interval", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "description")


class InicioGroup(SnippetViewSetGroup):
    menu_label = "Inicio"
    menu_icon = "home"
    menu_order = 100
    items = (TitleSectionViewSet, EventIntroViewSet, ImportantDateViewSet, FrequentlyAskQuestionViewSet)


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



class SeleccionNacionalViewSet(SnippetViewSet):
    model = selection_national
    menu_label = "Selecciones nacionales"
    icon = "list-ul"
    list_display = ("year", "status", "host_university", "is_active", "sort_order")
    list_filter = ("status", "is_active")
    search_fields = ("year", "host_university")

class ResultadosGroup(SnippetViewSetGroup):
    menu_label = "Resultados"
    menu_icon = "success"
    menu_order = 103
    items = (SeleccionInstitucionalViewSet, SeleccionNacionalViewSet)



# ─── Proyectos ───────────────────────────────────────────────────────

class AsesorViewSet(SnippetViewSet):
    model = consultant
    menu_label = "Asesores"
    icon = "user"
    list_display = ("name", "email", "institution", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "email", "institution")


class InvestigacionViewSet(SnippetViewSet):
    model = project
    menu_label = "Investigaciones"
    icon = "doc-full"
    list_display = ("title", "year", "university", "category", "winner")
    list_filter = ("year", "category", "winner")
    search_fields = ("title", "abstract", "university", "category")


class ProyectosGroup(SnippetViewSetGroup):
    menu_label = "Proyectos"
    menu_icon = "folder-open-inverse"
    menu_order = 102
    items = (AsesorViewSet, InvestigacionViewSet)


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
    list_display = ("title", "year", "doc_type", "is_active", "sort_order")
    list_filter = ("year", "doc_type", "is_active")
    search_fields = ("title", "description", "doc_type")
    ordering = ["-year", "doc_type", "sort_order"]


class GalleryViewSet(SnippetViewSet):
    model = Gallery
    menu_label = "Galería Ordenable"
    icon = "image"
    list_display = ("title",)
    search_fields = ("title",)
    permission_policy = SingletonPermissionPolicy(Gallery)


## class RecursosGroup(SnippetViewSetGroup): ##
@hooks.register("register_admin_menu_item")
def register_recursos_menu():
    recursos_menu = Menu(items=[
        LazyMenuItem("Documentos", "wagtaildocs:index", icon_name="doc-full"),
        LazyMenuItem("Imágenes", "wagtailimages:index", icon_name="image"),
        LazyMenuItem("Galería Ordenable", "wagtailsnippets_web_gallery:list", icon_name="image"),
        LazyMenuItem("Videos", "wagtailsnippets_web_video:list", icon_name="media"),
    ])
    return SubmenuMenuItem("Recursos", recursos_menu, icon_name="folder-open-inverse", order=104)

## list_display = (all items except images and documents) ##
@hooks.register("construct_main_menu")
def hide_original_menus(request, menu_items):
    """Hide the original top-level items so they only appear inside Resources."""
    hidden_items = ['images', 'documents']
    menu_items[:] = [item for item in menu_items if item.name not in hidden_items]


# ─── Register all groups ─────────────────────────────────────────────

register_snippet(InicioGroup)
register_snippet(JicGroup)
register_snippet(ResultadosGroup)
register_snippet(ProyectosGroup)

## register_snippet(RecursosGroup) is registered individually with the submenu above ##
register_snippet(VideoViewSet)
register_snippet(ResourceDocumentViewSet)
register_snippet(GalleryViewSet)


# ─── Import functionality ────────────────────────────────────────────

# Custom CSS to replace the Wagtail logo with the UTP logo in the admin interface
@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<style>'
        '.sidebar-wagtail-branding__icon-wrapper svg {{ display: none !important; }}'
        '.sidebar-wagtail-branding__icon-wrapper {{ background-image: url("{}"); background-size: 125%; background-repeat: no-repeat; background-position: center; background-color: hsl(254.3 50.4% 24.5%) !important; display: flex; align-items: center; justify-content: center; }}'
        '</style>',
        static("img/logo-de-la-utp.svg"),
    )
    
    
# Custom menu item for data import
@hooks.register('register_admin_urls')
def register_import_url():
    """Register the import data URL in the admin."""
    return [
        path('importar-datos/', import_view, name='importar_datos'),
    ]

# Sidebar menu item for access to the custom data import
@hooks.register('register_admin_menu_item')
def register_import_menu():
    """Add import data menu item to the admin sidebar."""
    return MenuItem(
        'Importar Datos',
        reverse('importar_datos'),
        icon_name='upload',
        order=105,
    )
