from django.db import migrations, models

import cla_member.models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_member', '0009_alter_website_colleges'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficialDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('statuts', "Statuts de l'association"), ('reglement-interieur', 'Règlement intérieur')], max_length=30, unique=True, verbose_name='Document')),
                ('file', models.FileField(upload_to=cla_member.models.FilePath.official_document, verbose_name='Fichier PDF')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Mis à jour le')),
            ],
            options={
                'verbose_name': 'Document officiel',
                'verbose_name_plural': 'Documents officiels',
                'ordering': ['type'],
            },
        ),
    ]
