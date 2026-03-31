from django import forms
from wagtail.admin.forms import WagtailAdminModelForm


class _FaqAdminForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Keep only one editable category control in admin.
        if "category" in self.fields:
            self.fields.pop("category")

        if "category_slug" in self.fields:
            self.fields["category_slug"].widget = forms.Select(
                choices=self.fields["category_slug"].choices
            )
            self.fields["category_slug"].error_messages["invalid_choice"] = (
                "Por favor, selecciona una categoría válida: Participación, Plataforma o Entregables."
            )
