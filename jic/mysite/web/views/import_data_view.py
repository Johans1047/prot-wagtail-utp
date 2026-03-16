"""
Views for importing consultants and projects from CSV/XLSX files.
"""
from django import forms
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from web.services.import_service import ImportService


class ImportForm(forms.Form):
    """Form for uploading CSV/XLSX files for import."""
    
    archivo = forms.FileField(
        label='Archivo XLSX o CSV',
        help_text='Cargue un archivo CSV o Excel con los datos a importar'
    )
    actualizar = forms.BooleanField(
        required=False,
        label='Actualizar existentes',
        help_text='Si estÃ¡ marcado, actualizarÃ¡ registros existentes; si no, solo crearÃ¡ nuevos'
    )

@staff_member_required
@require_http_methods(["GET", "POST"])
def import_view(request):
    """
    Handle CSV/XLSX file uploads for importing consultants and projects.
    Displays import results with statistics and any errors.
    """
    resultado = None
    error = None
    
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resultado = ImportService.procesar_archivo(
                    archivo=request.FILES['archivo'],
                    actualizar=form.cleaned_data['actualizar']
                )
                resultado = resultado.to_dict()
            except ValueError as e:
                error = f'Error de validación: {str(e)}'
            except Exception as e:
                error = f'Error al procesar archivo: {str(e)}'
    else:
        form = ImportForm()
    
    context = {
        'form': form,
        'resultado': resultado,
        'error': error,
        'titulo': 'Importar Datos',
        'header_title': 'Importar Datos',
        'header_icon': 'upload',
        'breadcrumbs_items': [
            {'url': '/panel/admin/', 'label': 'Home'},
            {'url': '', 'label': 'Importar Datos'}
        ],
    }
    return render(request, 'utilidades/wagtailadmin/importar_datos.html', context)
