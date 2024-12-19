# Generated by Django 5.0.8 on 2024-12-19 10:55

import c3nav.mapdata.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0121_level_level_index_alter_level_short_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationgroup',
            name='external_url',
            field=models.URLField(blank=True, null=True, verbose_name='external URL'),
        ),
        migrations.AddField(
            model_name='locationgroup',
            name='external_url_label',
            field=c3nav.mapdata.fields.I18nField(blank=True, fallback_any=True, fallback_value='', plural_name='external_url_labels', verbose_name='external URL label'),
        ),
    ]
