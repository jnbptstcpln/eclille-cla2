# Generated by Django 3.2 on 2021-06-01 15:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cla_ticketing', '0004_auto_20210601_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dancingparty',
            name='managers',
            field=models.ManyToManyField(help_text="Les administrateurs ont la possiblité de modifier les informations de l'événement ainsi que gérer la liste des inscrits", related_name='_cla_ticketing_dancingparty_managers_+', to=settings.AUTH_USER_MODEL, verbose_name='Administrateurs'),
        ),
        migrations.AlterField(
            model_name='event',
            name='managers',
            field=models.ManyToManyField(help_text="Les administrateurs ont la possiblité de modifier les informations de l'événement ainsi que gérer la liste des inscrits", related_name='_cla_ticketing_event_managers_+', to=settings.AUTH_USER_MODEL, verbose_name='Administrateurs'),
        ),
    ]
