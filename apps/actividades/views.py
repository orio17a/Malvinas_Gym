import datetime
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from apps.usuarios.models import EstadoUsuario, Rol, Usuario
from apps.socios.models import Socio
from .forms import ActividadForm, AsistenciaForm, HorarioForm, InscripcionForm, ProfesorForm
from .exports import exportar_asistencias_excel, exportar_asistencias_pdf
from .models import (
    DIAS_SEMANA,
    NOMBRES_ESTADOS_PREDEFINIDOS,
    Actividad,
    Asistencia,
    EstadoActividad,
    Horario,
    Inscripcion,
    Profesor, EstadoProfesor
)


def _eliminar_con_proteccion(request, obj, lista_url, mensaje_en_uso):
    """Borra `obj` y redirige a `lista_url`. Si tiene registros
    relacionados con on_delete=PROTECT, avisa en vez de tirar un error
    500 (mismo criterio que apps.socios.views.eliminar_socio)."""
    nombre = str(obj)

    try:
        obj.delete()
    except ProtectedError:
        messages.error(request, f'No se puede eliminar "{nombre}": {mensaje_en_uso}')
        return redirect(lista_url)

    messages.success(request, f'"{nombre}" fue eliminado correctamente.')
    return redirect(lista_url)


# ---------------------------------------------------------------------
# Actividad
#
# No hay ABM de EstadoActividad: los tres estados (Activo, Inactivo,
# Suspendido) son fijos y se siembran por migración
# (0007_seed_estados_predefinidos). El administrador ya no tiene forma
# de crear o editar estados a mano.
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_actividad", raise_exception=True)
def lista_actividades(request):
    buscar = request.GET.get("buscar", "").strip()
    estado_id = request.GET.get("estado", "").strip()
    dia_actividad = request.GET.get("dia_actividad", "").strip()
    tipo_actividad = request.GET.get("tipo_actividad", "").strip()

    actividades = (
        Actividad.objects
        .select_related("estado_actividad")
        .prefetch_related("horarios")
        .all()
    )

    # ---------------------------------------------------------
    # BUSCAR POR NOMBRE
    # ---------------------------------------------------------
    if buscar:
        actividades = actividades.filter(
            nombre__icontains=buscar
        )

    # ---------------------------------------------------------
    # FILTRAR POR ESTADO
    # ---------------------------------------------------------
    if estado_id:
        actividades = actividades.filter(
            estado_actividad_id=estado_id
        )

    # ---------------------------------------------------------
    # FILTRAR POR DÍA DE ACTIVIDAD
    # ---------------------------------------------------------
    if dia_actividad:
        actividades = actividades.filter(
            horarios__dia=dia_actividad
        )

        actividades = actividades.distinct()

    # ---------------------------------------------------------
    # FILTRAR POR NOMBRE DE ACTIVIDAD
    # ---------------------------------------------------------
    if tipo_actividad:
        actividades = actividades.filter(
            nombre__icontains=tipo_actividad
        )
    # ---------------------------------------------------------
    # ESTADOS DEL FILTRO
    # ---------------------------------------------------------
    estados_filtro = EstadoActividad.objects.filter(
        nombre__in=NOMBRES_ESTADOS_PREDEFINIDOS
    ).order_by("nombre")

    # ---------------------------------------------------------
    # DÍAS DISPONIBLES
    # ---------------------------------------------------------
    dias_con_actividades = set(
        Horario.objects.values_list("dia", flat=True).distinct()
    )
    dias_actividad = [
        dia for dia, _ in DIAS_SEMANA if dia in dias_con_actividades
    ]

    tipos_actividad = list(
        Actividad.objects
        .values_list("nombre", flat=True)
        .distinct()
        .order_by("nombre")
    )

    # ---------------------------------------------------------
    # CONTADORES
    # ---------------------------------------------------------
    actividades_totales = Actividad.objects.count()

    actividades_activas = Actividad.objects.filter(
        estado_actividad__nombre__iexact="Activo"
    ).count()

    actividades_inactivas = Actividad.objects.filter(
        estado_actividad__nombre__iexact="Inactivo"
    ).count()

    actividades_suspendidas = Actividad.objects.filter(
        estado_actividad__nombre__iexact="Suspendido"
    ).count()

    # ---------------------------------------------------------
    # PAGINACIÓN
    # ---------------------------------------------------------
    paginator = Paginator(actividades, 10)
    pagina = request.GET.get("page")

    actividades_paginadas = paginator.get_page(pagina)

    contexto = {
        "actividades": actividades_paginadas,

        # búsqueda
        "buscar": buscar,

        # estado
        "estado_id": estado_id,
        "estados_filtro": estados_filtro,

        # día de actividad
        "dia_actividad": dia_actividad,
        "dias_actividad": dias_actividad,

        # tipo de actividad
        "tipo_actividad": tipo_actividad,
        "tipos_actividad": tipos_actividad,

        # contadores
        "total_actividades": actividades_totales,
        "actividades_totales": actividades_totales,
        "actividades_activas": actividades_activas,
        "actividades_inactivas": actividades_inactivas,
        "actividades_suspendidas": actividades_suspendidas,
    }

    # ---------------------------------------------------------
    # SI VIENE DE AJAX, DEVOLVEMOS SOLO LA TABLA
    # ---------------------------------------------------------
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        plantilla = "actividades/_resultados_actividades.html"
    else:
        plantilla = "actividades/lista_actividades.html"

    return render(request, plantilla, contexto)

