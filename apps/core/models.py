from django.db import models


class ConfiguracionGimnasio(models.Model):
    """Datos de contacto y presentación del gimnasio, editables desde el
    admin sin tocar código (antes estaban hardcodeados en la vista)."""

    nombre = models.CharField(max_length=100)
    barrio = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=30)
    email = models.EmailField()
    instagram = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Configuración del gimnasio"
        verbose_name_plural = "Configuración del gimnasio"

    def __str__(self):
        return self.nombre
