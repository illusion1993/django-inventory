# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import manager.models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20160112_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id_number',
            field=models.CharField(default=None, max_length=10, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to=manager.models.get_image_path, blank=True),
        ),
    ]
