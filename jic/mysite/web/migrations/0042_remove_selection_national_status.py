from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0041_alter_selection_institutional_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="selection_national",
            name="status",
        ),
    ]
