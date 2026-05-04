# Generated migration to remove Minijuego model and minijuego ForeignKey from Edificio

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('juego', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edificio',
            name='minijuego',
        ),
        migrations.DeleteModel(
            name='Minijuego',
        ),
    ]
