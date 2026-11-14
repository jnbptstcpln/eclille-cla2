"""
Fournisseur OpenID Connect (django-oauth-toolkit) : claims transmis aux services.
Les vues sont dans cla_auth/views/oidc.py, les routes sous /auth/.
"""
from django.db.models import Prefetch
from oauth2_provider.oauth2_validators import OAuth2Validator

from cla_association.models import Association, AssociationMember


def _shares_all_associations(request):
    service = getattr(request.client, "service", None)
    return service is not None and service.share_all_associations


def _association_roles(request):
    include_type = _shares_all_associations(request)
    memberships = request.user.association_memberships.filter(association__active=True).select_related("association")
    roles = []
    for membership in memberships:
        role = {
            "association_slug": membership.association.slug,
            "association_name": membership.association.name,
            "role": membership.role,
        }
        if include_type:
            role["association_type"] = membership.association.type
        roles.append(role)
    return roles


def _all_associations(request):
    # Seulement pour les services share_all_associations, quand l'utilisateur est superutilisateur
    if not (_shares_all_associations(request) and request.user.is_superuser):
        return None
    members = AssociationMember.objects.filter(user__isnull=False).select_related("user")
    associations = Association.objects.filter(active=True).prefetch_related(Prefetch("members", queryset=members))
    return [
        {
            "slug": association.slug,
            "name": association.name,
            "type": association.type,
            "members": [
                {
                    "username": member.user.username,
                    "given_name": member.user.first_name,
                    "family_name": member.user.last_name,
                    "role": member.role,
                }
                for member in association.members.all()
            ],
        }
        for association in associations
    ]


class ClaOAuth2Validator(OAuth2Validator):
    # Scope requis pour chaque claim (les claims sans scope ne sont jamais transmis)
    oidc_claim_scope = {
        **OAuth2Validator.oidc_claim_scope,
        "cursus": "cla",
        "promo": "cla",
        "is_admin": "cla",
        "association_roles": "cla",
        "all_associations": "cla",
    }

    def get_additional_claims(self):
        # Sans paramètre `request` : la liste des claims est publiée dans le document de découverte
        return {
            # Même identifiant que l'ancien SSO, pour que les services retrouvent leurs utilisateurs
            "sub": lambda r: r.user.username,
            "preferred_username": lambda r: r.user.username,
            "name": lambda r: r.user.get_full_name(),
            "given_name": lambda r: r.user.first_name,
            "family_name": lambda r: r.user.last_name,
            "email": lambda r: r.user.infos.email_school,
            "email_verified": lambda r: r.user.infos.is_activated(),  # Activation par lien envoyé à cette adresse
            "cursus": lambda r: r.user.infos.cursus,
            "promo": lambda r: r.user.infos.promo,
            "is_admin": lambda r: r.user.is_superuser,
            "association_roles": _association_roles,
            "all_associations": _all_associations,
        }

    def get_oidc_claims(self, token, token_handler, request):
        claims = super().get_oidc_claims(token, token_handler, request)
        return {key: value for key, value in claims.items() if value is not None}

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        # Comme à la connexion : un compte qui n'est plus valide ou a changé de collège perd l'accès
        if not super().validate_refresh_token(refresh_token, client, request, *args, **kwargs):
            return False
        service = getattr(client, "service", None)
        return service is not None and service.access_error(request.user) is None
