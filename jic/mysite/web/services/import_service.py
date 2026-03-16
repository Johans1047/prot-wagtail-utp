"""
Import service for handling CSV/XLSX uploads of consultants and projects.
Prevents duplicate entries and provides detailed import results.
"""
import pandas as pd
from django.core.exceptions import ValidationError
from web.models import consultant, project


class ImportResult:
    """Holds import statistics and details."""
    
    def __init__(self):
        self.created_consultants = 0
        self.updated_consultants = 0
        self.created_projects = 0
        self.updated_projects = 0
        self.errors = []
    
    def add_error(self, row_num, model_name, error_msg):
        """Add an error entry."""
        self.errors.append({
            'fila': row_num,
            'modelo': model_name,
            'error': str(error_msg)
        })
    
    def to_dict(self):
        return {
            'creados_asesores': self.created_consultants,
            'actualizados_asesores': self.updated_consultants,
            'creados_proyectos': self.created_projects,
            'actualizados_proyectos': self.updated_projects,
            'errores': self.errors,
            'total_errores': len(self.errors)
        }


class ImportService:
    """Service for importing consultants and projects from files."""
    
    SUPPORTED_FORMATS = {'.csv', '.xlsx', '.xls'}
    CONSULTANT_REQUIRED_FIELDS = {'nombre'}
    PROJECT_REQUIRED_FIELDS = {'titulo', 'año', 'universidad'}
    
    @staticmethod
    def read_file(archivo):
        """Read CSV or XLSX file into DataFrame."""
        nombre = archivo.name.lower()
        
        if nombre.endswith('.csv'):
            return pd.read_csv(archivo)
        elif nombre.endswith(('.xlsx', '.xls')):
            return pd.read_excel(archivo)
        else:
            raise ValueError(f'Formato no soportado: {nombre}. Use CSV o XLSX.')
    
    @staticmethod
    def procesar_archivo(archivo, actualizar=False, tipo='auto'):
        """
        Process imported file for consultants and/or projects.
        
        Args:
            archivo: Uploaded file object
            actualizar: Whether to update existing records
            tipo: 'consultores', 'proyectos', or 'auto' (detect from sheet name)
        
        Returns:
            ImportResult object with statistics
        """
        try:
            df = ImportService.read_file(archivo)
        except Exception as e:
            raise ValueError(f'Error al leer archivo: {str(e)}')
        
        result = ImportResult()
        
        # Normalize column names to lowercase
        df.columns = df.columns.str.lower().str.strip()
        
        # Auto-detect import type from filename or first sheet
        if tipo == 'auto':
            nombre_archivo = archivo.name.lower()
            if 'consultant' in nombre_archivo or 'asesor' in nombre_archivo:
                tipo = 'consultores'
            elif 'project' in nombre_archivo or 'proyecto' in nombre_archivo:
                tipo = 'proyectos'
            else:
                # Try to detect by columns
                if 'nombre' in df.columns and 'email' in df.columns:
                    tipo = 'consultores'
                elif 'titulo' in df.columns and 'año' in df.columns:
                    tipo = 'proyectos'
                else:
                    raise ValueError('No se pudo detectar el tipo de importación. Especifique en el nombre del archivo.')
        
        if tipo == 'consultores':
            ImportService._importar_consultores(df, result, actualizar)
        elif tipo == 'proyectos':
            ImportService._importar_proyectos(df, result, actualizar)
        else:
            raise ValueError(f'Tipo de importación no válido: {tipo}')
        
        return result
    
    @staticmethod
    def _importar_consultores(df, result, actualizar):
        """Import consultants from DataFrame."""
        # Check required fields
        if 'nombre' not in df.columns:
            raise ValueError('Falta la columna "nombre" en el archivo de asesores')
        
        for idx, fila in df.iterrows():
            try:
                nombre = str(fila.get('nombre', '')).strip()
                
                if not nombre or nombre.lower() == 'nan':
                    result.add_error(idx + 2, 'Asesor', 'Nombre vacío')
                    continue
                
                email = str(fila.get('email', '')).strip()
                institucion = str(fila.get('institucion', '')).strip()
                is_active = fila.get('activo', True)
                
                # Normalize boolean
                if isinstance(is_active, str):
                    is_active = is_active.lower() in ('true', 'sí', 'yes', '1', 'verdadero')
                
                if actualizar:
                    # Update or create based on name (must be unique for this logic)
                    obj, created = consultant.objects.update_or_create(
                        name=nombre,
                        defaults={
                            'email': email if email and email.lower() != 'nan' else '',
                            'institution': institucion if institucion and institucion.lower() != 'nan' else '',
                            'is_active': bool(is_active),
                        }
                    )
                    if created:
                        result.created_consultants += 1
                    else:
                        result.updated_consultants += 1
                else:
                    # Create only if not exists
                    if not consultant.objects.filter(name=nombre).exists():
                        consultant.objects.create(
                            name=nombre,
                            email=email if email and email.lower() != 'nan' else '',
                            institution=institucion if institucion and institucion.lower() != 'nan' else '',
                            is_active=bool(is_active),
                        )
                        result.created_consultants += 1
                    else:
                        result.updated_consultants += 0  # Not updating
                        
            except Exception as e:
                result.add_error(idx + 2, 'Asesor', str(e))
    
    @staticmethod
    def _importar_proyectos(df, result, actualizar):
        """Import projects from DataFrame."""
        # Check required fields
        campos_requeridos = ['titulo', 'año', 'universidad']
        faltantes = [c for c in campos_requeridos if c not in df.columns]
        if faltantes:
            raise ValueError(f'Faltan columnas requeridas: {", ".join(faltantes)}')
        
        for idx, fila in df.iterrows():
            try:
                titulo = str(fila.get('titulo', '')).strip()
                año = fila.get('año')
                
                if not titulo or titulo.lower() == 'nan':
                    result.add_error(idx + 2, 'Proyecto', 'Título vacío')
                    continue
                
                if pd.isna(año):
                    result.add_error(idx + 2, 'Proyecto', 'Año no especificado')
                    continue
                
                año = int(float(año))  # Handle both int and float inputs
                universidad = str(fila.get('universidad', '')).strip()
                categoria = str(fila.get('categoria', '')).strip()
                resumen = str(fila.get('resumen', '')).strip()
                
                # Handle advisor lookup
                asesor_nombre = fila.get('asesor')
                advisor = None
                if asesor_nombre and str(asesor_nombre).lower() != 'nan':
                    asesor_nombre = str(asesor_nombre).strip()
                    try:
                        advisor = consultant.objects.get(name=asesor_nombre)
                    except consultant.DoesNotExist:
                        result.add_error(
                            idx + 2, 
                            'Proyecto', 
                            f'Asesor "{asesor_nombre}" no encontrado'
                        )
                        continue
                
                # Parse winner
                winner = int(fila.get('premio', 0))
                if winner not in [0, 1, 2, 3]:
                    winner = 0
                
                if actualizar:
                    # Update or create based on title + year
                    obj, created = project.objects.update_or_create(
                        title=titulo,
                        year=año,
                        defaults={
                            'abstract': resumen if resumen and resumen.lower() != 'nan' else '',
                            'advisor': advisor,
                            'university': universidad if universidad and universidad.lower() != 'nan' else '',
                            'category': categoria if categoria and categoria.lower() != 'nan' else '',
                            'winner': winner,
                        }
                    )
                    if created:
                        result.created_projects += 1
                    else:
                        result.updated_projects += 1
                else:
                    # Create only if not exists
                    if not project.objects.filter(title=titulo, year=año).exists():
                        project.objects.create(
                            title=titulo,
                            year=año,
                            abstract=resumen if resumen and resumen.lower() != 'nan' else '',
                            advisor=advisor,
                            university=universidad if universidad and universidad.lower() != 'nan' else '',
                            category=categoria if categoria and categoria.lower() != 'nan' else '',
                            winner=winner,
                        )
                        result.created_projects += 1
                        
            except ValueError as e:
                result.add_error(idx + 2, 'Proyecto', str(e))
            except Exception as e:
                result.add_error(idx + 2, 'Proyecto', str(e))
