# Generated by Django 3.2.4 on 2021-08-26 09:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cla_ticketing', '0021_alter_dancingpartyregistration_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='dancingparty',
            name='scanners',
            field=models.ManyToManyField(blank=True, help_text="Les scanneurs peuvent effectuer les entrées au sein de l'événement", related_name='_cla_ticketing_dancingparty_scanners_+', to=settings.AUTH_USER_MODEL, verbose_name='Scanneurs'),
        ),
    ]