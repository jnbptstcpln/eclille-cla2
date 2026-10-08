#!/bin/sh
set -e

# Migrations + statiques à chaque démarrage de conteneur.
# Le nouveau conteneur ne devient "healthy" (donc routé par Traefik) qu'une fois ce bloc terminé.
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn cla_web.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
