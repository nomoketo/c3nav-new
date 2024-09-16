# Generated by Django 5.0.8 on 2024-08-26 09:46

import c3nav.editor.operations
import django.core.serializers.json
import django_pydantic_field.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0003_changedobject_json_encoder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='changeset',
            name='last_cleaned_with',
        ),
        migrations.AddField(
            model_name='changeset',
            name='changes',
            field=django_pydantic_field.fields.PydanticSchemaField(config=None, default=c3nav.editor.operations.CollectedOperations, encoder=django.core.serializers.json.DjangoJSONEncoder, schema=c3nav.editor.operations.CollectedOperations),
        ),
        migrations.DeleteModel(
            name='ChangedObject',
        ),
    ]
