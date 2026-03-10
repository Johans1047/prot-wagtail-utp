# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='frequently_ask_question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_slug', models.SlugField(default='general', help_text='Identificador interno de la categoría (ej: participacion, plataforma, entregables)')),
                ('category', models.CharField(max_length=150)),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Pregunta frecuente',
                'verbose_name_plural': 'Preguntas frecuentes',
                'ordering': ['category_slug', 'sort_order'],
            },
        ),
    ]
