# Generated by Django 3.2.4 on 2022-01-21 00:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_association', '0009_auto_20220121_0114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handoverfolder',
            name='deposed_on',
            field=models.DateField(default=datetime.date.today, help_text="Doit correspondre à l'année de fin du mandat", verbose_name='Date de dépot'),
        ),
    ]
