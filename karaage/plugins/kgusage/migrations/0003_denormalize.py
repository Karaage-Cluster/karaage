# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def denormalize(apps, schema_editor):
    cpu_job_model = apps.get_model("kgusage", "CPUJob")
    institute_model = apps.get_model("karaage", "Institute")

    query = cpu_job_model.objects.all()
    query = query.values('account__person__institute')
    query = query.annotate()
    query = query.order_by()

    for row in query:
        print(row)

        if row['account__person__institute'] is not None:
            person_institute = \
                institute_model.objects.get(
                    pk=row['account__person__institute'])
        else:
            person_institute = None

        cpu_job_model.objects \
            .filter(account__person__institute=person_institute) \
            .update(person_institute=person_institute)

    query = cpu_job_model.objects.all()
    query = query.values('project__institute')
    query = query.annotate()
    query = query.order_by()

    for row in query:
        print(row)

        if row['project__institute'] is not None:
            project_institute = \
                institute_model.objects.get(pk=row['project__institute'])
        else:
            project_institute = None

        cpu_job_model.objects \
            .filter(project__institute=project_institute) \
            .update(project_institute=project_institute)


class Migration(migrations.Migration):

    dependencies = [
        ('kgusage', '0002_auto_20150415_0953'),
    ]

    operations = [
        migrations.RunPython(
            denormalize,
        ),
    ]
