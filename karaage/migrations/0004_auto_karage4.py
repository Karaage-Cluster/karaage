# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import django.utils.timezone
import jsonfield.fields
import datetime
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('karaage', '0003_unique_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='group',
            field=models.ForeignKey(to='karaage.Group', unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='institute',
            name='group',
            field=models.ForeignKey(to='karaage.Group', unique=True),
            preserve_default=True,
        ),
    ]
