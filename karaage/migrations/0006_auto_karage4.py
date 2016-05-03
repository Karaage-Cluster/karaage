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
        ('karaage', '0005_unique_groups'),
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
                ('name', models.CharField(unique=True, max_length=255)),
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
                'ordering': ['-period__end', '-project__end_date', 'project__name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CareerLevel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('level', models.CharField(unique=True, max_length=255)),
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
            name='AccountAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('username', models.CharField(max_length=255)),
                ('foreign_id', models.CharField(null=True, help_text='The foreign identifier from the datastore.', max_length=255, db_index=True)),
                ('date_created', models.DateField()),
                ('date_deleted', models.DateField(null=True, blank=True)),
                ('disk_quota', models.IntegerField(null=True, help_text='In GB', blank=True)),
                ('shell', models.CharField(max_length=50)),
                ('login_enabled', models.BooleanField(default=True)),
                ('extra_data', jsonfield.fields.JSONField(default={}, help_text='Datastore specific values should be stored in this field.')),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_account_audit_log_entry')),
                ('default_project', models.ForeignKey(blank=True, null=True, to='karaage.Project')),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
                ('person', models.ForeignKey(to='karaage.Person')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllocationAuditLogEntry',
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
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllocationPeriodAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_allocationperiod_audit_log_entry')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllocationPoolAuditLogEntry',
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
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CareerLevelAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('level', models.CharField(max_length=255, db_index=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_careerlevel_audit_log_entry')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GrantAuditLogEntry',
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
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('foreign_id', models.CharField(null=True, help_text='The foreign identifier from the datastore.', max_length=255, db_index=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('extra_data', jsonfield.fields.JSONField(default={}, help_text='Datastore specific values should be stored in this field.')),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_group_audit_log_entry')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstituteAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('saml_entityid', models.CharField(null=True, max_length=200, blank=True, db_index=True)),
                ('is_active', models.BooleanField(default=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_institute_audit_log_entry')),
                ('group', models.ForeignKey(to='karaage.Group')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstituteDelegateAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('send_email', models.BooleanField()),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_institutedelegate_audit_log_entry')),
                ('institute', models.ForeignKey(to='karaage.Institute')),
                ('person', models.ForeignKey(to='karaage.Person')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstituteQuotaAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('quota', models.DecimalField(max_digits=5, decimal_places=2)),
                ('cap', models.IntegerField(null=True, blank=True)),
                ('disk_quota', models.IntegerField(null=True, blank=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_institutequota_audit_log_entry')),
                ('institute', models.ForeignKey(to='karaage.Institute')),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MachineCategoryAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=100, db_index=True)),
                ('datastore', models.CharField(help_text='Modifying this value on existing categories will affect accounts created under the old datastore', max_length=255, choices=[('dummy', 'dummy'), ('ldap', 'ldap')])),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_machinecategory_audit_log_entry')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('allocation_mode', models.CharField(default='private', choices=[('private', 'Private (this project only)'), ('shared', 'Shared (this project and all sub-projects)')], max_length=20)),
                ('pid', models.CharField(max_length=255, db_index=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(null=True, blank=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('start_date', models.DateField(default=datetime.datetime.today)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('additional_req', models.TextField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=False)),
                ('date_approved', models.DateField(null=True, editable=False, blank=True)),
                ('date_deleted', models.DateField(null=True, editable=False, blank=True)),
                ('last_usage', models.DateField(null=True, editable=False, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_project_audit_log_entry')),
                ('approved_by', models.ForeignKey(blank=True, null=True, editable=False, related_name='_auditlog_project_approver', to='karaage.Person')),
                ('deleted_by', models.ForeignKey(blank=True, null=True, editable=False, related_name='_auditlog_project_deletor', to='karaage.Person')),
                ('group', models.ForeignKey(to='karaage.Group')),
                ('institute', models.ForeignKey(to='karaage.Institute')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, related_name='_auditlog_children', to='karaage.Project')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectLevelAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('level', models.CharField(max_length=255, db_index=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_projectlevel_audit_log_entry')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectQuotaAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('cap', models.IntegerField(null=True, blank=True)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_projectquota_audit_log_entry')),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('resource_name', models.CharField(max_length=255, null=True, blank=True)),
                ('scaling_factor', models.FloatField()),
                ('quantity', models.BigIntegerField()),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_resource_audit_log_entry')),
                ('machine', models.ForeignKey(to='karaage.Machine')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourcePoolAuditLogEntry',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, verbose_name='ID', db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('description', models.CharField(max_length=255)),
                ('resource_function', models.CharField(max_length=10)),
                ('resource_units', models.CharField(max_length=10)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')], editable=False)),
                ('action_user', audit_log.models.fields.LastUserField(to='karaage.Person', null=True, editable=False, related_name='_resourcepool_audit_log_entry')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchemeAuditLogEntry',
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
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectLevel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('level', models.CharField(unique=True, max_length=255)),
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
        migrations.AlterUniqueTogether(
            name='projectmembership',
            unique_together=set([('person', 'project')]),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('resource_name', models.CharField(max_length=255, null=True, blank=True)),
                ('scaling_factor', models.FloatField()),
                ('quantity', models.BigIntegerField()),
                ('machine', models.ForeignKey(to='karaage.Machine')),
            ],
            options={
                'ordering': ['machine'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourcePool',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('description', models.CharField(max_length=255)),
                ('resource_function', models.CharField(max_length=10)),
                ('resource_units', models.CharField(max_length=10)),
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
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('count', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('range_start', models.DateField()),
                ('range_end', models.DateField()),
                ('raw_used', models.BigIntegerField()),
                ('used', models.BigIntegerField()),
                ('account', models.ForeignKey(to='karaage.Account')),
                ('allocated_project', models.ForeignKey(to='karaage.Project', null=True, related_name='allocated_usage')),
                ('allocation_period', models.ForeignKey(null=True, to='karaage.AllocationPeriod')),
                ('allocation_pool', models.ForeignKey(null=True, to='karaage.AllocationPool')),
                ('machine', models.ForeignKey(to='karaage.Machine')),
                ('person', models.ForeignKey(null=True, to='karaage.Person')),
                ('person_career_level', models.ForeignKey(blank=True, null=True, to='karaage.CareerLevel')),
                ('person_institute', models.ForeignKey(to='karaage.Institute', null=True, related_name='person_usage')),
                ('person_project_level', models.ForeignKey(blank=True, null=True, to='karaage.ProjectLevel')),
                ('project_institute', models.ForeignKey(related_name='project_usage', to='karaage.Institute')),
                ('resource', models.ForeignKey(to='karaage.Resource')),
                ('resource_pool', models.ForeignKey(null=True, to='karaage.ResourcePool')),
                ('submitted_project', models.ForeignKey(related_name='submitted_usage', to='karaage.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='usage',
            unique_together=set([('range_start', 'range_end', 'account', 'machine', 'submitted_project', 'person_institute', 'person_career_level', 'person_project_level', 'project_institute')]),
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_pool',
            field=models.ForeignKey(to='karaage.ResourcePool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourceauditlogentry',
            name='resource_pool',
            field=models.ForeignKey(to='karaage.ResourcePool'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='resource',
            unique_together=set([('resource_pool', 'resource_name', 'machine')]),
        ),
        migrations.AddField(
            model_name='grantauditlogentry',
            name='scheme',
            field=models.ForeignKey(to='karaage.Scheme'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocationpoolauditlogentry',
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
        migrations.AlterUniqueTogether(
            name='allocationpool',
            unique_together=set([('project', 'period', 'resource_pool')]),
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
                ) SELECT DISTINCT
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
                    INNER JOIN project ON (
                        project.group_id = members.group_id
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
            name='allocation_mode',
            field=models.CharField(default='private', choices=[('private', 'Private (this project only)'), ('shared', 'Shared (this project and all sub-projects)')], max_length=20),
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
    ]
