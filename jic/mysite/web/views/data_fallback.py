from .data_types import (
    FAQItem,
    FAQCategory,
    ImportantDate,
    BackgroundItem,
    JicCategory,
    Award,
    EventIntro,
    Coordinator,
    OrganizerCommitteeMember,
    TitleSectionObject,
    TitleSectionImageObject,
    TitleSectionButtonObject,
)


def title_section_fallback() -> TitleSectionObject:
    ts = TitleSectionObject(
        title="JIC Nacional 2024",
        description="Fomentando la investigación entre jóvenes universitarios a nivel nacional. Una iniciativa de la Secretaría Nacional de Ciencia, Tecnología e Innovación.",
        carousel_interval=8000,
        _images=[
            TitleSectionImageObject(
                alt_text="Estudiantes presentando proyectos de investigación en la Jornada de Iniciación Científica",
                url="https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg"
            ),
            TitleSectionImageObject(
                alt_text="Proyectos",
                url="https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg"
            ),
            TitleSectionImageObject(
                alt_text="Innovación",
                url="https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg"
            )
        ],
        _buttons=[
            TitleSectionButtonObject(
                label="Participar ahora",
                url="Participar",
                button_type="primary"
            ),
            TitleSectionButtonObject(
                label="Conocer la JIC",
                url="Jic",
                button_type="secondary"
            )
        ]
    )
    return ts


def event_intro_fallback() -> EventIntro:
    return EventIntro(
        title="JIC Nacional",
        main_description="La Jornada de Iniciación Científica es el principal evento de investigación juvenil a nivel nacional panameño. Cada año, estudiantes de las diferentes universidades participantes presentan sus proyectos de investigación en diversas áreas de conocimiento.",
        secondary_description="Participa con tu proyecto de investigación y sé parte de una comunidad dedicada a la excelencia académica y la innovación científica. Comparte tus descubrimientos con la comunidad científica panameña.",
        framework_label="En el marco de",
        framework_text="Congreso IESTEC",
        logo_fallback_text="Logo JIC",
        is_active=True,
    )


def important_dates_fallback() -> list[ImportantDate]:
    return [
        ImportantDate(
            title="Apertura de inscripciones",
            event_date="2025-05-15",
            description="Inicio del periodo de inscripción de proyectos en la plataforma JIC.",
        ),
        ImportantDate(
            title="Cierre de inscripciones",
            event_date="2025-07-30",
            description="Fecha límite para registrar proyectos de investigación.",
        ),
        ImportantDate(
            title="Selección institucional",
            event_date="2025-08-20",
            description="Evaluación y selección de proyectos a nivel de cada universidad.",
        ),
        ImportantDate(
            title="Selección nacional",
            event_date="2025-09-15",
            description="Evaluación nacional de los proyectos seleccionados por cada universidad.",
        ),
        ImportantDate(
            title="JIC Nacional 2025",
            event_date="2025-10-24",
            description="Celebración de la Jornada de Iniciación Científica a nivel nacional.",
        ),
    ]


