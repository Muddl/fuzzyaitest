# Generated by Django 4.0.4 on 2022-04-13 20:04

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_game_black_captured_game_white_captured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='black_captured',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=1), null=True, size=10),
        ),
        migrations.AlterField(
            model_name='game',
            name='white_captured',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=1), null=True, size=10),
        ),
    ]