@login_required
@permission_required("actividades.add_actividad", raise_exception=True)
def crear_actividad(request):
    form = ActividadForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        actividad = form.save()

        messages.success(
            request,
            f'La actividad "{actividad}" fue creada correctamente.'
        )

        return redirect("actividades:actividad_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {
            "form": form,
            "titulo": "Nueva actividad",
            "cancelar_url": "actividades:actividad_lista",
        },
    )


@login_required
@permission_required("actividades.view_actividad", raise_exception=True)
def detalle_actividad(request, pk):
    actividad = get_object_or_404(
        Actividad.objects.select_related("estado_actividad"),
        pk=pk
    )

    horarios = actividad.horarios.select_related("profesor").all()

    return render(
        request,
        "actividades/detalle_actividad.html",
        {
            "actividad": actividad,
            "horarios": horarios,
        },
    )


@login_required
@permission_required("actividades.change_actividad", raise_exception=True)
def editar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)

    form = ActividadForm(
        request.POST or None,
        instance=actividad
    )

    if request.method == "POST" and form.is_valid():
        actividad = form.save()

        messages.success(
            request,
            f'La actividad "{actividad}" fue actualizada correctamente.'
        )

        return redirect("actividades:actividad_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {
            "form": form,
            "titulo": "Editar actividad",
            "cancelar_url": "actividades:actividad_lista",
        },
    )


@login_required
@permission_required("actividades.delete_actividad", raise_exception=True)
def eliminar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            actividad,
            "actividades:actividad_lista",
            "todavía tiene horarios asociados.",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {
            "objeto": actividad,
            "cancelar_url": "actividades:actividad_lista",
            "advertencia": (
                "No se puede eliminar una actividad que tenga "
                "horarios asociados."
            ),
        },
    )

# ---------------------------------------------------------------------
# Horario
#
# Tampoco hay ABM de EstadoProfesor, por la misma razón que
# EstadoActividad de arriba.
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_horario", raise_exception=True)
def lista_horarios(request):
    horarios = Horario.objects.select_related("actividad", "profesor").all()

    paginator = Paginator(horarios, 10)
    pagina = request.GET.get("page")

    return render(
        request,
        "actividades/lista_horarios.html",
        {"horarios": paginator.get_page(pagina)},
    )


@login_required
@permission_required("actividades.view_horario", raise_exception=True)
def detalle_horario(request, pk):
    horario = get_object_or_404(
        Horario.objects.select_related("actividad", "profesor"), pk=pk
    )
    inscriptos = horario.inscripciones.select_related("socio").all()

    return render(
        request,
        "actividades/detalle_horario.html",
        {"horario": horario, "inscriptos": inscriptos},
    )


@login_required
@permission_required("actividades.add_horario", raise_exception=True)
def crear_horario(request):
    form = HorarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        horario = form.save()
        messages.success(request, f'El horario "{horario}" fue creado correctamente.')
        return redirect("actividades:horario_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {
            "form": form,
            "titulo": "Nuevo horario",
            "cancelar_url": "actividades:horario_lista",
            "horario_autocomplete": True,
            "actividades_horario_autocomplete": list(
                Actividad.objects.order_by("nombre").values("id", "nombre")
            ),
            "profesores_horario_autocomplete": list(
                Profesor.objects.order_by("apellido", "nombre").values(
                    "id", "nombre", "apellido", "dni"
                )
            ),
        },
    )


