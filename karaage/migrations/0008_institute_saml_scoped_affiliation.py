# Generated by Django 2.2.2 on 2019-07-03 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("karaage", "0007_auto_20190315_1515"),
    ]

    operations = [
        migrations.AddField(
            model_name="institute",
            name="saml_scoped_affiliation",
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]
