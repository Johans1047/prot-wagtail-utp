from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.generic import RedirectView

from django.shortcuts import render

# Añadir a urlpatterns

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", RedirectView.as_view(url="/panel/admin/", permanent=False)),
    path("admin/<path:subpath>", RedirectView.as_view(url="/panel/admin/%(subpath)s", permanent=False)),
    path("panel/admin/", include(wagtailadmin_urls)),
    path("panel/admin/<path:subpath>", lambda request, subpath: render(request, "wagtailadmin/404.html", status=404)),
    path("panel/documents/", include(wagtaildocs_urls)),
    path("panel/documents/<path:subpath>", lambda request, subpath: render(request, "wagtailadmin/404.html", status=404)),
    path("busqueda/", search_views.search, name="Busqueda"),
    path('', include('web.urls')),
    path('test-404/', lambda request: render(request, '404.html')),
    path('test-500/', lambda request: render(request, '500.html')),

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("panel/", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
