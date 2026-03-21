from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from wagtail.models import Page
from wagtail.documents import get_document_model
from web.models import BlogPage, resource_document
from web.utils import get_processed_projects
from web.utils import WagtailDocWrapper


Document = get_document_model()

# To enable logging of search queries for use with the "Promoted search results" module
# <https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html>
# uncomment the following line and the lines indicated in the search function
# (after adding wagtail.contrib.search_promotions to INSTALLED_APPS):

# from wagtail.contrib.search_promotions.models import Query


def search(request):
    search_query = request.GET.get("query", None)
    content_page_number = request.GET.get("content_page", 1)
    projects_page_number = request.GET.get("projects_page", 1)
    documents_page_number = request.GET.get("documents_page", 1)
    news_page_number = request.GET.get("news_page", 1)

    def paginate_items(items, page_number, per_page):
        paginator = Paginator(items, per_page)
        try:
            return paginator.page(page_number)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    # Search
    project_results = []
    document_results = []
    news_results = []
    
    if search_query:
        raw_search_results = Page.objects.live().search(search_query)
        blog_content_type_id = ContentType.objects.get_for_model(BlogPage).id
        search_results = [
            result for result in raw_search_results
            if getattr(result, "content_type_id", None) != blog_content_type_id
        ]
        
        # Search in projects
        try:
            all_projects = get_processed_projects()
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
            document_results_list = list(resource_document.objects.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(doc_type__icontains=search_query),
                is_active=True
            ).order_by('-year', 'sort_order'))

            wagtail_docs = (
                Document.objects.filter(is_active=True)
                .filter(Q(title__icontains=search_query) | Q(tags__name__icontains=search_query))
                .distinct()
            )
            for doc in wagtail_docs:
                document_results_list.append(WagtailDocWrapper(doc))
                
            document_results = document_results_list
        except Exception:
            document_results = []

        # Search in news/blog pages
        try:
            news_results = list(
                BlogPage.objects.live()
                .public()
                .filter(
                    Q(title__icontains=search_query)
                    | Q(excerpt__icontains=search_query)
                    | Q(body__icontains=search_query)
                )
                .order_by("-publication_date", "-first_published_at")[:30]
            )
        except Exception:
            news_results = []
        # To log this query for use with the "Promoted search results" module:

        # query = Query.get(search_query)
        # query.add_hit()

    else:
        search_results = []

    search_results = paginate_items(search_results, content_page_number, 10)
    project_results = paginate_items(project_results, projects_page_number, 9)
    document_results = paginate_items(document_results, documents_page_number, 10)
    news_results = paginate_items(news_results, news_page_number, 6)

    return TemplateResponse(
        request,
        "utilidades/search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
            "project_results": project_results,
            "document_results": document_results,
            "news_results": news_results,
        },
    )
