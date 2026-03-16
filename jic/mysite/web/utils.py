import json
from django.utils import timezone

def get_raw_projects_data():
    return json.loads(
        """
        {
          "total": 13,
          "proyectos": [
            {
              "id": 606,
              "ano": 2024,
              "titulo": "Percepción, implicación y consecuencias del acoso escolar en instituciones educativas particulares y oficiales, en una muestra de docentes y estudiantes de distintas provincias de Panamá",
              "abstract": "El acoso escolar es una problemática cotidiana en el entorno educativo a nivel mundial. El objetivo de esta investigación fue analizar la percepción, implicación y consecuencias del acoso escolar en instituciones educativas, particulares y oficiales, en una muestra de docentes y estudiantes de distintas provincias de Panamá.",
              "asesor": "Abdel Alexander Solís Rodríguez",
              "contacto": "abdelsolis@gmail.com",
              "universidad": "Universidad Católica Santa María la Antigua",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 647,
              "ano": 2024,
              "titulo": "Densidad poblacional del mono tití panameño (Oedipomidas geoffroyi) en dos sitios del distrito de Chame, Panamá",
              "abstract": "El mono tití panameño (Oedipomidas geoffroyi) es considerado tolerante a perturbaciones antropogénica. Sin embargo, la última evaluación del estado de conservación lo consideran Casi Amenazado.",
              "asesor": "Pedro G Méndez Carvajal",
              "contacto": "giprimatologia.up@gmail.com",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 633,
              "ano": 2024,
              "titulo": "Uso de los sentidos por Alouatta coibensis en la evaluación/aceptación de frutos de Spondias mombin en Isla Coiba, Panamá",
              "abstract": "Los frutos de jobo (Spondias mombin) han sido reportados frecuentemente en la dieta del mono aullador (Alouatta sp.), usando sus sentidos para evaluar de manera efectiva la palatabilidad a estos frutos.",
              "asesor": "Karol M. Gutiérrez Pineda",
              "contacto": "gutierrezpinedakm@gmail.com",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 629,
              "ano": 2024,
              "titulo": "Identificación molecular de filogrupos y patotipos de cepas de Escherichia coli resistentes a los aminoglucósidos aisladas de aguas residuales y naturales en la Ciudad de Panamá.",
              "abstract": "El crecimiento poblacional, la urbanización, el cambio climático y la creciente demanda de agua han llevado a la degradación de muchas fuentes hídricas.",
              "asesor": "Jordi Querol",
              "contacto": "jordi.querol@up.ac.pa",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias de la Salud"
            },
            {
              "id": 610,
              "ano": 2024,
              "titulo": "Restauración del parque recreacional de Buena Vista",
              "abstract": "El Parque Recreacional de Buena Vista en Tocumen, Panamá, ha experimentado un deterioro significativo en su infraestructura, afectando la calidad de vida de la comunidad.",
              "asesor": "Maricela Ivonne Rodríguez C",
              "contacto": "mrodriguez@unicyt.net",
              "universidad": "Universidad Internacional de Ciencia y Tecnología",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 617,
              "ano": 2024,
              "titulo": "Aplicación y Efectividad de las Leyes de Protección de Afluentes Primarios en Los Algarrobos, Veraguas.",
              "abstract": "Panamá es un país rico en biodiversidad y recursos naturales, uno de éstos son los recursos hídricos.",
              "asesor": "Zoila Chilan",
              "contacto": "zchilan16@gmail.com",
              "universidad": "Universidad Metropolitana de Educación, Ciencia y Tecnología",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 420,
              "ano": 2024,
              "titulo": "Valoración de la capacidad antioxidante del puam (Muntingia calabura) y su potencial como alimento funcional",
              "abstract": "El árbol Muntingia calabura (puam) es de gran abundancia y accesibilidad en la República de Panamá.",
              "asesor": "Jhonny Correa",
              "contacto": "jhonny.correa@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 247,
              "ano": 2024,
              "titulo": "Impacto de campos electromagnéticos en el crecimiento de plantas: Un estudio experimental",
              "abstract": "Cuando la semilla se encuentra en un proceso germinativo, existen muchas condiciones fundamentales.",
              "asesor": "Hector Vergara",
              "contacto": "hector.vergara@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 388,
              "ano": 2024,
              "titulo": "Prototipo de una aplicación móvil para el reconocimiento, diagnóstico y sugerencias de tratamiento para melanomas",
              "abstract": "El cáncer de piel es causado por células cancerosas en tejidos de la piel.",
              "asesor": "Mariluz Centella",
              "contacto": "mariluz.centella@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ingeniería"
            },
            {
              "id": 476,
              "ano": 2024,
              "titulo": "Desarrollo de estrategias para potenciar el crecimiento de emprendimientos estudiantiles de la Universidad Tecnológica de Panamá",
              "abstract": "Este artículo aborda el impacto de factores como la asignatura Formación de Emprendedores y el uso de los servicios de la DGTC.",
              "asesor": "Enith González",
              "contacto": "enith.gonzalez@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 626,
              "ano": 2024,
              "titulo": "Biodiversidad Vegetal del Parque Nacional Camino de Cruces",
              "abstract": "Este proyecto se enfoca en obtener información biológica descriptiva sobre las especies vegetales presentes en el área protegida Parque Nacional Camino de Cruces.",
              "asesor": "Carlos Patricio Guerra Torres",
              "contacto": "guerrcarlos@gmail.com",
              "universidad": "Universidad de Panamá",
              "categoria": "Ciencias Naturales y Exactas"
            },
            {
              "id": 302,
              "ano": 2024,
              "titulo": "Propuesta de un índice técnico de caminabilidad (ICM) para microentornos educativos: diagnóstico de los alrededores del Campus Víctor Levi Sasso",
              "abstract": "Este estudio propone un Índice Técnico de Caminabilidad (ICM) para evaluar microentornos educativos, tomando como caso de estudio el Campus Víctor Levi Sasso.",
              "asesor": "Analissa Icaza",
              "contacto": "analissa.icaza@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ciencias Sociales y Humanísticas"
            },
            {
              "id": 332,
              "ano": 2024,
              "titulo": "Modelo metodológico para la evaluación de agua y saneamiento con soluciones a corto plazo para comunidades emergentes: Caso de Calle 50 y La Isla en la Cuenca del Río Mocambo",
              "abstract": "El agua es un recurso esencial y un derecho humano; este estudio evalúa soluciones a corto plazo para comunidades emergentes.",
              "asesor": "Viccelda María Domínguez de Franco",
              "contacto": "viccelda.dominguez@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ingeniería"
            },
            {
              "id": 411,
              "ano": 2024,
              "titulo": "Desarrollo de un adaptador electrónico basado en LoRaWAN para la medición remota de agua en dispositivos tradicionales",
              "abstract": "Con el objetivo de lograr un mundo más interconectado, se diseñó un prototipo para medir consumo de agua y transmitirlo por LoRaWAN.",
              "asesor": "Héctor Poveda",
              "contacto": "hector.poveda@utp.ac.pa",
              "universidad": "Universidad Tecnológica de Panamá",
              "categoria": "Ingeniería"
            }
          ]
        }
        """
    )


