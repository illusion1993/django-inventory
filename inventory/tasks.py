import StringIO
import csv
from celery.task import task
from django.core.mail import EmailMessage


@task(name="send_report_mail")
def send_report(data, email):

    attachment_file = StringIO.StringIO()
    data = data['csv']
    writer = csv.DictWriter(attachment_file, data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    # Sending mail with attachment
    mail = EmailMessage(
        subject='Report',
        body='Report attached',
        to=[email],
    )
    mail.attach('Report.csv', attachment_file.getvalue(), 'text/csv')
    mail.send()


@task(name="send_mail_task")
def send_mail_task(data):

    new_mail = EmailMessage(
        subject=data['subject'],
        body=data['body'],
        to=data['to'],
        cc=data['cc']
    )

    new_mail.send()