# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators

import inventory.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name=b'email address')),
                ('first_name', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Please enter a valid name. Only alphabets allowed.')])),
                ('last_name', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Please enter a valid name. Only alphabets allowed.')])),
                ('phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\d{10,10}$', message=b'Phone number must be entered in correct format. Only 10 digits are allowed.')])),
                ('address', models.TextField(default=None)),
                ('id_number', models.CharField(default=None, unique=True, max_length=10)),
                ('image', models.ImageField(null=True, upload_to=inventory.models.get_image_path, blank=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