def faqs_fallback() -> dict[str, FAQCategory]:
    return {
        'participacion': FAQCategory(
            title='Participación y Equipos',
            items=[
                FAQItem('¿Quiénes pueden participar en la JIC?', 'Pueden participar estudiantes, docentes e investigadores de las universidades acreditadas por el CONEAUPA.'),
                FAQItem('¿Si mi compañero es de otra facultad, puede participar en mi equipo?', 'Sí, se permite grupos de estudiantes de diferentes facultades, pero el proyecto solo puede estar registrado en una de las facultades.'),
                FAQItem('¿Puede mi asesor ser de otra facultad o sede?', 'Sí, puede ser de otra facultad o sede, pero el proyecto se registra donde pertenecen los estudiantes.'),
                FAQItem('¿Va a existir la figura de co-asesor?', 'Sí, los equipos pueden contar con un asesor y un co-asesor.'),
                FAQItem('¿Un estudiante podrá formar parte de más de un grupo?', 'Sí, los estudiantes pueden participar en más de un grupo simultáneamente.'),
                FAQItem('¿Cuáles son los pasos para participar?', 'Conformar un equipo de 2 o 3 estudiantes con un asesor y registrarse en la plataforma oficial.'),
                FAQItem('¿Se puede registrar una investigación individual?', 'No. Los grupos deben ser de 2 o 3 estudiantes más el asesor.'),
                FAQItem('¿Puedo participar en la JIC si estoy realizando tesis de licenciatura?', 'Sí, mientras aún no tenga el título universitario y se encuentre matriculado en el semestre respectivo.'),
                FAQItem('¿Es posible participar en la JIC siendo extranjero?', 'Todo estudiante regular de una universidad participante que cumpla los requisitos puede participar.'),
                FAQItem('¿Puedo participar si ya cuento con una licenciatura?', 'No, el programa de la JIC es para estudiantes que no estén graduados.'),
                FAQItem('¿Cuál es el siguiente paso para la final JIC?', 'Luego de finalizada la JIC Interna, cada universidad debe registrar a sus participantes en la plataforma. En el caso de la UTP, solo deben actualizar los artículos.'),
                FAQItem('¿Para participar en la final, el equipo debe registrarse en la plataforma del Congreso?', 'Sí, todos los integrantes del grupo deben registrarse en el Congreso.'),
            ],
        ),
        'plataforma': FAQCategory(
            title='Plataforma Tecnológica',
            items=[
                FAQItem('¿Dónde me registro para participar?', 'Debes ingresar en el enlace oficial: jic.utp.ac.pa/login'),
                FAQItem('¿Cuál es el procedimiento para registrar los proyectos?', 'El asesor registra el proyecto, los estudiantes suben documentos y el asesor aprueba finalmente.'),
                FAQItem('¿Soy asesor y la plataforma no me permite editar datos?', 'Solo los estudiantes cuentan con los permisos para editar los datos del proyecto.'),
                FAQItem('¿Existe un canal para estar enterados de forma expedita de cualquier información que afecte a los asesores o estudiantes?', 'Puede contactarnos a través de nuestro correo: jornada.cientifica@utp.ac.pa o por WhatsApp: 6958-4483'),
                FAQItem('¿A qué correo puedo escribir para soporte o consultas sobre la plataforma?', 'Para soporte técnico o consultas relacionadas con la plataforma (accesos, errores del sistema, problemas de registro), puedes escribirnos a: jic.soporte@utp.ac.pa. Para consultas generales e institucionales, utiliza: jornada.cientifica@utp.ac.pa'),
            ],
        ),
        'entregables': FAQCategory(
            title='Entregables y Evaluación',
            items=[
                FAQItem('¿Qué documentos pide la JIC final: artículos, pósteres u otros?', 'Todo grupo finalista debe entregar su artículo, póster y video. Estos son requisitos de la SENACYT para la evaluación.'),
                FAQItem('¿Cuánto debe durar el vídeo que se presenta por YouTube?', 'El vídeo debe tener una duración máxima de 10 minutos, donde los estudiantes presenten el póster de su investigación.'),
                FAQItem('¿Se cuenta con un formato de artículo y dónde se puede descargar?', 'Sí, se cuenta con un formato de artículo. Puede encontrarlo en la sección de recursos de la plataforma JIC.'),
                FAQItem('¿Se deben eliminar los nombres de los estudiantes, los logos o los nombres de los asesores?', 'Sí, en la versión digital no deben estar los nombres ni logos. El póster impreso para exhibición en congreso nacional organizado por APANAC u otra institución sí puede incluirlos.'),
                FAQItem('¿Se puede corregir nuevamente el artículo?', 'Sí, teniendo en cuenta la fecha que se asigne para este fin.'),
                FAQItem('¿Si clasifico a la siguiente etapa debo volver a subir los documentos a la plataforma JIC?', 'Sí. Se les habilitará la plataforma para que puedan subir nuevamente los documentos.'),
                FAQItem('¿El nombre del asesor va en el artículo? ¿El nombre del asesor va en el póster?', 'En la JIC de Unidades Académicas, los coordinadores deciden si colocan el nombre del asesor. En la JIC final UTP y en la JIC Nacional, el artículo y el póster en versión digital no deben tener nombres ni afiliaciones de asesores o estudiantes. En la sesión de pósteres impresos para la JIC Nacional de SENACYT sí pueden colocarse.'),
                FAQItem('¿Cómo compruebo el porcentaje de originalidad de mi proyecto?', 'Antes de subir el artículo final, debe pasarlo por un software anti-plagio gratuito y hacer los cambios necesarios si no cumple con el porcentaje mínimo aceptado. El artículo final será sometido a un software anti-plagio por parte de los organizadores.'),
                FAQItem('¿En cuánto tiempo se debe presentar el proyecto?', 'Se tienen 15 minutos para exponer el trabajo y 5 minutos para preguntas y respuestas. Todo depende de la dinámica establecida.'),
                FAQItem('¿Cuál es el tamaño y forma del póster?', 'El tamaño del póster es A0 vertical, y el diseño es a libre creatividad del grupo.'),
                FAQItem('¿En la JIC nacional se pedirá video, aunque sea presencial?', 'Sí. En la JIC Nacional UTP y en la JIC Nacional con SENACYT se solicitará video como material de apoyo para la evaluación.'),
            ],
        ),
    }


