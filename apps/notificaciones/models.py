from django.db import models

from apps.socios.models import Socio


class TipoNotificacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Tipo de notificación"
        verbose_name_plural = "Tipos de notificación"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class EstadoNotificacion(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de notificación"
        verbose_name_plural = "Estados de notificación"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Canal(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Canal"
        verbose_name_plural = "Canales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    socio = models.ForeignKey(
        Socio, on_delete=models.CASCADE, related_name="notificaciones"
    )
    estado_notificacion = models.ForeignKey(
        EstadoNotificacion, on_delete=models.PROTECT, related_name="notificaciones"
    )
    tipo_notificacion = models.ForeignKey(
        TipoNotificacion, on_delete=models.PROTECT, related_name="notificaciones"
    )
    canal = models.ForeignKey(
        Canal, on_delete=models.PROTECT, related_name="notificaciones"
    )
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"{self.socio} - {self.tipo_notificacion}"