def get_processed_projects():
    projects_payload = get_raw_projects_data()
    return [
        {
            "id": project["id"],
            "title": project["titulo"],
            "university": project["universidad"],
            "category": project["categoria"],
            "year": project["ano"],
            "contact": project["contacto"],
            "advisor": project["asesor"],
            "winner": project.get("winner", False),
            "abstract": project["abstract"],
        }
        for project in projects_payload["proyectos"]
    ]


def get_gallery_image_path(instance, filename):
    """
    Generate path for gallery images: galeria/{year}/{filename}
    Example: galeria/2025/photo_abc123.jpg
    """
    year = timezone.now().year
    return f"galeria/{year}/{filename}"


def get_video_file_path(instance, filename):
    """
    Generate path for video files: videos/{year}/{filename}
    Example: videos/2025/tutorial_abc123.mp4
    """
    year = timezone.now().year
    return f"videos/{year}/{filename}"


def get_video_thumbnail_path(instance, filename):
    """
    Generate path for video thumbnails: video_thumbnails/{year}/{filename}
    Example: video_thumbnails/2025/thumb_abc123.jpg
    """
    year = timezone.now().year
    return f"video_thumbnails/{year}/{filename}"


def get_document_path(instance, filename):
    """
    Generate path for documents: documentos/{doc_type}/{year}/{filename}
    Example: documentos/lineamientos/2025/lineamientos_jic.pdf
    """
    year = timezone.now().year
    doc_type = getattr(instance, 'doc_type', 'otros').lower()
    return f"documentos/{doc_type}/{year}/{filename}"
