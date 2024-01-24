from django.http import JsonResponse

from cla_auth.models import *


def cursus(req):
    return JsonResponse(data={"cursus": UserInfos.CursusChoices.choices}, status=200)
