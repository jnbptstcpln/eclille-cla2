from unittest import mock

from django.contrib.auth.models import User
from django.core import mail as outbox
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Mail
from .sending import send, send_to_users


@override_settings(EMAIL_HOST_FROM="noreply@example.com", CONTACT_EMAIL="contact@example.com",
                   ALLOWED_HOSTS=["site.example.com"])
class SendTest(TestCase):
    def test_success_is_logged(self):
        user = User.objects.create(username="jdupont", email="jean@example.com")
        mail = send(Mail.Kind.TEST, "jean@example.com", "[CLA] Test", "texte",
                    template="notification/mail.html", context={"title": "T", "content": "C"}, user=user)

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
