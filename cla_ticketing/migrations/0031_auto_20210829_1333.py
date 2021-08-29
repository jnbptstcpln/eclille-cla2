# Generated by Django 3.2.4 on 2021-08-29 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_ticketing', '0030_auto_20210827_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='dancingpartyregistrationcustomfield',
            name='editable',
            field=models.BooleanField(default=False, help_text="Permet aux étudiants de prendre leur place et de modifier après coup ce champ jusqu'au début de l'événement", verbose_name='Peut être édité après avoir coup'),
        ),
        migrations.AddField(
            model_name='eventregistrationcustomfield',
            name='editable',
            field=models.BooleanField(default=False, help_text="Permet aux étudiants de modifier ce champ après avoir pris leur place, jusqu'au début de l'événement", verbose_name='Peut être modifié'),
        ),
        migrations.AlterField(
            model_name='dancingpartyregistration',
            name='home',
            field=models.CharField(help_text='Résidence et numéro de chambre ou bien "Lille"', max_length=100, verbose_name='Logement après la soirée'),
        ),
    ]
