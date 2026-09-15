from django.core.exceptions import ValidationError
from django.db import models

from apps.membresias.models import Membresia


class EstadoCuota(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de cuota"
        verbose_name_plural = "Estados de cuota"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Cuota(models.Model):
    membresia = models.ForeignKey(
        Membresia, on_delete=models.PROTECT, related_name="cuotas"
    )
    estado_cuota = models.ForeignKey(
        EstadoCuota, on_delete=models.PROTECT, related_name="cuotas"
    )
    periodo = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ["-periodo"]
        constraints = [
            models.UniqueConstraint(
                fields=["membresia", "periodo"], name="unique_cuota_membresia_periodo"
            )
        ]

    def clean(self):
        if self.fecha_vencimiento and self.periodo and self.fecha_vencimiento < self.periodo:
            raise ValidationError(
                {"fecha_vencimiento": "El vencimiento no puede ser anterior al período facturado."}
            )

    def __str__(self):
        return f"{self.membresia} - {self.periodo}"
