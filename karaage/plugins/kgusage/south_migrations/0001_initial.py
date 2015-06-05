# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ('usage', '0013_auto__del_taskcacheforproject__del_unique_taskcacheforproject_date_sta'),
    )

    def forwards(self, orm):
        if not db.dry_run:
            orm['contenttypes.contenttype'].objects.filter(app_label='usage').update(app_label='kgusage')
            orm['contenttypes.contenttype'].objects.filter(app_label='usage_jobs').update(app_label='kgusage')
        db.send_create_signal('kgusage', ['Queue'])
        db.send_create_signal('kgusage', ['CPUJob'])
        db.send_create_signal('kgusage', ['UsedModules'])
        db.send_create_signal('kgusage', ['InstituteCache'])
        db.send_create_signal('kgusage', ['ProjectCache'])
        db.send_create_signal('kgusage', ['PersonCache'])
        db.send_create_signal('kgusage', ['MachineCategoryCache'])
        db.send_create_signal('kgusage', ['MachineCache'])
        return

        # Adding model 'Queue'
        db.create_table('queue', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('kgusage', ['Queue'])

        # Adding model 'CPUJob'
        db.create_table('cpu_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.Account'], null=True, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'], null=True, blank=True)),
            ('machine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.Machine'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kgusage.Queue'], null=True, blank=True)),
            ('cpu_usage', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('mem', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('vmem', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('qtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('etime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('act_wall_time', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('est_wall_time', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('jobid', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True, blank=True)),
            ('cores', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('list_mem', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('list_pmem', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('list_vmem', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('list_pvmem', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('exit_status', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('jobname', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('kgusage', ['CPUJob'])

        # Adding M2M table for field software on 'CPUJob'
        db.create_table('cpu_job_software', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cpujob', models.ForeignKey(orm['kgusage.cpujob'], null=False)),
            ('softwareversion', models.ForeignKey(orm['software.softwareversion'], null=False))
        ))
        db.create_unique('cpu_job_software', ['cpujob_id', 'softwareversion_id'])

        # Adding model 'UsedModules'
        db.create_table('jobs_usedmodules', (
            ('jobid', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modules', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('kgusage', ['UsedModules'])

        # Adding model 'InstituteCache'
        db.create_table('cache_institutecache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('cpu_time', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
            ('no_jobs', self.gf('django.db.models.fields.IntegerField')()),
            ('institute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutes.Institute'])),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
        ))
        db.send_create_signal('kgusage', ['InstituteCache'])

        # Adding unique constraint on 'InstituteCache', fields ['date', 'start', 'end', 'institute', 'machine_category']
        db.create_unique('cache_institutecache', ['date', 'start', 'end', 'institute_id', 'machine_category_id'])

        # Adding model 'ProjectCache'
        db.create_table('cache_projectcache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('cpu_time', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
            ('no_jobs', self.gf('django.db.models.fields.IntegerField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
        ))
        db.send_create_signal('kgusage', ['ProjectCache'])

        # Adding unique constraint on 'ProjectCache', fields ['date', 'start', 'end', 'project', 'machine_category']
        db.create_unique('cache_projectcache', ['date', 'start', 'end', 'project_id', 'machine_category_id'])

        # Adding model 'PersonCache'
        db.create_table('cache_personcache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('cpu_time', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
            ('no_jobs', self.gf('django.db.models.fields.IntegerField')()),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
        ))
        db.send_create_signal('kgusage', ['PersonCache'])

        # Adding unique constraint on 'PersonCache', fields ['date', 'start', 'end', 'person', 'project', 'machine_category']
        db.create_unique('cache_personcache', ['date', 'start', 'end', 'person_id', 'project_id', 'machine_category_id'])

        # Adding model 'MachineCategoryCache'
        db.create_table('cache_machinecategorycache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('cpu_time', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
            ('no_jobs', self.gf('django.db.models.fields.IntegerField')()),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
            ('available_time', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
        ))
        db.send_create_signal('kgusage', ['MachineCategoryCache'])

        # Adding unique constraint on 'MachineCategoryCache', fields ['date', 'start', 'end', 'machine_category']
        db.create_unique('cache_machinecategorycache', ['date', 'start', 'end', 'machine_category_id'])

        # Adding model 'MachineCache'
        db.create_table('cache_machinecache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('cpu_time', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
            ('no_jobs', self.gf('django.db.models.fields.IntegerField')()),
            ('machine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.Machine'])),
        ))
        db.send_create_signal('kgusage', ['MachineCache'])

        # Adding unique constraint on 'MachineCache', fields ['date', 'start', 'end', 'machine']
        db.create_unique('cache_machinecache', ['date', 'start', 'end', 'machine_id'])

    def backwards(self, orm):
        if not db.dry_run:
            orm['contenttypes.contenttype'].objects.filter(app_label='kgusage').update(app_label='usage')
        return

        # Removing unique constraint on 'MachineCache', fields ['date', 'start', 'end', 'machine']
        db.delete_unique('cache_machinecache', ['date', 'start', 'end', 'machine_id'])

        # Removing unique constraint on 'MachineCategoryCache', fields ['date', 'start', 'end', 'machine_category']
        db.delete_unique('cache_machinecategorycache', ['date', 'start', 'end', 'machine_category_id'])

        # Removing unique constraint on 'PersonCache', fields ['date', 'start', 'end', 'person', 'project', 'machine_category']
        db.delete_unique('cache_personcache', ['date', 'start', 'end', 'person_id', 'project_id', 'machine_category_id'])

        # Removing unique constraint on 'ProjectCache', fields ['date', 'start', 'end', 'project', 'machine_category']
        db.delete_unique('cache_projectcache', ['date', 'start', 'end', 'project_id', 'machine_category_id'])

        # Removing unique constraint on 'InstituteCache', fields ['date', 'start', 'end', 'institute', 'machine_category']
        db.delete_unique('cache_institutecache', ['date', 'start', 'end', 'institute_id', 'machine_category_id'])

        # Deleting model 'Queue'
        db.delete_table('queue')

        # Deleting model 'CPUJob'
        db.delete_table('cpu_job')

        # Removing M2M table for field software on 'CPUJob'
        db.delete_table('cpu_job_software')

        # Deleting model 'UsedModules'
        db.delete_table('jobs_usedmodules')

        # Deleting model 'InstituteCache'
        db.delete_table('cache_institutecache')

        # Deleting model 'ProjectCache'
        db.delete_table('cache_projectcache')

        # Deleting model 'PersonCache'
        db.delete_table('cache_personcache')

        # Deleting model 'MachineCategoryCache'
        db.delete_table('cache_machinecategorycache')

        # Deleting model 'MachineCache'
        db.delete_table('cache_machinecache')

    models = {
        'institutes.institute': {
            'Meta': {'ordering': "['name']", 'object_name': 'Institute', 'db_table': "'institute'"},
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'delegate_for'", 'to': "orm['people.Person']", 'through': "orm['institutes.InstituteDelegate']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'saml_entityid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'institutes.institutedelegate': {
            'Meta': {'object_name': 'InstituteDelegate', 'db_table': "'institutedelegate'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutes.Institute']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'send_email': ('django.db.models.fields.BooleanField', [], {})
        },
        'kgusage.cpujob': {
            'Meta': {'ordering': "['-date']", 'object_name': 'CPUJob', 'db_table': "'cpu_job'"},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.Account']", 'null': 'True', 'blank': 'True'}),
            'act_wall_time': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cores': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cpu_usage': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'est_wall_time': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'etime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'exit_status': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'jobname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'list_mem': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'list_pmem': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'list_pvmem': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'list_vmem': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.Machine']", 'null': 'True', 'blank': 'True'}),
            'mem': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']", 'null': 'True', 'blank': 'True'}),
            'qtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kgusage.Queue']", 'null': 'True', 'blank': 'True'}),
            'software': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['software.SoftwareVersion']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'vmem': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'kgusage.institutecache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'institute', 'machine_category'),)", 'object_name': 'InstituteCache', 'db_table': "'cache_institutecache'"},
            'cpu_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutes.Institute']"}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'kgusage.machinecache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'machine'),)", 'object_name': 'MachineCache', 'db_table': "'cache_machinecache'"},
            'cpu_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.Machine']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'kgusage.machinecategorycache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'machine_category'),)", 'object_name': 'MachineCategoryCache', 'db_table': "'cache_machinecategorycache'"},
            'available_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'cpu_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'kgusage.personcache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'person', 'project', 'machine_category'),)", 'object_name': 'PersonCache', 'db_table': "'cache_personcache'"},
            'cpu_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'kgusage.projectcache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'project', 'machine_category'),)", 'object_name': 'ProjectCache', 'db_table': "'cache_projectcache'"},
            'cpu_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'kgusage.queue': {
            'Meta': {'object_name': 'Queue', 'db_table': "'queue'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'kgusage.usedmodules': {
            'Meta': {'object_name': 'UsedModules'},
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'jobid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modules': ('django.db.models.fields.TextField', [], {})
        },
        'machines.account': {
            'Meta': {'ordering': "['person']", 'object_name': 'Account', 'db_table': "'account'"},
            'date_created': ('django.db.models.fields.DateField', [], {}),
            'date_deleted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'default_project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']", 'null': 'True', 'blank': 'True'}),
            'disk_quota': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'extra_data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'foreign_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'shell': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'machines.machine': {
            'Meta': {'object_name': 'Machine', 'db_table': "'machine'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'mem_per_core': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'no_cpus': ('django.db.models.fields.IntegerField', [], {}),
            'no_nodes': ('django.db.models.fields.IntegerField', [], {}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pbs_server_host': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'scaling_factor': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'machines.machinecategory': {
            'Meta': {'object_name': 'MachineCategory', 'db_table': "'machine_category'"},
            'datastore': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'people.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extra_data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'foreign_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groups'", 'symmetrical': 'False', 'to': "orm['people.Person']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'people.person': {
            'Meta': {'ordering': "['full_name', 'short_name']", 'object_name': 'Person', 'db_table': "'person'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_approver'", 'null': 'True', 'to': "orm['people.Person']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'date_approved': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_deleted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_deletor'", 'null': 'True', 'to': "orm['people.Person']"}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'db_index': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutes.Institute']"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_systemuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_usage': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'legacy_ldap_password': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'login_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'saml_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'supervisor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'projects.project': {
            'Meta': {'ordering': "['pid']", 'object_name': 'Project', 'db_table': "'project'"},
            'additional_req': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'project_approver'", 'null': 'True', 'to': "orm['people.Person']"}),
            'date_approved': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_deleted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'project_deletor'", 'null': 'True', 'to': "orm['people.Person']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutes.Institute']"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_usage': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'leaders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'leads'", 'symmetrical': 'False', 'to': "orm['people.Person']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 7, 15, 0, 0)'})
        },
        'software.software': {
            'Meta': {'ordering': "['name']", 'object_name': 'Software', 'db_table': "'software'"},
            'academic_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['software.SoftwareCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']", 'null': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'restricted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tutorial_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'software.softwarecategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'SoftwareCategory', 'db_table': "'software_category'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'software.softwareversion': {
            'Meta': {'ordering': "['-version']", 'object_name': 'SoftwareVersion', 'db_table': "'software_version'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_used': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'machines': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['machines.Machine']", 'symmetrical': 'False'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'software': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['software.Software']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
    }

    complete_apps = ['kgusage']