def background_items_fallback() -> list[BackgroundItem]:
    return [
        BackgroundItem(
            year_label="2002",
            description="El Dr. Alexis Tejedor inicia el Salón de Iniciación Científica en el Centro Regional de Veraguas de la Universidad Tecnológica de Panamá.",
        ),
        BackgroundItem(
            year_label="2015",
            description="Se celebra la primera Jornada de Iniciación Científica a nivel institucional en la Universidad Tecnológica de Panamá.",
        ),
        BackgroundItem(
            year_label="2016",
            description="Firma de convenio con la Secretaría Nacional de Ciencia, Tecnología e Innovación. La JIC se nacionaliza en el marco del Congreso de la Asociación Panameña para el Avance de la Ciencia (APANAC).",
        ),
        BackgroundItem(
            year_label="2017–2025",
            description="La JIC se consolida como el principal evento de investigación juvenil a nivel nacional, con la participación de más de cinco universidades.",
        ),
    ]


def jic_categories_fallback() -> list[JicCategory]:
    return [
        JicCategory(
            name="Ingeniería",
            description="Proyectos de investigación en todas las ramas de la ingeniería: civil, mecánica, eléctrica, industrial, de sistemas, entre otras.",
        ),
        JicCategory(
            name="Ciencias de la Salud",
            description="Investigaciones en medicina, enfermería, odontología, farmacia y ciencias biomédicas.",
        ),
        JicCategory(
            name="Ciencias Naturales y Exactas",
            description="Proyectos en matemáticas, física, química, biología y ciencias ambientales.",
        ),
        JicCategory(
            name="Ciencias Sociales y Humanísticas",
            description="Estudios en sociología, psicología, educación, economía, derecho y humanidades.",
        ),
        JicCategory(
            name="Tecnología e Informática",
            description="Desarrollo de software, inteligencia artificial, ciberseguridad y sistemas de información.",
        ),
        JicCategory(
            name="Agrociencias",
            description="Investigaciones en agronomía, veterinaria, biotecnología agrícola y recursos naturales.",
        ),
    ]


def awards_fallback() -> list[Award]:
    return [
        Award(
            premio="Premio Nacional de Innovación Juvenil",
            year="2024",
            entidad="SENACYT",
            descripcion="Reconocimiento a la mejor iniciativa de divulgación científica estudiantil a nivel nacional.",
        ),
        Award(
            premio="Mención de Honor APANAC",
            year="2023",
            entidad="APANAC",
            descripcion="Distinción por fomentar la investigación científica en universidades públicas panameñas.",
        ),
        Award(
            premio="Premio a la Excelencia Académica",
            year="2022",
            entidad="Ministerio de Educación",
            descripcion="Otorgado por el impacto en la formación científica de jóvenes panameños.",
        ),
        Award(
            premio="Reconocimiento a la Innovación Tecnológica",
            year="2021",
            entidad="Cámara de Comercio, Industrias y Agricultura de Panamá",
            descripcion="Reconocimiento a proyectos con mayor potencial de aplicación industrial y tecnológica.",
        ),
        Award(
            premio="Premio Iberoamericano de Iniciación Científica",
            year="2019",
            entidad="OEI – Organización de Estados Iberoamericanos",
            descripcion="Distinción internacional por el modelo de jornada científica estudiantil replicable en Iberoamérica.",
        ),
    ]


