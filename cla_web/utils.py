from django.utils import timezone
import random


def current_school_year():
    now = timezone.now()
    return now.year - 1 if 1 <= now.month < 9 else now.year


def next_back_to_school_year():
    now = timezone.now()
    return now.year if 1 <= now.month <= 9 else now.year+1


def random_six_digits():
    return random.randint(111111, 999999)
