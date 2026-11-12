from datetime import date, time, timedelta
from unittest import mock

from django.contrib.auth.models import Group, Permission, User
from django.core import mail as outbox
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse

from cla_association.models import Association
from cla_auth.models import UserInfos
from cla_event.models import Event, EventPlace, EventType

from .models import Mail
from .sending import send, send_to_users, users_with_permission


@override_settings(EMAIL_HOST_FROM="noreply@example.com", CONTACT_EMAIL="contact@example.com",
                   ALLOWED_HOSTS=["site.example.com"])
class SendTest(TestCase):
    def test_success_is_logged(self):
        user = User.objects.create(username="jdupont", email="jean@example.com")
        mail = send(Mail.Kind.TEST, "jean@example.com", "[CLA] Test", "texte",
                    template="cla_auth/reset/mail.html", context={"reset_href": "https://site.example.com/r"}, user=user)

        self.assertEqual(mail.status, Mail.Status.SENT)
        self.assertIsNotNone(mail.sent_on)
        self.assertEqual(Mail.objects.get().user, user)

        message = outbox.outbox[0]
        self.assertEqual(message.from_email, "noreply@example.com")
        self.assertEqual(message.to, ["jean@example.com"])
        self.assertEqual(message.reply_to, ["contact@example.com"])
        self.assertEqual(message.alternatives[0][1], "text/html")

    def test_failure_is_logged_without_raising(self):
        with mock.patch("cla_mail.sending.EmailMultiAlternatives.send", side_effect=RuntimeError("quota dépassé")):
            mail = send(Mail.Kind.TEST, "jean@example.com", "[CLA] Test", "texte")

        self.assertEqual(mail.status, Mail.Status.FAILED)
        self.assertIsNone(mail.sent_on)
        self.assertIn("quota dépassé", Mail.objects.get().error)

    def test_template_error_is_logged_without_raising(self):
        mail = send(Mail.Kind.TEST, "jean@example.com", "[CLA] Test", "texte", template="inexistant.html")
        self.assertEqual(mail.status, Mail.Status.FAILED)
        self.assertEqual(outbox.outbox, [])

    def test_one_mail_per_user(self):
        users = [User.objects.create(username=f"u{i}", email=f"u{i}@example.com") for i in range(3)]
        users.append(User.objects.create(username="sansmail", email=""))

        mails = send_to_users(Mail.Kind.EVENT_TO_VALIDATE, users, "[CLA] Événement", "texte")

        self.assertEqual(len(mails), 3)
        self.assertEqual([m.to for m in outbox.outbox], [["u0@example.com"], ["u1@example.com"], ["u2@example.com"]])


class MailAdminTest(TestCase):
    def test_journal_is_read_only(self):
        admin = User.objects.create_superuser("admin", "admin@example.com", "password")
        mail = Mail.objects.create(kind=Mail.Kind.TEST, recipient="jean@example.com", subject="[CLA] Test",
                                   status=Mail.Status.FAILED, error="RuntimeError : quota dépassé")
        self.client.force_login(admin)

        response = self.client.get(reverse("admin:cla_mail_mail_changelist"))
        self.assertContains(response, "jean@example.com")
        self.assertContains(response, "Échec")

        response = self.client.get(reverse("admin:cla_mail_mail_change", args=[mail.pk]))
        self.assertContains(response, "quota dépassé")
        self.assertNotContains(response, 'name="_save"')

        self.assertEqual(self.client.get(reverse("admin:cla_mail_mail_add")).status_code, 403)


class CallSitesTest(TestCase):
    """Les mails du site passent bien par le journal."""

    def test_activation_mail_on_account_creation(self):
        user = User.objects.create(username="jdupont", email="jean@example.com")
        UserInfos.objects.create(user=user, email_school="jean.dupont@centrale.centralelille.fr", cursus="G1",
                                 promo=date.today().year + 3, birthdate=date(2004, 1, 1))

        mail = Mail.objects.get()
        self.assertEqual((mail.kind, mail.recipient, mail.user), (Mail.Kind.ACTIVATION, "jean.dupont@centrale.centralelille.fr", user))
        self.assertIn("/activation/", outbox.outbox[0].alternatives[0][0])

    def test_event_notification_one_mail_per_manager(self):
        permission = Permission.objects.get(content_type__app_label="cla_event", codename="change_event")
        groups = [Group.objects.create(name=n) for n in ("Bureau", "Vie asso")]
        for group in groups:
            group.permissions.add(permission)
        both = User.objects.create(username="both", email="both@example.com")
        both.groups.add(*groups)  # dans les deux groupes : un seul mail
        User.objects.create(username="other", email="other@example.com").groups.add(groups[1])
        User.objects.create(username="old", email="old@example.com", is_active=False).groups.add(groups[0])
        User.objects.create(username="nogroup", email="nogroup@example.com")

        self.assertEqual(sorted(u.username for u in users_with_permission("cla_event", "change_event")), ["both", "other"])

        event = Event.objects.create(
            association=Association.objects.get_cla(), name="Soirée test", name_school="Soirée test",
            type=EventType.objects.create(name="Soirée"), place=EventPlace.objects.create(name="Foyer"),
            start_date=date.today() + timedelta(days=1), start_time=time(20), end_time=time(23),
        )
        outbox.outbox.clear()
        Mail.objects.all().delete()
        event.send_notification()

        self.assertEqual(sorted(m.to[0] for m in outbox.outbox), ["both@example.com", "other@example.com"])
        self.assertEqual(set(Mail.objects.values_list("kind", flat=True)), {Mail.Kind.EVENT_TO_VALIDATE})

    def test_mail_test_page_is_removed(self):
        with self.assertRaises(NoReverseMatch):
            reverse("cla_member:test_email")
