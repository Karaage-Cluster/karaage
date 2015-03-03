# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kgsoftware', '0004_auto_20150227_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='group',
            field=models.OneToOneField(blank=True, to='karaage.Group', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
