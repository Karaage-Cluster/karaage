# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0007_auto_20150317_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usage',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usage',
            name='range_end',
            field=models.DateField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usage',
            name='range_start',
            field=models.DateField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usage',
            name='raw_used',
            field=models.BigIntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usage',
            name='used',
            field=models.BigIntegerField(),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='usage',
            unique_together=set([('range_start', 'range_end', 'account', 'machine', 'submitted_project')]),
        ),
    ]
