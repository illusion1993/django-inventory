import os
from celery.task import task
from django.core.mail import EmailMessage


@task(name="send_report_mail")
def send_report(data):

    # Generating a temporary file for attaching in the mail
    filename = '/tmp/Report.csv'
    temp = open(filename, 'w+b')
    try:
        # Writing csv data to file
        temp.write(data['csv'])
        temp.close()
        temp = open(filename, 'r')

        # Sending mail with attachment
        mail = EmailMessage(
                subject='Report',
                body='Report attached',
                to=[data['user'], 'vikram.rathore@joshtechnologygroup.com'],
            )
        mail.attach('Report.csv', temp.read(), 'text/csv')
        mail.send()
    finally:
        os.remove(filename)