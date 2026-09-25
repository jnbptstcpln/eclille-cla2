# Written by hand (not generated): only adds one non-destructive boolean column.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0037_remove_usermembership_paiement_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='share_all_associations',
            field=models.BooleanField(default=False, verbose_name="Partager le type des associations et, pour les superutilisateurs, toutes les associations actives et leurs membres"),
        ),
    ]
