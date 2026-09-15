document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("profesoresFilterForm");
    const inputBuscar = document.getElementById("buscarProfesor");
    const sugerencias = document.getElementById("sugerenciasProfesor");

    if (!formulario || !inputBuscar || !sugerencias) {
        return;
    }

    const datosProfesores = JSON.parse(
        document.getElementById("profesores-autocomplete-data").textContent
    );

    function escapeHtml(texto) {
        const div = document.createElement("div");
        div.textContent = texto;
        return div.innerHTML;
    }

    function mostrarSugerencias() {
        const texto = inputBuscar.value.trim().toLowerCase();
        sugerencias.innerHTML = "";

        if (texto === "") {
            sugerencias.classList.remove("is-visible");
            return;
        }

        const coincidencias = datosProfesores
            .filter(function (profesor) {
                const nombre = (profesor.nombre || "").toLowerCase();
                const apellido = (profesor.apellido || "").toLowerCase();
                const dni = String(profesor.dni || "").toLowerCase();

                return nombre.startsWith(texto) ||
                    apellido.startsWith(texto) ||
                    dni.startsWith(texto);
            })
            .slice(0, 10);

        if (coincidencias.length === 0) {
            sugerencias.innerHTML = `
                <div class="profesor-autocomplete-empty">
                    No se encontraron profesores
                </div>
            `;
            sugerencias.classList.add("is-visible");
            return;
        }

        coincidencias.forEach(function (profesor) {
            const opcion = document.createElement("div");
            const nombreCompleto = `${profesor.apellido}, ${profesor.nombre}`;

            opcion.className = "profesor-autocomplete-item";
            opcion.innerHTML = `
                <strong>${escapeHtml(nombreCompleto)}</strong>
                <span>DNI ${escapeHtml(String(profesor.dni || "-"))}</span>
            `;

            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                inputBuscar.value = profesor.apellido;
                sugerencias.classList.remove("is-visible");
                formulario.submit();
            });

            sugerencias.appendChild(opcion);
        });

        sugerencias.classList.add("is-visible");
    }

    inputBuscar.addEventListener("input", mostrarSugerencias);

    inputBuscar.addEventListener("focus", function () {
        if (inputBuscar.value.trim()) {
            mostrarSugerencias();
        }
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".profesor-autocomplete-wrapper")) {
            sugerencias.classList.remove("is-visible");
        }
    });
});
