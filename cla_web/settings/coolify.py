"""
Réglages pour l'hébergement Coolify (Docker + Traefik + WhiteNoise).
Hérite de production.py, qui reste identique à celui utilisé sur l'ancien serveur.
"""
from .production import *  # noqa: F401,F403

# Derrière le reverse proxy (Traefik) : TLS terminé par le proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = config("SECURE_COOKIES", True, cast=bool)  # noqa: F405
CSRF_COOKIE_SECURE = config("SECURE_COOKIES", True, cast=bool)  # noqa: F405

# Statiques servis par WhiteNoise
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Médias servis par Django seulement si SERVE_MEDIA=true (cf. urls.py)
SERVE_MEDIA = config("SERVE_MEDIA", False, cast=bool)  # noqa: F405
