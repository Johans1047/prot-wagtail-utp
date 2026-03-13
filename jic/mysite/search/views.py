from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.db.models import Q

from wagtail.models import Page
from web.views import _get_processed_projects
from web.models import resource_document

# To enable logging of search queries for use with the "Promoted search results" module
# <https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html>
# uncomment the following line and the lines indicated in the search function
# (after adding wagtail.contrib.search_promotions to INSTALLED_APPS):

# from wagtail.contrib.search_promotions.models import Query


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    project_results = []
    document_results = []
    
    if search_query:
        search_results = Page.objects.live().search(search_query)
        
        # Search in projects (local JSON data)
        try:
            all_projects = _get_processed_projects()
            query_lower = search_query.lower()
            project_results = [
                p for p in all_projects
                if (p.get('title') and query_lower in p['title'].lower()) or 
                   (p.get('abstract') and query_lower in p['abstract'].lower()) or
                   (p.get('university') and query_lower in p['university'].lower())
            ]
        except Exception:
            project_results = []

        # Search in documents (database)
        try:
            query_lower = search_query.lower()
            document_results = resource_document.objects.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(doc_type__icontains=search_query),
                is_active=True
            ).order_by('-year', 'sort_order')
        except Exception:
            document_results = []

        # To log this query for use with the "Promoted search results" module:

        # query = Query.get(search_query)
        # query.add_hit()

    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "utilidades/search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
            "project_results": project_results,
            "document_results": document_results,
        },
    )
