# Generated by Django 4.0.4 on 2022-05-04 19:35

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0008_alter_game_readytoblitz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='black_captured',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=1), default=[], size=10),
        ),
        migrations.AlterField(
            model_name='game',
            name='white_captured',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=1), default=[], size=10),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('lobby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='game.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='game.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
