# Generated by Django 3.1.3 on 2021-04-17 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0011_delete_activationrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validationrequest',
            name='code',
            field=models.IntegerField(),
        ),
    ]