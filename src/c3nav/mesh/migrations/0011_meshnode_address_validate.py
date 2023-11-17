# Generated by Django 4.2.1 on 2023-11-10 17:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mesh", "0010_otaupdate_otaupdaterecipient"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meshnode",
            name="address",
            field=models.CharField(
                max_length=17,
                primary_key=True,
                serialize=False,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_macaddress",
                        message="Must be a lower-case mac address",
                        regex="^([a-f0-9]{2}:){5}[a-f0-9]{2}$",
                    )
                ],
                verbose_name="mac address",
            ),
        ),
    ]