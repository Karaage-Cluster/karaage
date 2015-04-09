# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Sum, Count
from django.db import migrations

import datetime


def amalgamate_usage(apps, schema_editor):
    cpu_job_model = apps.get_model("kgusage", "CPUJob")
    usage_model = apps.get_model("karaage", "Usage")
    resource_model = apps.get_model("karaage", "Resource")
    resource_pool_model = apps.get_model("karaage", "ResourcePool")

    account_model = apps.get_model("karaage", "Account")
    project_model = apps.get_model("karaage", "Project")
    machine_model = apps.get_model("karaage", "Machine")
    project_membership_model = apps.get_model("karaage", "ProjectMembership")

    resource_pool, _ = resource_pool_model.objects.get_or_create(
        name="CPU Hours")

    # Borken
    # content_type_model = apps.get_model("contenttypes", "ContentType")
    # content_type = content_type_model.objects.get(
    #    app_label="kgusage", model='cpujob')
    content_type = None

    query = cpu_job_model.objects.all()
    query = query.values('date', 'account', 'machine', 'project')
    query = query.annotate(usage=Sum('cpu_usage'), jobs=Count('id'))
    query = query.order_by()

    for row in query:
        print(row)

        if row['account'] is None:
            continue

        if row['project'] is None:
            continue

        if row['machine'] is None:
            continue

        range_start = row['date']
        range_end = range_start + datetime.timedelta(days=1)

        account = account_model.objects.get(pk=row['account'])
        project = project_model.objects.get(pk=row['project'])
        machine = machine_model.objects.get(pk=row['machine'])

        person = account.person
        try:
            membership = project_membership_model.objects.get(
                person=person, project=project)
            project_level = membership.project_level
        except project_membership_model.DoesNotExist:
            membership = None
            project_level = None

        resource, c = resource_model.objects.get_or_create(
            machine=machine,
            resource_pool=resource_pool,
            defaults={
                'scaling_factor': machine.scaling_factor,
                'resource_type': 'GPFS',
                'quantity': 0,
            }
        )
        used = row['usage'] * resource.scaling_factor

        # FIXME
        allocated_project = project

        usage_model.objects.update_or_create(
            range_start=range_start,
            range_end=range_end,
            account=account,
            machine=machine,
            submitted_project=project,
            defaults={
                'content_type': content_type,
                'person_institute': person.institute,
                'project_institute': project.institute,
                'person': person,
                'submitted_project': project,

                'person_project_level':  project_level,
                'person_career_level':  person.career_level,
                'count':  row['jobs'],
                'description': "WTF?",
                'raw_used':  row['usage'],
                'used': used,

                'resource':  resource,
                'resource_pool':  resource_pool,

                # FIXME
                'scheme': None,
                'grant': None,
                'allocation_pool': None,
                'allocation_period': None,
                'allocated_project':  allocated_project,
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0008_auto_20150409_1616'),
        ('kgusage', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            amalgamate_usage,
        ),
    ]
