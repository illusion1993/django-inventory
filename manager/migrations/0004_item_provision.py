# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_auto_20160112_2210'),
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
                ('item', models.ForeignKey(to='manager.Item')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
