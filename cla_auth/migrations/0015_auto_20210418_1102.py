# Generated by Django 3.2 on 2021-04-18 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0014_alter_usermembership_paid_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passwordresetrequest',
            name='attempt',
        ),
        migrations.RemoveField(
            model_name='passwordresetrequest',
            name='sent_on',
        ),
        migrations.RemoveField(
            model_name='passwordresetrequest',
            name='token',
        ),
        migrations.RemoveField(
            model_name='passwordresetrequest',
            name='used',
        ),
    ]