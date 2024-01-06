# Generated by Django 4.2.7 on 2024-01-06 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0012_userpermissions_grant_unlimited_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermissions',
            name='nonpublic_themes',
            field=models.BooleanField(default=False, verbose_name='show non-public themes in theme selector'),
        ),
    ]
