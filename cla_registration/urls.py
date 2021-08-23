from django.urls import path
from .views import *

app_name = "cla_registration"
urlpatterns = [
    path("adherer", register_introduction, name="register_introduction")
]
