import re
import unicodedata
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


def _normalize_category_key(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").lower())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    return text


@register.filter
def category_chip_class(value):
    category_key = _normalize_category_key(value)
    category_map = {
        "salud": "bg-sky-100 text-sky-700",
        "ingenieria": "bg-amber-100 text-amber-700",
        "ciencias de la salud": "bg-sky-100 text-sky-700",
        "de la salud": "bg-sky-100 text-sky-700",
        "ciencias naturales y exactas": "bg-emerald-200 text-emerald-700",
        "naturales y exactas": "bg-emerald-200 text-emerald-700",
        "sociales y humanisticas": "bg-violet-100 text-violet-700",
        "ciencias sociales y humanisticas": "bg-violet-100 text-violet-700",
    }
    return category_map.get(category_key, "bg-primary/10 text-primary")


@register.filter
def category_chip_outline_class(value):
    category_key = _normalize_category_key(value)
    category_map = {
        "salud": "border-sky-300 text-sky-300",
        "ingenieria": "border-amber-700 text-amber-700",
        "ciencias de la salud": "border-sky-300 text-sky-300",
        "de la salud": "border-sky-300 text-sky-300",
        "ciencias naturales y exactas": "border-emerald-600 text-emerald-600",
        "naturales y exactas": "border-emerald-600 text-emerald-600",
        "sociales y humanisticas": "border-violet-400 text-violet-400",
        "ciencias sociales y humanisticas": "border-violet-400 text-violet-400",
    }
    return category_map.get(category_key, "border-primary-foreground/40 text-primary-foreground")