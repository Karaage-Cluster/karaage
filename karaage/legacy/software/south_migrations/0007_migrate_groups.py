# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import DataMigration

from karaage.datastores import get_kg27_datastore


class Migration(DataMigration):

    def forwards(self, orm):
        datastore = get_kg27_datastore()
        if datastore is None:
            return
        for software in orm.SoftwarePackage.objects.iterator():
            if software.gid is None:
                software.group = None
                software.save()
            else:
                lgroup = datastore._groups().get(gidNumber=software.gid)

                if not db.dry_run:
                    group, c = orm['people.group'].objects.get_or_create(name=lgroup.cn)
                    software.group = group
                    software.save()

                    for member in lgroup.secondary_accounts.iterator():
                        person = orm['people.person'].objects.get(user__username=member.uid)
                        person.groups.add(group)

    def backwards(self, orm):
        datastore = get_kg27_datastore()
        if datastore is None:
            return
        for software in orm.SoftwarePackage.objects.iterator():
            lgroup = datastore._groups().get(cn=software.group.name)
            software.gid = lgroup.gidNumber
            software.save()

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        'machines.machine': {
            'Meta': {'object_name': 'Machine', 'db_table': "'machine'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['machines.MachineCategory']"}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mem_per_core': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'no_cpus': ('django.db.models.fields.IntegerField', [], {}),
            'no_nodes': ('django.db.models.fields.IntegerField', [], {}),
            'pbs_server_host': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'scaling_factor': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'machines.machinecategory': {
            'Meta': {'object_name': 'MachineCategory', 'db_table': "'machine_category'"},
            'datastore': ('django.db.models.fields.CharField', [], {'default': "'karaage.datastores.openldap_datastore'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'people.group': {
            'Meta': {'object_name': 'Group'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groups'", 'symmetrical': 'False', 'to': "orm['people.Person']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'people.person': {
            'Meta': {'object_name': 'Person', 'db_table': "'person'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_approver'", 'null': 'True', 'to': "orm['people.Person']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'date_approved': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_deleted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_deletor'", 'null': 'True', 'to': "orm['people.Person']"}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutes.Institute']"}),
            'is_systemuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_usage': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'login_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'saml_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'supervisor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'software.softwareaccessrequest': {
            'Meta': {'object_name': 'SoftwareAccessRequest', 'db_table': "'software_access_request'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'request_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'software_license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['software.SoftwareLicense']"})
        },
        'software.softwarecategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'SoftwareCategory', 'db_table': "'software_category'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'software.softwarelicense': {
            'Meta': {'ordering': "['-version']", 'object_name': 'SoftwareLicense', 'db_table': "'software_license'"},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['software.SoftwarePackage']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'software.softwarelicenseagreement': {
            'Meta': {'object_name': 'SoftwareLicenseAgreement', 'db_table': "'software_license_agreement'"},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['software.SoftwareLicense']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"})
        },
        'software.softwarepackage': {
            'Meta': {'ordering': "['name']", 'object_name': 'SoftwarePackage', 'db_table': "'software_package'"},
            'academic_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['software.SoftwareCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Group']", 'null': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'restricted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tutorial_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'software.softwareversion': {
            'Meta': {'ordering': "['-version']", 'object_name': 'SoftwareVersion', 'db_table': "'software_version'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_used': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'machines': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['machines.Machine']", 'symmetrical': 'False'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['software.SoftwarePackage']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['software']
    symmetrical = True
