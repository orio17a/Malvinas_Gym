from django.contrib import admin

from .models import Canal, EstadoNotificacion, Notificacion, TipoNotificacion


@admin.register(TipoNotificacion, EstadoNotificacion, Canal)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("socio", "tipo_notificacion", "canal", "estado_notificacion", "fecha_envio")
    list_filter = ("estado_notificacion", "tipo_notificacion", "canal")
    search_fields = ("socio__nombre", "socio__apellido")
