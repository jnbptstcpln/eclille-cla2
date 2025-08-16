from django.db import migrations

def migrate_payment_and_alumni(apps, schema_editor):
    UserMembership = apps.get_model("cla_auth", "UserMembership")
    mapping = {
        "cash": (1, 1),
        "month-2": (2, 2),
        "month-3": (3, 3),
        "month-4": (4, 4),
        "month-5": (5, 5),
        "month-6": (6, 6),
    }

    for m in UserMembership.objects.all():
        if m.paiement_method in mapping:
            k, l = mapping[m.paiement_method]
            m.payment_installments = k
            m.payment_months = l
        m.alumni_pack = None  # état "ne sait pas" pour tout le monde
        m.save()

class Migration(migrations.Migration):

    dependencies = [
        ('cla_auth', '0035_auto_20250812_2110'),
    ]

    operations = [
        migrations.RunPython(migrate_payment_and_alumni),
    ]
