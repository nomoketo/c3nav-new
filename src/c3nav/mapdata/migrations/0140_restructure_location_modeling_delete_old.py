# Generated by Django 5.1.5 on 2025-01-24 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0139_restructure_location_modeling_1'),
        ('control', '0021_alter_userpermissions_restructured_locations'),
    ]

    operations = [
        # we're done, so we can delete all the _old models
        migrations.DeleteModel(
            name='LocationGroup_Old',
        ),
        migrations.DeleteModel(
            name='Space_Old',
        ),
    ]