# Generated by Django 5.2.1 on 2025-06-01 07:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accident',
            name='note',
        ),
    ]
