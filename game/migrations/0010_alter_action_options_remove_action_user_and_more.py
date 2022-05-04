# Generated by Django 4.0.4 on 2022-05-04 21:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_alter_game_black_captured_alter_game_white_captured_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ('created_at',)},
        ),
        migrations.RemoveField(
            model_name='action',
            name='user',
        ),
        migrations.AddField(
            model_name='action',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]