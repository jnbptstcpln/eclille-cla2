# Generated by Django 3.2.4 on 2022-01-21 13:12

from django.db import migrations
import django_summernote.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cla_reservation', '0003_alter_reservationfoyer_beer_selection'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationbarbecue',
            name='rejected_for',
            field=django_summernote.fields.SummernoteTextField(blank=True, null=True, verbose_name='Raison du refus'),
        ),
        migrations.AddField(
            model_name='reservationfoyer',
            name='rejected_for',
            field=django_summernote.fields.SummernoteTextField(blank=True, null=True, verbose_name='Raison du refus'),
        ),
        migrations.AddField(
            model_name='reservationsynthe',
            name='rejected_for',
            field=django_summernote.fields.SummernoteTextField(blank=True, null=True, verbose_name='Raison du refus'),
        ),
    ]
