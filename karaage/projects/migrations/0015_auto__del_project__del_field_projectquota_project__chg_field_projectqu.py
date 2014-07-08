# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('applications', '0023_move_projects'),
        ('usage', '0009_move_projects'),
        ('cache', '0008_move_projects'),
        ('machines', '0015_move_projects'),
    )

    def forwards(self, orm):
        # Removing unique constraint on 'ProjectQuota', fields ['project', 'machine_category']
        db.delete_unique('project_quota', ['project_id', 'machine_category_id'])

        # Deleting model 'Project'
        db.delete_table('project')

        # Removing M2M table for field leaders on 'Project'
        db.delete_table('project_leaders')

        # Deleting field 'ProjectQuota.project'
        db.delete_column('project_quota', 'project_id')

        # Changing field 'ProjectQuota.project_tmp'
        db.alter_column('project_quota', 'project_tmp_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.ProjectTmp']))
        # Adding unique constraint on 'ProjectQuota', fields ['project_tmp', 'machine_category']
        db.create_unique('project_quota', ['project_tmp_id', 'machine_category_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'ProjectQuota', fields ['project_tmp', 'machine_category']
        db.delete_unique('project_quota', ['project_tmp_id', 'machine_category_id'])

        # Adding model 'Project'
        db.create_table('project', (
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('additional_req', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('institute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutes.Institute'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('pid', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_deleted', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('deleted_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='project_deletor', null=True, to=orm['people.Person'], blank=True)),
            ('approved_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='project_approver', null=True, to=orm['people.Person'], blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Group'])),
            ('last_usage', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 9, 17, 0, 0))),
            ('date_approved', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('projects', ['Project'])

        # Adding M2M table for field leaders on 'Project'
        db.create_table('project_leaders', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['projects.project'], null=False)),
            ('person', models.ForeignKey(orm['people.person'], null=False))
        ))
        db.create_unique('project_leaders', ['project_id', 'person_id'])

        # Adding field 'ProjectQuota.project'
        db.add_column('project_quota', 'project',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project']),
                      keep_default=False)

        # Changing field 'ProjectQuota.project_tmp'
        db.alter_column('project_quota', 'project_tmp_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.ProjectTmp'], null=True))
        # Adding unique constraint on 'ProjectQuota', fields ['project', 'machine_category']
        db.create_unique('project_quota', ['project_id', 'machine_category_id'])

    models = {
        'institutes.institute': {
            'Meta': {'ordering': "['name']", 'object_name': 'Institute', 'db_table': "'institute'"},
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'delegate'", 'to': "orm['people.Person']", 'through': "orm['institutes.InstituteDelegate']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
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
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'machines.machinecategory': {
            'Meta': {'object_name': 'MachineCategory', 'db_table': "'machine_category'"},
            'datastore': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'people.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
        'projects.projectquota': {
            'Meta': {'unique_together': "(('project_tmp', 'machine_category'),)", 'object_name': 'ProjectQuota', 'db_table': "'project_quota'"},
            'cap': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'project_tmp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.ProjectTmp']"})
        },
        'projects.projecttmp': {
            'Meta': {'ordering': "['pid']", 'object_name': 'ProjectTmp', 'db_table': "'project'"},
            'additional_req': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'project_approver_tmp'", 'null': 'True', 'to': "orm['people.Person']"}),
            'date_approved': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_deleted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'project_deletor_tmp'", 'null': 'True', 'to': "orm['people.Person']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_tmp'", 'to': "orm['institutes.Institute']"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_usage': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'leaders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'leaders_tmp'", 'symmetrical': 'False', 'to': "orm['people.Person']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 9, 17, 0, 0)'})
        }
    }

    complete_apps = ['projects']
