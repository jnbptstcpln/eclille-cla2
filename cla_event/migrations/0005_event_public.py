# Generated by Django 3.2.4 on 2022-01-21 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_event', '0004_event_rejected_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='public',
            field=models.BooleanField(default=True, help_text='Décocher cette case si cet événement correspond aux activités internes de votre association (par exemple une réunion pour laquelle vous souhaitez réserver un local)', verbose_name='Événement public à faire apparaitre sur le planning'),
        ),
    ]