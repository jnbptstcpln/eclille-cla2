# Generated by Django 3.2 on 2021-05-16 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0018_passwordresetrequest_attempt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceticket',
            name='token',
        ),
    ]
