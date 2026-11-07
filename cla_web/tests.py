"""
Tests de fumée : chargent les pages principales pour détecter ce qui casse lors des montées de version.
Lancer avec : DJANGO_SETTINGS_MODULE=cla_web.settings.test python manage.py test
"""
import io
import tempfile
from datetime import date, timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from weasyprint import HTML

from cla_auth.models import Service, UserInfos
from cla_registration.models import ImageRightAgreement

# Ajout seulement via un bouton depuis un évènement/une soirée (paramètres GET requis)
NO_ADD_VIEW = {"eventregistration", "dancingpartyregistration"}


class SmokeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser("jdupont", "jdupont@example.com", "password",
                                                 first_name="Jean", last_name="Dupont")
        UserInfos.objects.create(
            user=cls.user, email_school="jean.dupont@centrale.centralelille.fr", cursus="G1",
            promo=date.today().year + 3, birthdate=date(2004, 1, 1), activated_on=timezone.now(),
            valid_until=timezone.now() + timedelta(days=30),
        )

    def assertPagesLoad(self, urls):
        for url in urls:
            with self.subTest(url=url):
                self.assertLess(self.client.get(url).status_code, 400)

    def test_public_pages(self):
        self.assertPagesLoad(["/", "/connexion", "/oublier", "/adherer", "/inte", "/droit-image",
                              "/associations/", "/evenements/", "/reservations/"])

    def test_member_pages(self):
        self.client.force_login(self.user)
        self.assertPagesLoad(["/espace-adherent/", "/espace-adherent/mon-compte",
                              "/espace-adherent/mes-associations", "/espace-adherent/billetteries"])

    def test_admin_pages(self):
        # Les formulaires d'ajout utilisent le template admin/includes/fieldset.html surchargé
        self.client.force_login(self.user)
        urls = ["/admin/"]
        for model in admin.site._registry:
            info = (model._meta.app_label, model._meta.model_name)
            urls.append(reverse("admin:%s_%s_changelist" % info))
            if model._meta.model_name not in NO_ADD_VIEW:
                urls.append(reverse("admin:%s_%s_add" % info))
        self.assertPagesLoad(urls)

    def test_legacy_sso(self):
        service = Service.objects.create(
            identifier="test", name="Test", domain="example.com", endpoint="https://example.com/login",
            validation_required=True, authorization_required=False, colleges=list(UserInfos.Colleges.values),
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("cla_auth:service_authenticate", args=[service.identifier]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("https://example.com/login?ticket="))
        ticket = response.url.split("ticket=")[1]

        payload = self.client.get(reverse("cla_auth:service_validate", args=[service.identifier, ticket])).json()
        self.assertTrue(payload["success"], payload)
        self.assertEqual(payload["payload"]["username"], "jdupont")

        # Le ticket est à usage unique
        reused = self.client.get(reverse("cla_auth:service_validate", args=[service.identifier, ticket])).json()
        self.assertFalse(reused["success"])

    def test_picture_resize(self):
        image = io.BytesIO()
        Image.new("RGB", (1000, 800)).save(image, "PNG")
        with tempfile.TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            self.user.infos.picture_compressed.save("photo.png", ContentFile(image.getvalue()))
            with Image.open(self.user.infos.picture_compressed.path) as resized:
                self.assertEqual((resized.format, max(resized.size)), ("JPEG", 500))

    def test_pdf(self):
        agreement = ImageRightAgreement(first_name="Jean", last_name="Dupont", birthdate=date(2004, 1, 1),
                                        email_school="jean.dupont@centrale.centralelille.fr")
        html = render_to_string("cla_registration/imageright/pdf.html", {
            "image_right_agreement": agreement, "associations": {"cla": None, "bde": None}, "signature": "Jean",
        })
        self.assertTrue(HTML(string=html).write_pdf().startswith(b"%PDF"))
