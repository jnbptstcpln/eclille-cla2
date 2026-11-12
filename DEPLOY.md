# Déploiement en production

## Environnement

Le site est déployé avec [Coolify](https://coolify.io), à partir du `Dockerfile` du dépôt :

- Coolify construit l'image (Python 3.12, Debian bookworm) à chaque déploiement de la branche configurée ;
- au démarrage, `entrypoint.sh` applique les migrations (`migrate`), collecte les fichiers statiques (`collectstatic`) puis lance `gunicorn` sur le port 8000 ;
- Traefik (géré par Coolify) termine le TLS et transmet les requêtes au conteneur ;
- les fichiers statiques sont servis par WhiteNoise ;
- la base de données est un conteneur `mysql:8` géré par Coolify.

Les réglages Django utilisés sont `cla_web.settings.coolify` (valeur par défaut du `Dockerfile`). Pour une préproduction, utiliser `cla_web.settings.staging` : aucun mail n'est envoyé (ils apparaissent dans les logs).

> [!IMPORTANT]
> Le dossier `/usr/src/app/media` (photos, logos, affiches, PDF signés…) doit être un **volume persistant** dans Coolify, sinon les fichiers envoyés sont perdus à chaque déploiement.

## Variables d'environnement

| Variable | Obligatoire | Description |
|---|---|---|
| `SECRET_KEY` | oui | Clé secrète Django (longue et aléatoire). La changer invalide les sessions et les liens envoyés par mail. |
| `ALLOWED_HOSTS` | oui | Noms de domaine séparés par des virgules. Le premier sert à construire les liens absolus dans les mails. |
| `DATABASE_HOST`, `DATABASE_PORT` | non | Par défaut `127.0.0.1` et `3306`. |
| `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` | oui | Accès MySQL. |
| `EMAIL_FROM` | oui | Adresse d'expédition des mails : `noreply@send.centralelilleassos.fr` (voir [Mails](#mails-brevo)). |
| `BREVO_API_KEY` | oui | Clé API Brevo (v3). Inutile en préproduction. |
| `CONTACT_EMAIL` | non | Adresse qui reçoit les réponses aux mails du site, `cla@centralelille.fr` par défaut. |
| `MAIL_DAILY_LIMIT`, `MAIL_URGENT_RESERVE` | non | Quota de mails par jour (300 par défaut) et part réservée aux mails urgents (50 par défaut). Voir [Quota](#quota-et-mails-en-attente). |
| `MAIL_RETENTION_DAYS` | non | Durée de conservation du journal des mails, 90 jours par défaut. |
| `ERROR_RETENTION_DAYS` | non | Durée de conservation des erreurs réglées dans le journal des erreurs, 90 jours par défaut. |
| `DJANGO_SETTINGS_MODULE` | non | `cla_web.settings.coolify` par défaut, `cla_web.settings.staging` en préproduction. |
| `SECURE_COOKIES` | non | `True` par défaut (cookies réservés au HTTPS). |
| `SERVE_MEDIA` | non | `False` par défaut. `True` pour que Django serve lui-même `/media/`. |
| `GUNICORN_WORKERS` | non | Nombre de workers gunicorn, 3 par défaut. |

## Mails (Brevo)

Les mails du site (activation de compte, mot de passe oublié, code de validation, alertes aux responsables) sont envoyés par l'API de [Brevo](https://www.brevo.com), depuis `noreply@send.centralelilleassos.fr`.

- **Cette adresse n'a pas de boîte de réception** : personne ne peut lire les réponses. L'adresse de contact réelle est cla@centralelille.fr.
- Le serveur ne connaît **aucun mot de passe de boîte mail**. Il n'a que la clé API Brevo, qui sert uniquement à envoyer des mails depuis les expéditeurs vérifiés. Si elle fuit, on la supprime dans Brevo et on en crée une autre.
- Offre gratuite : **300 mails par jour**.
- Tous les mails envoyés (ou en échec) sont listés dans l'admin : *Mails › Journal des mails*. Le contenu n'y est pas enregistré, car il contient des liens secrets.
- Depuis ce journal, on peut **renvoyer** des mails (action « Renvoyer les mails sélectionnés », par exemple un mail d'activation en échec) et **s'envoyer un mail de test** (bouton en haut à droite) pour vérifier que Brevo fonctionne. Réservé aux superusers et aux comptes qui ont la permission « Peut renvoyer un mail et envoyer un mail de test ».

Configuration du compte Brevo (à refaire seulement si on change de compte) :

1. **Domaine** : *Senders, Domains & Dedicated IPs* → *Domains* → ajouter le sous-domaine `send.centralelilleassos.fr` et copier dans les DNS de `centralelilleassos.fr` les enregistrements donnés par Brevo (code Brevo, DKIM, DMARC). Un sous-domaine dédié isole la réputation des mails du site de celle du domaine principal. Attendre que le domaine soit *authentifié*.
2. **Expéditeur** : *Senders* → ajouter `noreply@send.centralelilleassos.fr`.
3. **Clé API** : *SMTP & API* → *API Keys* → créer une clé (v3, pas une clé SMTP) et la mettre dans `BREVO_API_KEY` sur Coolify.
4. **Sécurité** : *Security* → *Authorised IPs* → n'autoriser que l'IP du serveur Coolify. Une clé volée ne marche alors nulle part ailleurs.
5. **Suivi** : désactiver le suivi des clics (et des ouvertures) des mails transactionnels, sinon Brevo réécrit les liens d'activation et de réinitialisation.

En préproduction (`cla_web.settings.staging`) et en local, aucun mail n'est envoyé : ils sont affichés dans les logs.

### Quota et mails en attente

Pour ne jamais dépasser les 300 mails par jour (par exemple le jour où l'on valide toutes les adhésions de la rentrée), le site compte lui-même les mails envoyés depuis minuit :

- **Mails urgents** (mot de passe oublié, code de validation, mail de test) : toujours envoyés tout de suite. Les 50 derniers mails du quota leur sont réservés.
- **Mails qui peuvent attendre** (activation de compte, alertes « à valider » aux responsables) : envoyés tout de suite tant qu'on reste sous 250 mails dans la journée. Au-delà, ils passent **« En attente »** dans le journal et partent automatiquement dès que le quota le permet.

Les mails en attente sont envoyés par la [tâche planifiée](#tâche-planifiée), qui efface aussi du journal les mails de plus de 90 jours. Si Brevo refuse un mail en attente, il est réessayé au passage suivant, puis marqué « Échec » après 3 tentatives.

Si on passe à une offre Brevo payante, augmenter `MAIL_DAILY_LIMIT`.

## Erreurs du site

Les pages qui plantent (erreur 500) et les erreurs signalées par le code sont enregistrées dans l'admin : *Suivi du site › Journal des erreurs*. Elles apparaissent aussi dans les logs du conteneur.

- Les erreurs identiques sont regroupées sur une ligne, avec leur nombre d'occurrences et la dernière page concernée.
- Une fois le problème corrigé, sélectionner l'erreur et utiliser l'action « Marquer comme réglées ». Si elle se reproduit, elle repasse « À traiter ».
- Le journal ne contient jamais ce que l'utilisateur a tapé (formulaires, mots de passe).
- Les erreurs réglées depuis plus de 90 jours sont effacées par la tâche planifiée.

## Tâche planifiée

Une seule tâche planifiée Coolify, à créer une fois sur l'application (*Scheduled Tasks*) :

- **Commande** : `python manage.py scheduled_tasks`
- **Fréquence** : `0 * * * *` (toutes les heures)

Elle envoie les mails en attente et nettoie les journaux des mails et des erreurs.

## Déployer une nouvelle version

1. Lancer les tests (voir ci-dessous).
2. Si la version contient des migrations, **faire une sauvegarde de la base** (backup Coolify ou `mysqldump`).
3. Fusionner sur la branche déployée : Coolify construit l'image et remplace le conteneur. Le nouveau conteneur ne reçoit du trafic qu'une fois les migrations et `collectstatic` terminés.
4. Vérifier les logs du conteneur dans Coolify, puis le site (connexion, pages modifiées) et le journal des erreurs de l'admin.

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
