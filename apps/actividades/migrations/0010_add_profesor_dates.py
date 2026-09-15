from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("actividades", "0009_remove_profesor_fecha_ingreso_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profesor",
            name="fecha_nacimiento",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="profesor",
            name="fecha_ingreso",
            field=models.DateField(blank=True, null=True),
        ),
    ]