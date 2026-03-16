import pandas as pd
from django.core.exceptions import ValidationError
from web.models import consultant, project

class ImportResult:
    def __init__(self):
        self.created_consultants = 0
        self.updated_consultants = 0
        self.created_projects = 0
        self.updated_projects = 0
        self.errors = []

    def add_error(self, row_num, model_name, error_msg):
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
    SUPPORTED_FORMATS = {'.csv', '.xlsx', '.xls'}

    @staticmethod
    def read_file(archivo):
        nombre = archivo.name.lower()
        if nombre.endswith('.csv'): return pd.read_csv(archivo)
        elif nombre.endswith('.xlsx') or nombre.endswith('.xls'): return pd.read_excel(archivo)
        else: raise ValueError(f'Formato no soportado: {nombre}. Use CSV o XLSX.')

    @staticmethod
    def procesar_archivo(archivo, actualizar=False, tipo=None):
        try: df = ImportService.read_file(archivo)
        except Exception as e: raise ValueError(f'Error al leer archivo: {str(e)}')
        
        result = ImportResult()
        df.columns = df.columns.str.lower().str.strip()
        ImportService._importar_datos_unificados(df, result, actualizar)
        return result

    @staticmethod
    def _importar_datos_unificados(df, result, actualizar):
        campos_requeridos = ['titulo', 'año', 'universidad']
        faltantes = [c for c in campos_requeridos if c not in df.columns]
        if faltantes:
            campos_requeridos = ['titulo', 'ano', 'universidad']
            faltantes_alt = [c for c in campos_requeridos if c not in df.columns]
            if faltantes_alt:
                raise ValueError(f'Faltan columnas requeridas: {", ".join(faltantes_alt)}')

        for idx, fila in df.iterrows():
            try:
                asesor_nombre = str(fila.get('asesor', '')).strip()
                if asesor_nombre.lower() == 'nan': asesor_nombre = ''
                advisor = None

                if asesor_nombre:
                    asesor_email = str(fila.get('email', '')).strip()
                    if asesor_email.lower() == 'nan': asesor_email = ''
                    asesor_institucion = str(fila.get('institucion', '')).strip()
                    if asesor_institucion.lower() == 'nan': asesor_institucion = ''
                    asesor_activo = fila.get('activo', True)
                    
                    if isinstance(asesor_activo, str):
                        asesor_activo = asesor_activo.lower() in ('true', 'sí', 'yes', '1', 'verdadero')

                    if actualizar:
                        advisor, created = consultant.objects.update_or_create(
                            name=asesor_nombre,
                            defaults={
                                'email': asesor_email,
                                'institution': asesor_institucion,
                                'is_active': bool(asesor_activo),
                            }
                        )
                        if created: result.created_consultants += 1
                        else: result.updated_consultants += 1
                    else:
                        advisor, created = consultant.objects.get_or_create(
                            name=asesor_nombre,
                            defaults={
                                'email': asesor_email,
                                'institution': asesor_institucion,
                                'is_active': bool(asesor_activo),
                            }
                        )
                        if created: result.created_consultants += 1

                titulo = str(fila.get('titulo', '')).strip()
                año_val = fila.get('año') if 'año' in df.columns else fila.get('ano')

                if not titulo or titulo.lower() == 'nan':
                    result.add_error(idx + 2, 'Proyecto', 'Título vacío')
                    continue

                if pd.isna(año_val):
                    result.add_error(idx + 2, 'Proyecto', 'Año no especificado')
                    continue

                año_val = int(float(año_val))
                universidad = str(fila.get('universidad', '')).strip()
                if universidad.lower() == 'nan': universidad = ''
                
                siglas = str(fila.get('siglas', '')).strip()
                if siglas.lower() == 'nan': siglas = ''
                
                categoria = str(fila.get('categoria', '')).strip()
                if categoria.lower() == 'nan': categoria = ''
                
                resumen = str(fila.get('resumen', '')).strip()
                if resumen.lower() == 'nan': resumen = ''

                winner_val = fila.get('premio', 0)
                winner = int(float(winner_val)) if not pd.isna(winner_val) else 0
                if winner not in [0, 1, 2, 3]: winner = 0

                if actualizar:
                    obj, created = project.objects.update_or_create(
                        title=titulo,
                        year=año_val,
                        defaults={
                            'abstract': resumen,
                            'advisor': advisor,
                            'university': universidad,
                            'university_short_name': siglas,
                            'category': categoria,
                            'winner': winner,
                        }
                    )
                    if created: result.created_projects += 1
                    else: result.updated_projects += 1
                else:
                    if not project.objects.filter(title=titulo, year=año_val).exists():
                        project.objects.create(
                            title=titulo,
                            year=año_val,
                            abstract=resumen,
                            advisor=advisor,
                            university=universidad,
                            university_short_name=siglas,
                            category=categoria,
                            winner=winner,
                        )
                        result.created_projects += 1

            except ValueError as e:
                result.add_error(idx + 2, 'Fila Múltiple', str(e))
            except Exception as e:
                result.add_error(idx + 2, 'Fila Múltiple', str(e))
