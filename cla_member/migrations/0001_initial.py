# Generated by Django 3.2.4 on 2021-08-28 00:40

from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cla_auth', '0024_alter_userinfos_cursus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom du site')),
                ('description', models.TextField(max_length=500, verbose_name='Description')),
                ('href', models.CharField(max_length=250, verbose_name='Lien vers le site')),
                ('colleges', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('g1', 'G1'), ('g2', 'G2'), ('g3', 'G3'), ('alumni-centrale', 'Diplomé de Centrale'), ('ie1/ie2', 'IE1/IE2'), ('ie3', 'IE3'), ('ie4', 'IE4'), ('ie5', 'IE5'), ('alumni-iteem', "Diplomé de l'ITEEM")], max_length=57, verbose_name='Collèges concernés')),
                ('contributor_only', models.BooleanField(default=False, verbose_name='Afficher seulement aux comptes validés')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='cla_auth.service', verbose_name='Service associé')),
            ],
        ),
    ]