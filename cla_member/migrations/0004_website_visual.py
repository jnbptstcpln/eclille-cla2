# Generated by Django 3.2.4 on 2021-08-28 00:58

import cla_member.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_member', '0003_website_display'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='visual',
            field=models.ImageField(blank=True, null=True, upload_to=cla_member.models.FilePath.website_visual, verbose_name='Visuel du site'),
        ),
    ]
