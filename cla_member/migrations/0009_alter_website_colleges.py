# Generated by Django 3.2.4 on 2022-02-23 13:45

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cla_member', '0008_alter_website_colleges'),
    ]

    operations = [
        migrations.AlterField(
            model_name='website',
            name='colleges',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('g1', 'G1'), ('g2', 'G2'), ('g3', 'G3'), ('alumni-centrale', 'Diplomé de Centrale'), ('ie1/ie2', 'IE1/IE2'), ('ie3', 'IE3'), ('ie4', 'IE4'), ('ie5', 'IE5'), ('alumni-iteem', "Diplomé de l'ITEEM"), ('cpi1', 'ENSCL-CPI1'), ('cpi2', 'ENSCL-CPI2'), ('ch1', 'ENSCL-1A'), ('ch2', 'ENSCL-2A'), ('ch3', 'ENSCL-3A'), ('alumni-enscl', "Diplomé de l'ENSCL"), ('phd', 'Doctorant'), ('other', 'Autre')], max_length=102, verbose_name='Collèges concernés'),
        ),
    ]
