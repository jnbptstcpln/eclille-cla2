"""
Tests de fumée : chargent les pages principales pour détecter ce qui casse lors des montées de version.
Lancer avec : DJANGO_SETTINGS_MODULE=cla_web.settings.test python manage.py test
"""
import io
import tempfile
from datetime import date, time, timedelta

import bleach

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from weasyprint import HTML

from cla_association.models import Association
from cla_auth.models import Service, UserInfos, UserMembership
from cla_event.models import Event, EventPlace, EventType
from cla_registration.models import ImageRightAgreement
from cla_ticketing.models import DancingParty, Event as TicketingEvent

# Ajout seulement via un bouton depuis un évènement/une soirée (paramètres GET requis),
# ou jamais à la main (journaux des mails et des erreurs)
NO_ADD_VIEW = {"eventregistration", "dancingpartyregistration", "mail", "error"}

# Les styles en ligne sont tous vidés : aucun `styles`/`css_sanitizer` n'est passé à bleach.clean
BLEACH_EXPECTED = {
    '<p style="color: red; text-align: center;">Texte <b>gras</b> <sub>2</sub> <sup>3</sup></p>':
        '<p style="">Texte <b>gras</b> <sub>2</sub> <sup>3</sup></p>',
    '<script>alert(1)</script><a href="javascript:alert(1)" onclick="x()">lien</a>':
        '&lt;script&gt;alert(1)&lt;/script&gt;<a>lien</a>',
    '<a href="https://example.com" title="t" target="_blank">ok</a> <img src="https://example.com/a.png" style="width: 50%;" onerror="x()">':
        '<a href="https://example.com" title="t">ok</a> <img src="https://example.com/a.png" style="">',
    '<span style="font-weight: bold; background-image: url(javascript:alert(1))">s</span><table><tr><td>t</td></tr></table>':
        '<span style="">s</span>&lt;table&gt;&lt;tr&gt;&lt;td&gt;t&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;',
    '<h2 style="color:#123">Titre</h2><div class="c" style="margin:0">d</div><hr><ul><li>a</li></ul>':
        '<h2 style="">Titre</h2><div style="">d</div><hr><ul><li>a</li></ul>',
    # bleach 4.1 supprimait la balise non fermée, bleach 6 l'échappe
    'Texte & <non fermé':
        'Texte &amp; &lt;non fermé',
}


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
        urls = ["/admin/", "/summernote/editor/id_presentation_html/"]
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

    def test_qr_code(self):
        # Même balise que les billets de soirée (cla_ticketing/party/view_registration_*.html)
        url = Template(
            "{% load qr_code %}{% qr_url_from_text text size=8 version=10 image_format='png' dark_color='#34495e' %}"
        ).render(Context({"text": "billet"}))
        response = self.client.get(url.replace("&amp;", "&"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_membership_pdf(self):
        # Justificatif de cotisation généré par django-weasyprint depuis l'admin
        UserMembership.objects.create(user=self.user, amount=100, paid_on=date.today())
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:auth_user_membership", args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.rendered_content.startswith(b"%PDF"))

    def test_ics_export(self):
        tomorrow = date.today() + timedelta(days=1)
        Event.objects.create(
            association=Association.objects.get_cla(), name="Soirée test", name_school="Soirée test",
            type=EventType.objects.create(name="Soirée"), place=EventPlace.objects.create(name="Foyer"),
            start_date=tomorrow, start_time=time(20), end_time=time(23), validated=True, admin_display=True,
        )
        response = self.client.get(reverse("cla_event:school_admin:index-ics"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BEGIN:VEVENT", response.content)
        self.assertIn(b"Soir\xc3\xa9e test", response.content)
        self.assertIn(tomorrow.strftime("%Y%m%d").encode() + b"T200000", response.content)

    def test_bleach(self):
        # Sorties de bleach 4.1 avec les réglages du projet : la montée de version ne doit pas les changer
        def clean(html):
            return bleach.clean(html, tags=settings.BLEACH_ALLOWED_TAGS, attributes=settings.BLEACH_ALLOWED_ATTRIBUTES)

        for html, expected in BLEACH_EXPECTED.items():
            with self.subTest(html=html):
                self.assertEqual(clean(html), expected)

    def test_ticketing_description_is_sanitized(self):
        # Affichée avec |safe sur les pages publiques de billetterie
        for model in (TicketingEvent, DancingParty):
            with self.subTest(model=model.__name__):
                request = RequestFactory().get("/")
                request.user = self.user
                form = admin.site._registry[model].get_form(request)()
                form.cleaned_data = {"description": '<p onclick="x()">ok</p><script>alert(1)</script>'}
                self.assertEqual(form.clean_description(), "<p>ok</p>&lt;script&gt;alert(1)&lt;/script&gt;")

    def test_pdf(self):
        agreement = ImageRightAgreement(first_name="Jean", last_name="Dupont", birthdate=date(2004, 1, 1),
                                        email_school="jean.dupont@centrale.centralelille.fr")
        html = render_to_string("cla_registration/imageright/pdf.html", {
            "image_right_agreement": agreement, "associations": {"cla": None, "bde": None}, "signature": "Jean",
        })
        self.assertTrue(HTML(string=html).write_pdf().startswith(b"%PDF"))
