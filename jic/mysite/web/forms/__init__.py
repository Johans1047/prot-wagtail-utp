from importlib import import_module

__all__ = ["_FaqAdminForm", "ExtendedCollectionForm", "ImageAdminForm", "DocumentAdminForm"]


_FORM_EXPORTS = {
    "_FaqAdminForm": ("web.forms.forms", "_FaqAdminForm"),
    "ExtendedCollectionForm": ("web.forms.collection_forms", "ExtendedCollectionForm"),
    "ImageAdminForm": ("web.forms.image_forms", "ImageAdminForm"),
    "DocumentAdminForm": ("web.forms.image_forms", "DocumentAdminForm"),
}


def __getattr__(name):
    if name not in _FORM_EXPORTS:
        raise AttributeError(f"module 'web.forms' has no attribute '{name}'")

    module_path, attr_name = _FORM_EXPORTS[name]
    module = import_module(module_path)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
