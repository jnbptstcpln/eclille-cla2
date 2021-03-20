from django.utils import timezone


def current_school_year():
    now = timezone.now()
    return now.year - 1 if 1 <= now.month < 9 else now.year

