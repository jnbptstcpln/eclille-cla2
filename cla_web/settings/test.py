"""
Réglages pour `python manage.py test` : mêmes réglages que Coolify, mais SQLite et sans variables obligatoires.
"""
import os

for key in ("SECRET_KEY", "ALLOWED_HOSTS", "EMAIL_FROM", "EMAIL_HOST", "EMAIL_LOGIN", "EMAIL_PASSWORD",
            "DATABASE_USER", "DATABASE_PASSWORD", "DATABASE_NAME"):
    os.environ.setdefault(key, "test")

from .coolify import *  # noqa: E402,F401,F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
STORAGES = {**STORAGES, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # tests plus rapides
