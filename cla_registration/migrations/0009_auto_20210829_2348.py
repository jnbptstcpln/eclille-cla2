# Generated by Django 3.2.4 on 2021-08-29 21:48

import cla_registration.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_registration', '0008_imagerightagreement'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imagerightagreement',
            options={'verbose_name': "Formulaire de droit à l'image", 'verbose_name_plural': "Formulaires de droit à l'image"},
        ),
        migrations.AddField(
            model_name='imagerightagreement',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name="Date de l'enregistrement"),
        ),
        migrations.AlterField(
            model_name='imagerightagreement',
            name='file',
            field=models.FileField(editable=False, upload_to=cla_registration.models.FilePath.image_right_agreement, verbose_name="Formulaire de droit à l'image et à l'information"),
        ),
    ]