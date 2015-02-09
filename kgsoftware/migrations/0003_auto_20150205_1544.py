# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kgsoftware', '0002_auto_20141216_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='karaage.Group', null=True),
            preserve_default=True,
        ),
    ]
