# Generated by Django 3.2.4 on 2021-08-27 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_ticketing', '0028_auto_20210826_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='dancingparty',
            name='place_index',
            field=models.IntegerField(default=0),
        ),
    ]
