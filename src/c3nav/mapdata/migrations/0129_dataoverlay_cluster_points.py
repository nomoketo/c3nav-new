# Generated by Django 5.1.3 on 2024-12-26 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0128_space_identifyable'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataoverlay',
            name='cluster_points',
            field=models.BooleanField(default=False, verbose_name='cluster points together when zoomed out'),
        ),
    ]