# Generated by Django 4.2.7 on 2023-12-24 13:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("mapdata", "0094_hub_import_prepare"),
    ]

    operations = [
        migrations.AddField(
            model_name="accesspermission",
            name="session_token",
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="accesspermission",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="accesspermission",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("session_token__isnull", True),
                        ("user__isnull", True),
                        _negated=True,
                    ),
                    models.Q(
                        ("session_token__isnull", False),
                        ("user__isnull", False),
                        _negated=True,
                    ),
                ),
                name="permission_needs_user_or_session",
            ),
        ),
    ]