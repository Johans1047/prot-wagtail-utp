from django.conf import settings
from django.core.exceptions import ValidationError
from wagtail.documents.forms import BaseDocumentForm
from wagtail.images.forms import BaseImageForm


class ImageAdminForm(BaseImageForm):
    """Custom Wagtail image form to set help text on tags and validate file size."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "tags" in self.fields:
            self.fields["tags"].help_text = (
                "Identificadores utilizados para clasificar el contenido dentro del sitio web"
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
                "Identificadores utilizados para clasificar el contenido dentro del sitio web"
            )
            # Este es el campo que define si es requerido o no, pero queda a consulta auna si se quiere hacer obligatorio o no el uso de tags en las imágenes.
            # self.fields["tags"].required = True

    def clean(self):
        cleaned_data = super().clean()
        file_field = cleaned_data.get("file")

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
