import logging
from unittest import mock

from django.contrib.auth.models import Permission, User
from django.core.management import call_command
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import path, reverse
from django.utils import timezone

from .models import Error


def crashing_view(request):
    raise ValueError("division impossible")


def working_view(request):
    return HttpResponse("ok")


urlpatterns = [path("boom/", crashing_view), path("ok/", working_view)]


@override_settings(ROOT_URLCONF=__name__)
class ErrorJournalTest(TestCase):
    def setUp(self):
        self.client.raise_request_exception = False

    def test_crash_is_recorded(self):
        user = User.objects.create(username="jdupont")
        self.client.force_login(user)
        self.client.post("/boom/", {"password": "secret"})

        error = Error.objects.get()
        self.assertEqual(error.title, "ValueError : division impossible")
        self.assertEqual(error.location, "cla_monitoring/tests.py:15 (crashing_view)")
        self.assertEqual((error.path, error.user, error.count), ("POST /boom/", user, 1))
        self.assertIn("Traceback", error.traceback)
        self.assertNotIn("secret", error.traceback + error.title + error.path)

    def test_same_crash_is_grouped_and_reopened(self):
        self.client.get("/boom/")
        Error.objects.update(resolved_on=timezone.now())
        self.client.get("/boom/")

        error = Error.objects.get()
        self.assertEqual(error.count, 2)
        self.assertIsNone(error.resolved_on)

    def test_working_page_records_nothing(self):
        self.client.get("/ok/")
        self.assertFalse(Error.objects.exists())

    def test_logged_errors_are_grouped_by_message_template(self):
        logger = logging.getLogger("cla_auth.views.session")
        for email in ("a@example.com", "b@example.com"):
            logger.error("Plusieurs comptes utilisateur ont l'adresse %s", email)
        logger.warning("Simple avertissement")  # sous le niveau ERROR : ignoré

        error = Error.objects.get()
        self.assertEqual(error.count, 2)
        self.assertEqual(error.title, "Plusieurs comptes utilisateur ont l'adresse b@example.com")

    def test_journal_failure_never_breaks_the_site(self):
        with mock.patch.object(Error, "record", side_effect=RuntimeError("base indisponible")):
            response = self.client.get("/boom/")
        self.assertEqual(response.status_code, 500)

    def test_failed_mail_is_not_an_error(self):
        from cla_mail.models import Mail
        from cla_mail.sending import send
        user = User.objects.create(username="jdupont", email="jean@example.com")
        with mock.patch("cla_mail.sending.EmailMultiAlternatives.send", side_effect=RuntimeError("panne Brevo")):
            send(Mail.Kind.TEST, user=user)
        self.assertFalse(Error.objects.exists())  # visible dans le journal des mails, pas ici


class ErrorAdminTest(TestCase):
    def setUp(self):
        self.error = Error.objects.create(fingerprint="x", title="ValueError : division impossible",
                                          location="cla_x/views.py:12 (index)", last_seen=timezone.now(),
                                          traceback="Traceback (most recent call last): <script>")

    def test_pages_and_mark_resolved(self):
        self.client.force_login(User.objects.create_superuser("admin", "admin@example.com", "password"))

        response = self.client.get(reverse("admin:cla_monitoring_error_changelist"))
        self.assertContains(response, "division impossible")
        self.assertContains(response, "À traiter")

        response = self.client.get(reverse("admin:cla_monitoring_error_change", args=[self.error.pk]))
        self.assertContains(response, "&lt;script&gt;")  # le détail est échappé

        response = self.client.post(reverse("admin:cla_monitoring_error_changelist"),
                                    {"action": "mark_resolved", "_selected_action": [self.error.pk]}, follow=True)
        self.assertContains(response, "1 erreur(s) marquée(s) comme réglée(s)")
        self.error.refresh_from_db()
        self.assertIsNotNone(self.error.resolved_on)

    def test_view_only_staff_cannot_resolve(self):
        staff = User.objects.create(username="staff", is_staff=True)
        staff.user_permissions.add(Permission.objects.get(codename="view_error"))
        self.client.force_login(staff)
        response = self.client.get(reverse("admin:cla_monitoring_error_changelist"))
        self.assertContains(response, "division impossible")
        self.assertNotContains(response, "mark_resolved")


@override_settings(ERROR_RETENTION_DAYS=90)
class ScheduledTasksTest(TestCase):
    def test_purges_old_resolved_errors_and_sends_pending_mails(self):
        old = timezone.now() - timezone.timedelta(days=91)
        Error.objects.create(fingerprint="old-resolved", title="a", last_seen=old, resolved_on=old)
        Error.objects.create(fingerprint="old-open", title="b", last_seen=old)
        Error.objects.create(fingerprint="recent-resolved", title="c", last_seen=timezone.now(), resolved_on=old)

        with mock.patch("cla_monitoring.management.commands.scheduled_tasks.call_command") as sub_command:
            call_command("scheduled_tasks", stdout=mock.MagicMock())

        sub_command.assert_called_once_with("send_pending_mails", stdout=mock.ANY)
        self.assertEqual(set(Error.objects.values_list("fingerprint", flat=True)), {"old-open", "recent-resolved"})
