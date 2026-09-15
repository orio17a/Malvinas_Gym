from django.contrib import admin
from django.db import transaction

from apps.usuarios.models import EstadoUsuario, Rol, Usuario
from .models import (
    Actividad,
    Asistencia,
    EstadoActividad,
    EstadoProfesor,
    Horario,
    Inscripcion,
    Profesor,
)


@admin.register(EstadoProfesor, EstadoActividad)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    exclude = ('usuario',)
    list_display = ("nombre", "apellido", "dni", "telefono", "estado_profesor")
    list_filter = ("estado_profesor",)
    search_fields = ("nombre", "apellido", "dni")

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if not change and obj.usuario is None:
            rol_profesor = Rol.objects.get(nombre='Profesor')
            estado_activo = EstadoUsuario.objects.get(nombre='Activo')
            obj.usuario = Usuario.objects.create_user(
                username=obj.dni,
                password=obj.dni,
                first_name=obj.nombre,
                last_name=obj.apellido,
                email=obj.email,
                rol=rol_profesor,
                estado_usuario=estado_activo,
                debe_cambiar_password=True,
            )

        super().save_model(request, obj, form, change)


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado_actividad", "fecha_creacion")
    list_filter = ("estado_actividad",)
    search_fields = ("nombre",)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("actividad", "profesor", "dia", "hora_inicio", "hora_fin", "cupo")
    list_filter = ("dia", "actividad")
    search_fields = ("actividad__nombre", "profesor__apellido")


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("socio", "horario", "fecha_inscripcion")
    search_fields = ("socio__nombre", "socio__apellido")


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("socio", "horario", "profesor", "fecha", "hora")
    list_filter = ("fecha",)
    search_fields = ("socio__nombre", "socio__apellido")
