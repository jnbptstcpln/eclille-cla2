
# Site web de CLA

Ce dépôt contient tout le code source de la plateforme web de Centrale Lille Associations.

Il fournit toute une plateforme de gestion pour les cotisants de Centrale Lille Associations, 
notamment un système d'authentification qui permet aux utilisateurs de se connecter sur d'autres plateformes.

Cette plateforme a été initialement développée en 2020 par Jean-Baptiste Caplan (promo 2021).   


## Installation (développement)

### Configuration

Copier `cla_web/settings/settings.sample.ini` vers `cla_web/settings/settings.ini` et le remplir. Les mêmes valeurs peuvent aussi être passées en variables d'environnement (voir [DEPLOY.md](DEPLOY.md) pour la liste complète).

### Avec Docker (recommandé)

```shell
# Dans settings.ini : DATABASE_HOST=cla-web-db et les identifiants MySQL de docker-compose.yml
docker compose up
docker compose exec cla-web-back python manage.py migrate
docker compose exec cla-web-back python manage.py createsuperuser
```

Le site est alors disponible sur http://localhost:8000 avec les réglages `cla_web.settings.development`.

### Sans Docker

Il faut Python 3.12, un serveur MySQL 8, ainsi que les bibliothèques système de [WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) (génération des PDF) et de `mysqlclient`. Sous Debian/Ubuntu :

```shell
apt install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 default-libmysqlclient-dev pkg-config gcc
```

Puis :

```shell
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=cla_web.settings.development
python manage.py migrate
python manage.py runserver
```

### Tests

```shell
DJANGO_SETTINGS_MODULE=cla_web.settings.test python manage.py test
```

## Déploiement

Voir [DEPLOY.md](DEPLOY.md).
