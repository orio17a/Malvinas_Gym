from django.contrib import admin

from .models import (
    Caja,
    CategoriaGasto,
    ConceptoMovimiento,
    EstadoCaja,
    Gasto,
    MedioPago,
    Movimiento,
    TipoMovimiento,
)


@admin.register(EstadoCaja, TipoMovimiento, ConceptoMovimiento, MedioPago, CategoriaGasto)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "estado_caja",
        "fecha_apertura",
        "fecha_cierre",
        "saldo_inicial",
        "saldo_final",
    )
    list_filter = ("estado_caja",)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ("detalle", "categoria_gasto", "monto", "fecha", "usuario")
    list_filter = ("categoria_gasto", "fecha")
    search_fields = ("detalle",)


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = (
        "tipo_movimiento",
        "concepto_movimiento",
        "medio_pago",
        "monto",
        "fecha",
        "caja",
    )
    list_filter = ("tipo_movimiento", "medio_pago", "fecha")
