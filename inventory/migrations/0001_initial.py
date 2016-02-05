# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
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
                ('first_name', models.CharField(max_length=50, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Please enter a valid name')])),
                ('last_name', models.CharField(max_length=50, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z]+$', message=b'Please enter a valid name')])),
                ('phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\d{10,10}$', message=b'Please enter a valid phone number. Only 10 digits allowed.')])),
                ('address', models.TextField(null=True)),
                ('id_number', models.CharField(max_length=10, unique=True, null=True)),
                ('image', models.ImageField(null=True, upload_to=inventory.models.get_image_path, blank=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('returnable', models.BooleanField()),
                ('quantity', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Provision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_on', models.DateTimeField(null=True)),
                ('return_by', models.DateTimeField(null=True)),
                ('quantity', models.IntegerField(null=True)),
                ('returned', models.BooleanField(default=False)),
                ('returned_on', models.DateTimeField(null=True)),
                ('item', models.ForeignKey(to='inventory.Item')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