def coordinators_fallback() -> list[Coordinator]:
    return [
        Coordinator(
            university_short_name="UTP",
            name="Dr. Juan Pérez",
            email="jic.utp@utp.ac.pa",
            sort_order=0,
        ),
        Coordinator(
            university_short_name="UP",
            name="Dra. María Rodríguez",
            email="jic.up@up.ac.pa",
            sort_order=1,
        ),
        Coordinator(
            university_short_name="USMA",
            name="Mgtr. Carlos López",
            email="jic.usma@usma.ac.pa",
            sort_order=2,
        ),
        Coordinator(
            university_short_name="UNACHI",
            name="Dr. Roberto Gómez",
            email="jic.unachi@unachi.ac.pa",
            sort_order=3,
        ),
        Coordinator(
            university_short_name="ULAT",
            name="Mgtr. Ana Torres",
            email="jic.ulat@ulat.ac.pa",
            sort_order=4,
        ),
    ]


def organizer_committee_members_fallback() -> list[OrganizerCommitteeMember]:
    return [
        OrganizerCommitteeMember(
            name="Dr. Luis Herrera",
            role="Director General",
            institution="UTP",
            sort_order=0,
        ),
        OrganizerCommitteeMember(
            name="Dra. Sandra Morales",
            role="Coordinación Académica",
            institution="SENACYT",
            sort_order=1,
        ),
        OrganizerCommitteeMember(
            name="Mgtr. Ricardo Vega",
            role="Coordinación Logística",
            institution="UTP",
            sort_order=2,
        ),
        OrganizerCommitteeMember(
            name="Ing. Patricia Salas",
            role="Coordinación Tecnológica",
            institution="UTP",
            sort_order=3,
        ),
    ]


def selecciones_fallback() -> list[dict]:
    return [
        {
            "university": "Universidad Tecnológica de Panamá",
            "shortName": "UTP",
            "year": 2025,
            "status": "completada",
            "results": [
                {"category": "Ingeniería", "selected": 8, "total": 24},
                {"category": "Ciencias de la Salud", "selected": 4, "total": 12},
                {"category": "Ciencias Naturales y Exactas", "selected": 5, "total": 18},
                {"category": "Ciencias Sociales y Humanísticas", "selected": 3, "total": 10},
            ],
            "documents": [
                {"label": "Acta de resultados UTP 2025", "href": "#"},
                {"label": "Lista de proyectos seleccionados", "href": "#"},
            ],
        },
        {
            "university": "Universidad de Panamá",
            "shortName": "UP",
            "year": 2025,
            "status": "completada",
            "results": [
                {"category": "Ingeniería", "selected": 5, "total": 15},
                {"category": "Ciencias de la Salud", "selected": 6, "total": 20},
                {"category": "Ciencias Naturales y Exactas", "selected": 4, "total": 14},
                {"category": "Ciencias Sociales y Humanísticas", "selected": 5, "total": 16},
            ],
            "documents": [
                {"label": "Acta de resultados UP 2025", "href": "#"},
            ],
        },
        {
            "university": "Universidad Santa María La Antigua",
            "shortName": "USMA",
            "year": 2025,
            "status": "en_proceso",
            "results": [],
            "documents": [],
        },
        {
            "university": "Universidad Autónoma de Chiriquí",
            "shortName": "UNACHI",
            "year": 2025,
            "status": "pendiente",
            "results": [],
            "documents": [],
        },
        {
            "university": "Universidad Latina de Panamá",
            "shortName": "ULAT",
            "year": 2025,
            "status": "pendiente",
            "results": [],
            "documents": [],
        },
    ]


