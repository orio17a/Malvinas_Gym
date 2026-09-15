document.addEventListener("DOMContentLoaded", function () {
    const actividadesData = document.getElementById("actividades-horario-data");
    const profesoresData = document.getElementById("profesores-horario-data");

    function escapeHtml(texto) {
        const div = document.createElement("div");
        div.textContent = texto;
        return div.innerHTML;
    }

    function activarAutocomplete(select, items, configurarTexto) {
        if (!select || !items) return;

        const wrapper = document.createElement("div");
        wrapper.className = "horario-autocomplete-wrapper";
        select.classList.add("horario-select-hidden");
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        const input = document.createElement("input");
        input.type = "text";
        input.className = "horario-autocomplete-input";
        input.autocomplete = "off";
        input.value = configurarTexto.actual();
        input.placeholder = configurarTexto.placeholder;
        wrapper.insertBefore(input, select);

        const sugerencias = document.createElement("div");
        sugerencias.className = "horario-autocomplete-results";
        wrapper.appendChild(sugerencias);

        function mostrarSugerencias() {
            const texto = input.value.trim().toLowerCase();
            sugerencias.innerHTML = "";

            if (!texto) {
                select.value = "";
                sugerencias.classList.remove("is-visible");
                return;
            }

            const resultados = items.filter(function (item) {
                return configurarTexto.buscar(item, texto);
            }).slice(0, 10);

            if (!resultados.length) {
                sugerencias.innerHTML = '<div class="horario-autocomplete-empty">No se encontraron coincidencias</div>';
                sugerencias.classList.add("is-visible");
                return;
            }

            resultados.forEach(function (item) {
                const opcion = document.createElement("div");
                const textoPrincipal = configurarTexto.titulo(item);
                const textoSecundario = configurarTexto.subtitulo(item);
                opcion.className = "horario-autocomplete-item";
                opcion.innerHTML = `<strong>${escapeHtml(textoPrincipal)}</strong><span>${escapeHtml(textoSecundario)}</span>`;
                opcion.addEventListener("mousedown", function (event) {
                    event.preventDefault();
                    select.value = item.id;
                    input.value = configurarTexto.valor(item);
                    sugerencias.classList.remove("is-visible");
                });
                sugerencias.appendChild(opcion);
            });

            sugerencias.classList.add("is-visible");
        }

        input.addEventListener("input", function () {
            select.value = "";
            mostrarSugerencias();
        });
        input.addEventListener("focus", function () {
            if (input.value.trim()) mostrarSugerencias();
        });

        document.addEventListener("click", function (event) {
            if (!event.target.closest(".horario-autocomplete-wrapper")) {
                sugerencias.classList.remove("is-visible");
            }
        });
    }

    const actividades = actividadesData ? JSON.parse(actividadesData.textContent) : [];
    const profesores = profesoresData ? JSON.parse(profesoresData.textContent) : [];

    activarAutocomplete(
        document.getElementById("id_actividad"),
        actividades,
        {
            placeholder: "Actividad...",
            actual: function () {
                const item = actividades.find(item => String(item.id) === document.getElementById("id_actividad").value);
                return item ? item.nombre : "";
            },
            buscar: function (item, texto) {
                return item.nombre.toLowerCase().startsWith(texto);
            },
            titulo: item => item.nombre,
            subtitulo: () => "Seleccionar actividad",
            valor: item => item.nombre
        }
    );

    activarAutocomplete(
        document.getElementById("id_profesor"),
        profesores,
        {
            placeholder: "Nombre o DNI del profesor...",
            actual: function () {
                const item = profesores.find(item => String(item.id) === document.getElementById("id_profesor").value);
                return item ? `${item.apellido}, ${item.nombre}` : "";
            },
            buscar: function (item, texto) {
                return item.nombre.toLowerCase().startsWith(texto) ||
                    item.apellido.toLowerCase().startsWith(texto) ||
                    String(item.dni).toLowerCase().startsWith(texto);
            },
            titulo: item => `${item.apellido}, ${item.nombre}`,
            subtitulo: item => `DNI ${item.dni}`,
            valor: item => `${item.apellido}, ${item.nombre}`
        }
    );
});
