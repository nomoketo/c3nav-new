# Generated by Django 4.2.7 on 2023-12-11 13:11

from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    GroundAltitude = apps.get_model('mapdata', 'GroundAltitude')
    AltitudeMarker = apps.get_model('mapdata', 'AltitudeMarker')
    grouped = {}
    for marker in AltitudeMarker.objects.select_related('space'):
        grouped.setdefault(marker.id, []).append(marker)
    for altitude, markers in grouped.items():
        altitude = GroundAltitude.objects.create(
            altitude=altitude,
            name="(converted "+",".join(str(marker.id) for marker in markers)+") "+",".join(
                str(space.title)
                for space in set(m.space for m in markers)
                if space.title
            ),
        )
        altitude.altitudemarkers.set(markers)


def backwards_func(apps, schema_editor):
    AltitudeMarker = apps.get_model('mapdata', 'AltitudeMarker')
    for marker in AltitudeMarker.objects.select_related('groundaltitude'):
        marker.altitude = marker.groundaltitude.altitude
        marker.save()



class Migration(migrations.Migration):
    dependencies = [
        ("mapdata", "0088_remove_position_api_secret"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroundAltitude",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=70, unique=True, verbose_name="Name"),
                ),
                (
                    "altitude",
                    models.DecimalField(
                        decimal_places=2, max_digits=6, verbose_name="altitude"
                    ),
                ),
            ],
            options={
                "verbose_name": "Ground Altitude",
                "verbose_name_plural": "Ground altitudes",
                "default_related_name": "groundaltitudes",
            },
        ),
        migrations.AddField(
            model_name="altitudemarker",
            name="groundaltitude",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="mapdata.groundaltitude",
                verbose_name="altitude",
            ),
        ),
        migrations.RunPython(forwards_func, backwards_func),
        migrations.RemoveField(
            model_name="altitudemarker",
            name="altitude",
        ),
        migrations.AlterField(
            model_name="altitudemarker",
            name="groundaltitude",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="mapdata.groundaltitude",
                verbose_name="altitude",
            ),
        ),
    ]
