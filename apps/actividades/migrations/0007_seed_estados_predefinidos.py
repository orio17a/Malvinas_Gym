from django.db import migrations

NOMBRES = ["Activo", "Inactivo", "Suspendido"]


def sembrar_estados(apps, schema_editor):
    """Antes el administrador podía crear estados de actividad/profesor
    a mano, lo que permitía valores arbitrarios o mal escritos. Ahora
    los tres estados posibles son fijos y se siembran una sola vez acá;
    la interfaz para gestionarlos manualmente fue eliminada."""
    EstadoActividad = apps.get_model("actividades", "EstadoActividad")
    EstadoProfesor = apps.get_model("actividades", "EstadoProfesor")

    for nombre in NOMBRES:
        EstadoActividad.objects.get_or_create(nombre=nombre)
        EstadoProfesor.objects.get_or_create(nombre=nombre)


def eliminar_estados_sembrados(apps, schema_editor):
    EstadoActividad = apps.get_model("actividades", "EstadoActividad")
    EstadoProfesor = apps.get_model("actividades", "EstadoProfesor")

    EstadoActividad.objects.filter(nombre__in=NOMBRES, actividades__isnull=True).distinct().delete()
    EstadoProfesor.objects.filter(nombre__in=NOMBRES, profesores__isnull=True).distinct().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("actividades", "0006_asistencia_presente_alter_horario_dia"),
    ]

    operations = [
        migrations.RunPython(sembrar_estados, eliminar_estados_sembrados),
    ]
