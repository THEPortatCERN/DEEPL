# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-30 10:26
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classifier', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusteringModel',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='classifier.BaseModel')),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(editable=False, max_length=20, unique=True)),
                ('_data', models.BinaryField()),
                ('n_clusters', models.IntegerField()),
                ('extra_info', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            bases=('classifier.basemodel',),
        ),
    ]
