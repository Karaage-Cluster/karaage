# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    depends_on = (
        ("admin", "0004_auto__del_logentry"),
        ("applications", "0028_auto__chg_field_applicant_username"),
        ("cache", "0015_auto__del_taskmachinecategorycache__del_unique_taskmachinecategorycach"),
        ("common", "0007_fix_project_logs"),
        ("emails", "0002_auto__del_emailtemplate"),
        ("institutes", "0008_auto__chg_field_institute_name"),
        ("machines", "0021_auto__chg_field_account_username"),
        ("pbsmoab", "0001_initial"),
        ("people", "0024_auto__chg_field_person_username"),
        ("projects", "0018_auto__chg_field_project_pid"),
        ("software", "0013_rename_user_to_person"),
        ("usage", "0013_auto__del_taskcacheforproject__del_unique_taskcacheforproject_date_sta"),
    )

    def forwards(self, orm):
        if not db.dry_run:
            apps = ['admin', 'cache', 'common', 'emails',
                    'institutes', 'machines', 'pbsmoab', 'people', 'projects',
                    ]
            orm['contenttypes.contenttype'].objects \
                .filter(app_label__in=apps).update(app_label='karaage')

    def backwards(self, orm):
        pass

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['contenttypes']
