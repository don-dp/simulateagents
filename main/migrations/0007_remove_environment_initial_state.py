# Generated by Django 5.1.4 on 2025-01-24 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_simulation_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='environment',
            name='initial_state',
        ),
    ]
