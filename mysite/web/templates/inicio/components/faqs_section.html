<script lang="ts">
    import { slide } from "svelte/transition";

    let openCategory = $state<string | null>(null);
    let openQuestion = $state<string | null>(null);

    const faqs = {
        participacion: {
            title: "Participación y Equipos",
            items: [
                {
                    q: "¿Quiénes pueden participar en la JIC?",
                    a: "Pueden participar estudiantes, docentes e investigadores de las universidades acreditadas por el CONEAUPA.",
                },
                {
                    q: "¿Si mi compañero es de otra facultad, puede participar en mi equipo?",
                    a: "Sí, se permite grupos de estudiantes de diferentes facultades, pero el proyecto solo puede estar registrado en una de las facultades.",
                },
                {
                    q: "¿Puede mi asesor ser de otra facultad o sede?",
                    a: "Sí, puede ser de otra facultad o sede, pero el proyecto se registra donde pertenecen los estudiantes.",
                },
                {
                    q: "¿Va a existir la figura de co-asesor?",
                    a: "Sí, los equipos pueden contar con un asesor y un co-asesor.",
                },
                {
                    q: "¿Un estudiante podrá formar parte de más de un grupo?",
                    a: "Sí, los estudiantes pueden participar en más de un grupo simultáneamente.",
                },
                {
                    q: "¿Cuáles son los pasos para participar?",
                    a: "Conformar un equipo de 2 o 3 estudiantes con un asesor y registrarse en la plataforma oficial.",
                },
                {
                    q: "¿Se puede registrar una investigación individual?",
                    a: "No. Los grupos deben ser de 2 o 3 estudiantes más el asesor.",
                },
                {
                    q: "¿Puedo participar en la JIC si estoy realizando tesis de licenciatura? ",
                    a: "Sí, mientras aún no tenga el título universitario y se encuentre matriculado en el semestre respectivo. ",
                },
                {
                    q: "¿Es posible participar en la JIC siendo extranjero?",
                    a: "Todo estudiante regular de una universidad participante que cumpla los requisitos puede participar.",
                },
                {
                    q: "¿Puedo participar si ya cuento con una licenciatura?",
                    a: "No, el programa de la JIC es para estudiantes que no estén graduados.",
                },
                {
                    q: "¿Cuál es el siguiente paso para la final JIC?",
                    a: "Luego de finalizada la JIC Interna, cada universidad debe registrar a sus participantes en la plataforma. En el caso de la UTP, solo deben actualizar los artículos.",
                },
                {
                    q: "¿Para participar en la final, el equipo debe registrarse en la plataforma del Congreso?",
                    a: "Sí, todos los integrantes del grupo deben registrarse en el Congreso.",
                },
            ],
        },
        plataforma: {
            title: "Plataforma Tecnológica",
            items: [
                {
                    q: "¿Dónde me registro para participar?",
                    a: "Debes ingresar en el enlace oficial: jic.utp.ac.pa/login",
                },
                {
                    q: "¿Cuál es el procedimiento para registrar los proyectos?",
                    a: "El asesor registra el proyecto, los estudiantes suben documentos y el asesor aprueba finalmente.",
                },
                {
                    q: "¿Soy asesor y la plataforma no me permite editar datos?",
                    a: "Solo los estudiantes cuentan con los permisos para editar los datos del proyecto.",
                },
                {
                    q: "¿Existe un canal para estar enterados de forma expedita de cualquier información que afecte a los asesores o estudiantes?",
                    a: "Puede contactarnos a través de nuestro correo: jornada.cientifica@utp.ac.pa o por WhatsApp: 6958-4483",
                },
            ],
        },
        entregables: {
            title: "Entregables y Evaluación",
            items: [
                {
                    q: "¿Qué documentos pide la JIC final: artículos, pósteres u otros?",
                    a: "Todo grupo finalista debe entregar su artículo, póster y video. Estos son requisitos de la SENACYT para la evaluación.",
                },
                {
                    q: "¿Cuánto debe durar el vídeo que se presenta por YouTube?",
                    a: "El vídeo debe tener una duración máxima de 10 minutos, donde los estudiantes presenten el póster de su investigación.",
                },
                {
                    q: "¿Se cuenta con un formato de artículo y dónde se puede descargar?",
                    a: "Sí, se cuenta con un formato de artículo. Puede encontrarlo en...",
                },
                // {
                //     q: "No me carga la plantilla para los artículos en la página web de la JIC.",
                //     a: "Intente abrir la página web de la JIC desde el explorador Microsoft Edge o Firefox para descargar las plantillas; en ocasiones, desde Google Chrome no se descargan.",
                // },
                {
                    q: "¿Se deben eliminar los nombres de los estudiantes, los logos o los nombres de los asesores?",
                    a: "Sí, en la versión digital no deben estar los nombres ni logos. El póster impreso para exhibición en congreso nacional organizado por APANAC u otra institución sí puede incluirlos.",
                },
                {
                    q: "¿Se puede corregir nuevamente el artículo?",
                    a: "Sí, teniendo en cuenta la fecha que se asigne para este fin.",
                },
                {
                    q: "¿Si clasifico a la siguiente etapa debo volver a subir los documentos a la plataforma JIC?",
                    a: "Sí. Se les habilitará la plataforma para que puedan subir nuevamente los documentos.",
                },
                {
                    q: "¿El nombre del asesor va en el artículo? ¿El nombre del asesor va en el póster?",
                    a: "En la JIC de Unidades Académicas, los coordinadores deciden si colocan el nombre del asesor. En la JIC final UTP y en la JIC Nacional, el artículo y el póster en versión digital no deben tener nombres ni afiliaciones de asesores o estudiantes. En la sesión de pósteres impresos para la JIC Nacional de SENACYT sí pueden colocarse.",
                },
                {
                    q: "¿Cómo compruebo el porcentaje de originalidad de mi proyecto?",
                    a: "Antes de subir el artículo final, debe pasarlo por un software anti-plagio gratuito y hacer los cambios necesarios si no cumple con el porcentaje mínimo aceptado. El artículo final será sometido a un software anti-plagio por parte de los organizadores.",
                },
                {
                    q: "¿En cuánto tiempo se debe presentar el proyecto?",
                    a: "Se tienen 15 minutos para exponer el trabajo y 5 minutos para preguntas y respuestas. Todo depende de la dinámica establecida.",
                },
                {
                    q: "¿Cuál es el tamaño y forma del póster?",
                    a: "El tamaño del póster es A0 vertical, y el diseño es a libre creatividad del grupo.",
                },
                {
                    q: "¿En la JIC nacional se pedirá video, aunque sea presencial?",
                    a: "Sí. En la JIC Nacional UTP y en la JIC Nacional con SENACYT se solicitará video como material de apoyo para la evaluación.",
                },
            ],
        },
    };

    const toggleCategory = (id: string) => {
        openCategory = openCategory === id ? null : id;
        openQuestion = null;
    };

    const toggleQuestion = (id: string) => {
        openQuestion = openQuestion === id ? null : id;
    };
