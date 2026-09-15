from django.contrib import admin
from django.db import transaction

from apps.usuarios.models import Usuario, Rol, EstadoUsuario

from .models import (
    EstadoSocio,
    EstadoAptoFisico,
    Socio,
    Responsable,
    SocioResponsable,
)


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):

    # No mostramos usuario al crear/editar,
    # porque se administra automáticamente.
    exclude = ("usuario",)

    list_display = (
        "apellido",
        "nombre",
        "dni",
        "estado_socio",
        "estado_apto_fisico",
    )

    search_fields = (
        "dni",
        "nombre",
        "apellido",
    )

    list_filter = (
        "estado_socio",
        "estado_apto_fisico",
    )

    @transaction.atomic
    def save_model(self, request, obj, form, change):

        # Solo crear el usuario cuando se está creando
        # un socio nuevo.
        if not change and obj.usuario is None:

            dni = obj.dni

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
                first_name=obj.nombre,
                last_name=obj.apellido,
                email=obj.email,
                rol=rol_socio,
                estado_usuario=estado_activo,
                debe_cambiar_password=True,
            )

            obj.usuario = usuario

        super().save_model(
            request,
            obj,
            form,
            change
        )


@admin.register(EstadoSocio)
class EstadoSocioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "descripcion",
    )

@admin.register(EstadoAptoFisico)
class EstadoAptoFisicoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "descripcion",
    )

admin.site.register(Responsable)
admin.site.register(SocioResponsable)