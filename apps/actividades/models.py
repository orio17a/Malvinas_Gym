from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.socios.models import Socio

# Estados fijos del sistema. No son editables desde la interfaz (ver
# apps.actividades.views): antes existía una pantalla para que el
# administrador diera de alta estados propios, lo que permitía cargar
# valores arbitrarios o mal escritos. Ahora EstadoActividad y
# EstadoProfesor siguen siendo tablas (para no romper las FK ni perder
# la posibilidad de agregar un estado nuevo por migración el día de
# mañana), pero se siembran una única vez con estos tres valores y no
# se exponen para editar.
NOMBRES_ESTADOS_PREDEFINIDOS = ["Activo", "Inactivo", "Suspendido"]

DIAS_SEMANA = [
    ("Lunes", "Lunes"),
    ("Martes", "Martes"),
    ("Miércoles", "Miércoles"),
    ("Jueves", "Jueves"),
    ("Viernes", "Viernes"),
    ("Sábado", "Sábado"),
    ("Domingo", "Domingo"),
]


class EstadoProfesor(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de profesor"
        verbose_name_plural = "Estados de profesor"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Profesor(models.Model):
    estado_profesor = models.ForeignKey(
        EstadoProfesor, on_delete=models.PROTECT, related_name="profesores"
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profesor",
    )
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=15, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20)
    telefono_2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    domicilio = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class EstadoActividad(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Estado de actividad"
        verbose_name_plural = "Estados de actividad"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Actividad(models.Model):
    estado_actividad = models.ForeignKey(
        EstadoActividad, on_delete=models.PROTECT, related_name="actividades"
    )
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Horario(models.Model):
    actividad = models.ForeignKey(
        Actividad, on_delete=models.PROTECT, related_name="horarios"
    )
    profesor = models.ForeignKey(
        Profesor, on_delete=models.PROTECT, related_name="horarios"
    )
    # Antes era texto libre: se podía escribir "miercoles", "Miercoles ",
    # etc., y el sistema no reconocía esas variantes como el mismo día.
    # Con choices, el valor siempre es uno de los 7 días válidos.
    dia = models.CharField(max_length=15, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    cupo = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ["dia", "hora_inicio"]

    def clean(self):
        # Sin esto, la base aceptaba horarios invertidos (fin antes que
        # inicio) sin ningún aviso.
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError(
                {"hora_fin": "La hora de fin debe ser posterior a la hora de inicio."}
            )

    def __str__(self):
        return f"{self.actividad} - {self.dia} {self.hora_inicio} a {self.hora_fin}"


class Inscripcion(models.Model):
    socio = models.ForeignKey(
        Socio, on_delete=models.CASCADE, related_name="inscripciones"
    )
    horario = models.ForeignKey(
        Horario, on_delete=models.CASCADE, related_name="inscripciones"
    )
    fecha_inscripcion = models.DateField(auto_now_add=True)
    observacion = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        ordering = ["-fecha_inscripcion"]
        constraints = [
            models.UniqueConstraint(
                fields=["socio", "horario"], name="unique_inscripcion_socio_horario"
            )
        ]

    def __str__(self):
        return f"{self.socio} - {self.horario}"


class Asistencia(models.Model):
    socio = models.ForeignKey(
        Socio, on_delete=models.PROTECT, related_name="asistencias"
    )
    horario = models.ForeignKey(
        Horario, on_delete=models.PROTECT, related_name="asistencias"
    )
    # Se completa automáticamente con horario.profesor al tomar
    # asistencia (ver apps.actividades.views.tomar_asistencia): antes se
    # podía elegir cualquier profesor a mano, incluso uno que no
    # dictara esa clase.
    profesor = models.ForeignKey(
        Profesor, on_delete=models.PROTECT, related_name="asistencias_registradas"
    )
    fecha = models.DateField()
    hora = models.TimeField()
    # Antes solo existía la fila si el socio había asistido (no había
    # forma de registrar una ausencia explícita). Con este campo, tomar
    # asistencia genera un registro para cada inscripto de la clase,
    # presente o no, y se puede filtrar por estado en el listado.
    presente = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ["-fecha", "-hora"]
        constraints = [
            models.UniqueConstraint(
                fields=["socio", "horario", "fecha"],
                name="unique_asistencia_socio_horario_fecha",
            )
        ]

    def __str__(self):
        return f"{self.socio} - {self.fecha}"