@login_required
@permission_required("actividades.change_horario", raise_exception=True)
def editar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    form = HorarioForm(request.POST or None, instance=horario)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f'El horario "{horario}" fue actualizado correctamente.')
        return redirect("actividades:horario_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Editar horario", "cancelar_url": "actividades:horario_lista"},
    )


@login_required
@permission_required("actividades.delete_horario", raise_exception=True)
def eliminar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            horario,
            "actividades:horario_lista",
            "todavía tiene asistencias registradas (las inscripciones sí "
            "se eliminarían junto con el horario).",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {
            "objeto": horario,
            "cancelar_url": "actividades:horario_lista",
            "advertencia": (
                "Eliminar este horario también eliminará todas las "
                "inscripciones asociadas a él."
            ),
        },
    )

@login_required
@permission_required("actividades.view_horario", raise_exception=True)
def lista_horarios(request):
    dia = request.GET.get("dia", "").strip()
    profesor_id = request.GET.get("profesor", "").strip()
    turno = request.GET.get("turno", "").strip()
    horarios = (
        Horario.objects
        .select_related(
            "actividad",
            "profesor"
        )
        .prefetch_related("inscripciones")
        .all()
    )
# ---------------------------------------------------------
# FILTRAR POR DÍA
# ---------------------------------------------------------
    if dia:
        horarios = horarios.filter(
            dia=dia
        )
# ---------------------------------------------------------
# FILTRAR POR PROFESOR
# ---------------------------------------------------------
    if profesor_id:
        horarios = horarios.filter(
            profesor_id=profesor_id
        )
# ---------------------------------------------------------
# FILTRAR POR TURNO
# ---------------------------------------------------------
    if turno == "manana":

        horarios = horarios.filter(
            hora_inicio__lt="12:00"
        )
    elif turno == "tarde":
        horarios = horarios.filter(
            hora_inicio__gte="12:00"
        )
# ---------------------------------------------------------
# DÍAS DISPONIBLES
# ---------------------------------------------------------
    dias_con_horarios = set(
        Horario.objects
        .values_list("dia", flat=True)
        .distinct()
    )

    dias = [
        dia_nombre
        for dia_nombre, dia_label in DIAS_SEMANA
        if dia_nombre in dias_con_horarios
    ]
# ---------------------------------------------------------
# PROFESORES
# ---------------------------------------------------------
    profesores = (
        Profesor.objects
        .filter(horarios__isnull=False)
        .distinct()
        .order_by("apellido", "nombre")
    )
# ---------------------------------------------------------
# CONTADORES
# ---------------------------------------------------------
    horarios_totales = Horario.objects.count()
    horarios_manana = Horario.objects.filter(
        hora_inicio__lt="12:00"
    ).count()
    horarios_tarde = Horario.objects.filter(
        hora_inicio__gte="12:00"
    ).count()
    profesores_asignados = (
        Horario.objects
        .values("profesor")
        .distinct()
        .count()
    )
# ---------------------------------------------------------
# CANTIDAD DE RESULTADOS
# ---------------------------------------------------------
    cantidad_resultados = horarios.count()

# ---------------------------------------------------------
# PAGINACIÓN
# ---------------------------------------------------------
    paginator = Paginator(horarios, 10)
    pagina = request.GET.get("page")
    horarios_paginados = paginator.get_page(pagina)
# ---------------------------------------------------------
# CONTEXTO
# ---------------------------------------------------------
    contexto = {

        "horarios": horarios_paginados,

        # filtros
        "dia_seleccionado": dia,
        "profesor_seleccionado": profesor_id,
        "turno_seleccionado": turno,

        # opciones de filtros
        "dias": dias,
        "profesores": profesores,

        # contadores
        "horarios_totales": horarios_totales,
        "horarios_manana": horarios_manana,
        "horarios_tarde": horarios_tarde,
        "profesores_asignados": profesores_asignados,

        # resultados
        "cantidad_resultados": cantidad_resultados,
    }
# ---------------------------------------------------------
# SI VIENE DE AJAX
# ---------------------------------------------------------
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # El JavaScript extrae #horariosResults de esta respuesta completa.
        plantilla = "actividades/lista_horarios.html"
    else:
        plantilla = "actividades/lista_horarios.html"


    return render(
        request,
        plantilla,
        contexto
    )
