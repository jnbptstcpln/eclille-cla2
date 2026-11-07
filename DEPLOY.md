# Déploiement en production

## Environnement

Le site est déployé avec [Coolify](https://coolify.io), à partir du `Dockerfile` du dépôt :

- Coolify construit l'image (Python 3.12, Debian bookworm) à chaque déploiement de la branche configurée ;
- au démarrage, `entrypoint.sh` applique les migrations (`migrate`), collecte les fichiers statiques (`collectstatic`) puis lance `gunicorn` sur le port 8000 ;
- Traefik (géré par Coolify) termine le TLS et transmet les requêtes au conteneur ;
- les fichiers statiques sont servis par WhiteNoise ;
- la base de données est un conteneur `mysql:8` géré par Coolify.

Les réglages Django utilisés sont `cla_web.settings.coolify` (valeur par défaut du `Dockerfile`). Pour une préproduction, utiliser `cla_web.settings.staging` : aucun mail n'est envoyé (ils apparaissent dans les logs) et Bugsnag n'est pas notifié.

> [!IMPORTANT]
> Le dossier `/usr/src/app/media` (photos, logos, affiches, PDF signés…) doit être un **volume persistant** dans Coolify, sinon les fichiers envoyés sont perdus à chaque déploiement.

## Variables d'environnement

| Variable | Obligatoire | Description |
|---|---|---|
| `SECRET_KEY` | oui | Clé secrète Django (longue et aléatoire). La changer invalide les sessions et les liens envoyés par mail. |
| `ALLOWED_HOSTS` | oui | Noms de domaine séparés par des virgules. Le premier sert à construire les liens absolus dans les mails. |
| `DATABASE_HOST`, `DATABASE_PORT` | non | Par défaut `127.0.0.1` et `3306`. |
| `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` | oui | Accès MySQL. |
| `EMAIL_FROM`, `EMAIL_HOST`, `EMAIL_LOGIN`, `EMAIL_PASSWORD` | oui | Envoi des mails (SMTP, SSL sur le port 465). |
| `ADMINS` | non | Adresses des administrateurs, séparées par des virgules. |
| `BUGSNAG_KEY`, `BUGSNAG_STAGE` | non | Bugsnag n'est notifié que si `BUGSNAG_STAGE=production`. |
| `DJANGO_SETTINGS_MODULE` | non | `cla_web.settings.coolify` par défaut, `cla_web.settings.staging` en préproduction. |
| `SECURE_COOKIES` | non | `True` par défaut (cookies réservés au HTTPS). |
| `SERVE_MEDIA` | non | `False` par défaut. `True` pour que Django serve lui-même `/media/`. |
| `GUNICORN_WORKERS` | non | Nombre de workers gunicorn, 3 par défaut. |

## Déployer une nouvelle version

1. Lancer les tests (voir ci-dessous).
2. Si la version contient des migrations, **faire une sauvegarde de la base** (backup Coolify ou `mysqldump`).
3. Fusionner sur la branche déployée : Coolify construit l'image et remplace le conteneur. Le nouveau conteneur ne reçoit du trafic qu'une fois les migrations et `collectstatic` terminés.
4. Vérifier les logs du conteneur dans Coolify, puis le site (connexion, pages modifiées) et Bugsnag.

> [!WARNING]
> Pendant le déploiement, l'ancien conteneur continue de répondre alors que les migrations du nouveau sont déjà appliquées. Si une migration ajoute un champ qui **ne peut pas** être `null` sur un modèle existant, les enregistrements de ce modèle échouent (`This field cannot be null.`) jusqu'à la fin du déploiement : préférer un champ `null=True` ou avec une valeur par défaut.

### Revenir en arrière

Redéployer le commit précédent depuis Coolify. Les migrations ne sont **pas** annulées automatiquement : si la version fautive en contenait, les annuler avec `python manage.py migrate <app> <migration_précédente>` (dans le terminal du conteneur, **avant** de redéployer l'ancienne version) ou restaurer la sauvegarde.

## Tests

Les tests de fumée (`cla_web/tests.py`) chargent les pages principales, l'admin, l'aller-retour SSO, les PDF, les QR codes et l'export iCal, sur une base SQLite en mémoire :

```shell
DJANGO_SETTINGS_MODULE=cla_web.settings.test python manage.py test
```

Pour tester avec exactement les bibliothèques système de la production :

```shell
docker build -t cla-web .
docker run --rm -e DJANGO_SETTINGS_MODULE=cla_web.settings.test cla-web python manage.py test
```
