# Generated by Django 3.2 on 2021-05-12 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0017_passwordresetrequest_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwordresetrequest',
            name='attempt',
            field=models.IntegerField(default=0),
        ),
    ]
