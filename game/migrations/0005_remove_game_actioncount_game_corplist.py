# Generated by Django 4.0.4 on 2022-04-19 05:44

from django.db import migrations, models
import game.engine


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_game_created_at_game_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='actioncount',
        ),
        migrations.AddField(
            model_name='game',
            name='corplist',
            field=models.JSONField(default=game.engine.newcorplist),
        ),
    ]
