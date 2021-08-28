from django.urls import path
from .views.public import *

app_name = "cla_association"
urlpatterns = [
    path("", IndexView.as_view(), name="lobby"),
]
