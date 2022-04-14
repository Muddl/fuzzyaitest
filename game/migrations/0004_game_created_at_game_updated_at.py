# Generated by Django 4.0.4 on 2022-04-14 13:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_alter_game_black_captured_alter_game_white_captured'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
