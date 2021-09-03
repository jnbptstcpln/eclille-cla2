from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, FormView

from cla_auth.models import UserInfos
from cla_member.forms import UploadUserPicture
from cla_member.mixins import ClaMemberModuleMixin


@method_decorator(csrf_exempt, name='dispatch')
class PictureUploadView(ClaMemberModuleMixin, UserPassesTestMixin, FormView):
    template_name = "cla_member/picture/upload.html"
    cla_member_active_section = "photos"
    form_class = UploadUserPicture

    def test_func(self):
        return self.request.user.has_perm("cla_auth.upload_user_picture")

    def form_invalid(self, form: UploadUserPicture):
        return JsonResponse({
            'success': False,
            'errors': form.errors.as_json(),
        })

    def form_valid(self, form):
        picture = form.cleaned_data['picture']
        email_school = ".".join(picture.name.split('.')[:-1])
        print(email_school)

        user_infos = UserInfos.objects.filter(email_school=email_school).order_by("-activated_on").first()
        if user_infos is None:
            return HttpResponse(content="Aucun utilisateur correspondant", status=404)

        user_infos.picture.save(picture.name, picture, save=False)
        user_infos.picture_compressed.save(picture.name, picture, save=False)
        user_infos.save()
        return JsonResponse({
            'success': True
        })
