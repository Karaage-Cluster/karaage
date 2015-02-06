# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('description', models.TextField(null=True, blank=True)),
                ('homepage', models.URLField(null=True, blank=True)),
                ('tutorial_url', models.URLField(null=True, blank=True)),
                ('academic_only', models.BooleanField(default=False)),
                ('restricted', models.BooleanField(default=False, help_text='Will require admin approval')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'software',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SoftwareCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'software_category',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SoftwareLicense',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=100, null=True, blank=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('text', models.TextField()),
                ('software', models.ForeignKey(to='kgsoftware.Software')),
            ],
            options={
                'ordering': ['-version'],
                'db_table': 'software_license',
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SoftwareLicenseAgreement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('license', models.ForeignKey(to='kgsoftware.SoftwareLicense')),
                ('person', models.ForeignKey(to='karaage.Person')),
            ],
            options={
                'db_table': 'software_license_agreement',
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SoftwareVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=100)),
                ('module', models.CharField(max_length=100, null=True, blank=True)),
                ('last_used', models.DateField(null=True, blank=True)),
                ('machines', models.ManyToManyField(to='karaage.Machine')),
                ('software', models.ForeignKey(to='kgsoftware.Software')),
            ],
            options={
                'ordering': ['-version'],
                'db_table': 'software_version',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='software',
            name='category',
            field=models.ForeignKey(blank=True, to='kgsoftware.SoftwareCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='software',
            name='group',
            field=models.ForeignKey(blank=True, to='karaage.Group', null=True),
            preserve_default=True,
        ),
    ]
