# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import connection


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailTemplate'
        cursor = connection.cursor()
        if 'emails_emailtemplate' not in connection.introspection.get_table_list(cursor):
            db.create_table('emails_emailtemplate', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
                ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
                ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
                ('body', self.gf('django.db.models.fields.TextField')()),
            ))
            db.send_create_signal('emails', ['EmailTemplate'])

    def backwards(self, orm):
        # Deleting model 'EmailTemplate'
        db.delete_table('emails_emailtemplate')

    models = {
        'emails.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['emails']
