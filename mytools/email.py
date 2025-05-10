from django.core.mail import send_mail
from django.conf import settings
from decouple import config

def send_notification_email(subject: str, message: str, recipient_list: list[str] | None, html_message: str):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list or config("RECIPIENT_LIST").split(","),
        fail_silently=False,
        html_message=html_message
    )