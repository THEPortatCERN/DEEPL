# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-18 06:53
from __future__ import unicode_literals

from django.db import migrations

import requests


def populate_countries(apps, schema_editor):
    Country = apps.get_model('core', 'Country')
    # get data from source
    url = 'http://vocabulary.unocha.org/json/beta-v1/countries.json'

    resp = requests.get(url)
    data = resp.json()
    countries_info = data['data']

    Country.objects.bulk_create([
        Country(
            name=info['label']['default'],
            iso2=info.get('iso2') or '',
            iso3=info.get('iso3') or '',
        )
        for info in countries_info
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_countries),
    ]