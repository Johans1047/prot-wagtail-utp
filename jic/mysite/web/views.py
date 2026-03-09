from django.shortcuts import render

def Inicio(request):
    faqs = {
        'participacion': {
            'title': 'Participación y Equipos',
            'items': [
                {
                    'q': '¿Quiénes pueden participar en la JIC?',
                    'a': 'Pueden participar estudiantes, docentes e investigadores de las universidades acreditadas por el CONEAUPA.',
                },
                {
                    'q': '¿Si mi compañero es de otra facultad, puede participar en mi equipo?',
                    'a': 'Sí, se permite grupos de estudiantes de diferentes facultades, pero el proyecto solo puede estar registrado en una de las facultades.',
                },
                {
                    'q': '¿Puede mi asesor ser de otra facultad o sede?',
                    'a': 'Sí, puede ser de otra facultad o sede, pero el proyecto se registra donde pertenecen los estudiantes.',
                },
                {
                    'q': '¿Va a existir la figura de co-asesor?',
                    'a': 'Sí, los equipos pueden contar con un asesor y un co-asesor.',
                },
                {
                    'q': '¿Un estudiante podrá formar parte de más de un grupo?',
                    'a': 'Sí, los estudiantes pueden participar en más de un grupo simultáneamente.',
                },
                {
                    'q': '¿Cuáles son los pasos para participar?',
                    'a': 'Conformar un equipo de 2 o 3 estudiantes con un asesor y registrarse en la plataforma oficial.',
                },
                {
                    'q': '¿Se puede registrar una investigación individual?',
                    'a': 'No. Los grupos deben ser de 2 o 3 estudiantes más el asesor.',
                },
                {
                    'q': '¿Puedo participar en la JIC si estoy realizando tesis de licenciatura?',
                    'a': 'Sí, mientras aún no tenga el título universitario y se encuentre matriculado en el semestre respectivo.',
                },
                {
                    'q': '¿Es posible participar en la JIC siendo extranjero?',
                    'a': 'Todo estudiante regular de una universidad participante que cumpla los requisitos puede participar.',
                },
                {
                    'q': '¿Puedo participar si ya cuento con una licenciatura?',
                    'a': 'No, el programa de la JIC es para estudiantes que no estén graduados.',
                },
                {
                    'q': '¿Cuál es el siguiente paso para la final JIC?',
                    'a': 'Luego de finalizada la JIC Interna, cada universidad debe registrar a sus participantes en la plataforma. En el caso de la UTP, solo deben actualizar los artículos.',
                },
                {
                    'q': '¿Para participar en la final, el equipo debe registrarse en la plataforma del Congreso?',
                    'a': 'Sí, todos los integrantes del grupo deben registrarse en el Congreso.',
                },
            ],
        },
        'plataforma': {
            'title': 'Plataforma Tecnológica',
            'items': [
                {
                    'q': '¿Dónde me registro para participar?',
                    'a': 'Debes ingresar en el enlace oficial: jic.utp.ac.pa/login',
                },
                {
                    'q': '¿Cuál es el procedimiento para registrar los proyectos?',
                    'a': 'El asesor registra el proyecto, los estudiantes suben documentos y el asesor aprueba finalmente.',
                },
                {
                    'q': '¿Soy asesor y la plataforma no me permite editar datos?',
                    'a': 'Solo los estudiantes cuentan con los permisos para editar los datos del proyecto.',
                },
                {
                    'q': '¿Existe un canal para estar enterados de forma expedita de cualquier información que afecte a los asesores o estudiantes?',
                    'a': 'Puede contactarnos a través de nuestro correo: jornada.cientifica@utp.ac.pa o por WhatsApp: 6958-4483',
                },
            ],
        },
        'entregables': {
            'title': 'Entregables y Evaluación',
            'items': [
                {
                    'q': '¿Qué documentos pide la JIC final: artículos, pósteres u otros?',
                    'a': 'Todo grupo finalista debe entregar su artículo, póster y video. Estos son requisitos de la SENACYT para la evaluación.',
                },
                {
                    'q': '¿Cuánto debe durar el vídeo que se presenta por YouTube?',
                    'a': 'El vídeo debe tener una duración máxima de 10 minutos, donde los estudiantes presenten el póster de su investigación.',
                },
                {
                    'q': '¿Se cuenta con un formato de artículo y dónde se puede descargar?',
                    'a': 'Sí, se cuenta con un formato de artículo. Puede encontrarlo en...',
                },
                {
                    'q': '¿Se deben eliminar los nombres de los estudiantes, los logos o los nombres de los asesores?',
                    'a': 'Sí, en la versión digital no deben estar los nombres ni logos. El póster impreso para exhibición en congreso nacional organizado por APANAC u otra institución sí puede incluirlos.',
                },
                {
                    'q': '¿Se puede corregir nuevamente el artículo?',
                    'a': 'Sí, teniendo en cuenta la fecha que se asigne para este fin.',
                },
                {
                    'q': '¿Si clasifico a la siguiente etapa debo volver a subir los documentos a la plataforma JIC?',
                    'a': 'Sí. Se les habilitará la plataforma para que puedan subir nuevamente los documentos.',
                },
                {
                    'q': '¿El nombre del asesor va en el artículo? ¿El nombre del asesor va en el póster?',
                    'a': 'En la JIC de Unidades Académicas, los coordinadores deciden si colocan el nombre del asesor. En la JIC final UTP y en la JIC Nacional, el artículo y el póster en versión digital no deben tener nombres ni afiliaciones de asesores o estudiantes. En la sesión de pósteres impresos para la JIC Nacional de SENACYT sí pueden colocarse.',
                },
                {
                    'q': '¿Cómo compruebo el porcentaje de originalidad de mi proyecto?',
                    'a': 'Antes de subir el artículo final, debe pasarlo por un software anti-plagio gratuito y hacer los cambios necesarios si no cumple con el porcentaje mínimo aceptado. El artículo final será sometido a un software anti-plagio por parte de los organizadores.',
                },
                {
                    'q': '¿En cuánto tiempo se debe presentar el proyecto?',
                    'a': 'Se tienen 15 minutos para exponer el trabajo y 5 minutos para preguntas y respuestas. Todo depende de la dinámica establecida.',
                },
                {
                    'q': '¿Cuál es el tamaño y forma del póster?',
                    'a': 'El tamaño del póster es A0 vertical, y el diseño es a libre creatividad del grupo.',
                },
                {
                    'q': '¿En la JIC nacional se pedirá video, aunque sea presencial?',
                    'a': 'Sí. En la JIC Nacional UTP y en la JIC Nacional con SENACYT se solicitará video como material de apoyo para la evaluación.',
                },
            ],
        },
    }
    
    context = {
        'faqs': faqs,
    }
    
    return render(request, 'inicio/_index.html', context)

