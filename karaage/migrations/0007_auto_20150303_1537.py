# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0006_auto_karage4'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institute',
            name='group',
            field=models.OneToOneField(to='karaage.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='group',
            field=models.OneToOneField(to='karaage.Group'),
            preserve_default=True,
        ),
    ]
