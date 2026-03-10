# Data migration – populates initial FAQ content from the hardcoded dict in views.py

from django.db import migrations


FAQS = [
    # --- participacion ---
    ('participacion', 'Participación y Equipos', 1, '¿Quiénes pueden participar en la JIC?', 'Pueden participar estudiantes, docentes e investigadores de las universidades acreditadas por el CONEAUPA.'),
    ('participacion', 'Participación y Equipos', 2, '¿Si mi compañero es de otra facultad, puede participar en mi equipo?', 'Sí, se permite grupos de estudiantes de diferentes facultades, pero el proyecto solo puede estar registrado en una de las facultades.'),
    ('participacion', 'Participación y Equipos', 3, '¿Puede mi asesor ser de otra facultad o sede?', 'Sí, puede ser de otra facultad o sede, pero el proyecto se registra donde pertenecen los estudiantes.'),
    ('participacion', 'Participación y Equipos', 4, '¿Va a existir la figura de co-asesor?', 'Sí, los equipos pueden contar con un asesor y un co-asesor.'),
    ('participacion', 'Participación y Equipos', 5, '¿Un estudiante podrá formar parte de más de un grupo?', 'Sí, los estudiantes pueden participar en más de un grupo simultáneamente.'),
    ('participacion', 'Participación y Equipos', 6, '¿Cuáles son los pasos para participar?', 'Conformar un equipo de 2 o 3 estudiantes con un asesor y registrarse en la plataforma oficial.'),
    ('participacion', 'Participación y Equipos', 7, '¿Se puede registrar una investigación individual?', 'No. Los grupos deben ser de 2 o 3 estudiantes más el asesor.'),
    ('participacion', 'Participación y Equipos', 8, '¿Puedo participar en la JIC si estoy realizando tesis de licenciatura?', 'Sí, mientras aún no tenga el título universitario y se encuentre matriculado en el semestre respectivo.'),
    ('participacion', 'Participación y Equipos', 9, '¿Es posible participar en la JIC siendo extranjero?', 'Todo estudiante regular de una universidad participante que cumpla los requisitos puede participar.'),
    ('participacion', 'Participación y Equipos', 10, '¿Puedo participar si ya cuento con una licenciatura?', 'No, el programa de la JIC es para estudiantes que no estén graduados.'),
    ('participacion', 'Participación y Equipos', 11, '¿Cuál es el siguiente paso para la final JIC?', 'Luego de finalizada la JIC Interna, cada universidad debe registrar a sus participantes en la plataforma. En el caso de la UTP, solo deben actualizar los artículos.'),
    ('participacion', 'Participación y Equipos', 12, '¿Para participar en la final, el equipo debe registrarse en la plataforma del Congreso?', 'Sí, todos los integrantes del grupo deben registrarse en el Congreso.'),
    # --- plataforma ---
    ('plataforma', 'Plataforma Tecnológica', 1, '¿Dónde me registro para participar?', 'Debes ingresar en el enlace oficial: jic.utp.ac.pa/login'),
    ('plataforma', 'Plataforma Tecnológica', 2, '¿Cuál es el procedimiento para registrar los proyectos?', 'El asesor registra el proyecto, los estudiantes suben documentos y el asesor aprueba finalmente.'),
    ('plataforma', 'Plataforma Tecnológica', 3, '¿Soy asesor y la plataforma no me permite editar datos?', 'Solo los estudiantes cuentan con los permisos para editar los datos del proyecto.'),
    ('plataforma', 'Plataforma Tecnológica', 4, '¿Existe un canal para estar enterados de forma expedita de cualquier información que afecte a los asesores o estudiantes?', 'Puede contactarnos a través de nuestro correo: jornada.cientifica@utp.ac.pa o por WhatsApp: 6958-4483'),
    # --- entregables ---
    ('entregables', 'Entregables y Evaluación', 1, '¿Qué documentos pide la JIC final: artículos, pósteres u otros?', 'Todo grupo finalista debe entregar su artículo, póster y video. Estos son requisitos de la SENACYT para la evaluación.'),
    ('entregables', 'Entregables y Evaluación', 2, '¿Cuánto debe durar el vídeo que se presenta por YouTube?', 'El vídeo debe tener una duración máxima de 10 minutos, donde los estudiantes presenten el póster de su investigación.'),
    ('entregables', 'Entregables y Evaluación', 3, '¿Se cuenta con un formato de artículo y dónde se puede descargar?', 'Sí, se cuenta con un formato de artículo. Puede encontrarlo en...'),
    ('entregables', 'Entregables y Evaluación', 4, '¿Se deben eliminar los nombres de los estudiantes, los logos o los nombres de los asesores?', 'Sí, en la versión digital no deben estar los nombres ni logos. El póster impreso para exhibición en congreso nacional organizado por APANAC u otra institución sí puede incluirlos.'),
    ('entregables', 'Entregables y Evaluación', 5, '¿Se puede corregir nuevamente el artículo?', 'Sí, teniendo en cuenta la fecha que se asigne para este fin.'),
    ('entregables', 'Entregables y Evaluación', 6, '¿Si clasifico a la siguiente etapa debo volver a subir los documentos a la plataforma JIC?', 'Sí. Se les habilitará la plataforma para que puedan subir nuevamente los documentos.'),
    ('entregables', 'Entregables y Evaluación', 7, '¿El nombre del asesor va en el artículo? ¿El nombre del asesor va en el póster?', 'En la JIC de Unidades Académicas, los coordinadores deciden si colocan el nombre del asesor. En la JIC final UTP y en la JIC Nacional, el artículo y el póster en versión digital no deben tener nombres ni afiliaciones de asesores o estudiantes. En la sesión de pósteres impresos para la JIC Nacional de SENACYT sí pueden colocarse.'),
    ('entregables', 'Entregables y Evaluación', 8, '¿Cómo compruebo el porcentaje de originalidad de mi proyecto?', 'Antes de subir el artículo final, debe pasarlo por un software anti-plagio gratuito y hacer los cambios necesarios si no cumple con el porcentaje mínimo aceptado. El artículo final será sometido a un software anti-plagio por parte de los organizadores.'),
    ('entregables', 'Entregables y Evaluación', 9, '¿En cuánto tiempo se debe presentar el proyecto?', 'Se tienen 15 minutos para exponer el trabajo y 5 minutos para preguntas y respuestas. Todo depende de la dinámica establecida.'),
    ('entregables', 'Entregables y Evaluación', 10, '¿Cuál es el tamaño y forma del póster?', 'El tamaño del póster es A0 vertical, y el diseño es a libre creatividad del grupo.'),
    ('entregables', 'Entregables y Evaluación', 11, '¿En la JIC nacional se pedirá video, aunque sea presencial?', 'Sí. En la JIC Nacional UTP y en la JIC Nacional con SENACYT se solicitará video como material de apoyo para la evaluación.'),
]


def load_faqs(apps, schema_editor):
    FAQ = apps.get_model('web', 'frequently_ask_question')
    for slug, category, order, question, answer in FAQS:
        FAQ.objects.get_or_create(
            category_slug=slug,
            question=question,
            defaults={
                'category': category,
                'answer': answer,
                'sort_order': order,
                'is_active': True,
            },
        )


def unload_faqs(apps, schema_editor):
    FAQ = apps.get_model('web', 'frequently_ask_question')
    FAQ.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_frequently_ask_question'),
    ]

    operations = [
        migrations.RunPython(load_faqs, reverse_code=unload_faqs),
    ]
