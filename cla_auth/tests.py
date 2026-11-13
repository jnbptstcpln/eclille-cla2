from datetime import date
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cla_auth.models import PasswordChange, UserInfos, must_change_password

CHANGE_URL = reverse("cla_auth:password_change_required")


class PasswordChangeRecordTest(TestCase):
    def test_every_password_change_is_recorded(self):
        user = User.objects.create_user("jdupont", "jean@example.com", "ancien-mdp")
        first = PasswordChange.objects.get(user=user).changed_on

        user.set_password("nouveau-mdp")
        user.save()
        self.assertGreater(PasswordChange.objects.get(user=user).changed_on, first)

    def test_other_saves_are_not_password_changes(self):
        user = User.objects.create(username="jdupont", email="jean@example.com")
        user.first_name = "Jean"
        user.save()
        self.assertFalse(PasswordChange.objects.filter(user=user).exists())

    def test_who_must_change(self):
        with_password = User.objects.create_user("a", "a@example.com", "mdp-ancien")
        PasswordChange.objects.all().delete()  # comme juste après la migration
        without_password = User.objects.create(username="b")
        unusable = User.objects.create_user("c", "c@example.com", None)

        self.assertTrue(must_change_password(with_password))
        self.assertFalse(must_change_password(without_password))
        self.assertFalse(must_change_password(unusable))


class PasswordChangeRequiredTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("jdupont", "jean@example.com", "ancien-mdp")
        UserInfos.objects.create(user=self.user, email_school="jean@centrale.centralelille.fr", cursus="G1",
                                 promo=date.today().year + 3, birthdate=date(2004, 1, 1),
                                 activated_on=timezone.now(), valid_until=timezone.now() + timezone.timedelta(days=30))
        call_command("require_password_change", stdout=StringIO())
        self.client.login(username="jdupont", password="ancien-mdp")

    def test_every_page_redirects_until_password_is_changed(self):
        for url in (reverse("cla_member:lobby"), reverse("admin:index"), reverse("cla_member:account")):
            response = self.client.get(url)
            self.assertRedirects(response, f"{CHANGE_URL}?next={url.replace('/', '%2F')}", fetch_redirect_response=False)

    def test_change_password_then_back_to_requested_page(self):
        response = self.client.get(CHANGE_URL, {"next": reverse("admin:index")})
        self.assertContains(response, "incident de sécurité")

        response = self.client.post(CHANGE_URL, {"password1": "nouveau-mdp-solide", "password2": "nouveau-mdp-solide",
                                                 "next": reverse("admin:index")})

        self.assertRedirects(response, reverse("admin:index"))  # toujours connecté
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("nouveau-mdp-solide"))
        self.assertEqual(self.client.get(reverse("cla_member:lobby")).status_code, 200)

    def test_new_password_must_differ(self):
        response = self.client.post(CHANGE_URL, {"password1": "ancien-mdp", "password2": "ancien-mdp"})
        self.assertContains(response, "différent de l&#x27;ancien")
        self.assertTrue(must_change_password(self.user))

    def test_external_next_is_ignored(self):
        response = self.client.post(CHANGE_URL, {"password1": "nouveau-mdp-solide", "password2": "nouveau-mdp-solide",
                                                 "next": "https://pirate.example.com/"})
        self.assertRedirects(response, reverse("cla_member:lobby"), fetch_redirect_response=False)

    def test_logout_stays_possible(self):
        response = self.client.get(reverse("cla_auth:logout"))
        self.assertRedirects(response, reverse("cla_public:index"), fetch_redirect_response=False)


class ServiceValidateTest(TestCase):
    def test_unknown_service_is_a_404_not_a_crash(self):
        from cla_monitoring.models import Error
        # Requête réelle d'un robot qui cherchait un dossier .git exposé
        response = self.client.get("/authentification/.git/config")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["message"], "No service correspond to this identifier")
        self.assertFalse(Error.objects.exists())
