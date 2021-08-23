from django.contrib import admin
from .models import RegistrationSession, Registration


@admin.register(RegistrationSession)
class RegistrationSessionAdmin(admin.ModelAdmin):
    pass
