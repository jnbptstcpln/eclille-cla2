from django.db import connection
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def sante(request):
    """
    Healthcheck de Coolify : 200 « OK » si la base répond, 503 sinon.
    Exclue de la redirection HTTPS (SECURE_REDIRECT_EXEMPT), car Coolify l'appelle en HTTP sur localhost.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return HttpResponse("Base de données injoignable", status=503, content_type="text/plain")
    return HttpResponse("OK", content_type="text/plain")
