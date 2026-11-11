"""
Réglages pour `python manage.py test` : mêmes réglages que Coolify, mais SQLite et sans variables obligatoires.
"""
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

for key in ("SECRET_KEY", "ALLOWED_HOSTS", "EMAIL_FROM", "BREVO_API_KEY",
            "DATABASE_USER", "DATABASE_PASSWORD", "DATABASE_NAME"):
    os.environ.setdefault(key, "test")
# Clé OIDC jetable, générée à chaque lancement des tests
os.environ.setdefault("OIDC_RSA_PRIVATE_KEY", rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode())

from .coolify import *  # noqa: E402,F401,F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
STORAGES = {**STORAGES, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # tests plus rapides
