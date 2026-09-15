document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("inscripcionesFilterForm");
    const input = document.getElementById("actividadInscripcion");
    const valor = document.getElementById("actividadInscripcionValor");
    const sugerencias = document.getElementById("sugerenciasActividadInscripcion");
    const datos = document.getElementById("actividades-inscripciones-data");

    if (!formulario || !input || !valor || !sugerencias || !datos) return;

    const actividades = JSON.parse(datos.textContent);

    function escapeHtml(texto) {
        const div = document.createElement("div");
        div.textContent = texto;
        return div.innerHTML;
    }

    function mostrarSugerencias() {
        const texto = input.value.trim().toLowerCase();
        sugerencias.innerHTML = "";

        if (!texto) {
            sugerencias.classList.remove("is-visible");
            return;
        }

        const resultados = actividades.filter(function (actividad) {
            return actividad.toLowerCase().startsWith(texto);
        }).slice(0, 10);

        if (!resultados.length) {
            sugerencias.innerHTML = '<div class="inscripciones-autocomplete-empty">No se encontraron actividades</div>';
            sugerencias.classList.add("is-visible");
            return;
        }

        resultados.forEach(function (actividad) {
            const opcion = document.createElement("div");
            opcion.className = "inscripciones-autocomplete-item";
            opcion.innerHTML = `<strong>${escapeHtml(actividad)}</strong>`;
            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                input.value = actividad;
                valor.value = actividad;
                sugerencias.classList.remove("is-visible");
                formulario.submit();
            });
            sugerencias.appendChild(opcion);
        });

        sugerencias.classList.add("is-visible");
    }

    input.addEventListener("input", function () {
        valor.value = "";
        mostrarSugerencias();
    });

    input.addEventListener("focus", function () {
        if (input.value.trim()) mostrarSugerencias();
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".inscripciones-actividad-wrapper")) {
            sugerencias.classList.remove("is-visible");
        }
    });
});