def Jic(request):
    awards = [
        {
            "premio": "Premio Nacional de Innovación Juvenil",
            "año": "2024",
            "entidad": "SENACYT",
            "descripcion": "Reconocimiento a la mejor iniciativa de divulgación científica estudiantil."
        },
        {
            "premio": "Mención de Honor APANAC",
            "año": "2023",
            "entidad": "APANAC",
            "descripcion": "Distinción por fomentar la investigación en universidades públicas."
        },
        {
            "premio": "Premio a la Excelencia Académica",
            "año": "2022",
            "entidad": "Ministerio de Educación",
            "descripcion": "Otorgado por el impacto en la formación científica de jóvenes panameños."
        },
    ]
    
    organizations = [
        {
            "nombre": "Universidad Tecnológica de Panamá",
            "siglas": "UTP"
        }
    ]
    
    sponsors = [
        {
            "nombre": "Secretaría Nacional de Ciencia, Tecnología e Innovación",
            "siglas": "SENACYT"
        }
    ]
    
    context = {
        'awards': awards,
        'organizations': organizations,
        'sponsors': sponsors,
    }
    return render(request, 'jic/_index.html', context)

def Participar(request):
    schedule = [
        ["Apertura de inscripciones", "Mayo 2025"],
        ["Cierre de inscripciones", "Julio 2025"],
        ["Seleccion institucional", "Agosto 2025"],
        ["Seleccion nacional", "Septiembre - Octubre 2025"],
        ["JIC Nacional 2025", "Octubre 2025"],
    ]
    
    resource_categories = [
        {
            "title": "Estudiantes",
            "description": "Informacion para participantes",
            "accent": "bg-primary/90 text-primary-foreground",
            "resources": [
                {
                    "label": "Lineamientos de participacion 2025",
                    "href": "https://iniciacioncientifica.utp.ac.pa/subida-de-documentos-para-docentes/",
                },
                {
                    "label": "Plantilla para articulos",
                    "href": "https://iniciacioncientifica.utp.ac.pa/instructivos-y-ejemplos-para-estudiantes/",
                },
                {"label": "Manual de usuario: Estudiante", "href": "#"},
                {
                    "label": "Recursos digitales",
                    "href": "https://iniciacioncientifica.utp.ac.pa/subida-de-documentos-para-docentes/",
                },
            ]
        },
        {
            "title": "Asesores",
            "description": "Informacion para asesores",
            "accent": "bg-secondary-foreground/65 text-primary-foreground",
            "resources": [
                {"label": "Lineamientos para asesores", "href": "#"},
                {
                    "label": "Rubricas de evaluacion",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/05/manual-proce-JIC.pdf",
                },
                {"label": "Manual de usuario: Asesor", "href": "#"},
            ]
        },
        {
            "title": "Evaluadores",
            "description": "Informacion para evaluadores",
            "accent": "bg-amber-400 text-secondary-foreground",
            "resources": [
                {
                    "label": "Rubricas de evaluacion",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/05/manual-proce-JIC.pdf",
                },
                {"label": "Procedimiento de evaluacion", "href": "#"},
                {"label": "Documentos de induccion", "href": "#"},
            ]
        },
    ]
    
    context = {
        'schedule': schedule,
        'resource_categories': resource_categories,
    }
    return render(request, 'participar/_index..html', context)

