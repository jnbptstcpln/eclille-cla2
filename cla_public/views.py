from django.shortcuts import render
from django.views.generic import View
import bugsnag


def index(req):
    bugsnag.notify(Exception('Test error'))
    return render(
        req,
        "cla_public/index.html",
        {
            'page_active': "home"
        }
    )