def documents_by_edition_fallback() -> dict[str, list[dict]]:
    return {
        "2024": [
            {
                "label": "Misión, Visión, Valores y Objetivos de la JIC 2024",
                "type": "document",
                "href": "/static/documents/mision_vision.pdf",
                "description": "Conoce los principios que guían la Jornada de Iniciación Científica.",
                "date": "15/05/2024",
                "icon": "fa-file-pdf"
            },
            {
                "label": "Calendario Oficial JIC 2024",
                "type": "calendar",
                "href": "/static/documents/calendario_jic.pdf",
                "description": "Fechas importantes para inscripciones, entregas y eventos.",
                "date": "20/05/2024",
                "icon": "fa-calendar-alt"
            }
        ],
        "2023": [
            {
                "label": "Bases de Participación 2023",
                "type": "document",
                "href": "/static/documents/bases_2023.pdf",
                "description": "Reglas y requisitos para participar en la JIC 2023.",
                "date": "10/01/2023",
                "icon": "fa-file-pdf"
            }
        ],
        "2022": [
            {
                "label": "Resultados Finales JIC 2022",
                "type": "spreadsheet",
                "href": "/static/documents/resultados_2022.xlsx",
                "description": "Lista de ganadores y menciones honoríficas del 2022.",
                "date": "15/11/2022",
                "icon": "fa-file-excel"
            }
        ]
    }


def videos_fallback() -> list[dict]:
    return [
        {
            "title": "JIC - ¿Qué es la Ciencia?",
            "thumbnail": "https://img.youtube.com/vi/RvCvRVcGhcE/maxresdefault.jpg",
            "url": "https://www.youtube.com/watch?v=RvCvRVcGhcE",
            "description": "Introducción fundamental al concepto de ciencia, explorando sus definiciones, objetivos e impacto en el desarrollo del conocimiento humano.",
            "category": "Conceptos Básicos",
        },
        {
            "title": "JIC - ¿Cómo funciona la ciencia?",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/uPWVYp_ielY_f069202e.jpg",
            "url": "https://www.youtube.com/watch?v=uPWVYp_ielY",
            "description": "Explicación detallada del método científico, la formulación de hipótesis y el proceso de validación en la investigación.",
            "category": "Conceptos Básicos",
        },
        {
            "title": "JIC - Investigaciones Experimentales",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/R7_Nwx-re70_48aad951.jpg",
            "url": "https://www.youtube.com/watch?v=R7_Nwx-re70",
            "description": "Guía sobre metodologías experimentales, diseño de grupos de control y variables en entornos controlados y semi-controlados.",
            "category": "Metodología",
        },
        {
            "title": "JIC - Investigaciones No Experimentales",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/gB87b-cOxYE_20c88364.jpg",
            "url": "https://www.youtube.com/watch?v=gB87b-cOxYE",
            "description": "Análisis de diseños de investigación no experimentales, incluyendo estudios observacionales, correlacionales y descriptivos.",
            "category": "Metodología",
        },
        {
            "title": "JIC - Proyectos de Ingeniería y Desarrollo",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/cP7khhGqzjs_1e3177a2.jpg",
            "url": "https://www.youtube.com/watch?v=cP7khhGqzjs",
            "description": "Enfoque práctico para la investigación en ingeniería, desde la concepción de prototipos hasta la implementación de soluciones tecnológicas.",
            "category": "Ingeniería",
        },
        {
            "title": "JIC - Criterios a Evaluar",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/Kr8vZgOzTYE_e31a44ad.jpg",
            "url": "https://www.youtube.com/watch?v=Kr8vZgOzTYE",
            "description": "Desglose de los criterios de evaluación utilizados en la Jornada de Iniciación Científica para calificar los proyectos presentados.",
            "category": "Evaluación",
        },
        {
            "title": "Presentaciones Efectivas",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/h7OhKI89sDc_6ab18126.jpg",
            "url": "https://www.youtube.com/watch?v=h7OhKI89sDc",
            "description": "Consejos y técnicas para realizar presentaciones orales impactantes, estructurar el contenido y comunicar hallazgos científicos con claridad.",
            "category": "Habilidades Blandas",
        },
        {
            "title": "Pósteres Científicos",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/Jdx6j3a-pYU_0ac6e46c.jpg",
            "url": "https://www.youtube.com/watch?v=Jdx6j3a-pYU",
            "description": "Directrices para el diseño y elaboración de pósteres científicos, asegurando una visualización efectiva de los datos y resultados.",
            "category": "Presentación",
        },
        {
            "title": "Comunicación Oral Efectiva",
            "thumbnail": "http://localhost:9010/jic-media/video_thumbnails/2026/vq9FcTl3-AY_ebfc4388.jpg",
            "url": "https://www.youtube.com/watch?v=vq9FcTl3-AY",
            "description": "Taller sobre oratoria y comunicación verbal y no verbal para defender proyectos de investigación ante un jurado o audiencia.",
            "category": "Habilidades Blandas",
        },
    ]