# ---------------------------------------------------------------------
# Inscripcion (sin cambios en esta revisión)
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_inscripcion", raise_exception=True)
def lista_inscripciones(request):
    buscar = request.GET.get("buscar", "").strip()
    actividad = request.GET.get("actividad", "").strip()

    inscripciones = Inscripcion.objects.select_related(
        "socio", "horario", "horario__actividad"
    ).all()

    if buscar:
        inscripciones = inscripciones.filter(
            Q(socio__nombre__icontains=buscar)
            | Q(socio__apellido__icontains=buscar)
            | Q(socio__dni__icontains=buscar)
        )

    if actividad:
        inscripciones = inscripciones.filter(
            horario__actividad__nombre__icontains=actividad
        )

    paginator = Paginator(inscripciones, 10)
    pagina = request.GET.get("page")

    return render(
        request,
        "actividades/lista_inscripciones.html",
        {
            "inscripciones": paginator.get_page(pagina),
            "buscar": buscar,
            "actividad_seleccionada": actividad,
            "socios_autocomplete": list(
                Socio.objects.order_by("apellido", "nombre").values(
                    "nombre", "apellido", "dni"
                )
            ),
            "actividades_autocomplete": list(
                Actividad.objects.order_by("nombre")
                .values_list("nombre", flat=True)
                .distinct()
            ),
        },
    )


@login_required
@permission_required("actividades.add_inscripcion", raise_exception=True)
def crear_inscripcion(request):
    form = InscripcionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        inscripcion = form.save()
        messages.success(request, f'Inscripción registrada: {inscripcion}.')
        return redirect("actividades:inscripcion_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {
            "form": form,
            "titulo": "Nueva inscripción",
            "cancelar_url": "actividades:inscripcion_lista",
            "inscripcion_autocomplete": True,
            "socios_autocomplete": list(
                Socio.objects.order_by("apellido", "nombre").values(
                    "id", "nombre", "apellido", "dni"
                )
            ),
            "horarios_autocomplete": list(
                {
                    "id": horario.id,
                    "dia": horario.dia,
                    "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                    "hora_fin": horario.hora_fin.strftime("%H:%M"),
                    "actividad": horario.actividad.nombre,
                    "profesor": str(horario.profesor),
                }
                for horario in Horario.objects.select_related(
                    "actividad", "profesor"
                ).order_by("dia", "hora_inicio")
            ),
        },
    )


@login_required
@permission_required("actividades.change_inscripcion", raise_exception=True)
def editar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    form = InscripcionForm(request.POST or None, instance=inscripcion)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La inscripción fue actualizada correctamente.")
        return redirect("actividades:inscripcion_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Editar inscripción", "cancelar_url": "actividades:inscripcion_lista"},
    )


@login_required
@permission_required("actividades.delete_inscripcion", raise_exception=True)
def eliminar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            inscripcion,
            "actividades:inscripcion_lista",
            "no se pudo eliminar.",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {"objeto": inscripcion, "cancelar_url": "actividades:inscripcion_lista"},
    )


# ---------------------------------------------------------------------
# Asistencia
#
# Rediseño completo del módulo. Ya no existe un alta libre (elegir
# cualquier socio + cualquier horario + cualquier profesor + fecha/hora
# a mano). La única forma de generar asistencias es "tomar asistencia"
# sobre un horario puntual: se listan los socios ya inscriptos en ese
# horario y se marca presente/ausente. Editar y eliminar un registro
# puntual se mantienen para corregir errores de carga.
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_asistencia", raise_exception=True)
def lista_asistencias(request):
    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "").strip()
    asistencias = _filtrar_asistencias(buscar, estado)

    paginator = Paginator(asistencias, 15)
    pagina = request.GET.get("page")
    socios_autocomplete = list(
        Socio.objects.all()
        .order_by("apellido", "nombre")
        .values("nombre", "dni")
    )
    return render(
        request,
        "actividades/lista_asistencias.html",
        {
            "asistencias": paginator.get_page(pagina),
            "socios_autocomplete": socios_autocomplete,
            "buscar": buscar,
            "estado": estado,
        },
    )


def _filtrar_asistencias(buscar="", estado=""):
    asistencias = Asistencia.objects.select_related(
        "socio", "horario", "horario__actividad", "profesor"
    ).all()

    if buscar:
        asistencias = asistencias.filter(
            Q(socio__nombre__icontains=buscar) |
            Q(socio__apellido__icontains=buscar) |
            Q(socio__dni__icontains=buscar)
    )

    if estado == "presente":
        asistencias = asistencias.filter(presente=True)
    elif estado == "ausente":
        asistencias = asistencias.filter(presente=False)


    return asistencias.order_by("-fecha", "-hora")


