# Generated by Django 2.1.3 on 2019-11-27 16:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0008_validate_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wifimeasurement',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wifi_measurements', to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
    ]