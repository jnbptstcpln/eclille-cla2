# Generated by Django 3.1.3 on 2021-04-16 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0007_auto_20210416_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='validation_required',
            field=models.BooleanField(default=True, verbose_name="La validation du compte est requise pour se connecter (permet de s'assurer que l'utilisateur est encore cotisant)"),
        ),
    ]