@login_required
@permission_required("actividades.view_asistencia", raise_exception=True)
def exportar_asistencias_excel_view(request):
    asistencias = _filtrar_asistencias(
        request.GET.get("buscar", "").strip(),
        request.GET.get("estado", "").strip(),
    )
    return exportar_asistencias_excel(asistencias)


@login_required
@permission_required("actividades.view_asistencia", raise_exception=True)
def exportar_asistencias_pdf_view(request):
    asistencias = _filtrar_asistencias(
        request.GET.get("buscar", "").strip(),
        request.GET.get("estado", "").strip(),
    )
    return exportar_asistencias_pdf(asistencias)


@login_required
@permission_required("actividades.view_asistencia", raise_exception=True)
def detalle_asistencia(request, pk):
    asistencia = get_object_or_404(
        Asistencia.objects.select_related("socio", "horario", "horario__actividad", "profesor"),
        pk=pk,
    )

    return render(request, "actividades/detalle_asistencia.html", {"asistencia": asistencia})


@login_required
@permission_required("actividades.add_asistencia", raise_exception=True)
def tomar_asistencia(request, horario_id):
    """Reemplaza al alta libre de asistencias. Muestra la lista cerrada
    de socios inscriptos en `horario` y permite marcar presente/ausente
    para la fecha indicada (hoy por defecto). Todos parten marcados
    Presente; el profesor solo toca los que faltaron."""
    horario = get_object_or_404(
        Horario.objects.select_related("actividad", "profesor"), pk=horario_id
    )

    fecha_str = request.GET.get("fecha") or request.POST.get("fecha")
    try:
        fecha = datetime.date.fromisoformat(fecha_str) if fecha_str else datetime.date.today()
    except ValueError:
        fecha = datetime.date.today()

    inscripciones = horario.inscripciones.select_related("socio").order_by(
        "socio__apellido", "socio__nombre"
    )

    asistencias_existentes = {
        a.socio_id: a
        for a in Asistencia.objects.filter(horario=horario, fecha=fecha)
    }

    if request.method == "POST":
        ahora = datetime.datetime.now().time()

        for inscripcion in inscripciones:
            socio_id = inscripcion.socio_id
            # Cada socio llega marcado "presente" salvo que el profesor
            # haya tocado el botón "Ausente" (name=f"estado_{socio_id}",
            # value="ausente").
            presente = request.POST.get(f"estado_{socio_id}") != "ausente"

            Asistencia.objects.update_or_create(
                socio_id=socio_id,
                horario=horario,
                fecha=fecha,
                defaults={
                    "profesor": horario.profesor,
                    "hora": asistencias_existentes.get(socio_id).hora
                    if socio_id in asistencias_existentes
                    else ahora,
                    "presente": presente,
                },
            )

        messages.success(
            request,
            f"Asistencia de {inscripciones.count()} socios registrada para "
            f'"{horario}" el {fecha.strftime("%d/%m/%Y")}.',
        )
        return redirect("actividades:asistencia_lista")

    filas = [
        {
            "socio": inscripcion.socio,
            "presente": asistencias_existentes.get(inscripcion.socio_id).presente
            if inscripcion.socio_id in asistencias_existentes
            else True,
        }
        for inscripcion in inscripciones
    ]

    return render(
        request,
        "actividades/tomar_asistencia.html",
        {"horario": horario, "fecha": fecha, "filas": filas},
    )


@login_required
@permission_required("actividades.change_asistencia", raise_exception=True)
def editar_asistencia(request, pk):
    asistencia = get_object_or_404(
        Asistencia.objects.select_related("socio", "horario", "profesor"), pk=pk
    )
    form = AsistenciaForm(request.POST or None, instance=asistencia)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La asistencia fue actualizada correctamente.")
        return redirect("actividades:asistencia_lista")

    return render(
        request,
        "actividades/editar_asistencia.html",
        {"form": form, "asistencia": asistencia},
    )


@login_required
@permission_required("actividades.delete_asistencia", raise_exception=True)
def eliminar_asistencia(request, pk):
    asistencia = get_object_or_404(Asistencia, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            asistencia,
            "actividades:asistencia_lista",
            "no se pudo eliminar.",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {"objeto": asistencia, "cancelar_url": "actividades:asistencia_lista"},
    )

# NOTA DE SEGURIDAD: estas vistas no tenían NINGÚN control de autenticación
# ni de permisos, pese a estar enrutadas en /profesores/. Cualquier persona,
# sin necesidad de iniciar sesión, podía listar, crear, editar y eliminar
# profesores con solo conocer la URL. Se agregan los mixins/decoradores
# correspondientes, siguiendo el mismo patrón usado en el resto del
# proyecto (ver apps/socios/views.py).

