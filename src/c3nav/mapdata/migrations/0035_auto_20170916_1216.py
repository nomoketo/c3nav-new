# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-16 12:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0034_auto_20170807_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationgroup',
            name='color',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='background color'),
        ),
    ]
