# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kgapplications', '0001_initial'),
        ('kgsoftware', '0002_auto_20141216_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoftwareApplication',
            fields=[
                ('application_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='kgapplications.Application')),
                ('software_license', models.ForeignKey(to='kgsoftware.SoftwareLicense')),
            ],
            options={
                'db_table': 'applications_softwareapplication',
            },
            bases=('kgapplications.application',),
        ),
    ]
