# Generated by Django 3.2.4 on 2021-06-06 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0021_auto_20210606_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermembership',
            name='paid_by',
            field=models.CharField(blank=True, choices=[('pumpkin', 'Pumpkin'), ('check', 'Chèque'), ('cash', 'Liquide'), ('transfer', 'Virement'), ('card', 'Carte bancaire')], max_length=100, verbose_name='Moyen de paiement'),
        ),
        migrations.AlterField(
            model_name='usermembership',
            name='paid_on',
            field=models.DateField(blank=True, null=True, verbose_name='Date de paiement'),
        ),
    ]
