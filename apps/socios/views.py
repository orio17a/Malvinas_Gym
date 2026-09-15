from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.utils import timezone
from apps.cuotas.models import Cuota


from .forms import SocioForm, ResponsableForm
from .models import EstadoSocio, Socio
from .services import crear_socio_con_usuario

def formatear_telefono(valor):
    """Prepara el teléfono para mostrarlo sin modificar el valor guardado."""
    if not valor or not valor.strip():
        return "-"

    digitos = "".join(caracter for caracter in valor if caracter.isdigit())
    if len(digitos) == 10:
        return f"{digitos[:2]} {digitos[2:6]}-{digitos[6:]}"

    return valor


@login_required
@permission_required("socios.view_socio", raise_exception=True)
def lista_socios(request):
    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "").strip()

    # Estados cargados desde la base de datos
    estados_disponibles = EstadoSocio.objects.all().order_by("nombre")

    # Validar que el estado recibido exista realmente
    if estado:
        existe_estado = EstadoSocio.objects.filter(
            nombre__iexact=estado
        ).exists()

        if not existe_estado:
            estado = ""

    socios = (
        Socio.objects
        .select_related("estado_socio", "estado_apto_fisico")
        .all()
        .order_by("apellido", "nombre")
    )

    # ---------------------------
    # Estadísticas generales
    # ---------------------------

    total_socios = Socio.objects.count()

    socios_activos = Socio.objects.filter( estado_socio__nombre__iexact="Activo").count()

    socios_inactivos = Socio.objects.filter(estado_socio__nombre__iexact="Inactivo").count()

    aptos_pendientes = Socio.objects.filter(
        estado_apto_fisico__nombre__iexact="Pendiente"
    ).count()

    # ---------------------------
    # Búsqueda
    # ---------------------------

    if buscar:

        socios = socios.filter(
            Q(dni__icontains=buscar)
            | Q(nombre__icontains=buscar)
            | Q(apellido__icontains=buscar)
        )

    if estado:
        socios = socios.filter(estado_socio__nombre__iexact=estado)

    opciones_situacion = [
        ("con_deuda", "Con deuda"),
        ("apto_pendiente", "Apto físico pendiente"),
        ("apto_vencido", "Apto físico vencido"),


    ]
    situaciones = [clave for clave, _ in opciones_situacion if clave in request.GET.getlist("situacion")]
    if situaciones:
        socios = socios.alias(
            tiene_deuda=Exists(Cuota.objects.filter(
                membresia__socio_id=OuterRef("pk"), fecha_pago__isnull=True,
                fecha_vencimiento__lt=timezone.localdate(), monto__gt=0,
            )),

        )
        condiciones = {
            "con_deuda": Q(tiene_deuda=True),
            "apto_pendiente": Q(estado_apto_fisico__nombre__iexact="Pendiente"),
            "apto_vencido": Q(estado_apto_fisico__nombre__iexact="Vencido"),


        }
        filtro = Q()
        for situacion in situaciones:
            filtro |= condiciones[situacion]
        socios = socios.filter(filtro)
    ordenes_permitidos = {
        "nombre": ("apellido", "nombre"),
        "estado": ("estado_socio__nombre", "apellido", "nombre"),
        "fecha_ingreso": ("fecha_ingreso", "apellido", "nombre"),
    }
    orden = request.GET.get("orden", "")
    if orden not in ordenes_permitidos:
        orden = ""
    direccion = "desc" if request.GET.get("direccion") == "desc" else "asc"
    if orden:
        prefijo = "-" if direccion == "desc" else ""
        socios = socios.order_by(
            *(prefijo + campo for campo in ordenes_permitidos[orden]), "pk"
        )

    parametros = {"situacion": situaciones}
    if buscar:
        parametros["buscar"] = buscar
    if estado:
        parametros["estado"] = estado
    enlaces_orden = {}
    for clave in ordenes_permitidos:
        siguiente = "desc" if orden == clave and direccion == "asc" else "asc"
        enlaces_orden[clave] = urlencode(
            {**parametros, "orden": clave, "direccion": siguiente}, doseq=True
        )
    if orden:
        parametros.update(orden=orden, direccion=direccion)

    if request.GET.get("exportar") == "excel":
        from .exports import exportar_socios
        return exportar_socios(socios)

    cantidad_resultados = socios.count()

    # ---------------------------
    # Paginación
    # ---------------------------

    paginator = Paginator(
        socios,
        10
    )

    numero_pagina = request.GET.get("page")

    socios_paginados = paginator.get_page(
        numero_pagina
    )

    for socio in socios_paginados:
        socio.telefono_formateado = formatear_telefono(socio.telefono)

    contexto = {
        "socios": socios_paginados,

        "buscar": buscar,
        "estado": estado,
        "orden": orden,
        "estados_disponibles": estados_disponibles,
        "opciones_situacion": opciones_situacion,
        "situaciones": situaciones,

        "direccion": direccion,
        "enlaces_orden": enlaces_orden,
        "parametros_paginacion": urlencode(parametros, doseq=True),

        "cantidad_resultados": cantidad_resultados,

        "total_socios": total_socios,
        "socios_activos": socios_activos,
        "socios_inactivos": socios_inactivos,
        "aptos_pendientes": aptos_pendientes,
    }

    return render(
        request,
        "socios/_resultados_socios.html" if request.headers.get("X-Requested-With") == "XMLHttpRequest" else "socios/lista_socios.html",
        contexto
    )


