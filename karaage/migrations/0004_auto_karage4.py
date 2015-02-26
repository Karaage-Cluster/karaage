# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import django.utils.timezone
import jsonfield.fields
import datetime
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('karaage', '0003_unique_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('quantity', models.FloatField()),
            ],
            options={
                'ordering': ['allocation_pool'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllocationPeriod',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
            options={
                'ordering': ['-end', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllocationPool',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('period', models.ForeignKey(to='karaage.AllocationPeriod')),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'ordering': ['-period__end', '-grant__expires', '-grant__project__end_date', 'grant__project__name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CareerLevel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('level', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['level'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('begins', models.DateField()),
                ('expires', models.DateField()),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'ordering': ['-expires', '-project__end_date', 'project__name', 'description'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageAllocationAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('description', models.CharField(max_length=100)),
                ('quantity', models.FloatField()),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_allocation_audit_log_entry')),
                ('allocation_pool', models.ForeignKey(to='karaage.AllocationPool')),
                ('grant', models.ForeignKey(to='karaage.Grant')),
            ],
            options={
                'db_table': 'karaage_allocationauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageAllocationPeriodAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=255)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_allocationperiod_audit_log_entry')),
            ],
            options={
                'db_table': 'karaage_allocationperiodauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageAllocationPoolAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_allocationpool_audit_log_entry')),
                ('period', models.ForeignKey(to='karaage.AllocationPeriod')),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'db_table': 'karaage_allocationpoolauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageCareerLevelAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('level', models.CharField(max_length=255)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_careerlevel_audit_log_entry')),
            ],
            options={
                'db_table': 'karaage_careerlevelauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageGrantAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('description', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('begins', models.DateField()),
                ('expires', models.DateField()),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_grant_audit_log_entry')),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'db_table': 'karaage_grantauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageProjectLevelAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('level', models.CharField(max_length=255)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_projectlevel_audit_log_entry')),
            ],
            options={
                'db_table': 'karaage_projectlevelauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageResourceAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('scaling_factor', models.FloatField()),
                ('resource_type', models.CharField(max_length=255, choices=[('slurm_cpu', 'Slurm (CPU)'), ('slurm_mem', 'Slurm (MEM)'), ('gpfs', 'GPFS')])),
                ('quantity', models.BigIntegerField()),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_resource_audit_log_entry')),
                ('machine', models.ForeignKey(to='karaage.Machine')),
            ],
            options={
                'db_table': 'karaage_resourceauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageResourcePoolAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_resourcepool_audit_log_entry')),
            ],
            options={
                'db_table': 'karaage_resourcepoolauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KaraageSchemeAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('opened', models.DateField()),
                ('closed', models.DateField(null=True, blank=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_scheme_audit_log_entry')),
            ],
            options={
                'db_table': 'karaage_schemeauditlogentry',
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectLevel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('level', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['level'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectMembership',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('is_project_supervisor', models.BooleanField(default=False)),
                ('is_project_leader', models.BooleanField(default=False)),
                ('is_default_project', models.BooleanField(default=False)),
                ('is_primary_contact', models.BooleanField(default=False)),
                ('person', models.ForeignKey(to='karaage.Person')),
                ('project', models.ForeignKey(to='karaage.Project')),
                ('project_level', models.ForeignKey(null=True, to='karaage.ProjectLevel')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('scaling_factor', models.FloatField()),
                ('resource_type', models.CharField(max_length=255, choices=[('slurm_cpu', 'Slurm (CPU)'), ('slurm_mem', 'Slurm (MEM)'), ('gpfs', 'GPFS')])),
                ('quantity', models.BigIntegerField()),
                ('machine', models.ForeignKey(to='karaage.Machine')),
            ],
            options={
                'ordering': ['resource_type'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourcePool',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scheme',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('opened', models.DateField()),
                ('closed', models.DateField(null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_pool',
            field=models.ForeignKey(to='karaage.ResourcePool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='karaageresourceauditlogentry',
            name='resource_pool',
            field=models.ForeignKey(to='karaage.ResourcePool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='karaagegrantauditlogentry',
            name='scheme',
            field=models.ForeignKey(to='karaage.Scheme'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='karaageallocationpoolauditlogentry',
            name='resource_pool',
            field=models.ForeignKey(to='karaage.ResourcePool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grant',
            name='scheme',
            field=models.ForeignKey(to='karaage.Scheme'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocationpool',
            name='resource_pool',
            field=models.ForeignKey(to='karaage.ResourcePool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocation',
            name='allocation_pool',
            field=models.ForeignKey(to='karaage.AllocationPool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocation',
            name='grant',
            field=models.ForeignKey(to='karaage.Grant'),
            preserve_default=True,
        ),
        migrations.RunSQL(
            '''
                INSERT INTO karaage_projectmembership (
                    person_id,
                    project_id,
                    is_project_supervisor,
                    is_project_leader,
                    is_default_project,
                    is_primary_contact
                ) SELECT
                    members.person_id,
                    project.id,
                    '0',
                    leaders.id IS NOT NULL,
                    members.person_id IN (
                        SELECT person_id
                        FROM account
                        WHERE default_project_id = project.id
                    ),
                    '0'
                    FROM people_group_members members
                        INNER JOIN people_group grp ON (
                            members.group_id = grp.id
                        )
                        INNER JOIN project ON (
                            project.pid = grp.name
                        )
                        LEFT JOIN project_leaders leaders ON (
                            leaders.project_id = project.id
                        )
            ''',
            '''
                UPDATE account SET default_project_id = (
                    SELECT membership.project_id
                    FROM karaage_projectmembership membership
                    WHERE membership.is_default_project
                    AND account.person_id = membership.person_id
                );

                INSERT INTO project_leaders (
                    project_id,
                    person_id
                ) SELECT project_id, person_id
                FROM karaage_projectmembership
                WHERE is_project_leader
                ORDER BY id;
            ''',
        ),
        migrations.RemoveField(
            model_name='project',
            name='leaders',
        ),
        migrations.AddField(
            model_name='person',
            name='career_level',
            field=models.ForeignKey(null=True, to='karaage.CareerLevel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='lft',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, related_name='children', to='karaage.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='rght',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='tree_id',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
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
