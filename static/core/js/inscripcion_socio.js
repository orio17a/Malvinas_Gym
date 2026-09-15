document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("id_socio");
    const datos = document.getElementById("socios-inscripcion-data");

    if (!select || !datos) return;

    const socios = JSON.parse(datos.textContent);
    const wrapper = document.createElement("div");
    wrapper.className = "inscripcion-autocomplete-wrapper";
    select.classList.add("inscripcion-select-hidden");
    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);

    const input = document.createElement("input");
    input.type = "text";
    input.id = "socioInscripcionTexto";
    input.placeholder = "Nombre o DNI del socio...";
    input.autocomplete = "off";
    input.value = selectedLabel();
    wrapper.insertBefore(input, select);

    const sugerencias = document.createElement("div");
    sugerencias.className = "inscripcion-autocomplete-results";
    wrapper.appendChild(sugerencias);

    function selectedLabel() {
        const socio = socios.find(item => String(item.id) === select.value);
        return socio ? `${socio.apellido}, ${socio.nombre}` : "";
    }

    function escapeHtml(texto) {
        const div = document.createElement("div");
        div.textContent = texto;
        return div.innerHTML;
    }

    function mostrarSugerencias() {
        const texto = input.value.trim().toLowerCase();
        sugerencias.innerHTML = "";
        select.value = "";

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
            sugerencias.innerHTML = '<div class="inscripcion-autocomplete-empty">No se encontraron socios</div>';
            sugerencias.classList.add("is-visible");
            return;
        }

        resultados.forEach(function (socio) {
            const opcion = document.createElement("div");
            const nombre = `${socio.apellido}, ${socio.nombre}`;
            opcion.className = "inscripcion-autocomplete-item";
            opcion.innerHTML = `<strong>${escapeHtml(nombre)}</strong><span>DNI ${escapeHtml(String(socio.dni))}</span>`;
            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                select.value = socio.id;
                input.value = nombre;
                sugerencias.classList.remove("is-visible");
            });
            sugerencias.appendChild(opcion);
        });

        sugerencias.classList.add("is-visible");
    }

    input.addEventListener("input", mostrarSugerencias);
    input.addEventListener("focus", function () {
        if (input.value.trim()) mostrarSugerencias();
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".inscripcion-autocomplete-wrapper")) {
            sugerencias.classList.remove("is-visible");
        }
    });
});
