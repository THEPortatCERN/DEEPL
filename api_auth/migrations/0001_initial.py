# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-29 08:42
from __future__ import unicode_literals

import api_auth.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verified', models.BooleanField(default=False)),
                ('verification_key', models.CharField(default=api_auth.models.generate_verification_key, max_length=15)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('occupation', models.CharField(blank=True, max_length=200)),
                ('organization', models.CharField(blank=True, max_length=200)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=uuid.uuid4, max_length=64, unique=True)),
                ('is_test', models.BooleanField(default=True)),
                ('api_calls', models.IntegerField(default=0)),
                ('call_limit', models.IntegerField(default=10000)),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api_auth.Profile')),
            ],
        ),
    ]