@login_required
@permission_required("socios.add_socio", raise_exception=True)
def crear_socio(request):
    if request.method == "POST":
        form = SocioForm(
            request.POST,
            request.FILES
        )
        responsable_form = ResponsableForm(request.POST, prefix="responsable")

        if form.is_valid():
            try:
                socio = crear_socio_con_usuario(
                    **form.cleaned_data
                )

                messages.success(
                    request,
                    (
                        f"El socio {socio} fue registrado correctamente. "
                        f"Se creó automáticamente su usuario con DNI "
                        f"{socio.dni}."
                    )
                )

                return redirect("socios:lista")

            except ValueError as error:
                form.add_error(
                    None,
                    str(error)
                )

    else:
        form = SocioForm()
        responsable_form = ResponsableForm(prefix="responsable")

    return render(
        request,
        "socios/form_socio.html",
        {
            "form": form,
            "responsable_form": responsable_form,
            "titulo": "Nuevo socio"
        }
    )

@login_required
@permission_required("socios.view_socio", raise_exception=True)
def detalle_socio(request, pk):
    socio = get_object_or_404(
        Socio.objects.select_related(
            "estado_socio",
            "usuario__rol",
            "estado_apto_fisico",
            "usuario__estado_usuario",
        ),
        pk=pk
    )

    membresia_actual = (
        socio.membresias
        .select_related("plan", "estado_membresia")
        .filter(
            Q(estado_membresia__nombre__iexact="Activa")
            | Q(estado_membresia__nombre__iexact="Suspendida")
        )
        .order_by("-fecha_inicio", "-pk")
        .first()
    )

    return render(
        request,
        "socios/detalle_socio.html",
        {
            "membresia_actual": membresia_actual,
            "socio": socio,
            "telefono_formateado": formatear_telefono(socio.telefono),
            "telefono_emergencia_formateado": formatear_telefono(
                socio.telefono_emergencia
            ),
        }
    )


@login_required
@permission_required("socios.change_socio", raise_exception=True)
@require_POST
def dar_baja_socio(request, pk):

    with transaction.atomic():

        socio = get_object_or_404(
            Socio.objects
            .select_for_update()
            .select_related("estado_socio"),
            pk=pk,
        )

        estado_actual = socio.estado_socio.nombre.lower()

        if estado_actual not in ("activo", "suspendido"):
            messages.warning(
                request,
                "Solo se pueden dar de baja socios activos o suspendidos."
            )
            return redirect("socios:detalle", pk=pk)

        estado_inactivo = get_object_or_404(
            EstadoSocio,
            nombre__iexact="Inactivo",
        )

        socio.estado_socio = estado_inactivo
        socio.save(update_fields=["estado_socio"])

        if socio.usuario is not None:
            socio.usuario.is_active = False
            socio.usuario.save(update_fields=["is_active"])

    messages.success(
        request,
        f"El socio {socio.nombre} {socio.apellido} fue dado de baja correctamente.",
    )

    return redirect("socios:detalle", pk=socio.pk)

@login_required
@permission_required("socios.change_socio", raise_exception=True)
@require_POST
def reactivar_socio(request, pk):

    with transaction.atomic():

        socio = get_object_or_404(
            Socio.objects
            .select_for_update()
            .select_related("estado_socio"),
            pk=pk,
        )

        if socio.estado_socio.nombre.lower() != "inactivo":
            messages.warning(
                request,
                "Solo se pueden reactivar socios inactivos."
            )
            return redirect("socios:detalle", pk=pk)

        estado_activo = get_object_or_404(
            EstadoSocio,
            nombre__iexact="Activo"
        )

        socio.estado_socio = estado_activo
        socio.save(update_fields=["estado_socio"])

        if socio.usuario is not None:
            socio.usuario.is_active = True
            socio.usuario.save(update_fields=["is_active"])

    messages.success(
        request,
        "Socio reactivado correctamente."
    )

    return redirect("socios:detalle", pk=pk)

