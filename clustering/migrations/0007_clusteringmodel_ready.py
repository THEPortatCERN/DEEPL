# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-23 09:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clustering', '0006_doc2vecmodel_extra_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusteringmodel',
            name='ready',
            field=models.BooleanField(default=False),
        ),
    ]
