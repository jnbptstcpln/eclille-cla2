from .base import *

DEBUG = True


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'host': config("DATABASE_HOST", "127.0.0.1"),
            'port': int(config("DATABASE_PORT", "3306")),
            'user': config("DATABASE_USER"),
            'passwd': config("DATABASE_PASSWORD"),
            'db': config("DATABASE_NAME"),
        },
    }
}