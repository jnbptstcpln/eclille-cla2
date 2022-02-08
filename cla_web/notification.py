from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_generic_email(title, content):
    send_mail(
        subject=f"[centralelilleassos.fr] {title}",
        from_email=settings.EMAIL_HOST_FROM,
        recipient_list=[settings.EMAIL_HOST_FROM],
        message=content,
        html_message=render_to_string(
            'notification/mail.html',
            {
                'title': title,
                'content': content
            }
        )
    )
