from django.db import migrations


def crear_configuracion_inicial(apps, schema_editor):
    """Crea la fila de configuración inicial si todavía no existe ninguna,
    para que la home tenga datos reales desde el primer `migrate` y no
    dependa de valores hardcodeados en la vista."""
    ConfiguracionGimnasio = apps.get_model("core", "ConfiguracionGimnasio")

    if not ConfiguracionGimnasio.objects.exists():
        ConfiguracionGimnasio.objects.create(
            nombre="Malvinas Gym",
            barrio="Barrio Piedrabuena",
            direccion="Barrio Piedrabuena, Ciudad Autónoma de Buenos Aires",
            telefono="11 2560-8817",
            email="contacto@malvinasgym.com.ar",
            instagram="@malvinasgym",
        )


def eliminar_configuracion_inicial(apps, schema_editor):
    ConfiguracionGimnasio = apps.get_model("core", "ConfiguracionGimnasio")
    ConfiguracionGimnasio.objects.filter(nombre="Malvinas Gym").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            crear_configuracion_inicial,
            eliminar_configuracion_inicial,
        ),
    ]
