from datetime import timedelta

from django.db import models

from apps.socios.models import Socio


class TipoPlan(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Tipo de plan"
        verbose_name_plural = "Tipos de plan"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class EstadoPlan(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de plan"
        verbose_name_plural = "Estados de plan"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Plan(models.Model):
    tipo_plan = models.ForeignKey(
        TipoPlan, on_delete=models.PROTECT, related_name="planes"
    )
    estado_plan = models.ForeignKey(
        EstadoPlan, on_delete=models.PROTECT, related_name="planes"
    )
    nombre = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    vigencia_dias = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class EstadoMembresia(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de membresía"
        verbose_name_plural = "Estados de membresía"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Membresia(models.Model):
    socio = models.ForeignKey(
        Socio, on_delete=models.PROTECT, related_name="membresias"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="membresias")
    estado_membresia = models.ForeignKey(
        EstadoMembresia, on_delete=models.PROTECT, related_name="membresias"
    )
    fecha_inicio = models.DateField()
    # Se calcula siempre a partir de fecha_inicio + plan.vigencia_dias en
    # save(), por eso es editable=False: no debe cargarse a mano ni
    # quedar desincronizada del plan vigente.
    fecha_vencimiento = models.DateField(editable=False)

    class Meta:
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        ordering = ["-fecha_inicio"]

    def save(self, *args, **kwargs):
        if self.fecha_inicio and self.plan_id:
            self.fecha_vencimiento = self.fecha_inicio + timedelta(
                days=self.plan.vigencia_dias
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.socio} - {self.plan}"
