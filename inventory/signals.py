from django.core.mail import EmailMessage
from django.dispatch import Signal

send_mail_signal = Signal(providing_args=['mail_data', 'recipients', 'cc_to'])


def send_mail(sender, mail_data, recipients, cc_to, **kwargs):
    if mail_data and recipients:
        EmailMessage(
            subject=mail_data['subject'],
            body=mail_data['body'],
            to=recipients,
            cc=cc_to
        ).send()

send_mail_signal.connect(send_mail)