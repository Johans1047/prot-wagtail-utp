import os
import sys
import requests
import django
from django.core.files.base import ContentFile

# Setup Django environment
sys.path.append('/app')  # Adjust based on docker container path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.dev')
django.setup()

from web.models import video

VIDEOS_DATA = [
    {
        "url": "https://www.youtube.com/watch?v=RvCvRVcGhcE",
        "id": "RvCvRVcGhcE",
        "title": "JIC - ¿Qué es la Ciencia?",
        "description": "Introducción fundamental al concepto de ciencia, explorando sus definiciones, objetivos e impacto en el desarrollo del conocimiento humano.",
        "category": "Conceptos Básicos"
    },
    {
        "url": "https://www.youtube.com/watch?v=uPWVYp_ielY",
        "id": "uPWVYp_ielY",
        "title": "JIC - ¿Cómo funciona la ciencia?",
        "description": "Explicación detallada del método científico, la formulación de hipótesis y el proceso de validación en la investigación.",
        "category": "Conceptos Básicos"
    },
    {
        "url": "https://www.youtube.com/watch?v=R7_Nwx-re70",
        "id": "R7_Nwx-re70",
        "title": "JIC - Investigaciones Experimentales",
        "description": "Guía sobre metodologías experimentales, diseño de grupos de control y variables en entornos controlados y semi-controlados.",
        "category": "Metodología"
    },
    {
        "url": "https://www.youtube.com/watch?v=gB87b-cOxYE",
        "id": "gB87b-cOxYE",
        "title": "JIC - Investigaciones No Experimentales",
        "description": "Análisis de diseños de investigación no experimentales, incluyendo estudios observacionales, correlacionales y descriptivos.",
        "category": "Metodología"
    },
    {
        "url": "https://www.youtube.com/watch?v=cP7khhGqzjs",
        "id": "cP7khhGqzjs",
        "title": "JIC - Proyectos de Ingeniería y Desarrollo",
        "description": "Enfoque práctico para la investigación en ingeniería, desde la concepción de prototipos hasta la implementación de soluciones tecnológicas.",
        "category": "Ingeniería"
    },
    {
        "url": "https://www.youtube.com/watch?v=Kr8vZgOzTYE",
        "id": "Kr8vZgOzTYE",
        "title": "JIC - Criterios a Evaluar",
        "description": "Desglose de los criterios de evaluación utilizados en la Jornada de Iniciación Científica para calificar los proyectos presentados.",
        "category": "Evaluación"
    },
    {
        "url": "https://www.youtube.com/watch?v=h7OhKI89sDc",
        "id": "h7OhKI89sDc",
        "title": "Presentaciones Efectivas",
        "description": "Consejos y técnicas para realizar presentaciones orales impactantes, estructurar el contenido y comunicar hallazgos científicos con claridad.",
        "category": "Habilidades Blandas"
    },
    {
        "url": "https://www.youtube.com/watch?v=Jdx6j3a-pYU",
        "id": "Jdx6j3a-pYU",
        "title": "Pósteres Científicos",
        "description": "Directrices para el diseño y elaboración de pósteres científicos, asegurando una visualización efectiva de los datos y resultados.",
        "category": "Presentación"
    },
    {
        "url": "https://www.youtube.com/watch?v=vq9FcTl3-AY",
        "id": "vq9FcTl3-AY",
        "title": "Comunicación Oral Efectiva",
        "description": "Taller sobre oratoria y comunicación verbal y no verbal para defender proyectos de investigación ante un jurado o audiencia.",
        "category": "Habilidades Blandas"
    }
]

def run():
    print("Iniciando importación de videos de YouTube...")
    
    # Optional: Clear existing videos if needed, or simply append/update
    # video.objects.all().delete() 
    
    for item in VIDEOS_DATA:
        print(f"Procesando: {item['title']}")
        
        # Check if exists to avoid duplicates
        if video.objects.filter(youtube_url=item['url']).exists():
            print(f" - Ya existe: {item['title']}")
            continue

        # Get thumbnail
        thumb_url = f"https://img.youtube.com/vi/{item['id']}/hqdefault.jpg"
        try:
            response = requests.get(thumb_url)
            if response.status_code == 200:
                print(f" - Miniatura descargada")
                
                vid = video(
                    title=item['title'],
                    description=item['description'],
                    youtube_url=item['url'],
                    category=item['category'],
                    is_active=True
                )
                
                # Save thumbnail file
                vid.thumbnail.save(
                    f"{item['id']}.jpg",
                    ContentFile(response.content),
                    save=False
                )
                
                vid.save()
                print(" - Guardado exitosamente")
            else:
                print(f" - Error descargando miniatura: Status {response.status_code}")
                # Create without thumbnail if fails
                video.objects.create(
                    title=item['title'],
                    description=item['description'],
                    youtube_url=item['url'],
                    category=item['category'],
                    is_active=True
                )
        except Exception as e:
            print(f" - Error: {e}")

if __name__ == "__main__":
    run()
