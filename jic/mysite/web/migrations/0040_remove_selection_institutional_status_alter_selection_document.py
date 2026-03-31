# Generated migration for removing status and updating documents

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0039_remove_status_update_documents'),
    ]

    operations = [
        # Remove status field from selection_institutional
        migrations.RemoveField(
            model_name='selection_institutional',
            name='status',
        ),
        # Remove href field from selection_document
        migrations.RemoveField(
            model_name='selection_document',
            name='href',
        ),
        # Add document ForeignKey to selection_document (nullable to handle existing records)
        migrations.AddField(
            model_name='selection_document',
            name='document',
            field=models.ForeignKey(
                blank=True,
                help_text='Documento guardado en la biblioteca de documentos',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='wagtaildocs.document',
                verbose_name='Documento',
            ),
        ),
    ]