@login_required
@permission_required("socios.change_socio", raise_exception=True)
@require_POST
def activar_socio(request, pk):

    with transaction.atomic():

        socio = get_object_or_404(
            Socio.objects
            .select_for_update()
            .select_related("estado_socio"),
            pk=pk,
        )

        if socio.estado_socio.nombre.lower() != "pendiente":
            messages.warning(
                request,
                "Solo se pueden activar socios pendientes."
            )
            return redirect("socios:detalle", pk=pk)

        estado_activo = get_object_or_404(
            EstadoSocio,
            nombre__iexact="Activo"
        )

        socio.estado_socio = estado_activo
        socio.save(update_fields=["estado_socio"])

        if socio.usuario is not None:
            socio.usuario.is_active = True
            socio.usuario.save(update_fields=["is_active"])

    messages.success(
        request,
        "Socio activado correctamente."
    )

    return redirect("socios:detalle", pk=pk)

@login_required
@permission_required("socios.change_socio", raise_exception=True)
@require_POST
def suspender_socio(request, pk):

    with transaction.atomic():

        socio = get_object_or_404(
            Socio.objects
            .select_for_update()
            .select_related("estado_socio"),
            pk=pk,
        )

        if socio.estado_socio.nombre.lower() != "activo":
            messages.warning(
                request,
                "Solo se pueden suspender socios activos."
            )
            return redirect("socios:detalle", pk=pk)

        estado_suspendido = get_object_or_404(
            EstadoSocio,
            nombre__iexact="Suspendido"
        )

        socio.estado_socio = estado_suspendido
        socio.save(update_fields=["estado_socio"])

        if socio.usuario is not None:
            socio.usuario.is_active = False
            socio.usuario.save(update_fields=["is_active"])

    messages.success(
        request,
        f"El socio {socio.nombre} {socio.apellido} fue suspendido."
    )

    return redirect("socios:detalle", pk=pk)

@login_required
@permission_required("socios.change_socio", raise_exception=True)
@require_POST
def reanudar_socio(request, pk):

    with transaction.atomic():

        socio = get_object_or_404(
            Socio.objects
            .select_for_update()
            .select_related("estado_socio"),
            pk=pk,
        )

        if socio.estado_socio.nombre.lower() != "suspendido":
            messages.warning(
                request,
                "Solo se pueden reanudar socios suspendidos."
            )
            return redirect("socios:detalle", pk=pk)

        estado_activo = get_object_or_404(
            EstadoSocio,
            nombre__iexact="Activo"
        )

        socio.estado_socio = estado_activo
        socio.save(update_fields=["estado_socio"])

        if socio.usuario is not None:
            socio.usuario.is_active = True
            socio.usuario.save(update_fields=["is_active"])

    messages.success(
        request,
        "Socio reanudado correctamente."
    )

    return redirect("socios:detalle", pk=pk)

@login_required
@permission_required("socios.change_socio", raise_exception=True)
def editar_socio(request, pk):
    siguiente = request.POST.get("next", request.GET.get("next", "detalle"))
    if siguiente not in ("listado", "detalle"):
        siguiente = "detalle"

    socio = get_object_or_404(
        Socio,
        pk=pk
    )

    if request.method == "POST":
        form = SocioForm(
            request.POST,
            request.FILES,
            instance=socio
        )

        if form.is_valid():

            if socio.usuario:
                usuario = socio.usuario

                usuario.first_name = socio.nombre
                usuario.last_name = socio.apellido
                usuario.email = socio.email

                usuario.save(
                    update_fields=[
                        "first_name",
                        "last_name",
                        "email",
                    ]
                )
                
            socio = form.save()

            messages.success(
                request,
                f"Los datos de {socio} fueron actualizados correctamente."
            )

            return redirect(
                "socios:detalle",
                pk=socio.pk
            )

    else:
        form = SocioForm(
            instance=socio
        )

    return render(
        request,
        "socios/form_socio.html",
        {
            "form": form,
            "titulo": "Editar socio",
            "socio": socio,
            "es_edicion": True,
            "next": siguiente,
        }
    )


@login_required
@permission_required("socios.delete_socio", raise_exception=True)
@require_POST
def eliminar_socio(request, pk):
    try:
        with transaction.atomic():
            socio = get_object_or_404(Socio.objects.select_for_update(), pk=pk)
            if socio.estado_socio.nombre.lower() != "inactivo":
                messages.error(
                    request, "Solo se pueden eliminar definitivamente socios inactivos."
                )
                return redirect("socios:detalle", pk=pk)

            # La cuenta de Usuario se conserva; no es una relación en cascada saliente.
            socio.delete()
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar definitivamente este socio porque posee información histórica asociada.",
        )
        return redirect("socios:detalle", pk=pk)

    messages.success(request, "El socio fue eliminado definitivamente.")
    return redirect("socios:lista")
