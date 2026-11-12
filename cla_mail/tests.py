from datetime import date, time, timedelta
from unittest import mock

from django.contrib.auth.models import Group, Permission, User
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail as outbox
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from cla_association.models import Association
from cla_auth.models import PasswordResetRequest, UserInfos
from cla_event.models import Event, EventPlace, EventType
from cla_registration.views.admin import RegistrationValidationView

from .models import Mail
from .sending import send, send_to_users, users_with_permission

SEND = "cla_mail.sending.EmailMultiAlternatives.send"


def create_student(username="jdupont", activated=False):
    user = User.objects.create(username=username, email=f"{username}@example.com")
    UserInfos.objects.create(user=user, email_school=f"{username}@centrale.centralelille.fr", cursus="G1",
                             promo=date.today().year + 3, birthdate=date(2004, 1, 1),
                             activated_on=timezone.now() if activated else None)
    return user


def create_event():
    return Event.objects.create(
        association=Association.objects.get_cla(), name="Soirée test", name_school="Soirée test",
        type=EventType.objects.create(name="Soirée"), place=EventPlace.objects.create(name="Foyer"),
        start_date=date.today() + timedelta(days=1), start_time=time(20), end_time=time(23),
    )


def fill_quota(count):
    """Simule `count` mails déjà envoyés aujourd'hui."""
    Mail.objects.bulk_create(
        Mail(kind=Mail.Kind.TEST, recipient="x@example.com", status=Mail.Status.SENT, sent_on=timezone.now())
        for _ in range(count)
    )


@override_settings(EMAIL_HOST_FROM="noreply@example.com", CONTACT_EMAIL="contact@example.com",
                   ALLOWED_HOSTS=["site.example.com"])
class SendTest(TestCase):
    def test_success_is_logged(self):
        user = User.objects.create(username="jdupont", email="jean@example.com")
        mail = send(Mail.Kind.TEST, user=user)

        self.assertEqual(mail.status, Mail.Status.SENT)
        self.assertIsNotNone(mail.sent_on)
        self.assertEqual((mail.recipient, mail.subject, mail.attempts), ("jean@example.com", "[CLA] Mail de test", 1))

        message = outbox.outbox[0]
        self.assertEqual(message.from_email, "noreply@example.com")
        self.assertEqual(message.to, ["jean@example.com"])
        self.assertEqual(message.reply_to, ["contact@example.com"])

    def test_failure_is_logged_without_raising(self):
        user = User.objects.create(username="jdupont", email="jean@example.com")
        with mock.patch(SEND, side_effect=RuntimeError("panne Brevo")):
            mail = send(Mail.Kind.TEST, user=user)

        self.assertEqual(mail.status, Mail.Status.FAILED)
        self.assertIsNone(mail.sent_on)
        self.assertIn("panne Brevo", Mail.objects.get().error)

    def test_content_error_is_logged_without_raising(self):
        mail = send(Mail.Kind.TEST, user=None)  # pas d'utilisateur : le contenu ne peut pas être construit
        self.assertEqual(mail.status, Mail.Status.FAILED)
        self.assertEqual(outbox.outbox, [])

    def test_one_mail_per_user(self):
        users = [User.objects.create(username=f"u{i}", email=f"u{i}@example.com") for i in range(3)]
        users.append(User.objects.create(username="sansmail", email=""))

        mails = send_to_users(Mail.Kind.TEST, users)

        self.assertEqual(len(mails), 3)
        self.assertEqual([m.to for m in outbox.outbox], [["u0@example.com"], ["u1@example.com"], ["u2@example.com"]])

    def test_html_content_and_target(self):
        user = create_student()
        mail = Mail.objects.get()
        self.assertEqual((mail.kind, mail.target, mail.user), (Mail.Kind.ACTIVATION, user.infos, user))
        html = outbox.outbox[0].alternatives[0][0]
        self.assertIn("https://site.example.com/activation/", html)


