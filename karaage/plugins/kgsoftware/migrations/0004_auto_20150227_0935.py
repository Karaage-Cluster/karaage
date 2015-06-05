# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify
import django.db.models.deletion


def unique_group_for_software(apps, schema_editor):
    Group = apps.get_model('karaage', 'Group')
    Software = apps.get_model('karaage', 'Software')
    seen = set()
    for obj in Software.objects.all():
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
        ('kgsoftware', '0003_auto_20150205_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='karaage.Group', unique=True),
            preserve_default=True,
        ),
    ]
