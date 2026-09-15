from django.db import migrations, models
import django.db.models.deletion


ESTADOS = {
    "PENDIENTE": "Pendiente",
    "PRESENTADO": "Presentado",
    "VENCIDO": "Vencido",
}


def crear_estados(apps, schema_editor):
    Estado = apps.get_model("socios", "EstadoAptoFisico")
    alias = schema_editor.connection.alias
    for nombre in ESTADOS.values():
        Estado.objects.using(alias).get_or_create(nombre=nombre)


def migrar_estados(apps, schema_editor):
    Socio = apps.get_model("socios", "Socio")
    Estado = apps.get_model("socios", "EstadoAptoFisico")
    alias = schema_editor.connection.alias
    socios = Socio.objects.using(alias)

    valores = set(socios.values_list("estado_apto_fisico", flat=True).distinct())
    desconocidos = valores - set(ESTADOS)
    if desconocidos:
        raise ValueError(
            "Conversión cancelada: estados de apto físico desconocidos: "
            + repr(sorted(desconocidos, key=repr))
        )

    for codigo, nombre in ESTADOS.items():
        estado = Estado.objects.using(alias).get(nombre=nombre)
        socios.filter(estado_apto_fisico=codigo).update(
            estado_apto_fisico_nuevo_id=estado.pk
        )

    if socios.filter(estado_apto_fisico_nuevo__isnull=True).exists():
        raise ValueError("Conversión incompleta: existen socios sin estado migrado.")

    # Resolver las comprobaciones FK pendientes antes del siguiente ALTER TABLE.
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("socios", "0008_socio_nombre_contacto_emergencia_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EstadoAptoFisico",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name="ID",
                )),
                ("nombre", models.CharField(max_length=30, unique=True)),
                ("descripcion", models.CharField(blank=True, max_length=150)),
            ],
        ),
        migrations.RunPython(crear_estados, migrations.RunPython.noop),
        migrations.AddField(
            model_name="socio",
            name="estado_apto_fisico_nuevo",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="socios",
                to="socios.estadoaptofisico",
            ),
        ),
        # Sin reversa automática: no reconstruir el texto con valores por defecto.
        migrations.RunPython(migrar_estados),
        migrations.RemoveField(
            model_name="socio",
            name="estado_apto_fisico",
        ),
        migrations.RenameField(
            model_name="socio",
            old_name="estado_apto_fisico_nuevo",
            new_name="estado_apto_fisico",
        ),
        migrations.AlterField(
            model_name="socio",
            name="estado_apto_fisico",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="socios",
                to="socios.estadoaptofisico",
            ),
        ),
    ]
