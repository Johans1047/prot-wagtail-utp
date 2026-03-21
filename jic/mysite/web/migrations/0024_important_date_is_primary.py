from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0023_blogindexpage_blogpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="important_date",
            name="is_primary",
            field=models.BooleanField(
                default=True,
                help_text="Si está activa, se mostrará también en la página de inicio.",
                verbose_name="Fecha principal",
            ),
        ),
    ]
