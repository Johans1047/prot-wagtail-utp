from django import forms
from wagtail.admin.forms.collections import CollectionForm as WagtailCollectionForm


class ExtendedCollectionForm(WagtailCollectionForm):
    is_visible_in_resources = forms.BooleanField(
        label="Visible en galería de Recursos",
        required=False,
        initial=True,
        help_text="Controla si esta colección aparece en la pestaña Galería de Recursos.",
    )

    class Meta(WagtailCollectionForm.Meta):
        fields = WagtailCollectionForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_value = True

        from ..models import CollectionResourceVisibility

        if self.instance and self.instance.pk:
            visibility = CollectionResourceVisibility.objects.filter(
                collection=self.instance
            ).first()
            if visibility is not None:
                current_value = visibility.is_visible_in_resources

        self.fields["is_visible_in_resources"].initial = current_value

    def save(self, commit=True):
        instance = super().save(commit=commit)
        visible = self.cleaned_data.get("is_visible_in_resources", True)

        from ..models import CollectionResourceVisibility

        if commit and instance.pk:
            CollectionResourceVisibility.objects.update_or_create(
                collection=instance,
                defaults={"is_visible_in_resources": visible},
            )
        else:
            # Create view saves with commit=False first, then persists the collection.
            instance._resource_visibility_pending = bool(visible)

        return instance
