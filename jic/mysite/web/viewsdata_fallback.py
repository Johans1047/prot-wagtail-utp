from .viewsdata_types import (
    FAQItem,
    FAQCategory,
    ImportantDate,
    BackgroundItem,
    JicCategory,
    Award,
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



def important_dates_fallback() -> list[ImportantDate]:
    return [
        ImportantDate(
            title="Apertura de inscripciones",
            event_date="2025-05-15",
            description="Inicio del periodo de inscripcion de proyectos en la plataforma JIC.",
        ),
        ImportantDate(
            title="Cierre de inscripciones",
            event_date="2025-07-30",
            description="Fecha limite para registrar proyectos de investigacion.",
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
            ],
        ),
        'entregables': FAQCategory(
            title='Entregables y Evaluación',
            items=[
                FAQItem('¿Qué documentos pide la JIC final: artículos, pósteres u otros?', 'Todo grupo finalista debe entregar su artículo, póster y video. Estos son requisitos de la SENACYT para la evaluación.'),
                FAQItem('¿Cuánto debe durar el vídeo que se presenta por YouTube?', 'El vídeo debe tener una duración máxima de 10 minutos, donde los estudiantes presenten el póster de su investigación.'),
                FAQItem('¿Se cuenta con un formato de artículo y dónde se puede descargar?', 'Sí, se cuenta con un formato de artículo. Puede encontrarlo en...'),
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
        BackgroundItem("2002", "El Dr. Alexis Tejedor inicia el Salón de Iniciación Científica en el Centro Regional de Veraguas de la Universidad Tecnológica de Panamá."),
        BackgroundItem("2015", "Se celebra la primera Jornada de Iniciación Científica a nivel institucional en la Universidad Tecnológica de Panamá."),
        BackgroundItem("2016", "Firma de convenio con la Secretaría Nacional de Ciencia, Tecnología e Innovación. La JIC se nacionaliza en el marco del Congreso Asociación Panameña para el Avance de la Ciencia (APANAC)."),
        BackgroundItem("2017-2025", "La JIC se consolida como el principal evento de investigación juvenil a nivel nacional."),
    ]


def jic_categories_fallback() -> list[JicCategory]:
    return [
        JicCategory("Ingeniería", "Proyectos de investigación en todas las ramas de la ingeniería."),
        JicCategory("Ciencias de la Salud", "Investigaciones en medicina, enfermería y ciencias biomédicas."),
        JicCategory("Ciencias Naturales y Exactas", "Proyectos en matemáticas, física, química y biología."),
        JicCategory("Ciencias Sociales y Humanísticas", "Estudios en sociología, psicología, educación y humanidades."),
    ]


def awards_fallback() -> list[Award]:
    return [
        Award("Premio Nacional de Innovación Juvenil", "2024", "SENACYT", "Reconocimiento a la mejor iniciativa de divulgación científica estudiantil."),
        Award("Mención de Honor APANAC", "2023", "APANAC", "Distinción por fomentar la investigación en universidades públicas."),
        Award("Premio a la Excelencia Académica", "2022", "Ministerio de Educación", "Otorgado por el impacto en la formación científica de jóvenes panameños."),
    ]