</script>

<section class="bg-white dark:bg-gray-900">
    <div class="py-8 px-4 mx-auto max-w-7xl sm:py-16 lg:px-6">
        <h2
            class="font-serif mb-6 lg:mb-8 text-2xl md:text-3xl tracking-tight font-extrabold text-center text-foreground"
        >
            Preguntas Frecuentes
        </h2>
        <p
            class="mb-6 lg:mb-8 text-sm sm:text-base md:text-lg tracking-tight font-normal text-center text-muted-foreground"
        >
            Todo lo que necesitas saber sobre la Jornada de Iniciación
            Científica
        </p>

        <div class="mx-auto max-w-3xl">
            <div id="accordion-flush">
                {#each Object.entries(faqs) as [key, section]}
                    {@const isCatOpen = openCategory === key}

                    <div class="border-b border-border">
                        <h2 id="category-heading-{key}">
                            <button
                                type="button"
                                onclick={() => toggleCategory(key)}
                                class="flex justify-between items-center py-5 w-full font-bold text-left text-base md:text-lg cursor-pointer transition-colors duration-200 {isCatOpen
                                    ? 'text-foreground'
                                    : 'text-muted-foreground hover:text-foreground'}"
                            >
                                <span>{section.title}</span>
                                <svg
                                    class="w-6 h-6 shrink-0 transition-transform duration-300 {isCatOpen
                                        ? 'rotate-180'
                                        : ''}"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        fill-rule="evenodd"
                                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                        clip-rule="evenodd"
                                    ></path>
                                </svg>
                            </button>
                        </h2>

                        {#if isCatOpen}
                            <div
                                transition:slide={{ duration: 700 }}
                                class="overflow-hidden"
                            >
                                <div
                                    class="pl-4 border-l-2 border-gray-100 dark:border-gray-800 mb-2"
                                >
                                    {#each section.items as item, i}
                                        {@const qId = `${key}-${i}`}
                                        {@const isQOpen = openQuestion === qId}

                                        <div
                                            class="border-b border-border last:border-b-0"
                                        >
                                            <h3>
                                                <button
                                                    type="button"
                                                    onclick={() =>
                                                        toggleQuestion(qId)}
                                                    class="flex justify-between items-center py-4 w-full font-medium text-left text-sm sm:text-base cursor-pointer transition-colors duration-200 {isQOpen
                                                        ? 'text-foreground'
                                                        : 'text-muted-foreground hover:text-foreground'}"
                                                >
                                                    <span class="pr-4"
                                                        >{item.q}</span
                                                    >
                                                    <svg
                                                        class="w-5 h-5 shrink-0 transition-transform duration-200 {isQOpen
                                                            ? 'rotate-180'
                                                            : ''}"
                                                        fill="currentColor"
                                                        viewBox="0 0 20 20"
                                                    >
                                                        <path
                                                            fill-rule="evenodd"
                                                            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                                            clip-rule="evenodd"
                                                        ></path>
                                                    </svg>
                                                </button>
                                            </h3>

                                            {#if isQOpen}
                                                <div
                                                    transition:slide={{
                                                        duration: 200,
                                                    }}
                                                    class="overflow-hidden"
                                                >
                                                    <div class="pb-4">
                                                        <p
                                                            class="text-gray-500 dark:text-gray-400 leading-relaxed text-sm sm:text-base"
                                                        >
                                                            {item.a}
                                                        </p>
                                                    </div>
                                                </div>
                                            {/if}
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>
    </div>
</section>