# 1. LISTAR PROFESORES
class ProfesorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "actividades.view_profesor"
    model = Profesor
    template_name = 'profesores/profesor_list.html'
    context_object_name = 'profesores'

    def get_queryset(self):
        queryset = Profesor.objects.select_related('estado_profesor')

        # BUSCADOR
        buscar = self.request.GET.get('buscar', '').strip()

        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido__icontains=buscar) |
                Q(dni__icontains=buscar)
            )

        # FILTRO POR ESTADO
        estado = self.request.GET.get('estado', '').strip()

        if estado:
            queryset = queryset.filter(
                estado_profesor_id=estado
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # CONTADORES
        queryset_base = Profesor.objects.all()

        context['profesores_totales'] = queryset_base.count()

        context['profesores_activos'] = queryset_base.filter(
            estado_profesor__nombre__iexact='Activo'
        ).count()

        context['profesores_inactivos'] = queryset_base.exclude(
            estado_profesor__nombre__iexact='Activo'
        ).count()

        # VALORES ACTUALES DE LOS FILTROS
        context['buscar'] = self.request.GET.get('buscar', '')
        context['estado_seleccionado'] = self.request.GET.get('estado', '')

        # ESTADOS DEL DESPLEGABLE
        context['estados'] = EstadoProfesor.objects.all().order_by('nombre')

        context['profesores_autocomplete'] = list(
            Profesor.objects
            .order_by('apellido', 'nombre')
            .values('nombre', 'apellido', 'dni')
        )

        # CANTIDAD DE RESULTADOS
        context['cantidad_resultados'] = self.get_queryset().count()

        return context

# 2. CREAR PROFESOR
class ProfesorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "actividades.add_profesor"
    model = Profesor
    form_class = ProfesorForm
    template_name = 'profesores/profesor_form.html'
    success_url = reverse_lazy('actividades:profesor_list')

    @transaction.atomic
    def form_valid(self, form):
        profesor = form.save(commit=False)
        rol_profesor = Rol.objects.get(nombre='Profesor')
        estado_activo = EstadoUsuario.objects.get(nombre='Activo')
        usuario = Usuario.objects.create_user(
            username=profesor.dni,
            password=profesor.dni,
            first_name=profesor.nombre,
            last_name=profesor.apellido,
            email=profesor.email,
            rol=rol_profesor,
            estado_usuario=estado_activo,
            debe_cambiar_password=True,
        )
        profesor.usuario = usuario
        profesor.save()
        self.object = profesor
        return super().form_valid(form)

# 3. EDITAR PROFESOR
class ProfesorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "actividades.change_profesor"
    model = Profesor
    form_class = ProfesorForm
    template_name = 'profesores/profesor_form.html'
    success_url = reverse_lazy('actividades:profesor_list')

# 4. ELIMINAR PROFESOR
class ProfesorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "actividades.delete_profesor"
    model = Profesor
    template_name = 'profesores/profesor_confirm_delete.html'
    success_url = reverse_lazy('actividades:profesor_list')

# 5. DETALLE PROFESOR
class ProfesorDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "actividades.view_profesor"
    model = Profesor
    template_name = 'profesores/profesor_detalle.html'
    context_object_name = 'profesor'

# 6. CAMBIAR ESTADO PROFESOR (ACCIÓN RÁPIDA DE ALTA/BAJA)
# Antes era un GET sin login ni permisos: cualquiera podía activar/
# desactivar profesores con solo visitar la URL, y al ser GET quedaba
# expuesto a CSRF y a que un navegador/proxy la precargue por accidente.
# Se exige POST + login + permiso.
@login_required
@permission_required("actividades.change_profesor", raise_exception=True)
@require_POST
def cambiar_estado_profesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    
    # Alterna dinámicamente entre Activo e Inactivo
    if profesor.estado_profesor and profesor.estado_profesor.nombre.lower() == 'activo':
        nuevo_estado = EstadoProfesor.objects.get(nombre__iexact='Inactivo')
    else:
        nuevo_estado = EstadoProfesor.objects.get(nombre__iexact='Activo')
        
    profesor.estado_profesor = nuevo_estado
    profesor.save()
    
    # Redirige nuevamente a la misma pantalla de edición para ver el cambio
    return redirect('actividades:profesor_list')