# Generated by Django 2.2.10 on 2020-02-28 15:53

from django.db import migrations


def forward(apps, schema_editor):
    person_class = apps.get_model("karaage", "person")
    applicant_class = apps.get_model("kgapplications", "applicant")
    application_class = apps.get_model("kgapplications", "application")

    for application in application_class.objects.all():
        if application.content_type.model == "applicant":
            applicant = applicant_class.objects.get(pk=application.object_id)

            clash = application_class.objects.filter(new_applicant=application.object_id).all()
            if clash.count() > 0:
                applicant.id = None
                applicant.save()

            application.new_applicant = applicant
            application.existing_person = None
        elif application.content_type.model == "person":
            person = person_class.objects.get(pk=application.object_id)
            application.new_applicant = None
            application.existing_person = person
        else:
            raise RuntimeError("oops")
        application.save()


def reverse(apps, schema_editor):
    content_type = apps.get_model("contenttypes", "ContentType")
    person_type = content_type.objects.get(app_label="karaage", model="person")
    applicant_type = content_type.objects.get(app_label="kgapplications", model="applicant")
    application_class = apps.get_model("kgapplications", "application")

    for application in application_class.objects.all():
        if application.existing_person is not None:
            application.content_type = person_type
            application.object_id = application.existing_person.id
        elif application.new_applicant is not None:
            application.content_type = applicant_type
            application.object_id = application.new_applicant.id
        else:
            raise RuntimeError("oops")
        application.save()


class Migration(migrations.Migration):

    dependencies = [
        ("kgapplications", "0009_auto_20200227_1655"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
