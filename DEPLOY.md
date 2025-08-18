
# Déploiement en production

## Environnement
Le site web est actuellement déployé sur un VPS hébergé par OVH.

Le site tourne via le handler WSGI de Django qui est exécuté via `gunicorn` piloté par le daemon systemd ``centralelilleassos.service``.

Les requêtes web sont gérés par un serveur Apache configuré pour rediriger les requêtes vers gunicorn au travers d'un socket Unix.

## Déploiement

Une fois connecté au serveur, se rendre dans le répertoire ``/var/www/centralelilleassos.fr/`` et exécuter les commandes suivantes :

```bash
# Activation du virtualenv
source ./venv/bin/activate

# Mise à jour du code
git pull
```

A ce stade, le code est mis à jour dans le système de fichier mais le daemon est toujours exécuté avec l'ancienne version du code.

Avant de procéder au redémarrage du daemon, il faut exécuter les commandes suivantes pour mettre à jour la base de données avec les dernières migrations, ainsi que mettre à jour les ressources statiques.

> [!WARNING]
> Si votre migration contient l'ajout d'un nouveau champ sur un modèle existant, et que ce champ **ne peut pas** prendre la valeur `null` alors tant que le daemon n'aura pas été redémarré, toutes modifications de ce modèle ne pourront pas être enregistrées dans la base de données et résulteront en une erreur du type `This field cannot be null.`

```bash
# Mise à jour de la base de données
python manage.py migrate

# Mise à jour des ressources statiques
python manage.py collectstatic --noinput
```

Il est maintenant temps de redémarrer le daemon pour prendre en compte le nouveau code :

```bash
# Redémarrage du daemon
sudo systemctl restart centralelilleassos.service
```
> [!WARNING]
>Si un message d'erreur apparaît, alors le serveur est maintenant à l'arrêt, soit le problème est identifié rapidement sinon il faut rollback sur la version précédente puis redémarrer le serveur.

Si pas de message d'erreur, alors le serveur est correctement redémarré et le déploiement est terminé.
