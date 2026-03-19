import re
from django import template

register = template.Library()

@register.filter
def elided_page_range(page_obj):
    if not hasattr(page_obj, 'paginator'):
        return []
    return page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)

@register.filter
def extract_year(value):
    if not value:
        return ''
    match = re.search(r'\b(20\d{2}|19\d{2})\b', str(value))
    return match.group(1) if match else ''

@register.filter
def sort_by_year_desc(documents):
    def get_year(doc):
        match = re.search(r'\b(20\d{2}|19\d{2})\b', str(doc.title))
        return int(match.group(1)) if match else 0
    return sorted(documents, key=get_year, reverse=True)