from django.db import transaction

from apps.socios.models import EstadoSocio, Socio
from apps.usuarios.models import Usuario, Rol, EstadoUsuario


@transaction.atomic
def crear_socio_con_usuario(**datos_socio):
    try:
        estado_inicial = EstadoSocio.objects.get(nombre__iexact="Activo")
    except (EstadoSocio.DoesNotExist, EstadoSocio.MultipleObjectsReturned) as error:
        raise ValueError(
            "No se puede registrar el socio: debe existir un único EstadoSocio llamado Activo."
        ) from error

    # El alta define el estado; nunca se toma de datos enviados por el formulario.
    datos_socio.pop("estado_socio_id", None)
    datos_socio["estado_socio"] = estado_inicial
    dni = datos_socio["dni"]

    if Usuario.objects.filter(username=dni).exists():
        raise ValueError(
            f"Ya existe un usuario con el DNI {dni}."
        )

    rol_socio = Rol.objects.get(
        nombre="Socio"
    )

    estado_activo = EstadoUsuario.objects.get(
        nombre="Activo"
    )

    usuario = Usuario.objects.create_user(
        username=dni,
        password=dni,
        first_name=datos_socio["nombre"],
        last_name=datos_socio["apellido"],
        email=datos_socio.get("email", ""),
        rol=rol_socio,
        estado_usuario=estado_activo,
        debe_cambiar_password=True
    )

    socio = Socio.objects.create(
        usuario=usuario,
        **datos_socio
    )

    return socio
