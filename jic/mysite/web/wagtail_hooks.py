from django.urls import reverse, path
from django.utils.html import format_html
from django.templatetags.static import static
from functools import cached_property
from wagtail import hooks
from wagtail.admin.menu import MenuItem, SubmenuMenuItem, Menu
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.admin.views import collections as wagtail_collections_views
from wagtail.admin.forms.collections import CollectionForm
from .policies import SingletonPermissionPolicy
from .utils import LazyMenuItem, _is_photo_collection
from .forms.collection_forms import ExtendedCollectionForm
from .models import (
    important_date,
    frequently_ask_question,
    background_item,
    jic_category,
    award,
    event_intro,
    national_coordinators_section,
    coordinator,
    organizer_committee_member,
    selection_institutional,
    selection_national,
    video,
    resource_document,
    Gallery,
    title_section,
    consultant,
    project_category,
    project_university,
    project,
)
from .views.import_data_view import import_view


# ─── Home ─────────────────────────────────────────────────────────────

class ImportantDateViewSet(SnippetViewSet):
    model = important_date
    menu_label = "Fechas importantes"
    icon = "date"
    list_display = ("title", "event_date", "is_primary", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("is_primary", "is_active")
    search_fields = ("title", "description")


class FrequentlyAskQuestionViewSet(SnippetViewSet):
    model = frequently_ask_question
    menu_label = "Preguntas frecuentes"
    icon = "help"
    list_display = ("category_slug", "question", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("category_slug", "is_active")
    search_fields = ("category_slug", "question", "answer")


class EventIntroViewSet(SnippetViewSet):
    model = event_intro
    menu_label = "Introducción del evento"
    icon = "doc-full"
    list_display = ("title", "is_active", "frontend_usage_count")


class TitleSectionViewSet(SnippetViewSet):
    model = title_section
    menu_label = "Sección Hero/Título"
    icon = "image"
    list_display = ("title", "carousel_interval", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    permission_policy = SingletonPermissionPolicy(title_section)


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
    list_display = ("year_label", "frontend_usage_count", "sort_order")
    search_fields = ("year_label", "description")


class JicCategoryViewSet(SnippetViewSet):
    model = jic_category
    menu_label = "Categorías"
    icon = "folder-open-inverse"
    list_display = ("name", "frontend_usage_count", "sort_order")
    search_fields = ("name", "description")


class AwardViewSet(SnippetViewSet):
    model = award
    menu_label = "Reconocimientos"
    icon = "pick"
    list_display = ("prize", "year", "entity", "frontend_usage_count", "sort_order")
    search_fields = ("prize", "entity", "description")


class NationalCoordinatorsSectionViewSet(SnippetViewSet):
    model = national_coordinators_section
    menu_label = "Sección Coordinadores"
    icon = "cog"
    list_display = ("title", "is_active", "frontend_usage_count")
    permission_policy = SingletonPermissionPolicy(national_coordinators_section)


class CoordinatorViewSet(SnippetViewSet):
    model = coordinator
    menu_label = "Coordinadores"
    icon = "user"
    list_display = ("university_short_name", "name", "email", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "university_short_name")


class OrganizerCommitteeViewSet(SnippetViewSet):
    model = organizer_committee_member
    menu_label = "Comité organizador"
    icon = "group"
    list_display = ("name", "role", "institution", "is_active", "frontend_usage_count", "sort_order")
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
        NationalCoordinatorsSectionViewSet,
        CoordinatorViewSet,
        OrganizerCommitteeViewSet,
    )


# ─── Resultados ──────────────────────────────────────────────────────

class SeleccionInstitucionalViewSet(SnippetViewSet):
    model = selection_institutional
    menu_label = "Selecciones institucionales"
    icon = "list-ul"
    list_display = (
        "university",
        "short_name",
        "year",
        "is_active",
        "frontend_usage_count",
        "sort_order",
    )
    list_filter = ("is_active", "year")
    search_fields = ("university", "short_name")



class SeleccionNacionalViewSet(SnippetViewSet):
    model = selection_national
    menu_label = "Selecciones nacionales"
    icon = "list-ul"
    list_display = ("year", "host_place", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("year", "host_place")

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
    list_display = ("name", "email", "institution", "is_active", "frontend_usage_count")
    list_filter = ("is_active",)
    search_fields = ("name", "email", "institution")


class ProjectCategoryViewSet(SnippetViewSet):
    model = project_category
    menu_label = "Categorías"
    icon = "tag"
    list_display = ("name", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name",)


class ProjectUniversityViewSet(SnippetViewSet):
    model = project_university
    menu_label = "Universidades"
    icon = "site"
    list_display = ("name", "short_name", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "short_name")


class InvestigacionViewSet(SnippetViewSet):
    model = project
    menu_label = "Investigaciones"
    icon = "doc-full"
    list_display = ("title", "year", "university", "category", "winner", "frontend_usage_count")
    list_filter = ("year", "category", "winner")
    search_fields = ("title", "abstract", "university", "category")


class ProyectosGroup(SnippetViewSetGroup):
    menu_label = "Proyectos"
    menu_icon = "folder-open-inverse"
    menu_order = 102
    items = (AsesorViewSet, ProjectCategoryViewSet, ProjectUniversityViewSet, InvestigacionViewSet)


# ─── Recursos ────────────────────────────────────────────────────────

class VideoViewSet(SnippetViewSet):
    model = video
    menu_label = "Videos"
    icon = "media"
    list_display = ("title", "category", "is_active", "frontend_usage_count", "sort_order", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description", "category")


class ResourceDocumentViewSet(SnippetViewSet):
    model = resource_document
    menu_label = "Documentos de Recursos"
    icon = "doc-full"
    list_display = ("title", "year", "doc_type", "is_active", "frontend_usage_count", "sort_order")
    list_filter = ("year", "doc_type", "is_active")
    search_fields = ("title", "description", "doc_type")
    ordering = ["-year", "doc_type", "sort_order"]


class GalleryViewSet(SnippetViewSet):
    model = Gallery
    menu_label = "Galería Ordenable"
    icon = "image"
    list_display = ("title", "frontend_usage_count")
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
    return SubmenuMenuItem(
        "Recursos",
        recursos_menu,
        icon_name="folder-open-inverse",
        order=104,
        name="recursos",
    )

## list_display = (all items except images and documents) ##
@hooks.register("construct_main_menu")
def hide_original_menus(request, menu_items):
    """Hide selected top-level items and restrict Noticias users to Pages only."""
    user = request.user
    group_names = set(user.groups.values_list("name", flat=True)) if user.is_authenticated else set()
    is_news_only_user = user.is_authenticated and not user.is_superuser and group_names == {"Noticias"}

    if is_news_only_user:
        menu_items[:] = [item for item in menu_items if getattr(item, "name", "") == "explorer"]
        return

    hidden_items = ['images', 'documents', 'snippets', 'sites']
    menu_items[:] = [item for item in menu_items if item.name not in hidden_items]


@hooks.register("construct_reports_menu")
def customize_reports_menu(request, menu_items):
    """Hide page types usage report and rename aging pages entry."""
    user = request.user
    group_names = set(user.groups.values_list("name", flat=True)) if user.is_authenticated else set()
    is_news_only_user = user.is_authenticated and not user.is_superuser and group_names == {"Noticias"}
    if is_news_only_user:
        menu_items[:] = []
        return

    filtered_items = []
    for item in menu_items:
        item_name = str(getattr(item, "name", "") or "")
        item_url = str(getattr(item, "url", "") or "")

        if item_name == "page_types_usage" or "reports/page-types-usage" in item_url:
            continue

        if item_name == "aging_pages" or "reports/aging-pages" in item_url:
            item.label = "Historial de páginas"

        filtered_items.append(item)

    menu_items[:] = filtered_items


@hooks.register("construct_settings_menu")
def hide_sites_from_settings_menu(request, menu_items):
    """Hide the Sites option from the Settings submenu."""
    user = request.user
    group_names = set(user.groups.values_list("name", flat=True)) if user.is_authenticated else set()
    is_news_only_user = user.is_authenticated and not user.is_superuser and group_names == {"Noticias"}
    if is_news_only_user:
        menu_items[:] = []
        return

    menu_items[:] = [
        item
        for item in menu_items
        if getattr(item, "name", "") != "sites"
        and "admin/sites" not in str(getattr(item, "url", "") or "")
    ]


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
        '.sidebar-wagtail-branding__icon-wrapper {{ background-image: url("{}"); background-size: 500%; background-repeat: no-repeat; background-position: center; background-color: hsl(254.3 50.4% 24.5%) !important; display: flex; align-items: center; justify-content: center; }}'
        '.w-theme-dark .sidebar-wagtail-branding__icon-wrapper {{ background-color: hsl(0 0% 11.4%) !important; }}'
        '@media (prefers-color-scheme: dark) {{ .w-theme-system .sidebar-wagtail-branding__icon-wrapper {{ background-color: hsl(0 0% 11.4%) !important; }} }}'
        '.jic-logo-light, .jic-logo-dark {{ display: none; }}'
        '.w-theme-light .jic-logo-light {{ display: block; }}'
        '.w-theme-dark .jic-logo-dark {{ display: block; }}'
        '</style>',
        static("img/utp-logo-admin.svg"),
        # static("img/utp-logo-admin-dark.svg"),
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
        name='importar_datos',
        icon_name='upload',
        order=105,
    )


# ─────────── Custom create/edit views for collections to apply ExtendedCollectionForm ─────────── 
# ─────────── conditionally based on whether it's a photo collection or not. ───────────
_original_create_view_class = wagtail_collections_views.Create
_original_edit_view_class = wagtail_collections_views.Edit


class PhotoCollectionCreateView(_original_create_view_class):
    """Create view que aplica ExtendedCollectionForm solo si parent es colección de fotos."""
    
    @cached_property
    def form_class(self):
        from wagtail.models import Collection
        
        parent_id = self.request.GET.get('parent')
        if parent_id:
            try:
                parent = Collection.objects.get(id=parent_id)
                if _is_photo_collection(parent):
                    return ExtendedCollectionForm
            except Collection.DoesNotExist:
                pass
        return CollectionForm


class PhotoCollectionEditView(_original_edit_view_class):
    """Edit view que aplica ExtendedCollectionForm solo si la colección actual es de fotos."""
    
    @cached_property
    def form_class(self):
        if _is_photo_collection(self.object):
            return ExtendedCollectionForm
        return CollectionForm


wagtail_collections_views.Create = PhotoCollectionCreateView
wagtail_collections_views.Edit = PhotoCollectionEditView