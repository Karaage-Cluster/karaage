# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fix_applications(apps, schema_editor):
    content_type = apps.get_model("contenttypes", "ContentType")
    content_type.objects.filter(model="softwareapplication").update(app_label="kgsoftware.applications")


class Migration(migrations.Migration):

    dependencies = [
        ('kgsoftware', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_applications),
    ]
