import jwt
import random

from django.views.generic import View
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpRequest
from django.utils import timezone

from cla_auth.models import UserInfos
from cla_auth.forms.activation import ActivationRgpdForm, ActivationPasswordForm
from cla_web.utils import current_school_year


def ticketing(req: HttpRequest, event_slug):
    pass