@override_settings(MAIL_DAILY_LIMIT=5, MAIL_URGENT_RESERVE=2)
class QuotaTest(TestCase):
    def test_deferrable_mail_waits_when_quota_is_low(self):
        fill_quota(3)  # 5 - 2 de réserve : plus de place pour les mails qui peuvent attendre
        create_student()

        mail = Mail.objects.get(kind=Mail.Kind.ACTIVATION)
        self.assertEqual(mail.status, Mail.Status.PENDING)
        self.assertEqual(mail.recipient, "jdupont@centrale.centralelille.fr")
        self.assertEqual(outbox.outbox, [])

    def test_urgent_mail_uses_the_reserve(self):
        fill_quota(4)
        user = create_student(activated=True)
        reset_request = PasswordResetRequest.objects.create(user=user, email=user.email)

        mail = send(Mail.Kind.PASSWORD_RESET, target=reset_request, user=user)

        self.assertEqual(mail.status, Mail.Status.SENT)
        self.assertEqual(outbox.outbox[0].to, [user.email])

    def test_old_sent_mails_do_not_count(self):
        fill_quota(3)
        Mail.objects.update(sent_on=timezone.now() - timedelta(days=1))
        create_student()
        self.assertEqual(Mail.objects.get(kind=Mail.Kind.ACTIVATION).status, Mail.Status.SENT)


@override_settings(MAIL_DAILY_LIMIT=5, MAIL_URGENT_RESERVE=2)
class SendPendingMailsTest(TestCase):
    def setUp(self):
        fill_quota(3)
        self.users = [create_student(f"etudiant{i}") for i in range(3)]
        self.assertEqual(Mail.objects.filter(status=Mail.Status.PENDING).count(), 3)

    def run_command(self):
        call_command("send_pending_mails", stdout=mock.MagicMock())

    def test_pending_mails_wait_for_quota(self):
        self.run_command()
        self.assertEqual(Mail.objects.filter(status=Mail.Status.PENDING).count(), 3)

    def test_pending_mails_are_sent_the_next_day_within_quota(self):
        Mail.objects.filter(status=Mail.Status.SENT).update(sent_on=timezone.now() - timedelta(days=1))
        self.run_command()

        sent = Mail.objects.filter(kind=Mail.Kind.ACTIVATION, status=Mail.Status.SENT).order_by("created_on")
        self.assertEqual([m.user for m in sent], self.users[:3])  # 5 - 2 = 3 places : tous partent
        self.assertIn("/activation/", outbox.outbox[0].alternatives[0][0])

    def test_refused_mail_stays_pending_then_fails(self):
        Mail.objects.filter(status=Mail.Status.SENT).update(sent_on=timezone.now() - timedelta(days=1))
        with mock.patch(SEND, side_effect=RuntimeError("quota Brevo dépassé")):
            for _ in range(3):
                self.run_command()
                first = Mail.objects.filter(kind=Mail.Kind.ACTIVATION).earliest("created_on")
        self.assertEqual((first.status, first.attempts), (Mail.Status.FAILED, 3))
        # le passage s'arrête au premier refus : les suivants n'ont pas été tentés
        self.assertEqual(Mail.objects.filter(status=Mail.Status.PENDING, attempts=0).count(), 2)

    def test_deleted_target_fails(self):
        Mail.objects.filter(status=Mail.Status.SENT).update(sent_on=timezone.now() - timedelta(days=1))
        UserInfos.objects.filter(user=self.users[0]).delete()
        for _ in range(3):
            self.run_command()
        mail = Mail.objects.get(user=self.users[0])
        self.assertEqual(mail.status, Mail.Status.FAILED)
        self.assertIn("supprimé", mail.error)

    @override_settings(MAIL_RETENTION_DAYS=90)
    def test_old_mails_are_purged(self):
        Mail.objects.update(created_on=timezone.now() - timedelta(days=91))
        self.run_command()
        # les mails envoyés sont effacés, les mails en attente sont gardés
        self.assertEqual(set(Mail.objects.values_list("status", flat=True)), {Mail.Status.PENDING})


class MailAdminTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_login(self.admin)

    def test_journal_is_read_only(self):
        mail = Mail.objects.create(kind=Mail.Kind.TEST, recipient="jean@example.com", subject="[CLA] Test",
                                   status=Mail.Status.FAILED, error="RuntimeError : quota dépassé")

        response = self.client.get(reverse("admin:cla_mail_mail_changelist"))
        self.assertContains(response, "jean@example.com")
        self.assertContains(response, "Échec")
        self.assertContains(response, "Envoyer un mail de test")

        response = self.client.get(reverse("admin:cla_mail_mail_change", args=[mail.pk]))
        self.assertContains(response, "quota dépassé")
        self.assertNotContains(response, 'name="_save"')

        self.assertEqual(self.client.get(reverse("admin:cla_mail_mail_add")).status_code, 403)

    def test_send_test_mail(self):
        response = self.client.post(reverse("admin:cla_mail_mail_test"), follow=True)
        self.assertContains(response, "Mail de test envoyé à admin@example.com")
        self.assertEqual(outbox.outbox[0].to, ["admin@example.com"])
        self.assertEqual(self.client.get(reverse("admin:cla_mail_mail_test")).status_code, 405)

    def test_resend_failed_activation(self):
        with mock.patch(SEND, side_effect=RuntimeError("panne Brevo")):
            user = create_student()
        mail = Mail.objects.get()
        self.assertEqual(mail.status, Mail.Status.FAILED)

        response = self.client.post(reverse("admin:cla_mail_mail_changelist"),
                                    {"action": "resend", "_selected_action": [mail.pk]}, follow=True)

        self.assertContains(response, "1 mail(s) renvoyé(s)")
        mail.refresh_from_db()
        self.assertEqual((mail.status, mail.attempts), (Mail.Status.SENT, 2))
        self.assertEqual(outbox.outbox[0].to, [user.infos.email_school])

    def test_staff_without_permission_cannot_send(self):
        staff = User.objects.create(username="staff", email="staff@example.com", is_staff=True)
        staff.user_permissions.add(Permission.objects.get(codename="view_mail"))
        self.client.force_login(staff)

        response = self.client.get(reverse("admin:cla_mail_mail_changelist"))
        self.assertNotContains(response, "Envoyer un mail de test")
        self.assertEqual(self.client.post(reverse("admin:cla_mail_mail_test")).status_code, 403)


class ErrorMessagesTest(TestCase):
    """Quand un mail ne part pas, la personne concernée le sait."""

    def test_forgot_password_failure(self):
        create_student(activated=True)
        with mock.patch(SEND, side_effect=RuntimeError("panne Brevo")):
            response = self.client.post(reverse("cla_auth:forgot_password"), {"email": "jdupont@example.com"})
        self.assertContains(response, "n&#x27;a pas pu être envoyé")
        self.assertNotContains(response, "vient de vous être envoyé")

    def test_forgot_password_success(self):
        create_student(activated=True)
        response = self.client.post(reverse("cla_auth:forgot_password"), {"email": "jdupont@example.com"})
        self.assertContains(response, "vient de vous être envoyé")

    def test_validation_code_failure(self):
        user = create_student(activated=True)
        self.client.force_login(user)
        with mock.patch(SEND, side_effect=RuntimeError("panne Brevo")):
            response = self.client.get(reverse("cla_auth:validate"))
        self.assertContains(response, "Le mail contenant votre code n'a pas pu être envoyé")

    def admin_message_after_account_creation(self, status):
        user = create_student(f"etudiant_{status}")
        Mail.objects.filter(user=user).update(status=status)
        request = RequestFactory().get("/")
        request.session = {}
        request._messages = FallbackStorage(request)
        view = RegistrationValidationView()
        view.request = request
        view.report_activation_mail(user)
        return [str(m) for m in get_messages(request)][0]

    def test_admin_message_after_account_creation(self):
        self.assertIn("a été envoyé", self.admin_message_after_account_creation(Mail.Status.SENT))
        self.assertIn("en attente", self.admin_message_after_account_creation(Mail.Status.PENDING))
        self.assertIn("n'a pas pu être envoyé", self.admin_message_after_account_creation(Mail.Status.FAILED))


class CallSitesTest(TestCase):
    """Les mails du site passent bien par le journal."""

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

        event = create_event()
        outbox.outbox.clear()
        Mail.objects.all().delete()
        event.send_notification()

        self.assertEqual(sorted(m.to[0] for m in outbox.outbox), ["both@example.com", "other@example.com"])
        self.assertEqual(set(Mail.objects.values_list("kind", flat=True)), {Mail.Kind.EVENT_TO_VALIDATE})
        self.assertEqual(Mail.objects.first().target, event)

    def test_mail_test_page_is_removed(self):
        with self.assertRaises(NoReverseMatch):
            reverse("cla_member:test_email")
