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
