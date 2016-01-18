# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20160118_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(default=None, max_length=50, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Please enter a valid name')]),
        ),
    ]
