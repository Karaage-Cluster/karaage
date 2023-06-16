# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 18:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kgapplications", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicant",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name="applicant",
            name="username",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="projectapplication",
            name="machine_categories",
            field=models.ManyToManyField(blank=True, to="karaage.MachineCategory"),
        ),
    ]
