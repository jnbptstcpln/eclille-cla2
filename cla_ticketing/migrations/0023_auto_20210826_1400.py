# Generated by Django 3.2.4 on 2021-08-26 12:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cla_ticketing', '0022_dancingparty_scanners'),
    ]

    operations = [
        migrations.AddField(
            model_name='dancingpartyregistration',
            name='validated',
            field=models.BooleanField(default=False, verbose_name='Validée'),
        ),
        migrations.CreateModel(
            name='EventRegistrationCustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('text', 'Texte'), ('select', 'Choix'), ('checkbox', 'Case à cocher'), ('file', 'Fichier')], default='text', max_length=255, verbose_name='Type')),
                ('admin_only', models.BooleanField(default=False, verbose_name='Disponible seulement du côté administrateur')),
                ('required', models.BooleanField(default=False, verbose_name='Requis')),
                ('label', models.CharField(max_length=255, verbose_name='Nom')),
                ('help_text', models.CharField(blank=True, max_length=255, verbose_name='Description')),
                ('options', models.TextField(blank=True, help_text='Une valeur par ligne', null=True, verbose_name='Options pour le select')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fields', to='cla_ticketing.event', verbose_name='Champs additionnels')),
            ],
            options={
                'verbose_name': 'Champ additionnel',
                'verbose_name_plural': 'Champs additionnels',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DancingPartyRegistrationCustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('text', 'Texte'), ('select', 'Choix'), ('checkbox', 'Case à cocher'), ('file', 'Fichier')], default='text', max_length=255, verbose_name='Type')),
                ('admin_only', models.BooleanField(default=False, verbose_name='Disponible seulement du côté administrateur')),
                ('required', models.BooleanField(default=False, verbose_name='Requis')),
                ('label', models.CharField(max_length=255, verbose_name='Nom')),
                ('help_text', models.CharField(blank=True, max_length=255, verbose_name='Description')),
                ('options', models.TextField(blank=True, help_text='Une valeur par ligne', null=True, verbose_name='Options pour le select')),
                ('dancing_party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fields', to='cla_ticketing.dancingparty', verbose_name='Champs additionnels')),
            ],
            options={
                'verbose_name': 'Champ additionnel',
                'verbose_name_plural': 'Champs additionnels',
                'abstract': False,
            },
        ),
    ]