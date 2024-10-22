# Generated by Django 3.2.4 on 2021-09-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0028_alter_userinfos_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermembership',
            name='paid_validated',
            field=models.BooleanField(default=False, verbose_name='Paiement validé'),
        ),
        migrations.AddField(
            model_name='usermembership',
            name='paiement_method',
            field=models.CharField(blank=True, choices=[('cash', 'En une fois'), ('month-2', 'En 2 fois (étalé sur 2 mois)'), ('month-3', 'En 3 fois (étalé sur 3 mois)'), ('month-4', 'En 4 fois (étalé sur 4 mois)'), ('month-5', 'En 5 fois (étalé sur 5 mois)'), ('month-6', 'En 6 fois (étalé sur 6 mois)')], max_length=100, null=True, verbose_name='Méthode de paiement'),
        ),
    ]
