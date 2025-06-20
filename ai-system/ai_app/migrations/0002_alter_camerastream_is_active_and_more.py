# Generated by Django 5.2.1 on 2025-06-01 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camerastream',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='camerastream',
            name='stream_url',
            field=models.CharField(max_length=3000),
        ),
    ]
