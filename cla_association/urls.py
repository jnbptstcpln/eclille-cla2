from django.urls import path, include
from .views.public import *

app_name = "cla_association"
urlpatterns = [
    path("", ListView.as_view(), name="list"),
    path("<str:slug>", DetailView.as_view(), name="detail"),
]
