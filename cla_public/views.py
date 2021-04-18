from django.shortcuts import render
from django.views.generic import View


def index(req):
    return render(
        req,
        "cla_public/index.html",
        {
            'page_active': "home"
        }
    )
