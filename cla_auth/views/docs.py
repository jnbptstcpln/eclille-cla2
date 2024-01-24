from django.http import JsonResponse

from cla_auth.models import *


def cursus(req):
    return JsonResponse({"cursus": UserInfos.Colleges.choices})
