import base64
import hashlib
import json
from datetime import date, timedelta
from io import StringIO
from urllib.parse import parse_qs, urlencode, urlparse

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from jwcrypto import jwk, jwt
from oauth2_provider.models import get_application_model

from cla_auth.models import PasswordChange, Service, ServiceAuthorization, UserInfos, must_change_password

CHANGE_URL = reverse("cla_auth:password_change_required")

Application = get_application_model()

REDIRECT_URI = "https://service.example.com/callback"
CLIENT_SECRET = "secret-du-service"
CODE_VERIFIER = "v" * 64
CODE_CHALLENGE = base64.urlsafe_b64encode(hashlib.sha256(CODE_VERIFIER.encode()).digest()).rstrip(b"=").decode()


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


class OidcTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("jdupont", "jdupont@example.com", "password",
                                            first_name="Jean", last_name="Dupont")
        UserInfos.objects.create(
            user=cls.user, email_school="jean.dupont@centrale.centralelille.fr", cursus="G1",
            promo=date.today().year + 3, birthdate=date(2004, 1, 1), activated_on=timezone.now(),
            valid_until=timezone.now() + timedelta(days=30),
        )
        cls.application = Application.objects.create(
            name="Service", client_id="service", client_secret=CLIENT_SECRET,
            client_type=Application.CLIENT_CONFIDENTIAL, authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            algorithm=Application.RS256_ALGORITHM, redirect_uris=REDIRECT_URI, post_logout_redirect_uris=REDIRECT_URI,
        )
        cls.service = Service.objects.create(
            identifier="service", name="Service", domain="service.example.com", endpoint=REDIRECT_URI,
            colleges=list(UserInfos.Colleges.values), oidc_application=cls.application,
        )

    def authorize(self, **params):
        query = {"client_id": "service", "response_type": "code", "redirect_uri": REDIRECT_URI, "state": "xyz",
                 "scope": "openid profile email cla", "code_challenge": CODE_CHALLENGE,
                 "code_challenge_method": "S256", **params}
        return self.client.get(f"/auth/authorize/?{urlencode(query)}")

    def code_from(self, response):
        self.assertEqual(response.status_code, 302, getattr(response, "content", b"")[:500])
        self.assertTrue(response.url.startswith(REDIRECT_URI), response.url)
        query = parse_qs(urlparse(response.url).query)
        self.assertEqual(query["state"], ["xyz"])
        return query["code"][0]

    def token(self, **data):
        return self.client.post("/auth/token/", {"client_id": "service", "client_secret": CLIENT_SECRET, **data})

    def exchange(self, code):
        response = self.token(grant_type="authorization_code", code=code, redirect_uri=REDIRECT_URI,
                              code_verifier=CODE_VERIFIER)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_discovery(self):
        config = self.client.get("/auth/.well-known/openid-configuration").json()
        self.assertEqual(config["issuer"], "http://testserver/auth")
        self.assertEqual(config["authorization_endpoint"], "http://testserver/auth/authorize/")
        self.assertEqual(config["end_session_endpoint"], "http://testserver/auth/logout/")
        self.assertIn("cla", config["scopes_supported"])
        self.assertIn("association_roles", config["claims_supported"])
        self.assertEqual(len(self.client.get("/auth/.well-known/jwks.json").json()["keys"]), 1)

    def test_code_flow(self):
        self.client.force_login(self.user)

        # Premier passage : écran de consentement, enregistré comme pour l'ancien SSO
        response = self.authorize()
        self.assertContains(response, "service.example.com")
        response = self.client.post(response.request["PATH_INFO"] + "?" + response.request["QUERY_STRING"],
                                    {**{k: v for k, v in response.context["form"].initial.items() if v is not None},
                                     "allow": "1"})
        tokens = self.exchange(self.code_from(response))
        self.assertTrue(ServiceAuthorization.objects.filter(service=self.service, user=self.user).exists())

        keys = jwk.JWKSet.from_json(self.client.get("/auth/.well-known/jwks.json").content)
        id_token = json.loads(jwt.JWT(jwt=tokens["id_token"], key=keys).claims)
        self.assertEqual(id_token["iss"], "http://testserver/auth")
        self.assertEqual(id_token["sub"], "jdupont")
        self.assertEqual(id_token["email"], "jean.dupont@centrale.centralelille.fr")
        self.assertEqual(id_token["cursus"], "G1")
        self.assertEqual(id_token["association_roles"], [])
        self.assertNotIn("all_associations", id_token)

        userinfo = self.client.get("/auth/userinfo/", HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}").json()
        self.assertEqual(userinfo["preferred_username"], "jdupont")
        self.assertEqual(userinfo["given_name"], "Jean")
        self.assertFalse(userinfo["is_admin"])

    def test_scopes_limit_claims(self):
        self.client.force_login(self.user)
        self.service.authorization_required = False
        self.service.save()
        tokens = self.exchange(self.code_from(self.authorize(scope="openid")))
        userinfo = self.client.get("/auth/userinfo/", HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}").json()
        self.assertEqual(userinfo, {"sub": "jdupont"})

    def test_legacy_consent_is_reused(self):
        ServiceAuthorization.objects.create(service=self.service, user=self.user)
        self.client.force_login(self.user)
        self.code_from(self.authorize())

    def test_legacy_sso_can_be_disabled(self):
        self.client.force_login(self.user)
        self.service.authorization_required = False
        self.service.legacy_sso_enabled = False
        self.service.save()
        self.assertEqual(self.client.get("/authentification/service").status_code, 404)
        self.assertEqual(self.client.get("/authentification/service/ticket").status_code, 404)
        self.code_from(self.authorize())  # OIDC fonctionne toujours

    def test_access_rules(self):
        self.client.force_login(self.user)
        self.service.colleges = []
        self.service.save()
        self.assertContains(self.authorize(), "Votre cursus actuel", status_code=403)

        self.service.colleges = list(UserInfos.Colleges.values)
        self.service.save()
        self.user.infos.valid_until = timezone.now() - timedelta(days=1)
        self.user.infos.save()
        self.assertContains(self.authorize(), "Valider mon compte", status_code=403)

        self.service.oidc_application = None
        self.service.save()
        self.assertEqual(self.authorize().status_code, 403)

    def test_login_required(self):
        response = self.authorize()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/connexion?next="))

        # Une seule saisie du mot de passe, même si la connexion automatique est désactivée
        self.service.auto_login = False
        self.service.authorization_required = False
        self.service.save()
        next_url = parse_qs(urlparse(response.url).query)["next"][0]
        self.client.get(response.url)
        response = self.client.post("/connexion", {"username": "jdupont", "password": "password", "redirect": next_url})
        self.code_from(self.client.get(response.url))

    def test_forced_login(self):
        self.service.authorization_required = False
        self.service.save()
        self.client.force_login(self.user)

        # prompt=login : mot de passe redemandé, même si l'utilisateur est connecté
        response = self.authorize(prompt="login")
        self.assertEqual(response.status_code, 302)
        login_url = response.url
        self.assertIn("prompt=login", login_url)
        self.assertContains(self.client.get(login_url), "Mot de passe")
        next_url = parse_qs(urlparse(login_url).query)["next"][0]
        self.assertNotIn("prompt", next_url)
        response = self.client.post("/connexion", {"username": "jdupont", "password": "password", "redirect": next_url})
        self.code_from(self.client.get(response.url))

        # Connexion automatique désactivée : mot de passe redemandé à chaque fois
        self.service.auto_login = False
        self.service.save()
        self.assertTrue(self.authorize().url.startswith("/connexion?"))

    def test_refresh_checks_access(self):
        self.client.force_login(self.user)
        self.service.authorization_required = False
        self.service.save()
        tokens = self.exchange(self.code_from(self.authorize()))

        response = self.token(grant_type="refresh_token", refresh_token=tokens["refresh_token"])
        self.assertEqual(response.status_code, 200, response.content)

        self.user.infos.valid_until = timezone.now() - timedelta(days=1)
        self.user.infos.save()
        response = self.token(grant_type="refresh_token", refresh_token=response.json()["refresh_token"])
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        self.client.force_login(self.user)
        self.service.authorization_required = False
        self.service.save()
        tokens = self.exchange(self.code_from(self.authorize()))
        self.client.cookies["stay_logged_in"] = "jwt"

        response = self.client.get("/auth/logout/?" + urlencode({
            "id_token_hint": tokens["id_token"], "post_logout_redirect_uri": REDIRECT_URI, "state": "s"}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{REDIRECT_URI}?state=s")
        self.assertEqual(response.cookies["stay_logged_in"].value, "")
        self.assertNotIn("_auth_user_id", self.client.session)

        # Sans id_token_hint, confirmation demandée
        self.client.force_login(self.user)
        self.assertContains(self.client.get("/auth/logout/"), "Se déconnecter")


class LoginRedirectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("jdupont", "jdupont@example.com", "password")

    def login(self, next_url):
        self.client.get("/connexion", {"next": next_url})
        return self.client.post("/connexion", {"username": "jdupont", "password": "password", "redirect": next_url})

    def test_next_stays_on_site(self):
        self.assertEqual(self.login("/evenements/").url, "/evenements/")
        for url in ("https://evil.example.com/", "//evil.example.com/", "javascript:alert(1)"):
            with self.subTest(url=url):
                self.client.logout()
                self.assertEqual(self.login(url).url, "/espace-adherent/")
                self.assertEqual(self.client.get("/connexion", {"next": url}).url, "/espace-adherent/")

