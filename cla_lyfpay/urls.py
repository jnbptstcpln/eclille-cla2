from django.urls import path, re_path

from cla_lyfpay.views import *

app_name = "cla_lyfpay"
urlpatterns = [
    path("debug", debug, name="debug"),
    path("payment/<str:token>", payment, name="payment"),
    path("validate", validate, name="validate"),
    path("success/<str:token>", success, name="success"),
    path("cancel/<str:token>", cancel, name="cancel"),
    path("error/<str:token>", error, name="error"),
]
