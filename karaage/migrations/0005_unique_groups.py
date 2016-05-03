# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify


def unique_group_for_institute(apps, schema_editor):
    Group = apps.get_model('karaage', 'Group')
    Institute = apps.get_model('karaage', 'Institute')
    seen = set()
    for obj in Institute.objects.all():
        if obj.group_id not in seen:
            seen.add(obj.group_id)
            continue
        # got a unique violation, fix by adding a new group.
        obj.group, created = Group.objects.get_or_create(
            name=slugify(obj.name),
        )
        obj.save()


def unique_group_for_project(apps, schema_editor):
    Group = apps.get_model('karaage', 'Group')
    Project = apps.get_model('karaage', 'Project')
    seen = set()
    for obj in Project.objects.all():
        if obj.group_id not in seen:
            seen.add(obj.group_id)
            continue
        # got a unique violation, fix by adding a new group.
        obj.group, created = Group.objects.get_or_create(
            name=slugify(obj.name),
        )
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0004_auto_20160429_0927'),
    ]

    operations = [
        migrations.RunPython(unique_group_for_institute),
        migrations.RunPython(unique_group_for_project),
        migrations.AlterField(
            model_name='project',
            name='group',
            field=models.ForeignKey(to='karaage.Group', unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='institute',
            name='group',
            field=models.ForeignKey(to='karaage.Group', unique=True),
            preserve_default=True,
        ),
    ]
