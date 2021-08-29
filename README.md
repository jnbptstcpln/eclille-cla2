
# Site web de CLA

Ce dépôt contient tout le code source de la plateforme web de Centrale Lille Associations.

Il fournit toute une plateforme de gestion pour les cotisants de Centrale Lille Associations, 
notamment un système d'authentification qui permet aux utilisateurs de se connecter sur d'autres plateformes.

Cette plateforme a été initialement développée en 2020 par Jean-Baptiste Caplan (promo 2021).   


## Installation

### Installation des dépendances directes du projet

Ce projet utilise la librairie [WeasyPrint](https://doc.courtbouillon.org/weasyprint/latest/first_steps.html) pour générer des PDFs.
L'utilisation de cette librairie nécessite l'installation des packages suivant :
```shell
apt install python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libpangocairo-1.0-0
```

Après avoir récupéré le code depuis le dépôt GitHub il faut installer les dépendances en utilisant pip, mais avant cela il est recommandé de mettre en place un environnement virtuel avec ``virtualenv`` :
```shell script
virtualenv venv
source venv/bin/activate
pip install wheel  # Nécessaire pour l'installation de WeasyPrint
pip install -r requirements.txt
```

### Configuration du projet

Avant de lancer le projet, il faut mettre en place la configuration dans ``cla_web/settings/settings.ini`` en vous appuyant sur le modèle ``settings.sample.ini`` :
```
[settings]
; Project
SECRET_KEY=random_string
ALLOWED_HOSTS=host1,host2,...

; Email
EMAIL_FROM=
EMAIL_HOST=
EMAIL_LOGIN=
EMAIL_PASSWORD=

; DATABASE
DATABASE_HOST=
DATABASE_PORT=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_NAME=

; CLA_AUTH
CLA_AUTH_HOST=
CLA_AUTH_IDENTIFIER=
```

Prenez soin dans la configuration du projet de bien sélectionner l'environnement de développement (`cla_web.settings.development`) ou de production (`cla_web.settings.production`) :
- En définissant une variable d'environnement (par défaut l'environnement de production est utilisé) :
```shell script
DJANGO_SETTINGS_MODULE=cla_web.settings.development
```
- Directement dans le fichier ``manage.py``
```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cla_web.settings.development")
```

### Initialisation et mise à jour

Une fois configuré, le projet doit être initialisé. Ce processus correspond à la création des tables dans la base de données ainsi que la préparation des ressources statiques.

Ce processus doit être répété à chaque mise à jour pour que les modifications soient effectivement déployées.

Voici les commandes correspondantes :
 ```shell script
# Utilisation du virtual environment
source venv/bin/activate
# Mise à jour de la base de données
python3 manage.py makemigrations
python3 manage.py migrate
# Déploiement des ressources static
python3 manage.py collectstatic
```

### Configuration d'Apache

L'une des façon de déployer ce project en production est d'utiliser un serveur web, par exemple Apache avec le mod WSGI activé.

Voici un exemple de configuration :

```
<VirtualHost *:80>

    ServerName centralelilleassos.fr

    Alias /static/ /var/www/centralelilleassos.fr/static/

    <Directory /var/www/centralelilleassos.fr/static>
            Require all granted
    </Directory>

    WSGIDaemonProcess centralelilleassos.fr python-home=/var/www/centralelilleassos.fr/venv python-path=/var/www/centralelilleassos.fr
    WSGIProcessGroup centralelilleassos.fr

    WSGIScriptAlias / /var/www/centralelilleassos.fr/cla_web/wsgi.py process-group=centralelilleassos.fr

    <Directory /var/www/centralelilleassos.fr/cla_web>
            <Files wsgi.py>
                    Require all granted
            </Files>
    </Directory>

    ErrorLog /var/www/centralelilleassos.fr/error.log
    CustomLog /var/www/centralelilleassos.fr/access.log common

</VirtualHost>
```