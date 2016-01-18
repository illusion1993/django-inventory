# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20160118_0035'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('returnable', models.BooleanField(default=False)),
                ('quantity', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Provision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_on', models.DateTimeField(default=None, null=True, blank=True)),
                ('return_by', models.DateTimeField(default=None, null=True, blank=True)),
                ('quantity', models.IntegerField(default=None, null=True, blank=True)),
                ('returned', models.BooleanField(default=False)),
                ('returned_on', models.DateTimeField(default=None, null=True, blank=True)),
                ('item', models.ForeignKey(to='inventory.Item')),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\d{10,10}$', message=b"Phone number must be entered in the format: '999999999'. Only 10 digits allowed.")]),
        ),
        migrations.AddField(
            model_name='provision',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
