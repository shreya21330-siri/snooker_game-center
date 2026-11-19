
from django.conf import settings
from django.core.mail import send_mail


def send_notification_email(subject, message, recipient_list):
    """
    Send a notification email.
    In demo mode, the email appears in the terminal.
    """

    recipients = [email for email in recipient_list if email]

    if not recipients:
        print("No email recipients provided.")
        return False

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False,
    )

    print("Demo email generated successfully!")
    return True
