# Generated by Django 4.2.6 on 2023-11-01 21:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("karaage", "0010_project_rcao"),
    ]

    operations = [
        migrations.AddField(
            model_name="institute",
            name="project_prefix",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]