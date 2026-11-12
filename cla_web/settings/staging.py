"""
Préproduction : mêmes réglages que la prod, mais :
- aucun mail réel n'est envoyé (ils sont affichés dans les logs du conteneur).
"""
import os

# production.py exige la clé Brevo ; inutile ici car le backend est surchargé plus bas.
os.environ.setdefault("BREVO_API_KEY", "unused")

from .coolify import *  # noqa: E402,F401,F403

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
