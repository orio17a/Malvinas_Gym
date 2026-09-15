from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

def validar_tamano_apto(archivo):
    limite = 5 * 1024 * 1024  # 5 MB

    if archivo.size > limite:
        raise ValidationError(
            "El archivo del apto físico no puede superar los 5 MB."
        )

class EstadoSocio(models.Model):
    nombre = models.CharField(
        max_length=30,
        unique=True
    )

    descripcion = models.CharField(
        max_length=150,
        blank=True
    )

    def __str__(self):
        return self.nombre

class EstadoAptoFisico(models.Model):
    nombre = models.CharField(
        max_length=30,
        unique=True
    )

    descripcion = models.CharField(
        max_length=150,
        blank=True
    )

    def __str__(self):
        return self.nombre

class Socio(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="socio"
    )

    estado_socio = models.ForeignKey(
        EstadoSocio,
        on_delete=models.PROTECT,
        related_name="socios"
    )

    nombre = models.CharField(
        max_length=50
    )

    apellido = models.CharField(
        max_length=50
    )

    dni = models.CharField(
        max_length=15,
        unique=True
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )

    email = models.EmailField(
        max_length=100,
        blank=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    domicilio = models.CharField(
        max_length=150,
        blank=True
    )

    nombre_contacto_emergencia = models.CharField(
        max_length=100,
        blank=True
    )

    telefono_emergencia = models.CharField(
        max_length=20,
        blank=True
    )

    relacion_contacto_emergencia = models.CharField(
        max_length=50,
        blank=True
    )

    apto_fisico = models.FileField(
        upload_to="aptos_fisicos/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "jpg",
                    "jpeg",
                    "png"
                ]
            ),
            validar_tamano_apto
        ],
        null=True,
        blank=True
    )

    estado_apto_fisico = models.ForeignKey(
        EstadoAptoFisico,
        on_delete=models.PROTECT,
        related_name="socios"
    )

    fecha_presentacion_apto = models.DateField(
        null=True,
        blank=True
    )

    fecha_ingreso = models.DateField()

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None

        hoy = date.today()

        return (
            hoy.year
            - self.fecha_nacimiento.year
            - (
                (hoy.month, hoy.day)
                < (
                    self.fecha_nacimiento.month,
                    self.fecha_nacimiento.day
                )
            )
        )


    @property
    def es_menor(self):
        if self.edad is None:
            return False

        return self.edad < 15

    @property
    def requiere_responsable(self):
        edad = self.edad
        return edad is not None and edad < 15

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Responsable(models.Model):
    nombre = models.CharField(
        max_length=50
    )

    apellido = models.CharField(
        max_length=50
    )

    dni = models.CharField(
        max_length=15,
        unique=True
    )

    telefono = models.CharField(
        max_length=20
    )

    email = models.EmailField(
        max_length=100,
        blank=True
    )

    domicilio = models.CharField(
        max_length=150,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class SocioResponsable(models.Model):
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name="responsables"
    )

    responsable = models.ForeignKey(
        Responsable,
        on_delete=models.CASCADE,
        related_name="socios"
    )

    parentesco = models.CharField(
        max_length=30
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["socio", "responsable"],
                name="unique_socio_responsable"
            )
        ]

    def __str__(self):
        return f"{self.socio} - {self.responsable}"
