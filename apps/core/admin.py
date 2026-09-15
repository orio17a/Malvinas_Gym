from django.contrib import admin

from .models import ConfiguracionGimnasio


@admin.register(ConfiguracionGimnasio)
class ConfiguracionGimnasioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "barrio", "telefono", "email")
