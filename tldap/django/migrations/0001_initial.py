# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Counters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                 auto_created=True, primary_key=True)),
                ('scheme', models.CharField(max_length=20, db_index=True)),
                ('name', models.CharField(max_length=20, db_index=True)),
                ('count', models.IntegerField()),
            ],
            options={
                'db_table': 'tldap_counters',
            },
            bases=(models.Model,),
        ),
    ]
