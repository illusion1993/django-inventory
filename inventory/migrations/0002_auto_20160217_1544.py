# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=50, null=True, validators=[django.core.validators.RegexValidator(regex=b"^[A-Za-z]([a-zA-Z ,\\'\\.]*)$", message=b'Invalid first name entered')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='id_number',
            field=models.CharField(max_length=10, unique=True, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z0-9]*$', message=b'Enter a valid id number. Only alphabets and digits allowed.')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=50, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Invalid last name entered')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(regex=b'^\\d{10,10}$', message=b'Please enter a valid phone number. Only 10 digits allowed.')]),
        ),
    ]
