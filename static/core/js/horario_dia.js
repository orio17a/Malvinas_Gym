document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("id_dia");
    if (!select) return;

    const opciones = Array.from(select.options)
        .filter(option => option.value)
        .map(option => ({ id: option.value, nombre: option.textContent.trim() }));

    const wrapper = document.createElement("div");
    wrapper.className = "horario-autocomplete-wrapper";
    select.classList.add("horario-select-hidden");
    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);

    const input = document.createElement("input");
    input.type = "text";
    input.className = "horario-autocomplete-input";
    input.placeholder = "Día de la semana...";
    input.autocomplete = "off";
    input.value = select.value
        ? select.options[select.selectedIndex].textContent.trim()
        : "";
    wrapper.insertBefore(input, select);

    const sugerencias = document.createElement("div");
    sugerencias.className = "horario-autocomplete-results";
    wrapper.appendChild(sugerencias);

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

        const resultados = opciones.filter(option =>
            option.nombre.toLowerCase().startsWith(texto)
        );

        if (!resultados.length) {
            sugerencias.innerHTML = '<div class="horario-autocomplete-empty">No se encontraron días</div>';
            sugerencias.classList.add("is-visible");
            return;
        }

        resultados.forEach(function (dia) {
            const opcion = document.createElement("div");
            opcion.className = "horario-autocomplete-item";
            opcion.innerHTML = `<strong>${escapeHtml(dia.nombre)}</strong>`;
            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                select.value = dia.id;
                input.value = dia.nombre;
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
        if (!event.target.closest(".horario-autocomplete-wrapper")) {
            sugerencias.classList.remove("is-visible");
        }
    });
});
