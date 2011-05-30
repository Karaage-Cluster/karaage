# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'ProjectJoinRequest'
        db.delete_table('requests_projectjoinrequest')

        # Deleting model 'ProjectCreateRequest'
        db.delete_table('requests_projectcreaterequest')
    
    
    def backwards(self, orm):
        
        # Adding model 'ProjectJoinRequest'
        db.create_table('requests_projectjoinrequest', (
            ('leader_approved', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
        ))
        db.send_create_signal('requests', ['ProjectJoinRequest'])

        # Adding model 'ProjectCreateRequest'
        db.create_table('requests_projectcreaterequest', (
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('needs_account', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('requests', ['ProjectCreateRequest'])
    
    
    models = {
        
    }
    
    complete_apps = ['requests']
