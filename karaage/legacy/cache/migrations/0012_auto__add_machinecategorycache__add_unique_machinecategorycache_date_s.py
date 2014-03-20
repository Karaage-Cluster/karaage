# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        if not db.dry_run:
            orm.ProjectCache.objects.all().delete()
            orm.PersonCache.objects.all().delete()
            orm.InstituteCache.objects.all().delete()
            orm.MachineCache.objects.all().delete()

        # Adding model 'MachineCategoryCache'
        db.create_table(u'cache_machinecategorycache', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('cpu_hours', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
            ('no_jobs', self.gf('django.db.models.fields.IntegerField')()),
            ('machine_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['machines.MachineCategory'])),
            ('available_time', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=2)),
        ))
        db.send_create_signal(u'cache', ['MachineCategoryCache'])

        # Adding unique constraint on 'MachineCategoryCache', fields ['date', 'start', 'end', 'machine_category']
        db.create_unique(u'cache_machinecategorycache', ['date', 'start', 'end', 'machine_category_id'])

        # Changing field 'ProjectCache.cpu_hours'
        db.alter_column(u'cache_projectcache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=30, decimal_places=2))

        # Changing field 'ProjectCache.no_jobs'
        db.alter_column(u'cache_projectcache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(default=0))

        # Changing field 'PersonCache.cpu_hours'
        db.alter_column(u'cache_personcache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=30, decimal_places=2))

        # Changing field 'PersonCache.no_jobs'
        db.alter_column(u'cache_personcache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(default=0))

        # Changing field 'InstituteCache.cpu_hours'
        db.alter_column(u'cache_institutecache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=30, decimal_places=2))

        # Changing field 'InstituteCache.no_jobs'
        db.alter_column(u'cache_institutecache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(default=0))

        # Changing field 'MachineCache.cpu_hours'
        db.alter_column(u'cache_machinecache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=30, decimal_places=2))

        # Changing field 'MachineCache.no_jobs'
        db.alter_column(u'cache_machinecache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(default=0))

    def backwards(self, orm):
        # Removing unique constraint on 'MachineCategoryCache', fields ['date', 'start', 'end', 'machine_category']
        db.delete_unique(u'cache_machinecategorycache', ['date', 'start', 'end', 'machine_category_id'])

        # Deleting model 'MachineCategoryCache'
        db.delete_table(u'cache_machinecategorycache')

        # Changing field 'ProjectCache.cpu_hours'
        db.alter_column(u'cache_projectcache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=30, decimal_places=2))

        # Changing field 'ProjectCache.no_jobs'
        db.alter_column(u'cache_projectcache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'PersonCache.cpu_hours'
        db.alter_column(u'cache_personcache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=30, decimal_places=2))

        # Changing field 'PersonCache.no_jobs'
        db.alter_column(u'cache_personcache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'InstituteCache.cpu_hours'
        db.alter_column(u'cache_institutecache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=30, decimal_places=2))

        # Changing field 'InstituteCache.no_jobs'
        db.alter_column(u'cache_institutecache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'MachineCache.cpu_hours'
        db.alter_column(u'cache_machinecache', 'cpu_hours', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=30, decimal_places=2))

        # Changing field 'MachineCache.no_jobs'
        db.alter_column(u'cache_machinecache', 'no_jobs', self.gf('django.db.models.fields.IntegerField')(null=True))

    models = {
        u'cache.institutecache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'institute', 'machine_category'),)", 'object_name': 'InstituteCache'},
            'cpu_hours': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['institutes.Institute']"}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'cache.machinecache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'machine'),)", 'object_name': 'MachineCache'},
            'cpu_hours': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machines.Machine']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'cache.machinecategorycache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'machine_category'),)", 'object_name': 'MachineCategoryCache'},
            'available_time': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'cpu_hours': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'cache.personcache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'person', 'project', 'machine_category'),)", 'object_name': 'PersonCache'},
            'cpu_hours': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'cache.projectcache': {
            'Meta': {'unique_together': "(('date', 'start', 'end', 'project', 'machine_category'),)", 'object_name': 'ProjectCache'},
            'cpu_hours': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machines.MachineCategory']"}),
            'no_jobs': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'institutes.institute': {
            'Meta': {'ordering': "['name']", 'object_name': 'Institute', 'db_table': "'institute'"},
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'delegate'", 'to': u"orm['people.Person']", 'through': u"orm['institutes.InstituteDelegate']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'saml_entityid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'institutes.institutedelegate': {
            'Meta': {'object_name': 'InstituteDelegate', 'db_table': "'institutedelegate'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['institutes.Institute']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Person']"}),
            'send_email': ('django.db.models.fields.BooleanField', [], {})
        },
        u'machines.machine': {
            'Meta': {'object_name': 'Machine', 'db_table': "'machine'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['machines.MachineCategory']"}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        u'machines.machinecategory': {
            'Meta': {'object_name': 'MachineCategory', 'db_table': "'machine_category'"},
            'datastore': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'people.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groups'", 'symmetrical': 'False', 'to': u"orm['people.Person']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'people.person': {
            'Meta': {'ordering': "['full_name', 'short_name']", 'object_name': 'Person', 'db_table': "'person'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_approver'", 'null': 'True', 'to': u"orm['people.Person']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'date_approved': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_deleted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_deletor'", 'null': 'True', 'to': u"orm['people.Person']"}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'db_index': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['institutes.Institute']"}),
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
        u'projects.project': {
            'Meta': {'ordering': "['pid']", 'object_name': 'Project', 'db_table': "'project'"},
            'additional_req': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'project_approver'", 'null': 'True', 'to': u"orm['people.Person']"}),
            'date_approved': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_deleted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'project_deletor'", 'null': 'True', 'to': u"orm['people.Person']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['institutes.Institute']"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {}),
            'last_usage': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'leaders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'leaders'", 'symmetrical': 'False', 'to': u"orm['people.Person']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 11, 28, 0, 0)'})
        }
    }

    complete_apps = ['cache']
