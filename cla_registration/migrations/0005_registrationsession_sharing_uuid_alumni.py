# Generated by Django 3.2.4 on 2021-08-24 18:16

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cla_registration', '0004_auto_20210824_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationsession',
            name='sharing_uuid_alumni',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Identifiant de partage avec les Alumni'),
        ),
    ]