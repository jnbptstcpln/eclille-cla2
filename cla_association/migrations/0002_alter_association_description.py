# Generated by Django 3.2.4 on 2021-08-28 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_association', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='description',
            field=models.TextField(max_length=350, verbose_name='Description rapide'),
        ),
    ]