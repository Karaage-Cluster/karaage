# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0006_auto_karage4'),
        ('kgusage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cpujob',
            name='person_career_level',
            field=models.ForeignKey(to='karaage.CareerLevel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cpujob',
            name='person_institute',
            field=models.ForeignKey(related_name='person_institute_cpujob', to='karaage.Institute', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cpujob',
            name='person_project_level',
            field=models.ForeignKey(to='karaage.ProjectLevel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cpujob',
            name='project_institute',
            field=models.ForeignKey(related_name='project_institute_cpujob', to='karaage.Institute', null=True),
            preserve_default=True,
        ),
    ]
