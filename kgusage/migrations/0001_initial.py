# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0001_initial'),
        ('kgsoftware', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CPUJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50, null=True, blank=True)),
                ('date', models.DateField(db_index=True, null=True, blank=True)),
                ('cpu_usage', models.BigIntegerField(null=True, blank=True)),
                ('mem', models.BigIntegerField(null=True, blank=True)),
                ('vmem', models.BigIntegerField(null=True, blank=True)),
                ('ctime', models.DateTimeField(null=True, blank=True)),
                ('qtime', models.DateTimeField(null=True, blank=True)),
                ('etime', models.DateTimeField(null=True, blank=True)),
                ('start', models.DateTimeField(null=True, blank=True)),
                ('act_wall_time', models.BigIntegerField(null=True, blank=True)),
                ('est_wall_time', models.BigIntegerField(null=True, blank=True)),
                ('jobid', models.CharField(max_length=50, unique=True, null=True, blank=True)),
                ('cores', models.BigIntegerField(null=True, blank=True)),
                ('list_mem', models.BigIntegerField(null=True, blank=True)),
                ('list_pmem', models.BigIntegerField(null=True, blank=True)),
                ('list_vmem', models.BigIntegerField(null=True, blank=True)),
                ('list_pvmem', models.BigIntegerField(null=True, blank=True)),
                ('exit_status', models.BigIntegerField(null=True, blank=True)),
                ('jobname', models.CharField(max_length=256, null=True, blank=True)),
                ('account', models.ForeignKey(blank=True, to='karaage.Account', null=True)),
                ('machine', models.ForeignKey(blank=True, to='karaage.Machine', null=True)),
                ('project', models.ForeignKey(blank=True, to='karaage.Project', null=True)),
            ],
            options={
                'ordering': ['-date'],
                'db_table': 'cpu_job',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstituteCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('cpu_time', models.DecimalField(max_digits=30, decimal_places=2)),
                ('no_jobs', models.IntegerField()),
                ('institute', models.ForeignKey(to='karaage.Institute')),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
            ],
            options={
                'db_table': 'cache_institutecache',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MachineCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('cpu_time', models.DecimalField(max_digits=30, decimal_places=2)),
                ('no_jobs', models.IntegerField()),
                ('machine', models.ForeignKey(to='karaage.Machine')),
            ],
            options={
                'db_table': 'cache_machinecache',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MachineCategoryCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('cpu_time', models.DecimalField(max_digits=30, decimal_places=2)),
                ('no_jobs', models.IntegerField()),
                ('available_time', models.DecimalField(max_digits=30, decimal_places=2)),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
            ],
            options={
                'db_table': 'cache_machinecategorycache',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('cpu_time', models.DecimalField(max_digits=30, decimal_places=2)),
                ('no_jobs', models.IntegerField()),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
                ('person', models.ForeignKey(to='karaage.Person')),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'db_table': 'cache_personcache',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('cpu_time', models.DecimalField(max_digits=30, decimal_places=2)),
                ('no_jobs', models.IntegerField()),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'db_table': 'cache_projectcache',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'db_table': 'queue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UsedModules',
            fields=[
                ('jobid', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('modules', models.TextField()),
            ],
            options={
                'db_table': 'usage_usedmodules',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='projectcache',
            unique_together=set([('date', 'start', 'end', 'project', 'machine_category')]),
        ),
        migrations.AlterUniqueTogether(
            name='personcache',
            unique_together=set([('date', 'start', 'end', 'person', 'project', 'machine_category')]),
        ),
        migrations.AlterUniqueTogether(
            name='machinecategorycache',
            unique_together=set([('date', 'start', 'end', 'machine_category')]),
        ),
        migrations.AlterUniqueTogether(
            name='machinecache',
            unique_together=set([('date', 'start', 'end', 'machine')]),
        ),
        migrations.AlterUniqueTogether(
            name='institutecache',
            unique_together=set([('date', 'start', 'end', 'institute', 'machine_category')]),
        ),
        migrations.AddField(
            model_name='cpujob',
            name='queue',
            field=models.ForeignKey(blank=True, to='kgusage.Queue', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cpujob',
            name='software',
            field=models.ManyToManyField(to='kgsoftware.SoftwareVersion', null=True, blank=True),
            preserve_default=True,
        ),
    ]
