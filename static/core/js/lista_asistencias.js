document.addEventListener("DOMContentLoaded", function () {
    const inputSocio = document.getElementById("buscarSocio");
    const sugerencias = document.getElementById("sugerenciasSocio");
    const datosSocios = document.getElementById("socios-autocomplete-data");

    if (!inputSocio || !sugerencias || !datosSocios) {
        return;
    }

    const socios = JSON.parse(datosSocios.textContent);

    function mostrarSugerencias() {
        const texto = inputSocio.value.trim().toLowerCase();
        sugerencias.innerHTML = "";

        if (texto === "") {
            sugerencias.classList.remove("is-visible");
            return;
        }

        const resultados = socios
            .filter(function (socio) {
                const nombre = (socio.nombre || "").toLowerCase();
                const dni = (socio.dni || "").toLowerCase();

                return nombre.includes(texto) || dni.includes(texto);
            })
            .slice(0, 8);

        if (resultados.length === 0) {
            sugerencias.innerHTML = `
                <div class="autocomplete-empty-asistencia">
                    No se encontraron socios
                </div>
            `;
            sugerencias.classList.add("is-visible");
            return;
        }

        resultados.forEach(function (socio) {
            const opcion = document.createElement("div");
            opcion.className = "autocomplete-item-asistencia";
            opcion.innerHTML = `
                <strong>${escapeHtml(socio.nombre)}</strong>
                <span>DNI ${escapeHtml(socio.dni)}</span>
            `;

            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                inputSocio.value = socio.nombre;
                sugerencias.classList.remove("is-visible");
                inputSocio.form.submit();
            });

            sugerencias.appendChild(opcion);
        });

        sugerencias.classList.add("is-visible");
    }

    function escapeHtml(texto) {
        const div = document.createElement("div");
        div.textContent = texto;
        return div.innerHTML;
    }

    inputSocio.addEventListener("input", mostrarSugerencias);

    inputSocio.addEventListener("focus", function () {
        if (inputSocio.value.trim()) {
            mostrarSugerencias();
        }
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".autocomplete-wrapper-asistencia")) {
            sugerencias.classList.remove("is-visible");
        }
    });
});
