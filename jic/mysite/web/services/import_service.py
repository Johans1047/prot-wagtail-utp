"""
Import service for handling CSV/XLSX uploads of consultants and projects.
Prevents duplicate entries and provides detailed import results.
"""
import pandas as pd
import unicodedata
from django.core.exceptions import ValidationError
from web.models import consultant, project


class ImportResult:
    """Holds import statistics and details."""
    
    def __init__(self):
        self.created_consultants = 0
        self.updated_consultants = 0
        self.created_projects = 0
        self.updated_projects = 0
        self.deleted_projects = 0
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
            'eliminados_proyectos': self.deleted_projects,
            'errores': self.errors,
            'total_errores': len(self.errors)
        }


class ImportService:
    """Service for importing consultants and projects from files."""
    
    SUPPORTED_FORMATS = {'.csv', '.xlsx', '.xls'}
    CONSULTANT_REQUIRED_FIELDS = {'nombre'}
    PROJECT_REQUIRED_FIELDS = {'titulo', 'universidad'}
    OFFICIAL_UNIVERSITIES = [
        'Universidad Católica Santa María la Antigua',
        'Universidad Especializada de las Américas',
        'Universidad Internacional de Ciencia y Tecnología',
        'Universidad Latina de Panamá',
        'Universidad Marítima Internacional de Panamá',
        'Universidad Metropolitana de Educación, Ciencia y Tecnología',
        'Universidad Santander',
        'Universidad Tecnológica de Oteima',
        'Universidad Tecnológica de Panamá',
        'Universidad de Panamá',
    ]

    @staticmethod
    def _clean_optional_text(raw_value) -> str:
        if pd.isna(raw_value):
            return ''

        value = str(raw_value).strip()
        return '' if value.lower() == 'nan' else value

    @staticmethod
    def _parse_winner_value(raw_value) -> int:
        if pd.isna(raw_value):
            return 0

        normalized = str(raw_value).strip().lower()
        if normalized in {'1', 'primer lugar', 'primer', 'primero', '1er lugar'}:
            return 1
        if normalized in {'2', 'segundo lugar', 'segundo', '2do lugar'}:
            return 2
        if normalized in {'3', 'tercer lugar', 'tercero', '3er lugar'}:
            return 3

        return 0

    @staticmethod
    def _normalize_text_key(raw_value) -> str:
        """Normalize text for resilient category matching (accents/case/punctuation)."""
        value = ImportService._clean_optional_text(raw_value).lower()
        value = unicodedata.normalize('NFD', value)
        value = ''.join(ch for ch in value if unicodedata.category(ch) != 'Mn')
        value = ''.join(ch if ch.isalnum() or ch.isspace() else ' ' for ch in value)
        return ' '.join(value.split())

    @staticmethod
    def _normalize_category(raw_value) -> str:
        """
        Map category variants to canonical labels.
        Delegates to project.normalize_category() to avoid duplication.
        """
        raw_text = ImportService._clean_optional_text(raw_value)
        if not raw_text:
            return ''
        return project.normalize_category(raw_text)

    @staticmethod
    def _normalize_university(raw_value, university_catalog: dict | None = None) -> str:
        """
        Map university variants to a canonical label.
        Delegates to project.normalize_university() to avoid duplication.
        
        Note: university_catalog parameter kept for backwards compatibility but not used
        (model aliases are sufficient for canonicalization).
        """
        raw_text = ImportService._clean_optional_text(raw_value)
        if not raw_text:
            return ''
        return project.normalize_university(raw_text)

    @staticmethod
    def _build_university_catalog(df) -> dict:
        """
        Build key->canonical university map from official list.
        
        Note: (Kept for backwards compatibility; largely superseded by project model aliases)
        """
        return {
            ImportService._normalize_text_key(name): name
            for name in ImportService.OFFICIAL_UNIVERSITIES
        }
    
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
                elif ('titulo' in df.columns or 'título' in df.columns) and ('año' in df.columns or 'ano' in df.columns):
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
                    # Match existing consultant case-insensitively to avoid duplicates.
                    obj = consultant.objects.filter(name__iexact=nombre).first()
                    if obj:
                        obj.name = nombre
                        obj.email = email if email and email.lower() != 'nan' else ''
                        obj.institution = institucion if institucion and institucion.lower() != 'nan' else ''
                        obj.is_active = bool(is_active)
                        obj.save(update_fields=['name', 'email', 'institution', 'is_active'])
                        result.updated_consultants += 1
                    else:
                        consultant.objects.create(
                            name=nombre,
                            email=email if email and email.lower() != 'nan' else '',
                            institution=institucion if institucion and institucion.lower() != 'nan' else '',
                            is_active=bool(is_active),
                        )
                        result.created_consultants += 1
                else:
                    # Create only if not exists
                    if not consultant.objects.filter(name__iexact=nombre).exists():
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
        # Check required fields with accent variations
        year_field = 'año' if 'año' in df.columns else 'ano' if 'ano' in df.columns else None
        if not year_field:
            raise ValueError('Falta la columna "año" o "ano" en el archivo de proyectos')

        title_field = 'título' if 'título' in df.columns else 'titulo' if 'titulo' in df.columns else None
        if not title_field:
            raise ValueError('Falta la columna "título" o "titulo" en el archivo de proyectos')

        if 'universidad' not in df.columns:
            raise ValueError('Falta la columna "universidad" en el archivo de proyectos')
        
        university_catalog = ImportService._build_university_catalog(df)

        for idx, fila in df.iterrows():
            try:
                titulo = str(fila.get(title_field, '')).strip()
                año = fila.get(year_field)
                
                if not titulo or titulo.lower() == 'nan':
                    result.add_error(idx + 2, 'Proyecto', 'Título vacío')
                    continue
                
                if pd.isna(año):
                    result.add_error(idx + 2, 'Proyecto', 'Año no especificado')
                    continue
                
                año = int(float(año))  # Handle both int and float inputs
                universidad = ImportService._normalize_university(
                    fila.get('universidad', ''),
                    university_catalog=university_catalog,
                )
                universidad_siglas = str(fila.get('siglas', '')).strip()
                categoria = ImportService._normalize_category(
                    fila.get('categoría', fila.get('categoria', fila.get('category', '')))
                )
                resumen = str(fila.get('resumen', fila.get('abstract', ''))).strip()
                activo = fila.get('activo', 1)

                if isinstance(activo, str):
                    activo = activo.lower() in ('true', 'sí', 'si', 'yes', '1', 'verdadero')
                else:
                    activo = bool(activo)

                if not activo:
                    continue
                
                # Handle advisor lookup (asesor preferred, fallback to asesor1 and asesor2).
                asesor_nombre = ImportService._clean_optional_text(
                    fila.get('asesor', fila.get('asesor1', ''))
                )
                asesor2_nombre = ImportService._clean_optional_text(fila.get('asesor2', ''))

                if not asesor_nombre and asesor2_nombre:
                    asesor_nombre = asesor2_nombre

                advisor = None
                if asesor_nombre:
                    asesor_email = str(fila.get('email', '')).strip()
                    asesor_institucion = str(fila.get('institucion', universidad)).strip()

                    advisor = consultant.objects.filter(name__iexact=asesor_nombre).first()
                    if advisor is None:
                        advisor = consultant.objects.create(
                            name=asesor_nombre,
                            email=asesor_email if asesor_email and asesor_email.lower() != 'nan' else '',
                            institution=(
                                asesor_institucion
                                if asesor_institucion and asesor_institucion.lower() != 'nan'
                                else (universidad if universidad and universidad.lower() != 'nan' else '')
                            ),
                            is_active=True,
                        )
                        result.created_consultants += 1
                    elif actualizar:
                        updated = False
                        if asesor_email and asesor_email.lower() != 'nan' and advisor.email != asesor_email:
                            advisor.email = asesor_email
                            updated = True
                        if (
                            asesor_institucion
                            and asesor_institucion.lower() != 'nan'
                            and advisor.institution != asesor_institucion
                        ):
                            advisor.institution = asesor_institucion
                            updated = True
                        if not advisor.is_active:
                            advisor.is_active = True
                            updated = True

                        if updated:
                            advisor.save(update_fields=['email', 'institution', 'is_active'])
                            result.updated_consultants += 1
                
                # Parse winner from numeric or textual values.
                winner = ImportService._parse_winner_value(fila.get('premio', 0))
                
                if actualizar:
                    # Match by year + case-insensitive title to avoid duplicate rows.
                    obj = project.objects.filter(title__iexact=titulo, year=año).first()
                    if obj:
                        obj.title = titulo
                        obj.abstract = resumen if resumen and resumen.lower() != 'nan' else ''
                        obj.advisor = advisor
                        obj.university = universidad if universidad and universidad.lower() != 'nan' else ''
                        obj.university_short_name = universidad_siglas if universidad_siglas and universidad_siglas.lower() != 'nan' else ''
                        obj.category = categoria if categoria and categoria.lower() != 'nan' else ''
                        obj.winner = winner
                        obj.save(update_fields=['title', 'abstract', 'advisor', 'university', 'university_short_name', 'category', 'winner'])
                        result.updated_projects += 1
                    else:
                        project.objects.create(
                            title=titulo,
                            year=año,
                            abstract=resumen if resumen and resumen.lower() != 'nan' else '',
                            advisor=advisor,
                            university=universidad if universidad and universidad.lower() != 'nan' else '',
                            university_short_name=universidad_siglas if universidad_siglas and universidad_siglas.lower() != 'nan' else '',
                            category=categoria if categoria and categoria.lower() != 'nan' else '',
                            winner=winner,
                        )
                        result.created_projects += 1
                else:
                    # Create only if not exists
                    if not project.objects.filter(title__iexact=titulo, year=año).exists():
                        project.objects.create(
                            title=titulo,
                            year=año,
                            abstract=resumen if resumen and resumen.lower() != 'nan' else '',
                            advisor=advisor,
                            university=universidad if universidad and universidad.lower() != 'nan' else '',
                            university_short_name=universidad_siglas if universidad_siglas and universidad_siglas.lower() != 'nan' else '',
                            category=categoria if categoria and categoria.lower() != 'nan' else '',
                            winner=winner,
                        )
                        result.created_projects += 1
                        
            except ValueError as e:
                result.add_error(idx + 2, 'Proyecto', str(e))
            except Exception as e:
                result.add_error(idx + 2, 'Proyecto', str(e))