def Proyectos(request):
    # Datos de ejemplo de proyectos
    all_projects = [
        {
            "year": 2024,
            "title": "Sistema de monitoreo ambiental con IoT",
            "university": "UTP",
            "category": "Ingeniería",
            "contact": "proyecto1@utp.ac.pa",
            "winner": True,
        },
        {
            "year": 2024,
            "title": "Análisis de biomarcadores en diabetes",
            "university": "UP",
            "category": "Ciencias de la Salud",
            "contact": "proyecto2@up.ac.pa",
            "winner": True,
        },
        {
            "year": 2023,
            "title": "Modelado matemático de ecosistemas",
            "university": "UTP",
            "category": "Ciencias Naturales",
            "contact": "proyecto3@utp.ac.pa",
            "winner": False,
        },
        {
            "year": 2023,
            "title": "Plataforma de educación digital",
            "university": "UNIANDES",
            "category": "Tecnología",
            "contact": "proyecto4@uniandes.ac.pa",
            "winner": False,
        },
        {
            "year": 2022,
            "title": "Estudio de aguas residuales",
            "university": "UTP",
            "category": "Ingeniería Ambiental",
            "contact": "proyecto5@utp.ac.pa",
            "winner": True,
        },
    ]
    
    # Obtener parámetros de filtro
    tab = request.GET.get('tab', 'all')
    search = request.GET.get('search', '')
    year_filter = request.GET.get('year', 'all')
    category_filter = request.GET.get('category', 'all')
    
    # Filtrar proyectos
    filtered = all_projects
    
    if tab == 'winners':
        filtered = [p for p in filtered if p['winner']]
    
    if search:
        search_lower = search.lower()
        filtered = [p for p in filtered if search_lower in p['title'].lower() or search_lower in p['university'].lower()]
    
    if year_filter != 'all':
        try:
            year_filter_int = int(year_filter)
            filtered = [p for p in filtered if p['year'] == year_filter_int]
        except ValueError:
            pass
    
    if category_filter != 'all':
        filtered = [p for p in filtered if p['category'] == category_filter]
    
    # Obtener lista de años únicos
    years = sorted(set(p['year'] for p in all_projects), reverse=True)
    
    # Obtener opciones de categorías únicas
    categories_options = [
        {"value": "all", "label": "Todas las categorías"},
    ]
    for category in sorted(set(p['category'] for p in all_projects)):
        categories_options.append({"value": category, "label": category})
    
    context = {
        'filtered': filtered,
        'tab': tab,
        'search': search,
        'year_filter': year_filter,
        'category_filter': category_filter,
        'years': years,
        'categories_options': categories_options,
    }
    return render(request, 'proyectos/_index.html', context)

def Resultados(request):
    # Datos históricos de ediciones anteriores
    historical_results = [
        {
            "year": 2024,
            "totalProjects": 47,
            "universities": 5,
            "documents": [
                {
                    "label": "Acta de resultados",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/12/acta-jic-2024.pdf",
                },
                {
                    "label": "Listado de ganadores",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2024/12/ganadores-jic-2024.pdf",
                },
            ]
        },
        {
            "year": 2023,
            "totalProjects": 42,
            "universities": 5,
            "documents": [
                {
                    "label": "Acta de resultados",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2023/12/acta-jic-2023.pdf",
                },
                {
                    "label": "Listado de ganadores",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2023/12/ganadores-jic-2023.pdf",
                },
                {
                    "label": "Fotografías del evento",
                    "type": "ZIP",
                    "href": "https://iniciacioncientifica.utp.ac.pa/galeria-jic-2023/",
                },
            ]
        },
        {
            "year": 2022,
            "totalProjects": 38,
            "universities": 4,
            "documents": [
                {
                    "label": "Acta de resultados",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2022/11/acta-jic-2022.pdf",
                },
                {
                    "label": "Listado de ganadores",
                    "type": "PDF",
                    "href": "https://iniciacioncientifica.utp.ac.pa/wp-content/uploads/2022/11/ganadores-jic-2022.pdf",
                },
            ]
        },
    ]
    
    context = {
        'historical_results': historical_results,
    }
    return render(request, 'resultados/_index.html', context)

