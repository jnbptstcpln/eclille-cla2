"""
Vérification de la configuration des services (ancien SSO et OIDC).
Lancer avec : python manage.py check --database default
"""
from django.conf import settings
from django.core.checks import Error, Tags, Warning, register


@register(Tags.database)
def check_services(app_configs=None, databases=None, **kwargs):
    if not databases:  # Lit la base : ne tourne qu'avec --database
        return []
    from oauth2_provider.models import get_application_model
    from cla_auth.models import Service

    Application = get_application_model()
    oidc_enabled = settings.OAUTH2_PROVIDER["OIDC_ENABLED"]
    messages = []

    for service in Service.objects.select_related("oidc_application"):
        def problem(level, number, msg, hint=None):
            messages.append(level(f"Service « {service.identifier} » : {msg}", hint=hint, obj=service,
                                  id=f"cla_auth.S{number:03}"))

        if not service.colleges:
            problem(Warning, 1, "aucun collège autorisé, personne ne peut se connecter.")
        if not service.endpoint.startswith("https://"):
            problem(Warning, 2, f"l'endpoint de l'ancien SSO n'est pas en HTTPS ({service.endpoint}).")

        app = service.oidc_application
        if app is None:
            continue
        if not oidc_enabled:
            problem(Error, 3, "lié à une application OIDC alors qu'OIDC est désactivé.", "Définir OIDC_RSA_PRIVATE_KEY.")
        if app.authorization_grant_type != Application.GRANT_AUTHORIZATION_CODE:
            problem(Error, 4, f"l'application « {app.name} » n'utilise pas le type « Authorization code ».")
        if app.algorithm != Application.RS256_ALGORITHM:
            problem(Error, 5, f"l'application « {app.name} » n'utilise pas l'algorithme RS256.",
                    "Sans algorithme il n'y a pas d'ID token, et HS256 ne fonctionne pas avec un secret haché.")
        uris = app.redirect_uris.split()
        if not uris:
            problem(Error, 6, f"l'application « {app.name} » n'a aucune redirect uri.")
        for uri in uris:
            if not uri.startswith("https://"):
                problem(Warning, 7, f"la redirect uri {uri} n'est pas en HTTPS.")
        if app.skip_authorization and service.authorization_required:
            problem(Warning, 8, f"l'application « {app.name} » a « Skip authorization » coché : "
                             "le consentement demandé par le service est contourné.")

    for app in Application.objects.filter(service__isnull=True):
        messages.append(Warning(f"Application OIDC « {app.name} » liée à aucun service : elle est refusée.",
                                hint="La lier à un service ou la supprimer.", obj=app, id="cla_auth.A001"))
    return messages
