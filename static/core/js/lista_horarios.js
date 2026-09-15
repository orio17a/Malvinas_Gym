document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("horariosFilterForm");
    const filtroDia = document.getElementById("diaHorario");
    const valorDia = document.getElementById("diaHorarioValor");
    const sugerenciasDia = document.getElementById("sugerenciasDiaHorario");
    const filtroProfesor = document.getElementById("profesorHorario");
    const valorProfesor = document.getElementById("profesorHorarioValor");
    const sugerenciasProfesor = document.getElementById("sugerenciasProfesorHorario");
    const filtroTurno = document.getElementById("turnoHorario");
    const botonLimpiar = document.getElementById("limpiarFiltrosHorarios");
    const resultados = document.getElementById("horariosResults");

    if (!formulario || !filtroDia || !valorDia || !filtroProfesor || !valorProfesor || !filtroTurno || !botonLimpiar || !resultados) {
        return;
    }

    const diasHorarios = JSON.parse(
        document.getElementById("dias-horarios-data").textContent
    );
    const profesoresHorarios = JSON.parse(
        document.getElementById("profesores-horarios-data").textContent
    );

    const profesorSeleccionado = valorProfesor.value;
    if (profesorSeleccionado) {
        const profesorEncontrado = profesoresHorarios.find(function (profesor) {
            return profesor.id === profesorSeleccionado;
        });

        if (profesorEncontrado) {
            filtroProfesor.value = profesorEncontrado.nombre;
        }
    }

    function actualizarBotonLimpiar() {
        const hayFiltros = valorDia.value !== "" || valorProfesor.value !== "" || filtroTurno.value !== "";
        botonLimpiar.classList.toggle("is-visible", hayFiltros);
    }

    function buscarHorarios() {
        const parametros = new URLSearchParams();

        if (valorDia.value) parametros.set("dia", valorDia.value);
        if (valorProfesor.value) parametros.set("profesor", valorProfesor.value);
        if (filtroTurno.value) parametros.set("turno", filtroTurno.value);

        actualizarBotonLimpiar();

        const query = parametros.toString();
        const url = formulario.action + (query ? "?" + query : "");
        actualizarResultados(url);
    }

    async function actualizarResultados(url) {
        try {
            const respuesta = await fetch(url, {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            if (!respuesta.ok) {
                throw new Error("No se pudieron actualizar los horarios.");
            }

            const html = await respuesta.text();
            const documento = new DOMParser().parseFromString(html, "text/html");
            const nuevosResultados = documento.getElementById("horariosResults");

            if (nuevosResultados) {
                resultados.innerHTML = nuevosResultados.innerHTML;
            } else {
                const tabla = documento.querySelector(".table-wrapper");
                if (tabla) resultados.innerHTML = tabla.outerHTML;
            }

            window.history.replaceState({}, "", url);
        } catch (error) {
            console.error(error);
        }
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
                const textoItem = typeof item === "string" ? item : item.nombre;
                const textoNormalizado = textoItem.toLowerCase();

                if (typeof item === "string") {
                    return textoNormalizado.startsWith(texto);
                }

                return textoNormalizado
                    .split(/[\s,]+/)
                    .some(function (parte) {
                        return parte.startsWith(texto);
                    });
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
            const textoItem = typeof item === "string" ? item : item.nombre;

            opcion.className = "autocomplete-item";
            opcion.innerHTML = `<strong>${escapeHtml(textoItem)}</strong>`;
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
        sugerenciasProfesor.classList.remove("is-visible");
    }

    filtroDia.addEventListener("input", function () {
        valorDia.value = "";
        mostrarSugerencias(filtroDia, sugerenciasDia, diasHorarios, function (valor) {
            filtroDia.value = valor;
            valorDia.value = valor;
            sugerenciasDia.classList.remove("is-visible");
            buscarHorarios();
        });
        actualizarBotonLimpiar();
    });

    filtroDia.addEventListener("keydown", function (event) {
        if (event.key !== "Enter" || event.isComposing) return;
        event.preventDefault();

        const texto = filtroDia.value.trim();
        const coincidencia = diasHorarios.find(function (dia) {
            return dia.toLowerCase() === texto.toLowerCase();
        });

        if (coincidencia) {
            filtroDia.value = coincidencia;
            valorDia.value = coincidencia;
            cerrarSugerencias();
            buscarHorarios();
        }
    });

    filtroProfesor.addEventListener("input", function () {
        valorProfesor.value = "";
        mostrarSugerencias(filtroProfesor, sugerenciasProfesor, profesoresHorarios, function (profesor) {
            filtroProfesor.value = profesor.nombre;
            valorProfesor.value = profesor.id;
            sugerenciasProfesor.classList.remove("is-visible");
            buscarHorarios();
        });
        actualizarBotonLimpiar();
    });

    filtroProfesor.addEventListener("keydown", function (event) {
        if (event.key !== "Enter" || event.isComposing) return;
        event.preventDefault();

        const texto = filtroProfesor.value.trim().toLowerCase();
        const coincidencia = profesoresHorarios.find(function (profesor) {
            return profesor.nombre.toLowerCase() === texto;
        });

        if (coincidencia) {
            filtroProfesor.value = coincidencia.nombre;
            valorProfesor.value = coincidencia.id;
            cerrarSugerencias();
            buscarHorarios();
        }
    });

    filtroDia.addEventListener("focus", function () {
        if (!filtroDia.value.trim()) return;
        mostrarSugerencias(filtroDia, sugerenciasDia, diasHorarios, function (valor) {
            filtroDia.value = valor;
            valorDia.value = valor;
            cerrarSugerencias();
            buscarHorarios();
        });
    });

    filtroProfesor.addEventListener("focus", function () {
        if (!filtroProfesor.value.trim()) return;
        mostrarSugerencias(filtroProfesor, sugerenciasProfesor, profesoresHorarios, function (profesor) {
            filtroProfesor.value = profesor.nombre;
            valorProfesor.value = profesor.id;
            cerrarSugerencias();
            buscarHorarios();
        });
    });

    filtroTurno.addEventListener("change", buscarHorarios);

    formulario.addEventListener("submit", function (event) {
        event.preventDefault();
        cerrarSugerencias();

        const diaEscrito = filtroDia.value.trim();
        const diaCoincidencia = diasHorarios.find(function (dia) {
            return dia.toLowerCase() === diaEscrito.toLowerCase();
        });
        if (diaCoincidencia) valorDia.value = diaCoincidencia;

        const profesorEscrito = filtroProfesor.value.trim().toLowerCase();
        const profesorCoincidencia = profesoresHorarios.find(function (profesor) {
            return profesor.nombre.toLowerCase() === profesorEscrito;
        });
        if (profesorCoincidencia) valorProfesor.value = profesorCoincidencia.id;

        buscarHorarios();
    });

    botonLimpiar.addEventListener("click", function () {
        filtroDia.value = "";
        valorDia.value = "";
        filtroProfesor.value = "";
        valorProfesor.value = "";
        filtroTurno.value = "";
        cerrarSugerencias();
        actualizarBotonLimpiar();
        window.location.replace(formulario.action);
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".autocomplete-wrapper")) {
            cerrarSugerencias();
        }
    });

    actualizarBotonLimpiar();
});
