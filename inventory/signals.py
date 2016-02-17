from django.dispatch import Signal

from inventory.tasks import send_mail_task

send_mail_signal = Signal(providing_args=['mail_data', 'recipients', 'cc_to'])


def send_mail(sender, mail_data, recipients, cc_to, **kwargs):
    if mail_data and recipients:
        data = {
            'subject': mail_data['subject'],
            'body': mail_data['body'],
            'to': recipients,
            'cc': cc_to
        }
        send_mail_task.delay(data)

send_mail_signal.connect(send_mail)