def Recursos(request):
    tab = request.GET.get('tab', 'docs')
    
    documents_by_edition = [
        {
            "year": 2025,
            "docs": [
                {"label": "Lineamientos JIC 2025", "href": "https://iniciacioncientifica.utp.ac.pa/lineamientos-2025/"},
                {"label": "Informe de participacion institucional", "href": "#"},
                {"label": "Folleto JIC 2025", "href": "#"},
            ],
        },
        {
            "year": 2024,
            "docs": [
                {"label": "Lineamientos JIC 2024", "href": "https://iniciacioncientifica.utp.ac.pa/lineamientos-2024/"},
                {"label": "Programa final JIC 2024", "href": "#"},
                {"label": "Preguntas frecuentes 2024", "href": "#"},
                {"label": "Folleto JIC 2024", "href": "#"},
            ],
        },
        {
            "year": 2023,
            "docs": [
                {"label": "Lineamientos JIC 2023", "href": "#"},
                {"label": "Programa final JIC 2023", "href": "#"},
            ],
        },
    ]
    
    boletines = [
        {
            "title": "Boletin JIC 2024 - Momentos destacados",
            "description": "Ganadores, pasantias otorgadas y mejores momentos de la JIC Nacional 2024.",
            "href": "#",
        },
        {
            "title": "Boletin JIC 2023 - Resumen anual",
            "description": "Resumen de la edición 2023 con proyectos ganadores y estadisticas.",
            "href": "#",
        },
        {
            "title": "Boletin JIC 2022 - Innovacion juvenil",
            "description": "Destacados y logros de la edición 2022.",
            "href": "#",
        },
    ]
    
    memorias = [
        {
            "title": "Memorias JIC 2024",
            "description": "Publicaciones completas y documentacion de la edición 2024.",
            "href": "#",
        },
        {
            "title": "Memorias JIC 2023",
            "description": "Compendio de articulos e investigaciones presentadas en 2023.",
            "href": "#",
        },
        {
            "title": "Memorias JIC 2022",
            "description": "Documentacion integral de la edición 2022.",
            "href": "#",
        },
    ]
    
    gallery_images = [
        {"src": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=500&h=500&fit=crop", "alt": "Investigadores en laboratorio", "category": "Investigación"},
        {"src": "https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=500&h=500&fit=crop", "alt": "Presentación de proyecto", "category": "Presentaciones"},
        {"src": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=500&h=500&fit=crop", "alt": "Equipo científico", "category": "Investigación"},
        {"src": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=500&h=500&fit=crop", "alt": "Conferencia científica", "category": "Eventos"},
        {"src": "https://images.unsplash.com/photo-1516534775068-bb57b6439066?w=500&h=500&fit=crop", "alt": "Investigadores colaborando", "category": "Investigación"},
        {"src": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=500&h=500&fit=crop", "alt": "Presentación en auditorio", "category": "Presentaciones"},
        {"src": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&h=500&fit=crop", "alt": "Evento científico", "category": "Eventos"},
        {"src": "https://images.unsplash.com/photo-1537128191892-8ac93e876401?w=500&h=500&fit=crop", "alt": "Trabajo en equipo", "category": "Investigación"},
    ]
    
    videos = [
        {
            "title": "Video promocional JIC Nacional",
            "thumbnail": "/static/images/hero-jic.jpg",
            "url": "https://www.youtube.com/watch?v=oispNb8t79o",
            "description": "Conoce la JIC Nacional, el evento de investigacion mas importante para jovenes en Panama.",
        },
        {
            "title": "¿Cómo preparar tu proyecto de investigación?",
            "thumbnail": "/static/images/categories-science.jpg",
            "url": "https://www.youtube.com/watch?v=7VAMa-C7wG0",
            "description": "Conoce la JIC Nacional, el evento de investigacion mas importante para jovenes en Panama.",
        },
        {
            "title": "Inducción a la JIC 2024",
            "thumbnail": "/static/images/hero-jic.jpg",
            "url": "https://youtu.be/zxKc3FreHTQ?si=CORhb6r9ZoPpMf9d",
            "description": "Recursos sobre cómo presentar tu proyecto en la JIC.",
        },
    ]
    
    context = {
        'tab': tab,
        'documents_by_edition': documents_by_edition,
        'boletines': boletines,
        'memorias': memorias,
        'gallery_images': gallery_images,
        'gallery_categories': sorted(set(img['category'] for img in gallery_images)),
        'videos': videos,
    }
    return render(request, 'recursos/_index.html', context)

def Contacto(request):
    
    return render(request, 'contacto/_index.html')