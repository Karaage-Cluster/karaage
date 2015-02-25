# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings

from django.db import models, migrations
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


EXTRA_SELECTS = {
    'karaage.apps.Karaage': [
        (
            'karaage.institute',
            'institute_ids',
            '''(
                SELECT institute.id
                FROM institute
                WHERE institute.group_id = people_group.id
            )''',
        ),
        (
            'karaage.project',
            'project_ids',
            '''(
                SELECT project.id
                FROM project
                WHERE project.group_id = people_group.id
            )''',
        ),
    ],
    'kgsoftware.plugin': [
        (
            'kgsoftware.software',
            'software_ids',
            '''(
                SELECT software.id
                FROM software
                WHERE software.group_id = people_group.id
            )''',
        ),
    ],
}


def associate_groups(apps, schema_editor):
    """Associate groups with Projects/Institutes/Software."""
    Group = apps.get_model('karaage', 'Group')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    extra_select = dict()
    for app, extra_selects in EXTRA_SELECTS.items():
        if app not in settings.INSTALLED_APPS:
            for model_spec, attr, sql in extra_selects:
                extra_select[attr] = '(SELECT id FROM people_group WHERE id IS NULL)'
        else:
            for model_spec, attr, sql in extra_selects:
                extra_select[attr] = sql

    def make_list(obj):
        """Handle weird type mapping from queries."""
        if obj is None:
            return []
        if isinstance(obj, (list, tuple)):
            return [val for val in obj]
        else:
            return [obj]

    for group in Group.objects.extra(select=extra_select):
        group.institute_ids = make_list(group.institute_ids)
        group.project_ids = make_list(group.project_ids)
        group.software_ids = make_list(group.software_ids)
        ref_count = sum(
            len(foo)
            for foo
            in (group.institute_ids, group.project_ids, group.software_ids)
        )
        if ref_count == 0:
            warnings.warn(
                'Group %r not referenced by Institute/Project/Software.' % (
                    group.name,
                ),
                RuntimeWarning,
            )
        elif ref_count > 1:
            raise ValueError(
                'Group %r multiple references from %s.' % (
                    group.name,
                    ', '.join(
                        '%s%r' % (name, refs)
                        for name, refs
                        in [
                            ('Institutes', group.institute_ids),
                            ('Projects', group.project_ids),
                            ('Software', group.software_ids),
                        ]
                        if refs
                    ),
                ),
            )
        else:  # ref_count == 1
            for app, extra_selects in EXTRA_SELECTS.items():
                for model_spec, attr, sql in extra_selects:
                    parent_ids = getattr(group, attr)
                    if parent_ids:
                        app_label, model = model_spec.split('.')
                        content_type = ContentType.objects.get(
                            app_label=app_label,
                            model=model,
                        )
                        group.content_type = content_type
                        group.object_id = pk=parent_ids[0]
                        group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('karaage', '0004_auto_karage4'),
    ] + [
        dependency
        for dependency
        in [
            ('kgsoftware', '0001_initial'),
        ]
        if 'kgsoftware.plugin' in settings.INSTALLED_APPS
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='object_id',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='karaagegroupauditlogentry',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='karaagegroupauditlogentry',
            name='object_id',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(null=True, max_length=255, unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='karaagegroupauditlogentry',
            name='name',
            field=models.CharField(null=True, db_index=True, max_length=255),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('content_type', 'object_id')]),
        ),
        migrations.RunPython(
            code=associate_groups,
            reverse_code=lambda apps, schema_editor: None,
        ),
    ]
