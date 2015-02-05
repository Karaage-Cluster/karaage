# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0002_auto_20140924_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institute',
            name='group',
            field=models.ForeignKey(to='karaage.Group', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='group',
            field=models.ForeignKey(to='karaage.Group', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]
