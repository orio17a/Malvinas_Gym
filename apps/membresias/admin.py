from django.contrib import admin

from .models import EstadoMembresia, EstadoPlan, Membresia, Plan, TipoPlan


@admin.register(TipoPlan, EstadoPlan, EstadoMembresia)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo_plan", "precio", "vigencia_dias", "estado_plan")
    list_filter = ("tipo_plan", "estado_plan")
    search_fields = ("nombre",)


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = (
        "socio",
        "plan",
        "fecha_inicio",
        "fecha_vencimiento",
        "estado_membresia",
    )
    list_filter = ("estado_membresia", "plan")
    search_fields = ("socio__nombre", "socio__apellido")
