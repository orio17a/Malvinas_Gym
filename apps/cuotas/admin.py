from django.contrib import admin

from .models import Cuota, EstadoCuota


@admin.register(EstadoCuota)
class EstadoCuotaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = (
        "membresia",
        "periodo",
        "monto",
        "fecha_vencimiento",
        "fecha_pago",
        "estado_cuota",
    )
    list_filter = ("estado_cuota", "periodo")
    search_fields = ("membresia__socio__nombre", "membresia__socio__apellido")
