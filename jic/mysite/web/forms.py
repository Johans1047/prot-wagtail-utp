from wagtail.admin.forms import WagtailAdminModelForm


class _FaqAdminForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category_slug' in self.fields:
            self.fields['category_slug'].error_messages['invalid_choice'] = (
                'Por favor, selecciona una categoría válida: Participación, Plataforma o Entregables.'
            )
