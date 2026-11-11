# Connexion des services avec OpenID Connect

Le site est un fournisseur [OpenID Connect](https://openid.net/developers/how-connect-works/) (flux *authorization code* avec PKCE), servi sous `/auth/`.
Il fonctionne en parallèle de l'ancien SSO (`/authentification/<service>`) : chaque service passe à OIDC quand il le souhaite, sans rien changer pour les utilisateurs.

Les règles de l'ancien SSO s'appliquent de la même façon : collèges autorisés, validation du compte, consentement au partage des informations (un consentement donné via l'ancien SSO reste valable) et connexion automatique.

## Mise en place (une seule fois)

Générer une clé RSA et la mettre dans la variable `OIDC_RSA_PRIVATE_KEY` (voir [DEPLOY.md](DEPLOY.md)) :

```shell
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 | awk 'NF {printf "%s\\n", $0}'
```

La commande affiche la clé sur une ligne, avec des `\n`, pour `settings.ini` ou une variable d'environnement.

## Passer un service à OIDC (administrateurs)

1. Dans l'administration, *Django OAuth Toolkit › Applications › Ajouter* :
   - **Client type** : *Confidential* (ou *Public* pour une application sans serveur, qui utilisera seulement PKCE)
   - **Authorization grant type** : *Authorization code*
   - **Redirect uris** : l'URL de retour du service, par exemple `https://service.centralelille.fr/auth/callback`
   - **Post logout redirect uris** : l'URL vers laquelle revenir après une déconnexion (facultatif)
   - **Algorithm** : *RSA with SHA-2 256*
   - **Skip authorization** : laisser décoché (le consentement suit le réglage du service)
   - Copier **Client id** et **Client secret** *avant* d'enregistrer : le secret est ensuite haché et ne peut plus être affiché.
2. Dans *Services*, ouvrir le service et sélectionner l'application dans **Application OpenID Connect**.
3. Transmettre aux développeurs du service le client id, le client secret et l'URL de découverte.

Une application qui n'est liée à aucun service est refusée.

Pour vérifier la configuration de tous les services (ancien SSO et OIDC) :

```shell
python manage.py check --database default
```

## Intégrer OIDC dans un service (développeurs)

Toute bibliothèque OIDC standard convient. Il suffit de lui donner l'URL de découverte :

```
https://<domaine>/auth/.well-known/openid-configuration
```

| Point d'accès | URL |
|---|---|
| Autorisation | `/auth/authorize/` |
| Jeton | `/auth/token/` |
| Informations utilisateur | `/auth/userinfo/` |
| Clés publiques (JWKS) | `/auth/.well-known/jwks.json` |
| Déconnexion | `/auth/logout/` |
| Révocation | `/auth/revoke_token/` |

PKCE (`S256`) est obligatoire. Le paramètre `prompt=login` force la ressaisie du mot de passe.

### Scopes et claims

| Scope | Claims |
|---|---|
| `openid` (obligatoire) | `sub` : identifiant CLA (`prenom.nom`) |
| `profile` | `preferred_username`, `name`, `given_name`, `family_name` |
| `email` | `email` (adresse de l'école), `email_verified` |
| `cla` | `cursus`, `promo`, `is_admin`, `association_roles`, `all_associations` |

Les claims sont dans l'ID token et dans la réponse de `/auth/userinfo/`.
`all_associations` n'est envoyé qu'aux services qui partagent toutes les associations, et seulement pour les superutilisateurs.

Le jeton d'accès dure une heure et le refresh token 30 jours. Un refresh token est refusé dès que l'utilisateur n'a plus accès au service (compte qui n'est plus validé, changement de collège).

### Correspondance avec l'ancien SSO

`sub` est l'identifiant (`username`) de l'ancien SSO : un service retrouve ses utilisateurs existants sans migration.

| Ancien SSO | OIDC |
|---|---|
| `username` | `sub`, `preferred_username` |
| `firstName`, `lastName` | `given_name`, `family_name` |
| `emailSchool` | `email` |
| `cursus`, `promo` | `cursus`, `promo` |
| `isAdmin` | `is_admin` |
| `hasAssociationRole` | `association_roles` non vide |
| `associationRoles[]` : `associationSlug`, `associationName`, `associationType`, `role` | `association_roles[]` : `association_slug`, `association_name`, `association_type`, `role` |
| `allAssociations[]` : `slug`, `name`, `type`, `members[]` (`username`, `firstName`, `lastName`, `role`) | `all_associations[]` : `slug`, `name`, `type`, `members[]` (`username`, `given_name`, `family_name`, `role`) |

### Déconnexion

Pour déconnecter aussi l'utilisateur du site CLA, rediriger vers :

```
/auth/logout/?id_token_hint=<id_token>&post_logout_redirect_uri=<url>&state=<state>
```

`post_logout_redirect_uri` doit faire partie des *post logout redirect uris* de l'application. Sans `id_token_hint` valide, une confirmation est demandée à l'utilisateur.
