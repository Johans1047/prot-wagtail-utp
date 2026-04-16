from django.conf import settings
from django.core.exceptions import ValidationError
from wagtail.documents.forms import BaseDocumentForm
from wagtail.images.forms import BaseImageForm


VALID_DOCUMENT_TAGS = {
    "imprenta",
    "lineamiento",
    "ganadores",
    "estudiante",
    "manual",
    "memoria",
    "boletin",
}

TAG_ALIASES = {
    "lineamientos": "lineamiento",
    "ganador": "ganadores",
    "manuales": "manual",
    "memorias": "memoria",
    "boletines": "boletin",
    "estudiantes": "estudiante",
}


def _normalize_tag_name(value: str) -> str:
    cleaned = str(value or "").strip().lower()
    return TAG_ALIASES.get(cleaned, cleaned)


def _extract_tag_names(raw_tags: str) -> list[str]:
    if not raw_tags:
        return []
    return [piece.strip() for piece in str(raw_tags).split(",") if piece.strip()]


class ImageAdminForm(BaseImageForm):
    """Custom Wagtail image form to set help text on tags and validate file size."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "tags" in self.fields:
            self.fields["tags"].help_text = (
                "Identificadores para clasificar contenido."
                " Ejemplos recomendados: 2026, ganadores, estudiante."
            )
            # Este es el campo que define si es requerido o no, pero queda a consulta auna si se quiere hacer obligatorio o no el uso de tags en las imágenes.
            # self.fields["tags"].required = True

    def clean(self):
        cleaned_data = super().clean()
        file_field = cleaned_data.get("file")

        if file_field:
            max_size = getattr(settings, "WAGTAILIMAGES_MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
            file_size = file_field.size

            if file_size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                file_size_mb = file_size / (1024 * 1024)
                raise ValidationError(
                    f"El archivo es demasiado grande ({file_size_mb:.2f} MB). "
                    f"El tamaño máximo permitido es {max_size_mb:.2f} MB."
                )

        return cleaned_data


class DocumentAdminForm(BaseDocumentForm):
    """Custom Wagtail document form to validate file size."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "tags" in self.fields:
            self.fields["tags"].help_text = (
                "Identificadores para clasificar documentos."
                " Usa al menos un año (ej: 2026) y/o: imprenta, lineamiento, ganadores, estudiante, manual, memoria."
            )
            # Este es el campo que define si es requerido o no, pero queda a consulta auna si se quiere hacer obligatorio o no el uso de tags en las imágenes.
            # self.fields["tags"].required = True

    def clean(self):
        cleaned_data = super().clean()
        file_field = cleaned_data.get("file")
        raw_tags = self.data.get("tags", "")
        submitted_tags = _extract_tag_names(raw_tags)

        invalid_tags = []
        for tag_name in submitted_tags:
            normalized = _normalize_tag_name(tag_name)
            is_year = normalized.isdigit() and len(normalized) == 4 and normalized.startswith(("19", "20"))
            if not is_year and normalized not in VALID_DOCUMENT_TAGS:
                invalid_tags.append(tag_name)

        if invalid_tags:
            raise ValidationError(
                "Tags no válidos: "
                + ", ".join(invalid_tags)
                + ". Usa un año (YYYY) o alguno de: imprenta, lineamiento, ganadores, estudiante, manual, memoria."
            )

        if file_field:
            max_size = getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", 20 * 1024 * 1024)
            file_size = file_field.size

            if file_size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                file_size_mb = file_size / (1024 * 1024)
                raise ValidationError(
                    f"El archivo es demasiado grande ({file_size_mb:.2f} MB). "
                    f"El tamaño máximo permitido es {max_size_mb:.2f} MB."
                )

        return cleaned_data
