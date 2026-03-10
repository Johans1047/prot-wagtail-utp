from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ImportantDate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=150)),
                ("event_date", models.DateField()),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Fecha importante",
                "verbose_name_plural": "Fechas importantes",
                "ordering": ["sort_order", "event_date"],
            },
        ),
    ]
