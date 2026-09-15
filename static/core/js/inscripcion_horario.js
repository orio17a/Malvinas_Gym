document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("id_horario");
    const datos = document.getElementById("horarios-inscripcion-data");

    if (!select || !datos) return;

    const horarios = JSON.parse(datos.textContent);
    const wrapper = document.createElement("div");
    wrapper.className = "inscripcion-autocomplete-wrapper";
    select.classList.add("inscripcion-select-hidden");
    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);

    const input = document.createElement("input");
    input.type = "text";
    input.id = "horarioInscripcionTexto";
    input.placeholder = "Actividad, día u horario...";
    input.autocomplete = "off";
    input.value = selectedLabel();
    wrapper.insertBefore(input, select);

    const sugerencias = document.createElement("div");
    sugerencias.className = "inscripcion-autocomplete-results";
    wrapper.appendChild(sugerencias);

    function selectedLabel() {
        const horario = horarios.find(item => String(item.id) === select.value);
        return horario ? label(horario) : "";
    }

    function label(horario) {
        return `${horario.actividad} - ${horario.dia} ${horario.hora_inicio} a ${horario.hora_fin} (${horario.profesor})`;
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

        const resultados = horarios.filter(function (horario) {
            return label(horario).toLowerCase().includes(texto);
        }).slice(0, 10);

        if (!resultados.length) {
            sugerencias.innerHTML = '<div class="inscripcion-autocomplete-empty">No se encontraron horarios</div>';
            sugerencias.classList.add("is-visible");
            return;
        }

        resultados.forEach(function (horario) {
            const opcion = document.createElement("div");
            opcion.className = "inscripcion-autocomplete-item";
            opcion.innerHTML = `<strong>${escapeHtml(horario.actividad)} - ${escapeHtml(horario.dia)}</strong><span>${escapeHtml(horario.hora_inicio)} a ${escapeHtml(horario.hora_fin)} | ${escapeHtml(horario.profesor)}</span>`;
            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                select.value = horario.id;
                input.value = label(horario);
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
