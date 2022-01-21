# Generated by Django 3.2.4 on 2021-10-28 21:55

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cla_member', '0006_alter_website_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='website',
            name='colleges',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('g1', 'G1'), ('g2', 'G2'), ('g3', 'G3'), ('alumni-centrale', 'Diplomé de Centrale'), ('ie1/ie2', 'IE1/IE2'), ('ie3', 'IE3'), ('ie4', 'IE4'), ('ie5', 'IE5'), ('alumni-iteem', "Diplomé de l'ITEEM"), ('phd', 'Doctorant')], max_length=61, verbose_name='Collèges concernés'),
        ),
    ]
