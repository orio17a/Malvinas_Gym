document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("actividadesSearchForm");
    const filtroEstado = document.getElementById("estadoActividad");
    const filtroDia = document.getElementById("diaActividad");
    const valorDia = document.getElementById("diaActividadValor");
    const filtroTipo = document.getElementById("tipoActividad");
    const valorTipo = document.getElementById("tipoActividadValor");
    const botonLimpiar = document.getElementById("limpiarFiltrosActividades");
    const resultados = document.getElementById("actividadesResults");
    const sugerenciasDia = document.getElementById("sugerenciasDia");
    const sugerenciasTipo = document.getElementById("sugerenciasTipo");

    if (!formulario || !filtroEstado || !filtroDia || !valorDia || !filtroTipo || !valorTipo || !botonLimpiar || !resultados) {
        return;
    }

    let temporizador = null;
    let solicitudActiva = null;
    const diasActividad = JSON.parse(document.getElementById("dias-actividad-data").textContent);
    const tiposActividad = JSON.parse(document.getElementById("tipos-actividad-data").textContent);

    async function actualizarResultados(url) {
        if (solicitudActiva) solicitudActiva.abort();

        const solicitud = new AbortController();
        solicitudActiva = solicitud;

        try {
            const respuesta = await fetch(url, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
                signal: solicitud.signal
            });

            if (!respuesta.ok) throw new Error("No se pudo actualizar la lista de actividades.");

            const html = await respuesta.text();
            const documento = new DOMParser().parseFromString(html, "text/html");
            const nuevosResultados = documento.getElementById("actividadesResults");

            if (!nuevosResultados) throw new Error("La respuesta no contiene actividadesResults.");
            if (solicitud.signal.aborted || solicitudActiva !== solicitud) return;

            resultados.innerHTML = nuevosResultados.innerHTML;
            window.history.replaceState({}, "", url);
        } catch (error) {
            if (error.name !== "AbortError" && !solicitud.signal.aborted) console.error(error);
        }
    }

    function actualizarBotonLimpiar() {
        const hayFiltros = filtroEstado.value !== "" || valorDia.value !== "" || valorTipo.value !== "";
        botonLimpiar.classList.toggle("is-visible", hayFiltros);
    }

    function buscarActividades() {
        const parametros = new URLSearchParams();
        if (filtroEstado.value) parametros.set("estado", filtroEstado.value);
        if (valorDia.value) parametros.set("dia_actividad", valorDia.value);
        if (valorTipo.value) parametros.set("tipo_actividad", valorTipo.value);

        actualizarBotonLimpiar();
        const query = parametros.toString();
        actualizarResultados(formulario.action + (query ? "?" + query : ""));
    }

    function mostrarSugerencias(input, contenedor, lista, seleccionar) {
        const texto = input.value.trim().toLowerCase();
        contenedor.innerHTML = "";

        if (texto === "") {
            contenedor.classList.remove("is-visible");
            return;
        }

        const coincidencias = lista
            .filter(function (item) {
                return item.toLowerCase().includes(texto);
            })
            .slice(0, 10);

        if (coincidencias.length === 0) {
            contenedor.innerHTML = `
                <div class="autocomplete-empty">
                    No se encontraron coincidencias
                </div>
            `;
            contenedor.classList.add("is-visible");
            return;
        }

        coincidencias.forEach(function (item) {
            const opcion = document.createElement("div");
            opcion.className = "autocomplete-item";
            opcion.innerHTML = `<strong>${escapeHtml(item)}</strong>`;
            opcion.addEventListener("mousedown", function (event) {
                event.preventDefault();
                seleccionar(item);
            });
            contenedor.appendChild(opcion);
        });

        contenedor.classList.add("is-visible");
    }

    function escapeHtml(texto) {
        const div = document.createElement("div");
        div.textContent = texto;
        return div.innerHTML;
    }

    function cerrarSugerencias() {
        sugerenciasDia.classList.remove("is-visible");
        sugerenciasTipo.classList.remove("is-visible");
    }

    function seleccionarDia(valor) {
        filtroDia.value = valor;
        valorDia.value = valor;
        cerrarSugerencias();
        buscarActividades();
    }

    function seleccionarTipo(valor) {
        filtroTipo.value = valor;
        valorTipo.value = valor;
        cerrarSugerencias();
        buscarActividades();
    }

    filtroDia.addEventListener("input", function () {
        valorDia.value = "";
        mostrarSugerencias(filtroDia, sugerenciasDia, diasActividad, seleccionarDia);
        actualizarBotonLimpiar();
    });

    filtroTipo.addEventListener("input", function () {
        valorTipo.value = "";
        mostrarSugerencias(filtroTipo, sugerenciasTipo, tiposActividad, seleccionarTipo);
        actualizarBotonLimpiar();
    });

    filtroDia.addEventListener("focus", function () {
        if (filtroDia.value.trim()) mostrarSugerencias(filtroDia, sugerenciasDia, diasActividad, seleccionarDia);
    });

    filtroTipo.addEventListener("focus", function () {
        if (filtroTipo.value.trim()) mostrarSugerencias(filtroTipo, sugerenciasTipo, tiposActividad, seleccionarTipo);
    });

    filtroDia.addEventListener("keydown", function (event) {
        if (event.key !== "Enter" || event.isComposing) return;
        event.preventDefault();
        const coincidencia = diasActividad.find(function (dia) {
            return dia.toLowerCase() === filtroDia.value.trim().toLowerCase();
        });
        if (coincidencia) seleccionarDia(coincidencia);
    });

    filtroTipo.addEventListener("keydown", function (event) {
        if (event.key !== "Enter" || event.isComposing) return;
        event.preventDefault();
        const coincidencia = tiposActividad.find(function (tipo) {
            return tipo.toLowerCase() === filtroTipo.value.trim().toLowerCase();
        });
        if (coincidencia) seleccionarTipo(coincidencia);
    });

    filtroEstado.addEventListener("change", function () {
        clearTimeout(temporizador);
        buscarActividades();
    });

    formulario.addEventListener("submit", function (event) {
        event.preventDefault();
        clearTimeout(temporizador);
        cerrarSugerencias();

        const diaCoincidencia = diasActividad.find(function (dia) {
            return dia.toLowerCase() === filtroDia.value.trim().toLowerCase();
        });
        if (diaCoincidencia) valorDia.value = diaCoincidencia;

        const tipoCoincidencia = tiposActividad.find(function (tipo) {
            return tipo.toLowerCase() === filtroTipo.value.trim().toLowerCase();
        });
        if (tipoCoincidencia) valorTipo.value = tipoCoincidencia;

        buscarActividades();
    });

    botonLimpiar.addEventListener("click", function () {
        clearTimeout(temporizador);
        filtroEstado.value = "";
        filtroDia.value = "";
        valorDia.value = "";
        filtroTipo.value = "";
        valorTipo.value = "";
        cerrarSugerencias();
        actualizarBotonLimpiar();
        window.location.href = formulario.action;
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".autocomplete-wrapper")) cerrarSugerencias();
    });

    resultados.addEventListener("click", function (event) {
        const enlace = event.target.closest(".pagination a");
        if (!enlace || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        clearTimeout(temporizador);
        actualizarResultados(enlace.href);
    });

    actualizarBotonLimpiar();
});
