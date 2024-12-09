# Generated by Django 5.0.8 on 2024-12-09 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0112_alter_dataoverlay_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationgroup',
            name='can_report_mistake',
            field=models.CharField(choices=[('allow', "don't offer"), ('reject', 'reject for all locations with this group')], default='allow', max_length=16, verbose_name='report mistakes'),
        ),
    ]
