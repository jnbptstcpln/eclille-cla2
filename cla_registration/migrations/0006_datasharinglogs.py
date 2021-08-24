# Generated by Django 3.2.4 on 2021-08-24 18:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cla_registration', '0005_registrationsession_sharing_uuid_alumni'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSharingLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_on', models.DateTimeField(auto_now_add=True)),
                ('download_by', models.CharField(choices=[('alumni', 'Centrale Lille Alumni')], max_length=255)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='cla_registration.registrationsession')),
            ],
        ),
    ]