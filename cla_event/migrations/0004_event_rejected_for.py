# Generated by Django 3.2.4 on 2022-01-21 13:12

from django.db import migrations
import django_summernote.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cla_event', '0003_auto_20220120_2212'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='rejected_for',
            field=django_summernote.fields.SummernoteTextField(blank=True, null=True, verbose_name='Raison du refus'),
        ),
    ]
