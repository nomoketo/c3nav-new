# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-10 13:30
from __future__ import unicode_literals

import c3nav.mapdata.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0069_auto_20170510_1329'),
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geometry', c3nav.mapdata.fields.GeometryField(geomtype='point')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='mapdata.Space', verbose_name='space')),
            ],
            options={
                'verbose_name': 'Point',
                'verbose_name_plural': 'Points',
                'default_related_name': 'points',
            },
        ),
    ]
