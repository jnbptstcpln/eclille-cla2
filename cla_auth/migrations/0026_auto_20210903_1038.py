# Generated by Django 3.2.4 on 2021-09-03 08:38

import cla_auth.models
from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0025_alter_userinfos_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfos',
            name='picture',
        ),
        migrations.AddField(
            model_name='userinfos',
            name='picture_compressed',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='JPEG', keep_meta=False, null=True, quality=90, size=[500, 500], upload_to=cla_auth.models.FilePath.picture, verbose_name='Photo de profil compressée'),
        ),
    ]
