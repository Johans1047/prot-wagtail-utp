from wagtail.images.forms import BaseImageForm


class ImageAdminForm(BaseImageForm):
    """Custom Wagtail image form to set help text on tags."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "tags" in self.fields:
            self.fields["tags"].help_text = (
                "Identificadores utilizados para clasificar el contenido dentro del sitio web"
            )
            # Este es el campo que define si es requerido o no, pero queda a consulta auna si se quiere hacer obligatorio o no el uso de tags en las imágenes.
            # self.fields["tags"].required = True
