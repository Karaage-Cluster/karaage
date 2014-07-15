# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'TaskCacheForMachineCategory', fields ['date', 'start', 'end', 'machine_category']
        db.delete_unique('cache_taskcacheformachinecategory', ['date', 'start', 'end', 'machine_category_id'])

        # Removing unique constraint on 'TaskCacheForInstitute', fields ['date', 'start', 'end', 'institute', 'machine_category']
        db.delete_unique('cache_taskcacheforinstitute', ['date', 'start', 'end', 'institute_id', 'machine_category_id'])

        # Removing unique constraint on 'TaskMachineCategoryCache', fields ['date', 'start', 'end']
        db.delete_unique('cache_taskmachinecategorycache', ['date', 'start', 'end'])

        # Removing unique constraint on 'TaskCacheForProject', fields ['date', 'start', 'end', 'project', 'machine_category']
        db.delete_unique('cache_taskcacheforproject', ['date', 'start', 'end', 'project_id', 'machine_category_id'])

        # Deleting model 'TaskCacheForProject'
        db.delete_table('cache_taskcacheforproject')

        # Deleting model 'TaskMachineCategoryCache'
        db.delete_table('cache_taskmachinecategorycache')

        # Deleting model 'TaskCacheForInstitute'
        db.delete_table('cache_taskcacheforinstitute')

        # Deleting model 'TaskCacheForMachineCategory'
        db.delete_table('cache_taskcacheformachinecategory')

    def backwards(self, orm):
        # Adding model 'TaskCacheForProject'
        db.create_table('cache_taskcacheforproject', (
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('ready', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
            ('celery_task_id', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('usage', ['TaskCacheForProject'])

        # Adding unique constraint on 'TaskCacheForProject', fields ['date', 'start', 'end', 'project', 'machine_category']
        db.create_unique('cache_taskcacheforproject', ['date', 'start', 'end', 'project_id', 'machine_category_id'])

        # Adding model 'TaskMachineCategoryCache'
        db.create_table('cache_taskmachinecategorycache', (
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('ready', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('celery_task_id', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('usage', ['TaskMachineCategoryCache'])

        # Adding unique constraint on 'TaskMachineCategoryCache', fields ['date', 'start', 'end']
        db.create_unique('cache_taskmachinecategorycache', ['date', 'start', 'end'])

        # Adding model 'TaskCacheForInstitute'
        db.create_table('cache_taskcacheforinstitute', (
            ('institute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutes.Institute'])),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
            ('celery_task_id', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('ready', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('usage', ['TaskCacheForInstitute'])

        # Adding unique constraint on 'TaskCacheForInstitute', fields ['date', 'start', 'end', 'institute', 'machine_category']
        db.create_unique('cache_taskcacheforinstitute', ['date', 'start', 'end', 'institute_id', 'machine_category_id'])

        # Adding model 'TaskCacheForMachineCategory'
        db.create_table('cache_taskcacheformachinecategory', (
            ('ready', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
            ('celery_task_id', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('usage', ['TaskCacheForMachineCategory'])

        # Adding unique constraint on 'TaskCacheForMachineCategory', fields ['date', 'start', 'end', 'machine_category']
        db.create_unique('cache_taskcacheformachinecategory', ['date', 'start', 'end', 'machine_category_id'])

    models = {
        'institutes.institute': {
            'Meta': {'ordering': "['name']", 'object_name': 'Institute', 'db_table': "'institute'"},
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'delegate_for'", 'to': "orm['people.Person']", 'through': "orm['institutes.InstituteDelegate']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'saml_entityid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'institutes.institutedelegate': {
            'Meta': {'object_name': 'InstituteDelegate', 'db_table': "'institutedelegate'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutes.Institute']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'send_email': ('django.db.models.fields.BooleanField', [], {})
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
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
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
            'pid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 3, 4, 0, 0)'})
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
        'usage.cpujob': {
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
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['usage.Queue']", 'null': 'True', 'blank': 'True'}),
            'software': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['software.SoftwareVersion']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'vmem': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'usage.institutecache': {
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
        'usage.machinecache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'machine'),)", 'object_name': 'MachineCache', 'db_table': "'cache_machinecache'"},
            'cpu_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.Machine']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'usage.machinecategorycache': {
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
        'usage.personcache': {
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
        'usage.projectcache': {
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
        'usage.queue': {
            'Meta': {'object_name': 'Queue', 'db_table': "'queue'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'usage.usedmodules': {
            'Meta': {'object_name': 'UsedModules'},
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'jobid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modules': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['usage']
