# Generated by Django 5.1.4 on 2025-01-22 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_environment_initial_state_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulation',
            name='title',
            field=models.CharField(default='comment', max_length=200),
            preserve_default=False,
        ),
    ]