def gallery_images_fallback() -> list[dict]:
    return [
           {
               "src": "https://picsum.photos/seed/jic1/800/600",
               "alt": "Estudiantes presentando proyecto de robótica",
               "title": "Presentación de Robótica",
               "description": "Estudiantes de ingeniería electromecánica demostrando su brazo robótico educativo en la feria principal.",
               "category": "2023"
           },
           {
               "src": "https://picsum.photos/seed/jic2/800/600",
               "alt": "Autoridades en la mesa principal",
               "title": "Inauguración JIC",
               "description": "El Rector y el comité organizador durante la ceremonia de apertura en el auditorio central.",
               "category": "Ceremonias"
           },
           {
               "src": "https://picsum.photos/seed/jic3/800/600",
               "alt": "Público observando pósters científicos",
               "title": "Exhibición de Pósters",
               "description": "Asistentes revisando las metodologías y resultados de los más de 50 proyectos exhibidos.",
               "category": "2023"
           },
           {
               "src": "https://picsum.photos/seed/jic4/600/800",
               "alt": "Ganadores recibiendo medallas",
               "title": "Premiación 1er Lugar",
               "description": "El equipo 'AquaTech' recibiendo el primer lugar en la categoría de Ciencias Ambientales.",
               "category": "Ceremonias"
           },
           {
               "src": "https://picsum.photos/seed/jic5/800/600",
               "alt": "Estudiante explicando software a jurado",
               "title": "Evaluación del Jurado",
               "description": "Participantes defendiendo su aplicación de monitoreo de tráfico ante los evaluadores externos.",
               "category": "2022"
           },
           {
               "src": "https://picsum.photos/seed/jic6/800/600",
               "alt": "Grupo de voluntarios JIC",
               "title": "Voluntarios 2023",
               "description": "El equipo de logística y apoyo que hizo posible la ejecución impecable del evento.",
               "category": "2023"
           },
           {
               "src": "https://picsum.photos/seed/jic7/800/600",
               "alt": "Prototipo de vehículo solar",
               "title": "Innovación en Transporte",
               "description": "Pruebas en exteriores del prototipo de transporte impulsado por energía solar.",
               "category": "Proyectos"
           },
           {
               "src": "https://picsum.photos/seed/jic8/600/800",
               "alt": "Conferencista internacional",
               "title": "Charla Magistral",
               "description": "El Dr. Smith compartiendo sus experiencias sobre transferencia tecnológica academia-industria.",
               "category": "Conferencias"
           },
           {
               "src": "https://picsum.photos/seed/jic9/800/600",
               "alt": "Equipo trabajando en laboratorio",
               "title": "Preparativos",
               "description": "Sesiones de ajuste fino de proyectos en los laboratorios de química semanas antes del evento.",
               "category": "2022"
           },
           {
               "src": "https://picsum.photos/seed/jic10/800/600",
               "alt": "Foto grupal de ganadores",
               "title": "Clausura y Celebración",
               "description": "Todos los premiados de la edición 2023 celebrando al final de la jornada de tres días.",
               "category": "Ceremonias"
           }
       ]
