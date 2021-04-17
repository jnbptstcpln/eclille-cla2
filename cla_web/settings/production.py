from .base import *

# Debug
DEBUG = False


# Email

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_HOST_FROM = config("EMAIL_FROM")
EMAIL_HOST_USER = config("EMAIL_LOGIN")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD")
EMAIL_PORT = 465
EMAIL_USE_SSL = True


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

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


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]