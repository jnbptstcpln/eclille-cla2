from django.contrib.auth.models import User
from django.utils.text import slugify


def create_username(first_name, last_name):
    base = f"{slugify(first_name.replace(' ', '').replace('-', ''))}.{slugify(last_name.replace(' ', '').replace('-', ''))}"
    count = 0
    username = base
    while User.objects.filter(username=username).count() > 0:
        count += 1
        username = f"{base}{count}"
    return username
