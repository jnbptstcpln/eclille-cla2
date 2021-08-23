from django.shortcuts import render
from django.views.generic import View


def register_introduction(req):
    return render(
        req,
        "cla_registration/introduction.html",
        {
            'page_active': "registration"
        }
    )
