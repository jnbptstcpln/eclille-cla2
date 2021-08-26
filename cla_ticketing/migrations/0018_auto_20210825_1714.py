# Generated by Django 3.2.4 on 2021-08-25 15:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cla_ticketing', '0017_auto_20210608_1926'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dancingpartyregistration',
            options={'permissions': (('dancingparty_manager', "Accès à l'interface de gestion des soirées dansantes pour lesquelles l'utilisateur est administrateur"),), 'verbose_name': 'Inscription', 'verbose_name_plural': 'Inscriptions'},
        ),
        migrations.AddField(
            model_name='dancingpartyregistration',
            name='guarantor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
        migrations.AddField(
            model_name='dancingpartyregistration',
            name='staff_description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='dancingpartyregistration',
            name='type',
            field=models.CharField(choices=[('contributor_soft', 'Cotisant sans alcool'), ('contributor', 'Cotisant'), ('non_contributor_soft', 'Non cotisant sans alcool'), ('non_contributor', 'Non cotisant'), ('staff', 'Staff')], default='contributor', max_length=255),
        ),
    ]