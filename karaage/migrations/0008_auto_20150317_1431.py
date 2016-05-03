# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0007_auto_20150303_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machinecategory',
            name='datastore',
            field=models.CharField(help_text='Modifying this value on existing categories will affect accounts created under the old datastore', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='machinecategoryauditlogentry',
            name='datastore',
            field=models.CharField(help_text='Modifying this value on existing categories will affect accounts created under the old datastore', max_length=255),
            preserve_default=True,
        ),
    ]
