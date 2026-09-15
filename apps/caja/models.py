from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EstadoCaja(models.Model):
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de caja"
        verbose_name_plural = "Estados de caja"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class TipoMovimiento(models.Model):
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Tipo de movimiento"
        verbose_name_plural = "Tipos de movimiento"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ConceptoMovimiento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Concepto de movimiento"
        verbose_name_plural = "Conceptos de movimiento"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class MedioPago(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Medio de pago"
        verbose_name_plural = "Medios de pago"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class CategoriaGasto(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría de gasto"
        verbose_name_plural = "Categorías de gasto"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Caja(models.Model):
    estado_caja = models.ForeignKey(
        EstadoCaja, on_delete=models.PROTECT, related_name="cajas"
    )
    fecha_apertura = models.DateField()
    hora_apertura = models.TimeField()
    fecha_cierre = models.DateField(null=True, blank=True)
    hora_cierre = models.TimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_final = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "Caja"
        verbose_name_plural = "Cajas"
        ordering = ["-fecha_apertura", "-hora_apertura"]

    def clean(self):
        if self.fecha_cierre and self.fecha_apertura and self.fecha_cierre < self.fecha_apertura:
            raise ValidationError(
                {"fecha_cierre": "La fecha de cierre no puede ser anterior a la de apertura."}
            )

    def __str__(self):
        return f"Caja #{self.id} - {self.fecha_apertura}"


class Gasto(models.Model):
    categoria_gasto = models.ForeignKey(
        CategoriaGasto, on_delete=models.PROTECT, related_name="gastos"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="gastos_registrados",
    )
    detalle = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    hora = models.TimeField()

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ["-fecha", "-hora"]

    def __str__(self):
        return f"{self.detalle} - ${self.monto}"


class Movimiento(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name="movimientos")
    tipo_movimiento = models.ForeignKey(
        TipoMovimiento, on_delete=models.PROTECT, related_name="movimientos"
    )
    concepto_movimiento = models.ForeignKey(
        ConceptoMovimiento,
        on_delete=models.PROTECT,
        related_name="movimientos",
        null=True,
        blank=True,
    )
    medio_pago = models.ForeignKey(
        MedioPago, on_delete=models.PROTECT, related_name="movimientos"
    )
    cuota = models.ForeignKey(
        "cuotas.Cuota",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos",
    )
    gasto = models.OneToOneField(
        Gasto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimiento",
    )
    detalle = models.CharField(max_length=200, blank=True)
    fecha = models.DateField()
    hora = models.TimeField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        ordering = ["-fecha", "-hora"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(cuota__isnull=False, gasto__isnull=True)
                    | models.Q(cuota__isnull=True, gasto__isnull=False)
                    | models.Q(cuota__isnull=True, gasto__isnull=True)
                ),
                name="movimiento_cuota_xor_gasto",
            )
        ]

    def clean(self):
        if self.cuota_id and self.gasto_id:
            raise ValidationError(
                "Un movimiento no puede estar asociado a una cuota y a un gasto a la vez."
            )

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.concepto_movimiento} - ${self.monto}"
