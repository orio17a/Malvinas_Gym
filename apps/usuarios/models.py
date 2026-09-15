from django.contrib.auth.models import AbstractUser
from django.db import models


class EstadoUsuario(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de usuario"
        verbose_name_plural = "Estados de usuario"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    estado_usuario = models.ForeignKey(
        EstadoUsuario,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
    )
    rol = models.ForeignKey(
        Rol, on_delete=models.PROTECT, related_name="usuarios", null=True, blank=True
    )
    telefono = models.CharField(max_length=20, blank=True)
    telefono_2 = models.CharField(max_length=20, blank=True)
    domicilio = models.CharField(max_length=150, blank=True)
    debe_cambiar_password = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username
    
