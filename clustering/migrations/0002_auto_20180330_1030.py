# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-30 10:30
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clustering', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clusteringmodel',
            name='extra_info',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
    ]
