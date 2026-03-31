from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0042_remove_selection_national_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="selection_document",
            name="href",
            field=models.URLField(
                blank=True,
                help_text="Enlace público del documento (opcional si eliges un documento del dropdown)",
                verbose_name="URL pública",
            ),
        ),
        migrations.AddField(
            model_name="selection_national_document",
            name="document",
            field=models.ForeignKey(
                blank=True,
                help_text="Documento guardado en la biblioteca de documentos",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="wagtaildocs.document",
                verbose_name="Documento",
            ),
        ),
        migrations.AlterField(
            model_name="selection_national_document",
            name="href",
            field=models.URLField(
                blank=True,
                help_text="Enlace público del documento (opcional si eliges un documento del dropdown)",
                verbose_name="URL pública",
            ),
        ),
    ]
