from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario, Rol, EstadoUsuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Datos adicionales",
            {
                "fields": (
                    "estado_usuario",
                    "rol",
                    "telefono",
                    "telefono_2",
                    "domicilio",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Datos adicionales",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "estado_usuario",
                    "rol",
                    "telefono",
                    "telefono_2",
                    "domicilio",
                )
            },
        ),
    )

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "rol",
        "estado_usuario",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "rol",
        "estado_usuario",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "descripcion",
    )

    search_fields = ("nombre",)


@admin.register(EstadoUsuario)
class EstadoUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "descripcion",
    )

    search_fields = ("nombre",)