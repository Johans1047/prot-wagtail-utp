from dataclasses import dataclass, field


@dataclass
class FAQItem:
    q: str
    a: str


@dataclass
class FAQCategory:
    title: str
    items: list[FAQItem] = field(default_factory=list)


@dataclass
class ImportantDate:
    title: str
    event_date: str
    description: str


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