# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20160118_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(default=None, max_length=50, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Please enter a valid name')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(default=None, max_length=50, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Please enter a valid name')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\d{10,10}$', message=b'Please enter a valid phone number. Only 10 digits allowed.')]),
        ),
    ]
