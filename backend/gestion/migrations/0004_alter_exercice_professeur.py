# Generated by Django 4.2.19 on 2025-04-04 00:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0003_alter_exercice_professeur'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercice',
            name='professeur',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
