import hashlib
import logging
import os
import threading
import traceback

from django.conf import settings

_local = threading.local()
MAX_TRACEBACK_LENGTH = 20_000


class DatabaseHandler(logging.Handler):
    """
    Handler de logging qui enregistre les erreurs (niveau ERROR et plus) dans le journal des erreurs
    de l'admin (Suivi du site › Journal des erreurs). Branché dans LOGGING (cla_web/settings/base.py).
    """

    def emit(self, record):
        if getattr(_local, "busy", False):  # une erreur pendant l'enregistrement d'une erreur
            return
        _local.busy = True
        try:
            from .models import Error
            Error.record(**describe(record))
        except Exception:
            pass  # le journal ne doit jamais faire planter le site (base indisponible, migration à faire…)
        finally:
            _local.busy = False


def describe(record):
    """Transforme un enregistrement de logging en champs du modèle Error."""
    exc_type, exc_value, exc_tb = record.exc_info or (None, None, None)
    if exc_type:
        title = f"{exc_type.__name__} : {exc_value}"
        frames = [f for f in traceback.extract_tb(exc_tb) if _is_project_file(f.filename)]
        frame = frames[-1] if frames else traceback.extract_tb(exc_tb)[-1]
        location = f"{_relative(frame.filename)}:{frame.lineno} ({frame.name})"
        details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        key = exc_type.__name__
    else:
        title = record.getMessage()
        location = f"{_relative(record.pathname)}:{record.lineno} ({record.funcName})"
        details = ""
        key = str(record.msg)  # le message sans ses paramètres : « …l'adresse %s » regroupe toutes les adresses

    fields = {
        "fingerprint": hashlib.sha256(f"{record.name}|{key}|{location}".encode()).hexdigest(),
        "title": title.splitlines()[0][:255] if title else record.name,
        "location": location[:255],
        "logger": record.name[:100],
        "traceback": details[-MAX_TRACEBACK_LENGTH:],
        "path": "",
        "user": None,
    }
    request = getattr(record, "request", None)
    if request is not None:
        fields["path"] = f"{request.method} {request.path}"[:255]
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            fields["user"] = user
    return fields


def _is_project_file(filename):
    path = os.path.abspath(filename)
    return path.startswith(str(settings.BASE_DIR)) and "site-packages" not in path


def _relative(filename):
    path = os.path.abspath(filename)
    if path.startswith(str(settings.BASE_DIR)):
        return os.path.relpath(path, settings.BASE_DIR).replace("\\", "/")
    return path
