# Generated by Django 3.2 on 2021-06-05 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_ticketing', '0013_alter_event_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventregistrationtype',
            name='price',
            field=models.FloatField(blank=True, verbose_name='Prix'),
        ),
    ]