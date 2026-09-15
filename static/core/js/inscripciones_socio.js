document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("inscripcionesFilterForm");
    const input = document.getElementById("buscarSocioInscripcion");
    const valor = document.getElementById("buscarSocioInscripcionValor");
    const sugerencias = document.getElementById("sugerenciasSocioInscripcion");
    const datos = document.getElementById("socios-inscripciones-data");

    if (!formulario || !input || !valor || !sugerencias || !datos) return;

    const socios = JSON.parse(datos.textContent);

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

        const resultados = socios.filter(function (socio) {
            return (socio.nombre || "").toLowerCase().startsWith(texto) ||
                (socio.apellido || "").toLowerCase().startsWith(texto) ||
                String(socio.dni || "").toLowerCase().startsWith(texto);
        }).slice(0, 10);

        if (!resultados.length) {
            sugerencias.innerHTML = '<div class="inscripciones-autocomplete-empty">No se encontraron socios</div>';
            sugerencias.classList.add("is-visible");
            return;
        }

        resultados.forEach(function (socio) {
            const opcion = document.createElement("div");
            const nombre = `${socio.apellido}, ${socio.nombre}`;
            opcion.className = "inscripciones-autocomplete-item";
            opcion.innerHTML = `<strong>${escapeHtml(nombre)}</strong><span>DNI ${escapeHtml(String(socio.dni))}</span>`;
            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                input.value = nombre;
                valor.value = socio.dni;
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
        if (!event.target.closest(".inscripciones-socio-wrapper")) {
            sugerencias.classList.remove("is-visible");
        }
    });
});
