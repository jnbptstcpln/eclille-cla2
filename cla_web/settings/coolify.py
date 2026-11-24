"""
Réglages pour l'hébergement Coolify (Docker + Traefik + WhiteNoise).
Hérite de production.py, qui reste identique à celui utilisé sur l'ancien serveur.
"""
from .production import *  # noqa: F401,F403

# Derrière le reverse proxy (Traefik) : TLS terminé par le proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = config("SECURE_COOKIES", True, cast=bool)  # noqa: F405
CSRF_COOKIE_SECURE = config("SECURE_COOKIES", True, cast=bool)  # noqa: F405

# Redirection HTTP -> HTTPS, sauf pour le healthcheck que Coolify appelle en HTTP sur localhost.
# « connexion » : ancien chemin du healthcheck, à retirer une fois Coolify passé sur /sante/.
SECURE_SSL_REDIRECT = config("SSL_REDIRECT", True, cast=bool)  # noqa: F405
SECURE_REDIRECT_EXEMPT = [r"^sante/$", r"^connexion$"]

# HSTS : le navigateur n'utilise plus que HTTPS pendant cette durée (en secondes).
# Commencer court (1 h), puis passer à 1 an (31536000) une fois le HTTPS vérifié : difficile à annuler.
# Pas d'includeSubDomains : d'autres services peuvent tourner en HTTP sur les sous-domaines.
SECURE_HSTS_SECONDS = config("HSTS_SECONDS", 3600, cast=int)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Statiques servis par WhiteNoise
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Médias servis par Django seulement si SERVE_MEDIA=true (cf. urls.py)
SERVE_MEDIA = config("SERVE_MEDIA", False, cast=bool)  # noqa: F405
